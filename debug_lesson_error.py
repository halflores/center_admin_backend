import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import SessionLocal
from app.models.models import AudioLesson
from app.services.audio_storage_service import audio_storage_service

def debug_lesson():
    db = SessionLocal()
    try:
        # Search for the lesson
        lesson = db.query(AudioLesson).filter(AudioLesson.titulo.like("%Metropolitan Train%")).first()
        
        if not lesson:
            print("Lesson not found.")
            return

        print(f"ID: {lesson.id}")
        print(f"Title: {lesson.titulo}")
        print(f"Status: {lesson.estado}")
        print(f"Audio URL (DB): {lesson.audio_url}")
        print(f"Transcript Length: {len(lesson.transcript_text) if lesson.transcript_text else 0}")
        
        if lesson.audio_url:
            abs_path = audio_storage_service.get_absolute_path(lesson.audio_url)
            print(f"Absolute Path: {abs_path}")
            print(f"File Exists: {abs_path.exists()}")
            
            if abs_path.exists():
                print(f"File Size: {abs_path.stat().st_size} bytes")
        else:
            print("No Audio URL in DB")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure app directory is in python path
    sys.path.append(os.getcwd())
    debug_lesson()
