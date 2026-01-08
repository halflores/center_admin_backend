"""
Seed Sample Dialogues
=====================

Creates sample dialogues for conversation practice.
Includes "A Visit to Tunari" and others.

Run: python seed_sample_dialogues.py
"""

import sys
import os
# Add current directory to sys.path to allow importing 'app'
sys.path.insert(0, os.path.abspath(os.getcwd()))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import Dialogue, DialogueLine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_dialogues():
    db = SessionLocal()
    try:
        logger.info("Seeding sample dialogues...")
        
        # 1. A Visit to Tunari
        dialogue_data = {
            "title": "A Visit to Tunari",
            "description": "Practice a conversation about planning a trip to Mount Tunari.",
            "difficulty_level": "beginner",
            "student_role": "Maria",
            "tutor_role": "Alex",
            "voice_gender": "male",
            "voice_accent": "en-US",
            "lines": [
                {"role": "Alex", "text": "Look at that mountain! What is it?"},
                {"role": "Maria", "text": "That is the Tunari. It is a very big mountain in Cochabamba."},
                {"role": "Alex", "text": "It is beautiful. Does it have snow?"},
                {"role": "Maria", "text": "Yes, sometimes in winter. It is very cold there."},
                {"role": "Alex", "text": "Can we go there?"},
                {"role": "Maria", "text": "Yes, people go hiking and take photos."},
                {"role": "Alex", "text": "I want to visit it tomorrow."},
                {"role": "Maria", "text": "Great! Let's go."}
            ]
        }
        
        create_dialogue(db, dialogue_data)
        
        # 2. Ordering Coffee
        coffee_data = {
            "title": "At the Coffee Shop",
            "description": "Learn how to order your favorite coffee.",
            "difficulty_level": "beginner",
            "student_role": "Customer",
            "tutor_role": "Barista",
            "voice_gender": "female",
            "voice_accent": "en-US",
            "lines": [
                {"role": "Barista", "text": "Hi there! What can I get for you today?"},
                {"role": "Customer", "text": "Hi, I would like a large latte, please."},
                {"role": "Barista", "text": "Sure thing. Do you want regular milk or oat milk?"},
                {"role": "Customer", "text": "Oat milk, please."},
                {"role": "Barista", "text": "Would you like anything to eat with that?"},
                {"role": "Customer", "text": "No, just the coffee thanks."},
                {"role": "Barista", "text": "Alright, that will be $4.50."},
                {"role": "Customer", "text": "Here you go. Thank you!"}
            ]
        }
        
        create_dialogue(db, coffee_data)
        
        logger.info("Seeding completed!")
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
    finally:
        db.close()

def create_dialogue(db: Session, data: dict):
    # Check if exists
    exists = db.query(Dialogue).filter(Dialogue.title == data["title"]).first()
    if exists:
        logger.info(f"Dialogue '{data['title']}' already exists. Skipping.")
        return

    logger.info(f"Creating dialogue: {data['title']}")
    
    dialogue = Dialogue(
        title=data["title"],
        description=data["description"],
        difficulty_level=data["difficulty_level"],
        student_role=data["student_role"],
        tutor_role=data["tutor_role"],
        voice_gender=data.get("voice_gender", "female"),
        voice_accent=data.get("voice_accent", "en-US")
    )
    db.add(dialogue)
    db.flush()
    
    for i, line in enumerate(data["lines"]):
        db_line = DialogueLine(
            dialogue_id=dialogue.id,
            role=line["role"],
            text=line["text"],
            order_index=i
        )
        db.add(db_line)
    
    db.commit()

if __name__ == "__main__":
    seed_dialogues()
