
from app.db.session import SessionLocal
from app.models.models import DialogueLine

def check_lines():
    db = SessionLocal()
    lines = db.query(DialogueLine).filter(DialogueLine.dialogue_id == 1).order_by(DialogueLine.order_index).all()
    for line in lines:
        print(f"ID: {line.id}, Role: {line.role}, Text: {line.text}")

if __name__ == "__main__":
    check_lines()
