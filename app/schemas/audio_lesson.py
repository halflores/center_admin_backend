"""
Schemas for Audio Lessons - Sincronización Audio-Texto
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AudioLessonStatus(str, Enum):
    """Estados posibles de una lección de audio"""
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    LISTO = "LISTO"
    ERROR = "ERROR"


class WordTimestamp(BaseModel):
    """Timestamp individual para una palabra"""
    word: str
    start: int = Field(..., description="Tiempo de inicio en milisegundos")
    end: int = Field(..., description="Tiempo de fin en milisegundos")
    confidence: Optional[float] = Field(None, ge=0, le=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "word": "Hello",
                "start": 0,
                "end": 450,
                "confidence": 0.98
            }
        }


class TimestampsData(BaseModel):
    """Estructura completa de timestamps"""
    words: List[WordTimestamp]
    duration_ms: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "words": [
                    {"word": "Hello", "start": 0, "end": 450},
                    {"word": "my", "start": 500, "end": 700},
                    {"word": "name", "start": 750, "end": 1100}
                ],
                "duration_ms": 5000
            }
        }


# ============ CREATE Schemas ============

class AudioLessonCreate(BaseModel):
    """Schema para crear una nueva lección de audio"""
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    modulo_id: Optional[int] = None
    curso_id: Optional[int] = None
    transcript_text: str = Field(..., min_length=1, description="Texto completo de la lección")
    orden: Optional[int] = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Lesson 1: Greetings",
                "descripcion": "Learn basic greetings in English",
                "modulo_id": 1,
                "transcript_text": "Hello, my name is John. Nice to meet you.",
                "orden": 1
            }
        }


class AudioLessonUpdate(BaseModel):
    """Schema para actualizar una lección de audio"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    transcript_text: Optional[str] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None


# ============ RESPONSE Schemas ============

class AudioLessonBase(BaseModel):
    """Schema base para respuestas de lección de audio"""
    id: int
    titulo: str
    descripcion: Optional[str] = None
    modulo_id: Optional[int] = None
    curso_id: Optional[int] = None
    audio_url: Optional[str] = None
    audio_duration_ms: Optional[int] = None
    estado: AudioLessonStatus
    orden: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AudioLessonResponse(AudioLessonBase):
    """Respuesta completa de una lección de audio (sin timestamps para listados)"""
    modulo_nombre: Optional[str] = None
    curso_nombre: Optional[str] = None


class AudioLessonDetail(AudioLessonBase):
    """Respuesta detallada con timestamps para reproducción"""
    transcript_text: str
    timestamps_json: Optional[TimestampsData] = None
    modulo_nombre: Optional[str] = None
    curso_nombre: Optional[str] = None


class AudioLessonList(BaseModel):
    """Lista paginada de lecciones de audio"""
    items: List[AudioLessonResponse]
    total: int
    page: int
    page_size: int


# ============ PROGRESS Schemas ============

class StudentAudioProgressCreate(BaseModel):
    """Schema para crear/actualizar progreso del estudiante"""
    last_position_ms: int = Field(..., ge=0)
    completed: Optional[bool] = False


class StudentAudioProgressResponse(BaseModel):
    """Respuesta del progreso del estudiante"""
    id: int
    estudiante_id: int
    audio_lesson_id: int
    last_position_ms: int
    times_completed: int
    total_time_listened_ms: int
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StudentLessonWithProgress(AudioLessonResponse):
    """Lección con información de progreso del estudiante"""
    progress: Optional[StudentAudioProgressResponse] = None
    progress_percentage: Optional[float] = None


# ============ PROCESSING Schemas ============

class ProcessAudioRequest(BaseModel):
    """Request para procesar audio con Gentle"""
    force_reprocess: bool = Field(False, description="Forzar reprocesamiento aunque ya existan timestamps")


class ProcessAudioResponse(BaseModel):
    """Respuesta del procesamiento de audio"""
    success: bool
    message: str
    lesson_id: int
    estado: AudioLessonStatus
    words_count: Optional[int] = None
    duration_ms: Optional[int] = None
