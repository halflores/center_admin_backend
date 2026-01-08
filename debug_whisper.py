
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    print("Attempting to import faster_whisper...")
    from faster_whisper import WhisperModel
    print("Success: faster_whisper imported.")
    
    print("Attempting to load model 'tiny' (for speed test)...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    print("Success: Model loaded.")
    
    # We won't transcribe files to avoid path issues, just loading is a big step.
    # But if we did:
    # segments, info = model.transcribe("some_audio.mp3")
    
except ImportError:
    print("ERROR: faster_whisper module not found.")
except Exception as e:
    print(f"ERROR: Failed to initialize Whisper: {e}")
