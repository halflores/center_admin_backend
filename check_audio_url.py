
from app.db.session import SessionLocal
from app.models.models import DialogueLine

def check_line(line_id):
    db = SessionLocal()
    try:
        line = db.query(DialogueLine).filter(DialogueLine.id == line_id).first()
        if line:
            print(f"Line {line.id} Audio URL: '{line.audio_url}'")
            print(f"Line Data: {line.__dict__}")
        else:
            print(f"Line {line_id} not found")
    finally:
        db.close()

if __name__ == "__main__":
    check_line(41)
