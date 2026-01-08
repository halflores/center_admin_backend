"""
Servicio de Almacenamiento de Archivos de Audio
================================================

Maneja el almacenamiento y recuperación de archivos de audio para las lecciones.
Soporta almacenamiento local con opción de migrar a S3/MinIO en el futuro.
"""

import os
import shutil
import hashlib
import mimetypes
import logging
from pathlib import Path
from typing import Optional, Tuple, BinaryIO
from datetime import datetime
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class AudioStorageError(Exception):
    """Error en operaciones de almacenamiento de audio"""
    pass


class AudioStorageService:
    """
    Servicio para gestionar el almacenamiento de archivos de audio.
    
    Actualmente usa almacenamiento local, pero está diseñado para
    facilitar la migración a servicios cloud (S3, MinIO) en el futuro.
    """
    
    # Tipos MIME permitidos para audio
    ALLOWED_MIME_TYPES = {
        'audio/mpeg': '.mp3',
        'audio/mp3': '.mp3',
        'audio/wav': '.wav',
        'audio/x-wav': '.wav',
        'audio/wave': '.wav',
        'audio/ogg': '.ogg',
        'audio/flac': '.flac',
        'audio/m4a': '.m4a',
        'audio/mp4': '.m4a',
        'audio/aac': '.aac',
    }
    
    # Tamaño máximo de archivo (50 MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Inicializa el servicio de almacenamiento.
        
        Args:
            base_path: Ruta base para almacenar archivos (default: uploads/audio)
        """
        self.base_path = Path(base_path or os.getenv(
            "AUDIO_STORAGE_PATH", 
            "uploads/audio"
        ))
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Crea los directorios necesarios si no existen."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "lessons").mkdir(exist_ok=True)
        (self.base_path / "temp").mkdir(exist_ok=True)
        logger.info(f"Audio storage initialized at: {self.base_path.absolute()}")
    
    def _validate_file(self, file: UploadFile) -> str:
        """
        Valida el archivo de audio.
        
        Args:
            file: Archivo subido
        
        Returns:
            Extensión del archivo
        
        Raises:
            AudioStorageError: Si el archivo no es válido
        """
        # Verificar tipo MIME
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        if content_type not in self.ALLOWED_MIME_TYPES:
            raise AudioStorageError(
                f"File type not allowed: {content_type}. "
                f"Allowed types: {', '.join(self.ALLOWED_MIME_TYPES.keys())}"
            )
        
        return self.ALLOWED_MIME_TYPES[content_type]
    
    def _generate_filename(self, lesson_id: int, extension: str) -> str:
        """
        Genera un nombre de archivo único para la lección.
        
        Args:
            lesson_id: ID de la lección
            extension: Extensión del archivo
        
        Returns:
            Nombre de archivo único
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"lesson_{lesson_id}_{timestamp}{extension}"
    
    async def save_audio_file(
        self,
        file: UploadFile,
        lesson_id: int
    ) -> Tuple[str, int]:
        """
        Guarda un archivo de audio para una lección.
        
        Args:
            file: Archivo de audio subido
            lesson_id: ID de la lección
        
        Returns:
            Tuple de (ruta relativa del archivo, tamaño en bytes)
        
        Raises:
            AudioStorageError: Si hay error al guardar
        """
        try:
            # Validar archivo
            extension = self._validate_file(file)
            
            # Generar nombre único
            filename = self._generate_filename(lesson_id, extension)
            file_path = self.base_path / "lessons" / filename
            
            # Leer y guardar el contenido
            content = await file.read()
            file_size = len(content)
            
            # Validar tamaño
            if file_size > self.MAX_FILE_SIZE:
                raise AudioStorageError(
                    f"File too large: {file_size / (1024*1024):.2f} MB. "
                    f"Maximum allowed: {self.MAX_FILE_SIZE / (1024*1024)} MB"
                )
            
            # Guardar archivo
            with open(file_path, 'wb') as f:
                f.write(content)
            
            logger.info(f"Saved audio file: {file_path} ({file_size} bytes)")
            
            # Retornar ruta relativa al base_path
            relative_path = str(file_path.relative_to(self.base_path.parent))
            return relative_path, file_size
        
        except AudioStorageError:
            raise
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            raise AudioStorageError(f"Failed to save audio file: {e}")
        finally:
            # Asegurar que el archivo se cierre
            await file.seek(0)
    
    def save_audio_from_bytes(
        self,
        content: bytes,
        lesson_id: int,
        extension: str = ".mp3"
    ) -> Tuple[str, int]:
        """
        Guarda audio desde bytes directamente.
        
        Args:
            content: Contenido del archivo en bytes
            lesson_id: ID de la lección
            extension: Extensión del archivo
        
        Returns:
            Tuple de (ruta relativa, tamaño en bytes)
        """
        filename = self._generate_filename(lesson_id, extension)
        file_path = self.base_path / "lessons" / filename
        
        file_size = len(content)
        
        if file_size > self.MAX_FILE_SIZE:
            raise AudioStorageError(f"File too large: {file_size} bytes")
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        relative_path = str(file_path.relative_to(self.base_path.parent))
        return relative_path, file_size
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """
        Obtiene la ruta absoluta de un archivo.
        
        Args:
            relative_path: Ruta relativa del archivo
        
        Returns:
            Path absoluto
        """
        # Si la ruta ya es absoluta, verificar si existe
        if os.path.isabs(relative_path):
            path = Path(relative_path)
            if path.exists():
                return path
            
            # Si no existe (ej: ruta de otra PC), intentar buscar solo por nombre en carpeta default
            logger.warning(f"Absolute path {path} not found. Attempting recovery in {self.base_path}")
            fallback = self.base_path / "lessons" / path.name
            if fallback.exists():
                logger.info(f"Recovered file at: {fallback}")
                return fallback
                
            return path
        
        # Construir ruta desde el parent del base_path
        # Expected: base_path=uploads/audio, relative_path=audio/lessons/file.mp3
        # Result: uploads/audio/lessons/file.mp3
        path = self.base_path.parent / relative_path
        
        if path.exists():
            return path
            
        # Fallback: Si la ruta en DB es antigua (ej: lessons/file.mp3)
        # Check relative to base_path (uploads/audio)
        # Result: uploads/audio/lessons/file.mp3
        path_fallback = self.base_path / relative_path
        if path_fallback.exists():
            logger.info(f"files path fallback used: {path_fallback}")
            return path_fallback
            
        return path
    
    def file_exists(self, relative_path: str) -> bool:
        """
        Verifica si un archivo existe.
        
        Args:
            relative_path: Ruta relativa del archivo
        
        Returns:
            True si existe, False en caso contrario
        """
        return self.get_absolute_path(relative_path).exists()
    
    def get_file_info(self, relative_path: str) -> dict:
        """
        Obtiene información de un archivo.
        
        Args:
            relative_path: Ruta relativa del archivo
        
        Returns:
            Dict con información del archivo
        """
        abs_path = self.get_absolute_path(relative_path)
        
        if not abs_path.exists():
            raise AudioStorageError(f"File not found: {relative_path}")
        
        stat = abs_path.stat()
        mime_type = mimetypes.guess_type(str(abs_path))[0] or 'audio/mpeg'
        
        return {
            "path": str(abs_path),
            "size": stat.st_size,
            "mime_type": mime_type,
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime)
        }
    
    def delete_audio_file(self, relative_path: str) -> bool:
        """
        Elimina un archivo de audio.
        
        Args:
            relative_path: Ruta relativa del archivo
        
        Returns:
            True si se eliminó, False si no existía
        """
        try:
            abs_path = self.get_absolute_path(relative_path)
            
            if abs_path.exists():
                abs_path.unlink()
                logger.info(f"Deleted audio file: {abs_path}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting audio file: {e}")
            raise AudioStorageError(f"Failed to delete audio file: {e}")
    
    def get_stream_path(self, relative_path: str) -> Path:
        """
        Obtiene la ruta para streaming de un archivo.
        
        Args:
            relative_path: Ruta relativa del archivo
        
        Returns:
            Path absoluto para streaming
        
        Raises:
            AudioStorageError: Si el archivo no existe
        """
        abs_path = self.get_absolute_path(relative_path)
        
        if not abs_path.exists():
            raise AudioStorageError(f"Audio file not found: {relative_path}")
        
        return abs_path


# Instancia global del servicio
audio_storage_service = AudioStorageService()
