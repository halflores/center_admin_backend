
import logging
import asyncio
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add app to path
sys.path.append(os.getcwd())

from app.services.pronunciation_service import pronunciation_service

async def test_transcription():
    # File we saw in the logs (8984 bytes) -> ID 2 "That is the Tunari..."
    file_path = "uploads/dialogues/student_recordings/dialogue_1_line_2_anon.wav"
    expected_text = "That is the Tunari. It is a very big mountain in Cochabamba."
    
    if not os.path.exists(file_path):
        print("File not found.")
        return

    print(f"Testing FULL EVALUATION on: {file_path}")
    print(f"Expected: {expected_text}")
    
    try:
        # Run evaluation
        result = await pronunciation_service.evaluate(file_path, expected_text)
        print("\n--- EVALUATION RESULT ---")
        print(f"Score: {result.score}%")
        print(f"Transcription: '{result.transcription}'")
        print(f"Matched Words: {result.matched_words}/{result.word_count}")
        print(f"Feedback: {result.feedback}")
        print("-------------------------\n")
        
        # Print word evaluations
        for w in result.word_evaluations:
            status = "MATCH" if w['matched'] else "MISS"
            print(f"{w['word']:<15} {status} (Conf: {w.get('confidence', 0):.2f})")
            
    except Exception as e:
        print(f"\nERROR: Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_transcription())
