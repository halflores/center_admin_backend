"""
Servicio Principal de Lecciones de Audio
==========================================

Gestiona las lecciones de audio con sincronización de texto,
incluyendo almacenamiento, procesamiento con Gentle, y tracking de progreso.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import BackgroundTasks

from app.models.models import AudioLesson, StudentAudioProgress, Modulo, Curso
from app.services.gentle_service import gentle_service, GentleAlignmentError
from app.services.audio_storage_service import audio_storage_service, AudioStorageError
from app.schemas.audio_lesson import (
    AudioLessonCreate, AudioLessonUpdate, AudioLessonStatus,
    TimestampsData, WordTimestamp
)

logger = logging.getLogger(__name__)


class AudioLessonServiceError(Exception):
    """Error en operaciones del servicio de lecciones de audio"""
    pass


class AudioLessonService:
    """
    Servicio para gestionar lecciones de audio con sincronización de texto.
    
    Funcionalidades:
    - CRUD de lecciones de audio
    - Procesamiento de audio con Gentle para generar timestamps
    - Tracking de progreso de estudiantes
    - Streaming de audio
    """
    
    # ==================== CRUD Operations ====================
    
    def create_lesson(
        self,
        db: Session,
        lesson_data: AudioLessonCreate,
        audio_url: Optional[str] = None
    ) -> "AudioLesson":
        """
        Crea una nueva lección de audio.
        
        Args:
            db: Sesión de base de datos
            lesson_data: Datos de la lección
            audio_url: URL/path del audio (opcional, se puede agregar después)
        
        Returns:
            La lección creada
        """
        db_lesson = AudioLesson(
            titulo=lesson_data.titulo,
            descripcion=lesson_data.descripcion,
            modulo_id=lesson_data.modulo_id,
            curso_id=lesson_data.curso_id,
            transcript_text=lesson_data.transcript_text,
            audio_url=audio_url,
            estado=AudioLessonStatus.PENDIENTE.value,
            orden=lesson_data.orden or 0,
            activo=True
        )
        
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        
        logger.info(f"Created audio lesson: {db_lesson.id} - {db_lesson.titulo}")
        return db_lesson
    
    def get_lesson(self, db: Session, lesson_id: int) -> Optional["AudioLesson"]:
        """Obtiene una lección por ID."""
        return db.query(AudioLesson).filter(AudioLesson.id == lesson_id).first()
    
    def get_lessons(
        self,
        db: Session,
        modulo_id: Optional[int] = None,
        curso_id: Optional[int] = None,
        estado: Optional[AudioLessonStatus] = None,
        activo_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List["AudioLesson"]:
        """
        Lista lecciones de audio con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            modulo_id: Filtrar por módulo
            curso_id: Filtrar por curso
            estado: Filtrar por estado
            activo_only: Solo lecciones activas
            skip: Offset para paginación
            limit: Límite de resultados
        
        Returns:
            Lista de lecciones
        """
        query = db.query(AudioLesson)
        
        if activo_only:
            query = query.filter(AudioLesson.activo == True)
        
        if modulo_id:
            query = query.filter(AudioLesson.modulo_id == modulo_id)
        
        if curso_id:
            query = query.filter(AudioLesson.curso_id == curso_id)
        
        if estado:
            query = query.filter(AudioLesson.estado == estado.value)
        
        return query.order_by(AudioLesson.orden).offset(skip).limit(limit).all()
    
    def count_lessons(
        self,
        db: Session,
        modulo_id: Optional[int] = None,
        curso_id: Optional[int] = None,
        estado: Optional[AudioLessonStatus] = None,
        activo_only: bool = True
    ) -> int:
        """Cuenta el total de lecciones según filtros."""
        query = db.query(AudioLesson)
        
        if activo_only:
            query = query.filter(AudioLesson.activo == True)
        
        if modulo_id:
            query = query.filter(AudioLesson.modulo_id == modulo_id)
        
        if curso_id:
            query = query.filter(AudioLesson.curso_id == curso_id)
        
        if estado:
            query = query.filter(AudioLesson.estado == estado.value)
        
        return query.count()
    
    def update_lesson(
        self,
        db: Session,
        lesson_id: int,
        lesson_data: AudioLessonUpdate
    ) -> Optional["AudioLesson"]:
        """
        Actualiza una lección de audio.
        
        Args:
            db: Sesión de base de datos
            lesson_id: ID de la lección
            lesson_data: Datos a actualizar
        
        Returns:
            La lección actualizada o None si no existe
        """
        db_lesson = self.get_lesson(db, lesson_id)
        
        if not db_lesson:
            return None
        
        update_data = lesson_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_lesson, field, value)
        
        db_lesson.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_lesson)
        
        logger.info(f"Updated audio lesson: {lesson_id}")
        return db_lesson
    
    def delete_lesson(self, db: Session, lesson_id: int) -> bool:
        """
        Elimina una lección de audio (soft delete).
        
        Args:
            db: Sesión de base de datos
            lesson_id: ID de la lección
        
        Returns:
            True si se eliminó, False si no existe
        """
        db_lesson = self.get_lesson(db, lesson_id)
        
        if not db_lesson:
            return False
        
        db_lesson.activo = False
        db_lesson.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Soft deleted audio lesson: {lesson_id}")
        return True
    
    def set_audio_url(
        self,
        db: Session,
        lesson_id: int,
        audio_url: str,
        duration_ms: Optional[int] = None
    ) -> Optional["AudioLesson"]:
        """
        Establece la URL del audio para una lección.
        
        Args:
            db: Sesión de base de datos
            lesson_id: ID de la lección
            audio_url: URL/path del archivo de audio
            duration_ms: Duración del audio en milisegundos
        
        Returns:
            La lección actualizada
        """
        db_lesson = self.get_lesson(db, lesson_id)
        
        if not db_lesson:
            return None
        
        db_lesson.audio_url = audio_url
        if duration_ms:
            db_lesson.audio_duration_ms = duration_ms
        db_lesson.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_lesson)
        
        return db_lesson
    
    # ==================== Audio Processing ====================
    
    async def process_audio_with_gentle(
        self,
        db: Session,
        lesson_id: int,
        force_reprocess: bool = False
    ) -> Dict[str, Any]:
        """
        Procesa el audio de una lección con Gentle para generar timestamps.
        
        Args:
            db: Sesión de base de datos
            lesson_id: ID de la lección
            force_reprocess: Forzar reprocesamiento
        
        Returns:
            Dict con resultado del procesamiento
        
        Raises:
            AudioLessonServiceError: Si hay error en el procesamiento
        """
        db_lesson = self.get_lesson(db, lesson_id)
        
        if not db_lesson:
            raise AudioLessonServiceError(f"Lesson not found: {lesson_id}")
        
        if not db_lesson.audio_url:
            raise AudioLessonServiceError("Lesson has no audio file")
        
        if not db_lesson.transcript_text:
            raise AudioLessonServiceError("Lesson has no transcript")
        
        # Verificar si ya está procesado
        if db_lesson.estado == AudioLessonStatus.LISTO.value and not force_reprocess:
            return {
                "success": True,
                "message": "Lesson already processed",
                "lesson_id": lesson_id,
                "estado": db_lesson.estado,
                "words_count": len(db_lesson.timestamps_json.get("words", [])) if db_lesson.timestamps_json else 0
            }
        
        # Marcar como procesando
        db_lesson.estado = AudioLessonStatus.PROCESANDO.value
        db.commit()
        
        try:
            # Obtener ruta absoluta del audio
            # Si ya es ruta absoluta, usarla directamente
            if os.path.isabs(db_lesson.audio_url):
                audio_path = db_lesson.audio_url
            else:
                audio_path = str(audio_storage_service.get_absolute_path(db_lesson.audio_url))
            
            # Verificar que el archivo existe
            if not os.path.exists(audio_path):
                raise AudioLessonServiceError(f"Audio file not found: {audio_path}")
            
            # Procesar con Gentle
            result = await gentle_service.align_with_retry(
                audio_path=audio_path,
                transcript=db_lesson.transcript_text
            )
            
            # Guardar timestamps (como JSON string para la columna Text)
            timestamps_data = {
                "words": result["words"],
                "duration_ms": result["duration_ms"]
            }
            
            db_lesson.timestamps_json = json.dumps(timestamps_data)
            db_lesson.audio_duration_ms = result["duration_ms"]
            db_lesson.estado = AudioLessonStatus.LISTO.value
            db_lesson.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(db_lesson)
            
            logger.info(
                f"Successfully processed lesson {lesson_id}: "
                f"{result['aligned_words']}/{result['total_words']} words aligned"
            )
            
            return {
                "success": True,
                "message": "Audio processed successfully",
                "lesson_id": lesson_id,
                "estado": db_lesson.estado,
                "words_count": len(result["words"]),
                "duration_ms": result["duration_ms"],
                "success_rate": result["success_rate"]
            }
        
        except (GentleAlignmentError, AudioStorageError) as e:
            db_lesson.estado = AudioLessonStatus.ERROR.value
            db.commit()
            
            logger.error(f"Error processing lesson {lesson_id}: {e}")
            
            # Log critical error to file
            try:
                with open("debug_gentle_error.log", "a") as f:
                    f.write(f"Service Error processing lesson {lesson_id}: {str(e)}\n\n")
            except:
                pass
                
            raise AudioLessonServiceError(f"Processing failed: {e}")
    
    def process_audio_background(
        self,
        background_tasks: BackgroundTasks,
        db: Session,
        lesson_id: int
    ) -> None:
        """
        Inicia el procesamiento de audio en background.
        
        Args:
            background_tasks: FastAPI BackgroundTasks
            db: Sesión de base de datos
            lesson_id: ID de la lección
        """
        db_lesson = self.get_lesson(db, lesson_id)
        
        if db_lesson:
            db_lesson.estado = AudioLessonStatus.PROCESANDO.value
            db.commit()
        
        # Nota: Para background tasks async, necesitaríamos usar Celery o similar
        # Por ahora, el procesamiento se hace sincrónicamente en el endpoint
        background_tasks.add_task(
            self._background_process_wrapper,
            lesson_id
        )
    
    async def _background_process_wrapper(self, lesson_id: int) -> None:
        """Wrapper para procesamiento en background."""
        # Nota: Esto requiere crear una nueva sesión de DB
        # En producción, usar Celery o similar
        logger.info(f"Background processing for lesson {lesson_id}")
    
    # ==================== Student Progress ====================
    
    def get_student_progress(
        self,
        db: Session,
        estudiante_id: int,
        lesson_id: int
    ) -> Optional["StudentAudioProgress"]:
        """Obtiene el progreso de un estudiante en una lección."""
        return db.query(StudentAudioProgress).filter(
            and_(
                StudentAudioProgress.estudiante_id == estudiante_id,
                StudentAudioProgress.audio_lesson_id == lesson_id
            )
        ).first()
    
    def update_student_progress(
        self,
        db: Session,
        estudiante_id: int,
        lesson_id: int,
        position_ms: int,
        completed: bool = False
    ) -> "StudentAudioProgress":
        """
        Actualiza el progreso de un estudiante en una lección.
        
        Args:
            db: Sesión de base de datos
            estudiante_id: ID del estudiante
            lesson_id: ID de la lección
            position_ms: Posición actual en milisegundos
            completed: Si completó la lección
        
        Returns:
            El progreso actualizado o creado
        """
        progress = self.get_student_progress(db, estudiante_id, lesson_id)
        
        if not progress:
            progress = StudentAudioProgress(
                estudiante_id=estudiante_id,
                audio_lesson_id=lesson_id,
                last_position_ms=position_ms,
                total_time_listened_ms=0,
                times_completed=0,
                completed=False
            )
            db.add(progress)
        
        # Actualizar tiempo escuchado (delta desde última posición)
        if position_ms > progress.last_position_ms:
            delta = position_ms - progress.last_position_ms
            progress.total_time_listened_ms += delta
        
        progress.last_position_ms = position_ms
        
        if completed and not progress.completed:
            progress.completed = True
            progress.times_completed += 1
        
        progress.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(progress)
        
        return progress
    
    def get_student_lessons_with_progress(
        self,
        db: Session,
        estudiante_id: int,
        modulo_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las lecciones de un estudiante con su progreso.
        
        Args:
            db: Sesión de base de datos
            estudiante_id: ID del estudiante
            modulo_id: Filtrar por módulo
        
        Returns:
            Lista de lecciones con progreso
        """
        lessons = self.get_lessons(db, modulo_id=modulo_id)
        
        result = []
        for lesson in lessons:
            progress = self.get_student_progress(db, estudiante_id, lesson.id)
            
            lesson_dict = {
                "id": lesson.id,
                "titulo": lesson.titulo,
                "descripcion": lesson.descripcion,
                "audio_url": lesson.audio_url,
                "audio_duration_ms": lesson.audio_duration_ms,
                "estado": lesson.estado,
                "orden": lesson.orden,
                "progress": None,
                "progress_percentage": 0
            }
            
            if progress:
                lesson_dict["progress"] = {
                    "last_position_ms": progress.last_position_ms,
                    "times_completed": progress.times_completed,
                    "total_time_listened_ms": progress.total_time_listened_ms,
                    "completed": progress.completed
                }
                
                if lesson.audio_duration_ms and lesson.audio_duration_ms > 0:
                    lesson_dict["progress_percentage"] = round(
                        (progress.last_position_ms / lesson.audio_duration_ms) * 100,
                        1
                    )
            
            result.append(lesson_dict)
        
        return result
    
    # ==================== Utility Methods ====================
    
    def get_lesson_with_details(
        self,
        db: Session,
        lesson_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene una lección con información adicional del módulo y curso.
        
        Args:
            db: Sesión de base de datos
            lesson_id: ID de la lección
        
        Returns:
            Dict con la lección y detalles o None
        """
        db_lesson = self.get_lesson(db, lesson_id)
        
        if not db_lesson:
            return None
        
        result = {
            "id": db_lesson.id,
            "titulo": db_lesson.titulo,
            "descripcion": db_lesson.descripcion,
            "modulo_id": db_lesson.modulo_id,
            "curso_id": db_lesson.curso_id,
            "audio_url": db_lesson.audio_url,
            "audio_duration_ms": db_lesson.audio_duration_ms,
            "transcript_text": db_lesson.transcript_text,
            "timestamps_json": db_lesson.timestamps_json,
            "estado": db_lesson.estado,
            "orden": db_lesson.orden,
            "activo": db_lesson.activo,
            "created_at": db_lesson.created_at,
            "updated_at": db_lesson.updated_at,
            "modulo_nombre": None,
            "curso_nombre": None
        }
        
        # Obtener nombre del módulo
        if db_lesson.modulo_id:
            modulo = db.query(Modulo).filter(Modulo.id == db_lesson.modulo_id).first()
            if modulo:
                result["modulo_nombre"] = modulo.nombre
        
        # Obtener nombre del curso si existe
        if db_lesson.curso_id:
            curso = db.query(Curso).filter(Curso.id == db_lesson.curso_id).first()
            if curso:
                result["curso_nombre"] = f"Curso {curso.id}"
        
        return result


# Instancia global del servicio
audio_lesson_service = AudioLessonService()
