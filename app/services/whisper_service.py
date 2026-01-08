"""
Whisper Speech-to-Text Service (Local - Free)
==============================================

Uses faster-whisper for local speech transcription.
No API costs - runs entirely on the server.

Installation:
    pip install faster-whisper

Models available (trade-off speed/accuracy):
    - tiny: ~1GB RAM, fastest, basic accuracy
    - base: ~1GB RAM, fast, good accuracy
    - small: ~2GB RAM, moderate, very good accuracy (RECOMMENDED)
    - medium: ~5GB RAM, slow, excellent accuracy
    - large-v3: ~10GB RAM, slowest, maximum accuracy
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy load to avoid startup delay if not used
_model = None
_model_size = None


def get_whisper_model(model_size: str = "small"):
    """
    Get or initialize the Whisper model (singleton pattern).
    Model is loaded once and reused for all transcriptions.
    """
    global _model, _model_size
    
    if _model is None or _model_size != model_size:
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"Loading Whisper model '{model_size}'...")
            
            # Check for GPU availability
            device = "cpu"
            compute_type = "int8"  # Optimized for CPU
            
            try:
                import torch
                if torch.cuda.is_available():
                    device = "cuda"
                    compute_type = "float16"
                    logger.info("Using GPU for Whisper transcription")
            except ImportError:
                pass
            
            _model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type
            )
            _model_size = model_size
            
            logger.info(f"Whisper model '{model_size}' loaded successfully on {device}")
            
        except ImportError:
            logger.error("faster-whisper not installed. Run: pip install faster-whisper")
            raise ImportError("faster-whisper is required. Install with: pip install faster-whisper")
    
    return _model


class WhisperService:
    """
    Speech-to-text service using faster-whisper (local, free).
    
    Usage:
        service = WhisperService()
        result = service.transcribe("audio.wav")
        print(result["text"])
    """
    
    def __init__(self, model_size: str = "small"):
        """
        Initialize Whisper service.
        
        Args:
            model_size: Model to use (tiny, base, small, medium, large-v3)
        """
        self.model_size = model_size
        self._model = None
    
    @property
    def model(self):
        """Lazy load model on first use"""
        if self._model is None:
            self._model = get_whisper_model(self.model_size)
        return self._model
    
    def transcribe(
        self, 
        audio_path: str,
        language: str = "en",
        word_timestamps: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code (default: "en" for English)
            word_timestamps: Include word-level timestamps
            
        Returns:
            Dictionary with:
                - text: Full transcription
                - words: List of words with timestamps (if word_timestamps=True)
                - language: Detected/specified language
                - duration_ms: Audio duration in milliseconds
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Transcribing audio: {audio_path}")
        
        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=word_timestamps,
                beam_size=5,
                vad_filter=True  # Filter out silence
            )
            
            words = []
            full_text = []
            
            for segment in segments:
                full_text.append(segment.text.strip())
                
                if word_timestamps and segment.words:
                    for word in segment.words:
                        words.append({
                            "word": word.word.strip(),
                            "start": int(word.start * 1000),  # Convert to ms
                            "end": int(word.end * 1000),
                            "confidence": round(word.probability, 3) if hasattr(word, 'probability') else 0.9
                        })
            
            result = {
                "text": " ".join(full_text),
                "words": words if word_timestamps else [],
                "language": info.language,
                "duration_ms": int(info.duration * 1000)
            }
            
            logger.info(f"Transcription complete: {len(result['text'])} chars, {len(words)} words")
            return result
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
    
    def transcribe_for_comparison(
        self,
        audio_path: str,
        expected_text: str
    ) -> Dict[str, Any]:
        """
        Transcribe and prepare results for comparison with expected text.
        
        Args:
            audio_path: Path to student's audio recording
            expected_text: The text the student was supposed to say
            
        Returns:
            Transcription result with comparison-ready data
        """
        result = self.transcribe(audio_path, language="en", word_timestamps=True)
        
        # Normalize for comparison
        result["normalized_text"] = self._normalize_text(result["text"])
        result["expected_normalized"] = self._normalize_text(expected_text)
        
        return result
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison (lowercase, remove punctuation)"""
        import re
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text)      # Normalize whitespace
        return text


# Global service instance (uses default model size)
whisper_service = WhisperService(model_size="base")
