"""
Servicio de Alineación Forzada con Gentle
==========================================

Gentle es un alineador forzado que toma un archivo de audio y su transcripción
correspondiente, y produce timestamps precisos por palabra (~10-20ms de precisión).

Documentación: https://github.com/lowerquality/gentle
Docker: docker run -p 8765:8765 lowerquality/gentle
"""

import os
import json
import logging
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class GentleAlignmentError(Exception):
    """Error durante el proceso de alineación con Gentle"""
    pass


class GentleService:
    """
    Servicio para realizar alineación forzada de audio con texto usando Gentle.
    
    Gentle produce timestamps muy precisos (~10-20ms) cuando se le proporciona
    tanto el audio como el texto correspondiente.
    """
    
    def __init__(self, gentle_url: Optional[str] = None):
        """
        Inicializa el servicio de Gentle.
        
        Args:
            gentle_url: URL del servicio Gentle (default: http://localhost:8765)
        """
        self.gentle_url = gentle_url or os.getenv("GENTLE_URL", "http://localhost:8765")
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 minutos máximo
    
    async def check_health(self) -> bool:
        """
        Verifica si el servicio Gentle está disponible.
        
        Returns:
            True si está disponible, False en caso contrario
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.gentle_url}/") as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"Gentle service not available: {e}")
            return False
    
    async def align_audio_with_transcript(
        self,
        audio_path: str,
        transcript: str,
        conservative: bool = False
    ) -> Dict[str, Any]:
        """
        Realiza la alineación forzada de un archivo de audio con su transcripción.
        """
        # Validar que el archivo existe
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Validar que el transcript no está vacío
        if not transcript or not transcript.strip():
            raise GentleAlignmentError("Transcript cannot be empty")
        
        logger.info(f"Starting alignment for: {audio_path}")
        logger.debug(f"Transcript length: {len(transcript)} characters")
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Preparar el form data
                data = aiohttp.FormData()
                
                # Agregar el archivo de audio
                with open(audio_path, 'rb') as audio_file:
                    data.add_field(
                        'audio',
                        audio_file.read(),
                        filename=os.path.basename(audio_path),
                        content_type='audio/mpeg'
                    )
                
                # Agregar la transcripción
                data.add_field('transcript', transcript)
                
                # Hacer la petición a Gentle
                url = f"{self.gentle_url}/transcriptions?async=false"
                if conservative:
                    url += "&conservative=true"
                
                # Use retry logic for connection
                async with session.post(url, data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise GentleAlignmentError(
                            f"Gentle returned status {response.status}: {error_text}"
                        )
                    
                    result = await response.json()
            
            # Procesar el resultado usando el transcript original para preservar formato
            return self._process_gentle_response(result, transcript)
        
        except aiohttp.ClientError as e:
            raise GentleAlignmentError(f"Connection error with Gentle: {e}")
        except asyncio.TimeoutError:
            raise GentleAlignmentError("Timeout waiting for Gentle alignment")
        except json.JSONDecodeError as e:
            raise GentleAlignmentError(f"Invalid JSON response from Gentle: {e}")
    
    def _process_gentle_response(self, response: Dict[str, Any], original_transcript: str = "") -> Dict[str, Any]:
        """
        Procesa la respuesta de Gentle y la convierte al formato estándar,
        preservando el formato original (saltos de línea) del transcript.
        """
        words = []
        successful_alignments = 0
        total_words = 0
        max_end_time = 0
        
        # Obtener palabras raw de Gentle
        gentle_words = response.get("words", [])
        
        # Si tenemos transcript original, lo usamos para preservar formato
        if original_transcript:
            import re
            
            # Tokenizar preservando espacios para detectar saltos de línea
            tokens = re.split(r'(\s+)', original_transcript)
            word_tokens = []
            for t in tokens:
                if not t.strip():
                    if word_tokens:
                        # Append whitespace to previous word tuple
                        word_tokens[-1] = (word_tokens[-1][0], word_tokens[-1][1] + t)
                else:
                    word_tokens.append((t, "")) # (Word, TrailingWhitespace)
            
            gentle_idx = 0
            
            for original_word, trailing_space in word_tokens:
                # Buscar correspondencia en Gentle
                # Gentle a veces normaliza o salta palabras, intentamos alinear simple
                start_ms = 0
                end_ms = 0
                confidence = 0.0
                
                # Avanzar en gentle_words hasta encontrar match o agotar
                # Estrategia simple: Asignar 1-a-1 si es posible, si no buscar
                if gentle_idx < len(gentle_words):
                    g_word = gentle_words[gentle_idx]
                    
                    # Usamos el timestamp de Gentle
                    start_seconds = g_word.get("start", 0)
                    end_seconds = g_word.get("end", start_seconds)
                    start_ms = int(start_seconds * 1000)
                    end_ms = int(end_seconds * 1000)
                    
                    # Calcular confianza
                    phones = g_word.get("phones", [])
                    if phones:
                        confidence = 0.95
                    else:
                        confidence = 0.80 if g_word.get("case") == "success" else 0.0
                    
                    if g_word.get("case") == "success":
                        successful_alignments += 1
                        
                    gentle_idx += 1
                
                # Construir la palabra final preservando el formato original
                final_word_str = original_word
                
                # Inyectar saltos de línea si existen en el espacio posterior
                newlines = trailing_space.count('\n')
                if newlines > 0:
                    final_word_str += "\n" * newlines
                
                words.append({
                    "word": final_word_str,
                    "start": start_ms,
                    "end": end_ms,
                    "confidence": confidence
                })
                
                total_words += 1
                max_end_time = max(max_end_time, end_ms)
                
        else:
            # Fallback a lógica antigua si no hay transcript original (no debería pasar)
            for word_data in gentle_words:
                total_words += 1
                case = word_data.get("case", "unknown")
                if case == "success":
                    successful_alignments += 1
                    start_seconds = word_data.get("start", 0)
                    end_seconds = word_data.get("end", start_seconds)
                    words.append({
                        "word": word_data.get("word", ""), # Usar word del input, no alignedWord
                        "start": int(start_seconds * 1000),
                        "end": int(end_seconds * 1000),
                        "confidence": 0.95
                    })
                    max_end_time = max(max_end_time, int(end_seconds * 1000))

        # Calcular tasa de éxito
        success_rate = successful_alignments / len(gentle_words) if gentle_words else 0
        
        logger.info(
            f"Alignment complete: {successful_alignments}/{len(gentle_words)} gentle words processed into {len(words)} formatted words."
        )
        
        return {
            "words": words,
            "duration_ms": max_end_time,
            "transcript": response.get("transcript", ""),
            "success_rate": success_rate,
            "total_words": total_words,
            "aligned_words": successful_alignments
        }

    def _calculate_confidence(self, word_data: Dict[str, Any]) -> float:
        # Helper antiguo mantenido por compatibilidad si se necesita
        pass

    async def align_with_retry(
        self,
        audio_path: str,
        transcript: str,
        max_retries: int = 3,
        delay_seconds: float = 2.0
    ) -> Dict[str, Any]:
        """
        Realiza alineación con reintentos automáticos en caso de fallo.
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await self.align_audio_with_transcript(audio_path, transcript)
            except GentleAlignmentError as e:
                last_error = e
                logger.warning(f"Alignment attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay_seconds)
        
        raise GentleAlignmentError(
            f"All {max_retries} alignment attempts failed. Last error: {last_error}"
        )


# Instancia global del servicio
gentle_service = GentleService()
