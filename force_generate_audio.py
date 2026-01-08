
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.models import Dialogue

# Check if I can import the logic or just call the service manually.
# accessing endpoint logic is harder without Request object.
# I'll just use the service directly.

from app.services.tts_service import tts_service

async def generate_all():
    db = SessionLocal()
    try:
        dialogue_id = 1
        dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
        if not dialogue:
            print("Dialogue 1 not found")
            return

        print(f"Generating audio for Dialogue 1: {dialogue.title}")
        for line in dialogue.lines:
            print(f"  Line {line.id} ({line.role})...")
            try:
                audio_path, alignment_json = await tts_service.generate_dialogue_audio(
                    dialogue_id=dialogue.id,
                    line_id=line.id,
                    text=line.text,
                    gender=dialogue.voice_gender,
                    accent=dialogue.voice_accent
                )
                
                # Update DB
                line.audio_url = audio_path
                line.alignment_json = alignment_json
                db.add(line)
                print(f"    -> Generated: {audio_path} (aligned)")
            except Exception as e:
                print(f"    -> ERROR: {e}")
        
        db.commit()
        print("Done. DB Updated.")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate_all())
