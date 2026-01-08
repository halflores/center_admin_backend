import sys
import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import AudioLesson
from app.core.config import settings

def debug_all_lessons():
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    db = SessionLocal()
    try:
        # Get ALL lessons
        lessons = db.query(AudioLesson).all()
        
        if not lessons:
            print("No lessons found in the database AT ALL.")
            return

        print(f"Found {len(lessons)} total lessons:")
        for lesson in lessons:
            print("-" * 30)
            print(f"ID: {lesson.id}")
            print(f"Title: {lesson.titulo}")
            print(f"Active (activo): {lesson.activo}")
            print(f"Status (estado): {lesson.estado}")
            print(f"Module ID: {lesson.modulo_id}")
            print(f"Audio URL: {lesson.audio_url}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    debug_all_lessons()
