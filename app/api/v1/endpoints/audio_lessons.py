"""
API Endpoints para Lecciones de Audio
======================================

Endpoints para gestionar lecciones de audio con sincronización de texto:
- CRUD de lecciones
- Subida de archivos de audio
- Procesamiento con Gentle
- Streaming de audio
- Tracking de progreso del estudiante
"""

import os
import json
import logging
from typing import Optional, List
from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, 
    Form, Query, BackgroundTasks, status
)
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.models import Usuario, AudioLesson, Estudiante
from app.schemas.audio_lesson import (
    AudioLessonCreate, AudioLessonUpdate, AudioLessonResponse,
    AudioLessonDetail, AudioLessonList, AudioLessonStatus,
    StudentAudioProgressCreate, StudentAudioProgressResponse,
    StudentLessonWithProgress, ProcessAudioRequest, ProcessAudioResponse,
    TimestampsData
)
from app.services.audio_lesson_service import audio_lesson_service, AudioLessonServiceError
from app.services.audio_storage_service import audio_storage_service, AudioStorageError
from app.services.gentle_service import gentle_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Health Check ====================

@router.get("/health", tags=["Audio Lessons"])
async def check_gentle_health():
    """
    Verifica el estado del servicio Gentle.
    
    Returns:
        Estado del servicio de alineación
    """
    is_healthy = await gentle_service.check_health()
    
    return {
        "gentle_available": is_healthy,
        "gentle_url": gentle_service.gentle_url,
        "message": "Gentle is ready" if is_healthy else "Gentle service is not available"
    }


# ==================== CRUD Endpoints ====================

@router.post("/", response_model=AudioLessonResponse, status_code=status.HTTP_201_CREATED)
async def create_audio_lesson(
    lesson_data: AudioLessonCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva lección de audio.
    
    El audio se puede subir después usando el endpoint de upload.
    """
    try:
        db_lesson = audio_lesson_service.create_lesson(db, lesson_data)
        return _lesson_to_response(db_lesson)
    except Exception as e:
        logger.error(f"Error creating lesson: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=AudioLessonList)
def list_audio_lessons(
    modulo_id: Optional[int] = Query(None, description="Filtrar por módulo"),
    curso_id: Optional[int] = Query(None, description="Filtrar por curso"),
    estado: Optional[AudioLessonStatus] = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista lecciones de audio con paginación y filtros.
    """
    logger.info(f"Listing lessons. Filters: modulo_id={modulo_id}, curso_id={curso_id}, estado={estado}, active_only (implicit)=True")
    
    skip = (page - 1) * page_size
    
    lessons = audio_lesson_service.get_lessons(
        db,
        modulo_id=modulo_id,
        curso_id=curso_id,
        estado=estado,
        skip=skip,
        limit=page_size
    )
    
    total = audio_lesson_service.count_lessons(
        db,
        modulo_id=modulo_id,
        curso_id=curso_id,
        estado=estado
    )
    
    return AudioLessonList(
        items=[_lesson_to_response(l) for l in lessons],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{lesson_id}", response_model=AudioLessonDetail)
def get_audio_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene una lección de audio con todos sus detalles incluyendo timestamps.
    """
    lesson_data = audio_lesson_service.get_lesson_with_details(db, lesson_id)
    
    if not lesson_data:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Parsear timestamps si existen
    timestamps = None
    if lesson_data.get("timestamps_json"):
        try:
            if isinstance(lesson_data["timestamps_json"], str):
                timestamps = json.loads(lesson_data["timestamps_json"])
            else:
                timestamps = lesson_data["timestamps_json"]
        except:
            pass
    
    return AudioLessonDetail(
        id=lesson_data["id"],
        titulo=lesson_data["titulo"],
        descripcion=lesson_data["descripcion"],
        modulo_id=lesson_data["modulo_id"],
        curso_id=lesson_data["curso_id"],
        audio_url=f"/api/v1/audio-lessons/{lesson_id}/stream" if lesson_data["audio_url"] else None,
        audio_duration_ms=lesson_data["audio_duration_ms"],
        estado=lesson_data["estado"],
        orden=lesson_data["orden"],
        activo=lesson_data["activo"],
        created_at=lesson_data["created_at"],
        updated_at=lesson_data["updated_at"],
        transcript_text=lesson_data["transcript_text"],
        timestamps_json=timestamps,
        modulo_nombre=lesson_data.get("modulo_nombre"),
        curso_nombre=lesson_data.get("curso_nombre")
    )


@router.put("/{lesson_id}", response_model=AudioLessonResponse)
def update_audio_lesson(
    lesson_id: int,
    lesson_data: AudioLessonUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza una lección de audio.
    """
    db_lesson = audio_lesson_service.update_lesson(db, lesson_id, lesson_data)
    
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    return _lesson_to_response(db_lesson)


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_audio_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina una lección de audio (soft delete).
    """
    success = audio_lesson_service.delete_lesson(db, lesson_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Lesson not found")


# ==================== Audio Upload & Streaming ====================

@router.post("/{lesson_id}/upload-audio", response_model=AudioLessonResponse)
async def upload_audio_file(
    lesson_id: int,
    audio: UploadFile = File(..., description="Archivo de audio (MP3, WAV, etc.)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Sube un archivo de audio para una lección existente.
    
    Formatos soportados: MP3, WAV, OGG, FLAC, M4A, AAC
    Tamaño máximo: 50 MB
    """
    # Verificar que la lección existe
    db_lesson = audio_lesson_service.get_lesson(db, lesson_id)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    try:
        # Guardar el archivo
        relative_path, file_size = await audio_storage_service.save_audio_file(
            audio, lesson_id
        )
        
        # Actualizar la lección con la URL del audio
        db_lesson = audio_lesson_service.set_audio_url(db, lesson_id, relative_path)
        
        logger.info(f"Uploaded audio for lesson {lesson_id}: {relative_path} ({file_size} bytes)")
        
        return _lesson_to_response(db_lesson)
    
    except AudioStorageError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{lesson_id}/stream")
async def stream_audio(
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """
    Streaming del archivo de audio con soporte para Range requests.
    
    Esto permite que los reproductores de audio soliciten partes específicas
    del archivo (seeking).
    """
    db_lesson = audio_lesson_service.get_lesson(db, lesson_id)
    
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    if not db_lesson.audio_url:
        raise HTTPException(status_code=404, detail="Lesson has no audio file")
    
    try:
        logger.info(f"Streaming audio for lesson {lesson_id}. URL: {db_lesson.audio_url}")
        file_info = audio_storage_service.get_file_info(db_lesson.audio_url)
        logger.info(f"File info found: {file_info}")
        
        return FileResponse(
            path=file_info["path"],
            media_type=file_info["mime_type"],
            filename=f"lesson_{lesson_id}.mp3"
        )
    except AudioStorageError as e:
        logger.error(f"AudioStorageError for lesson {lesson_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error streaming lesson {lesson_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lesson_id}/timestamps")
def get_lesson_timestamps(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene solo los timestamps de una lección.
    
    Este endpoint es optimizado para la app Android que solo necesita
    los timestamps después de descargar el audio.
    """
    db_lesson = audio_lesson_service.get_lesson(db, lesson_id)
    
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    if not db_lesson.timestamps_json:
        raise HTTPException(
            status_code=404, 
            detail="Lesson has no timestamps. Process the audio first."
        )
    
    try:
        timestamps = json.loads(db_lesson.timestamps_json)
        return timestamps
    except:
        raise HTTPException(status_code=500, detail="Error parsing timestamps")


# ==================== Audio Processing ====================

@router.post("/{lesson_id}/process", response_model=ProcessAudioResponse)
async def process_audio_lesson(
    lesson_id: int,
    request: ProcessAudioRequest = ProcessAudioRequest(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Procesa el audio de una lección con Gentle para generar timestamps.
    
    Este proceso:
    1. Toma el archivo de audio y el texto de la lección
    2. Envía ambos a Gentle para alineación forzada
    3. Guarda los timestamps resultantes en la base de datos
    
    El proceso puede tomar varios segundos dependiendo de la duración del audio.
    """
    try:
        result = await audio_lesson_service.process_audio_with_gentle(
            db, lesson_id, force_reprocess=request.force_reprocess
        )
        
        return ProcessAudioResponse(
            success=result["success"],
            message=result["message"],
            lesson_id=lesson_id,
            estado=result["estado"],
            words_count=result.get("words_count"),
            duration_ms=result.get("duration_ms")
        )
    
    except AudioLessonServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Student Progress ====================

@router.post("/{lesson_id}/progress", response_model=StudentAudioProgressResponse)
def update_student_progress(
    lesson_id: int,
    progress_data: StudentAudioProgressCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza el progreso de reproducción de un estudiante.
    
    Este endpoint debe llamarse periódicamente desde la app Android
    para guardar la posición de reproducción actual.
    """
    # Verificar que la lección existe
    db_lesson = audio_lesson_service.get_lesson(db, lesson_id)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Obtener el estudiante asociado al usuario
    estudiante = db.query(Estudiante).filter(
        Estudiante.usuario_id == current_user.id
    ).first()
    
    if not estudiante:
        raise HTTPException(
            status_code=400, 
            detail="User is not associated with a student profile"
        )
    
    progress = audio_lesson_service.update_student_progress(
        db,
        estudiante_id=estudiante.id,
        lesson_id=lesson_id,
        position_ms=progress_data.last_position_ms,
        completed=progress_data.completed
    )
    
    return StudentAudioProgressResponse(
        id=progress.id,
        estudiante_id=progress.estudiante_id,
        audio_lesson_id=progress.audio_lesson_id,
        last_position_ms=progress.last_position_ms,
        times_completed=progress.times_completed,
        total_time_listened_ms=progress.total_time_listened_ms,
        completed=progress.completed,
        created_at=progress.created_at,
        updated_at=progress.updated_at
    )


@router.get("/student/lessons", response_model=List[StudentLessonWithProgress])
def get_student_lessons_with_progress(
    modulo_id: Optional[int] = Query(None, description="Filtrar por módulo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene las lecciones disponibles con el progreso del estudiante.
    
    Ideal para mostrar una lista de lecciones con indicación visual
    del progreso de cada una.
    """
    # Obtener el estudiante asociado al usuario
    estudiante = db.query(Estudiante).filter(
        Estudiante.usuario_id == current_user.id
    ).first()
    
    if not estudiante:
        raise HTTPException(
            status_code=400, 
            detail="User is not associated with a student profile"
        )
    
    lessons = audio_lesson_service.get_student_lessons_with_progress(
        db, estudiante_id=estudiante.id, modulo_id=modulo_id
    )
    
    return lessons


# ==================== Batch Operations ====================

@router.post("/batch/create-with-audio", response_model=AudioLessonResponse)
async def create_lesson_with_audio(
    titulo: str = Form(...),
    transcript_text: str = Form(...),
    descripcion: Optional[str] = Form(None),
    modulo_id: Optional[int] = Form(None),
    curso_id: Optional[int] = Form(None),
    orden: int = Form(0),
    audio: UploadFile = File(...),
    auto_process: bool = Form(False, description="Procesar automáticamente con Gentle"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una lección y sube el audio en una sola operación.
    
    Opcionalmente puede procesar automáticamente el audio con Gentle.
    """
    try:
        # 1. Crear la lección
        lesson_data = AudioLessonCreate(
            titulo=titulo,
            descripcion=descripcion,
            modulo_id=modulo_id,
            curso_id=curso_id,
            transcript_text=transcript_text,
            orden=orden
        )
        
        db_lesson = audio_lesson_service.create_lesson(db, lesson_data)
        
        # 2. Subir el audio
        relative_path, file_size = await audio_storage_service.save_audio_file(
            audio, db_lesson.id
        )
        
        db_lesson = audio_lesson_service.set_audio_url(db, db_lesson.id, relative_path)
        
        # 3. Procesar con Gentle si se solicitó
        if auto_process:
            try:
                await audio_lesson_service.process_audio_with_gentle(db, db_lesson.id)
                db.refresh(db_lesson)
            except AudioLessonServiceError as e:
                logger.warning(f"Auto-processing failed: {e}")
                # Log critical error to file
                try:
                    with open("debug_gentle_error.log", "a") as f:
                        f.write(f"Error processing lesson {db_lesson.id}: {str(e)}\n")
                except:
                    pass
                # No fallar la creación por error de procesamiento
        
        return _lesson_to_response(db_lesson)
    
    except AudioStorageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating lesson with audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Helper Functions ====================

def _lesson_to_response(lesson: AudioLesson) -> AudioLessonResponse:
    """Convierte un modelo AudioLesson a response schema."""
    return AudioLessonResponse(
        id=lesson.id,
        titulo=lesson.titulo,
        descripcion=lesson.descripcion,
        modulo_id=lesson.modulo_id,
        curso_id=lesson.curso_id,
        audio_url=f"/api/v1/audio-lessons/{lesson.id}/stream" if lesson.audio_url else None,
        audio_duration_ms=lesson.audio_duration_ms,
        estado=lesson.estado,
        orden=lesson.orden,
        activo=lesson.activo,
        created_at=lesson.created_at,
        updated_at=lesson.updated_at
    )
