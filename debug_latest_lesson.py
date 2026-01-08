import sys
import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import AudioLesson
from app.services.audio_storage_service import audio_storage_service

def debug_all_attempts():
    db = SessionLocal()
    try:
        # Search for ALL lessons with this title
        lessons = db.query(AudioLesson).filter(AudioLesson.titulo.like("%Metropolitan Train%")).all()
        
        if not lessons:
            print("No lessons found with that title.")
            return

        print(f"Found {len(lessons)} lessons matching 'Metropolitan Train':")
        for lesson in lessons:
            print("-" * 30)
            print(f"ID: {lesson.id}")
            print(f"Created At: {lesson.created_at}")
            print(f"Status: {lesson.estado}")
            print(f"Audio URL: {lesson.audio_url}")
            
            if lesson.audio_url:
                try:
                    abs_path = audio_storage_service.get_absolute_path(lesson.audio_url)
                    exists = abs_path.exists()
                    print(f"File Exists: {exists}")
                    if exists:
                        print(f"Size: {abs_path.stat().st_size}")
                except Exception as e:
                    print(f"Error checking file: {e}")
            else:
                print("No Audio URL")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    debug_all_attempts()
