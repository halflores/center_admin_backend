import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.models import AudioLesson

def fix_path(lesson_id):
    db = SessionLocal()
    try:
        lesson = db.query(AudioLesson).filter(AudioLesson.id == lesson_id).first()
        if not lesson:
            print(f"Lesson {lesson_id} not found")
            return

        print(f"Current URL: {lesson.audio_url}")
        
        # Check if it looks like the absolute path we want to fix
        if "lesson_3_nemo.mp3" in lesson.audio_url:
            new_path = "audio/lessons/lesson_3_nemo.mp3"
            print(f"Updating to: {new_path}")
            
            lesson.audio_url = new_path
            db.commit()
            print("Update committed.")
            
            # Verify retrieval
            db.refresh(lesson)
            print(f"New URL in DB: {lesson.audio_url}")
        else:
            print("Current URL does not match expected filename pattern. Skipping.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_path(3)
