
import sys
import os

def check_whisper():
    print("Checking faster-whisper...")
    try:
        from faster_whisper import WhisperModel
        print("faster-whisper imported successfully.")
    except ImportError as e:
        print(f"ERROR: faster-whisper import failed: {e}")
        return

    print("Checking FFmpeg...")
    # faster-whisper usually bundles ctranslate2 which bundles some libs, but often needs system ffmpeg or libraries.
    # We'll try to init a model (this downloads it if missing, might take time)
    # Use "tiny" for speed test.
    try:
        print("Initializing 'tiny' model (CPU)...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        print("Model initialized successfully.")
    except Exception as e:
        print(f"ERROR: Model initialization failed: {e}")
        # Check if ffmpeg issue
        if "ffmpeg" in str(e).lower():
            print("Possible missing FFmpeg.")

if __name__ == "__main__":
    check_whisper()
