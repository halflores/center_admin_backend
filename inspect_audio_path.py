import sys
import os
from pathlib import Path

# Add app to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.models import AudioLesson
from app.services.audio_storage_service import audio_storage_service

def inspect_lesson(lesson_id):
    db = SessionLocal()
    try:
        lesson = db.query(AudioLesson).filter(AudioLesson.id == lesson_id).first()
        if not lesson:
            print(f"Lesson {lesson_id} not found")
            return

        print(f"Lesson ID: {lesson.id}")
        print(f"Audio URL (DB): '{lesson.audio_url}'")
        
        if not lesson.audio_url:
            print("No audio URL")
            return

        # Test resolution
        try:
            abs_path = audio_storage_service.get_absolute_path(lesson.audio_url)
            print(f"Resolved Absolute Path: {abs_path}")
            print(f"Exists: {abs_path.exists()}")
            
            # Print base path info
            print(f"Service Base Path: {audio_storage_service.base_path.absolute()}")
            print(f"Base Parent: {audio_storage_service.base_path.parent.absolute()}")
            
            # Check manual fallback manually just in case
            p1 = audio_storage_service.base_path.parent / lesson.audio_url
            p2 = audio_storage_service.base_path / lesson.audio_url
            print(f"Path Check 1 ({p1}): {p1.exists()}")
            print(f"Path Check 2 ({p2}): {p2.exists()}")
            
        except Exception as e:
            print(f"Error resolving path: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    inspect_lesson(3)
