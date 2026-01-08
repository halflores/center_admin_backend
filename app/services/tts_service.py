"""
Text-to-Speech Service using Edge TTS (Free)
=============================================

Uses Microsoft Edge's TTS service via edge-tts library.
Completely free, high quality voices, multiple languages.

Installation:
    pip install edge-tts

Available American English voices:
    - en-US-GuyNeural (male)
    - en-US-JennyNeural (female)
    - en-US-AriaNeural (female)
    - en-US-DavisNeural (male)
"""

import os
import asyncio
import logging
import hashlib
import re
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Voice mapping
VOICES = {
    ("male", "en-US"): "en-US-GuyNeural",
    ("female", "en-US"): "en-US-JennyNeural",
    ("male", "en-GB"): "en-GB-RyanNeural",
    ("female", "en-GB"): "en-GB-SoniaNeural",
}

# Default paths
DIALOGUE_AUDIO_DIR = "uploads/dialogues/tts"


class TTSService:
    """
    Text-to-Speech service using Edge TTS (free).
    
    Usage:
        service = TTSService()
        audio_path = await service.generate_audio("Hello, how are you?", "female", "en-US")
    """
    
    def __init__(self, output_dir: str = DIALOGUE_AUDIO_DIR):
        """
        Initialize TTS service.
        
        Args:
            output_dir: Directory to store generated audio files
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_voice(self, gender: str, accent: str) -> str:
        """Get voice name from gender and accent"""
        key = (gender.lower(), accent)
        return VOICES.get(key, VOICES[("female", "en-US")])
    
    def _get_cache_filename(self, text: str, voice: str) -> str:
        """Generate cache filename based on text and voice"""
        content = f"{voice}:{text}"
        hash_value = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"{hash_value}.mp3"
    
    async def generate_audio(
        self,
        text: str,
        gender: str = "female",
        accent: str = "en-US",
        rate: str = "+0%",
        use_cache: bool = True
    ) -> str:
        """
        Generate audio file from text.
        
        Args:
            text: Text to convert to speech
            gender: Voice gender ("male" or "female")
            accent: Voice accent ("en-US" or "en-GB")
            rate: Speaking rate adjustment (e.g., "+10%", "-10%")
            use_cache: Use cached audio if available
            
        Returns:
            Path to generated audio file (relative to uploads/)
        """
        try:
            import edge_tts
        except ImportError:
            raise ImportError("edge-tts is required. Install with: pip install edge-tts")
        
        voice = self._get_voice(gender, accent)
        filename = self._get_cache_filename(text, voice)
        output_path = os.path.join(self.output_dir, filename)
        
        # Check cache
        if use_cache and os.path.exists(output_path):
            logger.debug(f"Using cached TTS audio: {filename}")
            return output_path
        
        logger.info(f"Generating TTS audio with voice '{voice}': {text[:50]}...")
        
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(output_path)
            
            logger.info(f"TTS audio generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            raise
    
    def generate_audio_sync(
        self,
        text: str,
        gender: str = "female",
        accent: str = "en-US",
        rate: str = "+0%",
        use_cache: bool = True
    ) -> str:
        """
        Synchronous wrapper for generate_audio.
        """
        return asyncio.run(self.generate_audio(text, gender, accent, rate, use_cache))
    
    async def generate_dialogue_audio(
        self,
        dialogue_id: int,
        line_id: int,
        text: str,
        gender: str,
        accent: str
    ) -> str:
        """
        Generate audio for a specific dialogue line.
        
        Args:
            dialogue_id: ID of the dialogue
            line_id: ID of the dialogue line
            text: Text to speak
            gender: Voice gender
            accent: Voice accent
            
        Returns:
            Relative path to audio file
        """
        # Use dialogue-specific subdirectory
        dialogue_dir = os.path.join(self.output_dir, f"dialogue_{dialogue_id}")
        os.makedirs(dialogue_dir, exist_ok=True)
        
        filename = f"line_{line_id}.mp3"
        output_path = os.path.join(dialogue_dir, filename)
        
        # Check if already exists
        if os.path.exists(output_path):
            logger.debug(f"Dialogue audio already exists: {output_path}")
            return output_path, None
        
        try:
            import edge_tts
            import json
            from app.services.gentle_service import gentle_service
            
            voice = self._get_voice(gender, accent)
            communicate = edge_tts.Communicate(text, voice)
            
            # Generate audio file
            await communicate.save(output_path)
            
            # Use Gentle to align the text with the generated audio
            alignment_data = []
            try:
                # Gentle provides word-level timestamps
                gentle_result = await gentle_service.align_audio_with_transcript(output_path, text)
                
                # Convert Gentle format to our WordBoundary format
                for word_data in gentle_result.get("words", []):
                    alignment_data.append({
                        "type": "WordBoundary",
                        "offset": word_data["start"] * 10000,  # Convert ms to 100-nanosecond units
                        "duration": (word_data["end"] - word_data["start"]) * 10000,
                        "text": word_data["word"].strip()
                    })
                
                logger.info(f"Aligned {len(alignment_data)} words using Gentle")
                
            except Exception as e:
                print(f"GENTLE ERROR: {e}")
                import traceback
                traceback.print_exc()
                logger.warning(f"Gentle alignment failed: {e}. Audio will play without word highlighting.")

            logger.info(f"Generated dialogue audio: {output_path} with {len(alignment_data)} words aligned")
            return output_path, json.dumps(alignment_data)
            
        except Exception as e:
            logger.error(f"Error generating dialogue audio: {e}")
            raise
    
    @staticmethod
    def list_available_voices() -> dict:
        """Return available voice options"""
        return {
            "en-US": {
                "male": ["en-US-GuyNeural", "en-US-DavisNeural"],
                "female": ["en-US-JennyNeural", "en-US-AriaNeural"]
            },
            "en-GB": {
                "male": ["en-GB-RyanNeural"],
                "female": ["en-GB-SoniaNeural", "en-GB-LibbyNeural"]
            }
        }


# Global service instance
tts_service = TTSService()
