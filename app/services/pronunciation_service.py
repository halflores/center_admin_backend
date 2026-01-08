"""
Pronunciation Evaluation Service
================================

Combines Whisper (STT) and Gentle (alignment) to evaluate
student pronunciation against expected dialogue text.

Flow:
1. Transcribe student audio with Whisper
2. Align audio with expected text using Gentle
3. Calculate score based on aligned words
4. Generate feedback
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .whisper_service import whisper_service
from .gentle_service import gentle_service

logger = logging.getLogger(__name__)


@dataclass
class WordEvaluation:
    """Evaluation result for a single word"""
    expected: str
    spoken: Optional[str]
    matched: bool
    confidence: float
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None


@dataclass
class PronunciationResult:
    """Complete pronunciation evaluation result"""
    score: float  # 0-100
    transcription: str
    expected_text: str
    word_count: int
    matched_words: int
    missed_words: List[str]
    word_evaluations: List[Dict]
    feedback: str
    alignment_data: Optional[Dict] = None


class PronunciationService:
    """
    Service to evaluate student pronunciation.
    
    Uses:
    - faster-whisper: Transcribe what the student said
    - Gentle: Align student audio with expected text for precise scoring
    
    The combination provides:
    - Transcription of actual speech (from Whisper)
    - Word-by-word alignment (from Gentle)
    - Confidence scores for each word
    """
    
    def __init__(self):
        self.whisper = whisper_service
        self.gentle = gentle_service
    
    async def evaluate(
        self,
        audio_path: str,
        expected_text: str
    ) -> PronunciationResult:
        """
        Evaluate pronunciation of student audio against expected text.
        
        Args:
            audio_path: Path to student's recorded audio
            expected_text: The text the student was supposed to say
            
        Returns:
            PronunciationResult with score, feedback, and word-level details
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Evaluating pronunciation for: {expected_text[:50]}...")
        
        # Step 1: Transcribe with Whisper (what the student actually said)
        try:
            transcription_result = self.whisper.transcribe(audio_path)
            transcription = transcription_result.get("text", "")
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            transcription = ""
        
        # Step 2: Align with Gentle (compare audio to expected text)
        alignment_data = None
        aligned_words = []
        
        try:
            alignment_data = await self.gentle.align_audio_with_transcript(
                audio_path,
                expected_text
            )
            aligned_words = alignment_data.get("words", [])
        except Exception as e:
            logger.warning(f"Gentle alignment failed, using simple comparison: {e}")
        
        # Step 3: Calculate score
        score, word_evaluations, missed_words = self._calculate_score(
            expected_text,
            aligned_words,
            transcription
        )
        
        # Step 4: Generate feedback
        feedback = self._generate_feedback(score, missed_words, word_evaluations)
        
        # Step 5: Build result
        result = PronunciationResult(
            score=round(score, 1),
            transcription=transcription,
            expected_text=expected_text,
            word_count=len(expected_text.split()),
            matched_words=len([w for w in word_evaluations if w.get("matched", False)]),
            missed_words=missed_words,
            word_evaluations=word_evaluations,
            feedback=feedback,
            alignment_data=alignment_data
        )
        
        logger.info(f"Pronunciation evaluation complete: {result.score}% ({result.matched_words}/{result.word_count} words)")
        
        return result
    
    def _calculate_score(
        self,
        expected_text: str,
        aligned_words: List[Dict],
        transcription: str
    ) -> tuple:
        """
        Calculate pronunciation score based on alignment results.
        
        Returns:
            (score, word_evaluations, missed_words)
        """
        expected_words = self._normalize_text(expected_text).split()
        
        if not expected_words:
            return 100.0, [], []
        
        word_evaluations = []
        missed_words = []
        matched_count = 0
        
        if aligned_words:
            # Use Gentle alignment results
            aligned_word_texts = [
                self._normalize_text(w.get("word", "")) 
                for w in aligned_words 
                if w.get("case") == "success"
            ]
            
            for expected_word in expected_words:
                normalized_expected = self._normalize_text(expected_word)
                
            # Prepare transcribed words for fallback lookup
            transcribed_words = set(self._normalize_text(transcription).split())
            
            for expected_word in expected_words:
                normalized_expected = self._normalize_text(expected_word)
                
                # Check 1: Is it in Gentle's aligned words? (High Precision)
                matched_alignment = normalized_expected in aligned_word_texts
                
                # Check 2: Is it in Whisper's raw transcription? (Recall)
                # Only check if alignment failed
                matched_transcription = False
                if not matched_alignment:
                     matched_transcription = normalized_expected in transcribed_words
                
                matched = matched_alignment or matched_transcription
                
                # Find alignment data for this word if available
                word_data = next(
                    (w for w in aligned_words 
                     if self._normalize_text(w.get("word", "")) == normalized_expected),
                    None
                )
                
                if matched:
                    matched_count += 1
                    confidence = 0.8 # Default for transcription match
                    if matched_alignment and word_data:
                        confidence = word_data.get("confidence", 0.9)
                        
                    word_evaluations.append({
                        "word": expected_word,
                        "matched": True,
                        "confidence": confidence,
                        "start_ms": word_data.get("start") if word_data else None,
                        "end_ms": word_data.get("end") if word_data else None
                    })
                else:
                    missed_words.append(expected_word)
                    word_evaluations.append({
                        "word": expected_word,
                        "matched": False,
                        "confidence": 0.0
                    })
        else:
            # Fallback: Simple word matching with transcription
            transcribed_words = self._normalize_text(transcription).split()
            
            for expected_word in expected_words:
                normalized = self._normalize_text(expected_word)
                matched = normalized in transcribed_words
                
                if matched:
                    matched_count += 1
                    word_evaluations.append({
                        "word": expected_word,
                        "matched": True,
                        "confidence": 0.8
                    })
                else:
                    missed_words.append(expected_word)
                    word_evaluations.append({
                        "word": expected_word,
                        "matched": False,
                        "confidence": 0.0
                    })
        
        # Calculate score percentage
        score = (matched_count / len(expected_words)) * 100 if expected_words else 100.0
        
        return score, word_evaluations, missed_words
    
    def _generate_feedback(
        self,
        score: float,
        missed_words: List[str],
        word_evaluations: List[Dict]
    ) -> str:
        """Generate human-readable feedback based on evaluation"""
        
        if score >= 90:
            feedback = "¡Excelente! Tu pronunciación es muy buena."
        elif score >= 75:
            feedback = "¡Muy bien! Tu pronunciación es buena."
        elif score >= 50:
            feedback = "Buen intento. Sigue practicando para mejorar."
        else:
            feedback = "Necesitas más práctica. Escucha el audio del tutor e intenta de nuevo."
        
        if missed_words and len(missed_words) <= 3:
            words_str = ", ".join(f"'{w}'" for w in missed_words[:3])
            feedback += f" Practica las palabras: {words_str}."
        elif len(missed_words) > 3:
            feedback += f" Hay {len(missed_words)} palabras que necesitan más práctica."
        
        return feedback
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        import re
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def evaluate_sync(
        self,
        audio_path: str,
        expected_text: str
    ) -> PronunciationResult:
        """Synchronous wrapper for evaluate()"""
        import asyncio
        return asyncio.run(self.evaluate(audio_path, expected_text))


# Global service instance
pronunciation_service = PronunciationService()
