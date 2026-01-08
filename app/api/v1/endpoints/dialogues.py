"""
Dialogues API Endpoints for Conversation Practice
==================================================

Endpoints:
- GET /dialogues - List all dialogues
- POST /dialogues - Create new dialogue
- GET /dialogues/{id} - Get dialogue with lines
- PUT /dialogues/{id} - Update dialogue
- DELETE /dialogues/{id} - Soft delete dialogue
- POST /dialogues/{id}/lines - Update dialogue lines
- POST /dialogues/{id}/generate-audio - Generate TTS for tutor lines
- POST /dialogues/{id}/evaluate - Evaluate student pronunciation
"""

import os
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.models import Dialogue, DialogueLine, StudentDialogueAttempt, Estudiante, DialogueRole
from app.schemas.dialogue import (
    DialogueCreate, DialogueUpdate, DialogueListResponse, DialogueDetailResponse,
    DialogueLineCreate, DialogueLineResponse, DialogueLinesUpdate,
    EvaluationRequest, EvaluationResponse, WordEvaluation,
    StudentDialogueProgress, StudentAttemptResponse
)
from app.services.pronunciation_service import pronunciation_service
from app.services.tts_service import tts_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Upload directory for student recordings
STUDENT_AUDIO_DIR = "uploads/dialogues/student_recordings"
os.makedirs(STUDENT_AUDIO_DIR, exist_ok=True)


# =====================================================
# CRUD Endpoints
# =====================================================

@router.get("/", response_model=List[DialogueListResponse])
def list_dialogues(
    skip: int = 0,
    limit: int = 100,
    difficulty: Optional[str] = None,
    activo: bool = True,
    db: Session = Depends(get_db)
):
    """List all dialogues with optional filtering"""
    query = db.query(Dialogue)
    
    if activo is not None:
        query = query.filter(Dialogue.activo == activo)
    
    if difficulty:
        query = query.filter(Dialogue.difficulty_level == difficulty)
    
    dialogues = query.offset(skip).limit(limit).all()
    
    # Add line count
    result = []
    for d in dialogues:
        item = DialogueListResponse(
            id=d.id,
            title=d.title,
            description=d.description,
            difficulty_level=d.difficulty_level,
            student_role=d.student_role,
            tutor_role=d.tutor_role,
            roles=d.roles,
            line_count=len(d.lines),

            activo=d.activo,
            modulo_id=d.modulo_id,
            modulo_nombre=d.modulo.nombre if d.modulo else None
        )
        result.append(item)
    
    return result


@router.post("/", response_model=DialogueDetailResponse)
def create_dialogue(
    dialogue_data: DialogueCreate,
    db: Session = Depends(get_db)
):
    """Create a new dialogue with optional lines"""
    dialogue = Dialogue(
        title=dialogue_data.title,
        description=dialogue_data.description,
        difficulty_level=dialogue_data.difficulty_level,

        student_role="legacy_ignored", # Required by model but ignored in new logic
        tutor_role="legacy_ignored",   # Required by model but ignored in new logic
        modulo_id=dialogue_data.modulo_id
    )
    
    # If legacy fields are present but no roles provided, create default roles
    # (Assuming frontend might still send old format or we want backward compat)
    # However, since we updated schemas, we should expect roles list.
    
    # Simple defaults for backward compat if strings provided but no roles list
    if not dialogue_data.roles and dialogue_data.student_role and dialogue_data.tutor_role:
        pass # We will handle this by requiring roles in frontend, or creating them here.
        
    db.add(dialogue)
    db.flush()  # Get ID
    
    # Add roles
    for role_data in dialogue_data.roles:
        role = DialogueRole(
            dialogue_id=dialogue.id,
            name=role_data.name,
            voice_gender=role_data.voice_gender,
            voice_accent=role_data.voice_accent
        )
        db.add(role)
        
    # Add lines if provided
    
    # Add lines if provided
    for i, line_data in enumerate(dialogue_data.lines or []):
        line = DialogueLine(
            dialogue_id=dialogue.id,
            role=line_data.role,
            text=line_data.text,
            order_index=line_data.order_index if line_data.order_index is not None else i
        )
        db.add(line)
    
    db.commit()
    db.refresh(dialogue)
    
    logger.info(f"Created dialogue: {dialogue.id} - {dialogue.title}")
    return dialogue


@router.get("/{dialogue_id}", response_model=DialogueDetailResponse)
def get_dialogue(
    dialogue_id: int,
    db: Session = Depends(get_db)
):
    """Get dialogue with all lines"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    
    return dialogue


@router.put("/{dialogue_id}", response_model=DialogueDetailResponse)
def update_dialogue(
    dialogue_id: int,
    dialogue_data: DialogueUpdate,
    db: Session = Depends(get_db)
):
    """Update dialogue metadata"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    
    update_data = dialogue_data.model_dump(exclude_unset=True)
    
    # Handle roles separately
    roles_data = update_data.pop('roles', None)
    
    for field, value in update_data.items():
        setattr(dialogue, field, value)
        
    if roles_data is not None:
        # Replace roles (simple strategy: delete all and recreate)
        # In a more complex app we might want to update by ID to preserve external refs, 
        # but DialogueLines use role name (string) so ID persistence isn't critical for integrity 
        # as long as names match.
        db.query(DialogueRole).filter(DialogueRole.dialogue_id == dialogue_id).delete()
        for role_d in roles_data:
            new_role = DialogueRole(
                dialogue_id=dialogue_id,
                name=role_d['name'],
                voice_gender=role_d['voice_gender'],
                voice_accent=role_d['voice_accent']
            )
            db.add(new_role)
    
    db.commit()
    db.refresh(dialogue)
    
    return dialogue


@router.delete("/{dialogue_id}")
def delete_dialogue(
    dialogue_id: int,
    db: Session = Depends(get_db)
):
    """Soft delete dialogue"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    
    dialogue.activo = False
    db.commit()
    
    return {"message": "Dialogue deactivated", "id": dialogue_id}


# =====================================================
# Lines Management
# =====================================================

@router.post("/{dialogue_id}/lines", response_model=DialogueDetailResponse)
def update_dialogue_lines(
    dialogue_id: int,
    lines_data: DialogueLinesUpdate,
    db: Session = Depends(get_db)
):
    """Replace all lines for a dialogue"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    
    # Delete existing lines
    db.query(DialogueLine).filter(DialogueLine.dialogue_id == dialogue_id).delete()
    
    # Add new lines
    for i, line_data in enumerate(lines_data.lines):
        line = DialogueLine(
            dialogue_id=dialogue_id,
            role=line_data.role,
            text=line_data.text,
            order_index=line_data.order_index if line_data.order_index is not None else i,
            audio_url=line_data.audio_url,
            alignment_json=line_data.alignment_json
        )
        db.add(line)
    
    db.commit()
    db.refresh(dialogue)
    
    return dialogue


# =====================================================
# TTS Audio Generation
# =====================================================

@router.post("/{dialogue_id}/generate-audio")
async def generate_dialogue_audio(
    dialogue_id: int,
    db: Session = Depends(get_db)
):
    """Generate TTS audio for all tutor lines in the dialogue"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    
    # Generate audio for ALL lines so roles can be swapped
    lines_to_generate = dialogue.lines
    
    if not lines_to_generate:
        raise HTTPException(status_code=400, detail="No lines found in dialogue")
    
    generated = []
    
    # Map role names to their settings
    role_map = {r.name: r for r in dialogue.roles}
    
    for line in lines_to_generate:
        try:
            role_settings = role_map.get(line.role)
            # Default to female/US if role not found (though it should be)
            gender = role_settings.voice_gender if role_settings else 'female'
            accent = role_settings.voice_accent if role_settings else 'en-US'
            
            audio_path, alignment_json = await tts_service.generate_dialogue_audio(
                dialogue_id=dialogue_id,
                line_id=line.id,
                text=line.text,
                gender=gender,
                accent=accent
            )
            
            # Update line with audio URL and alignment
            line.audio_url = audio_path
            line.alignment_json = alignment_json
            db.add(line) # Explicitly join session
            generated.append({"line_id": line.id, "audio_url": audio_path, "alignment": "captured"})
            
        except Exception as e:
            logger.error(f"Failed to generate audio for line {line.id}: {e}")
            generated.append({"line_id": line.id, "error": str(e)})
    
    db.commit()
    
    return {
        "message": f"Generated audio for {len(generated)} lines",
        "dialogue_id": dialogue_id,
        "results": generated
    }


# =====================================================
# Pronunciation Evaluation
# =====================================================

@router.post("/{dialogue_id}/evaluate", response_model=EvaluationResponse)
async def evaluate_pronunciation(
    dialogue_id: int,
    line_id: int = Form(...),
    audio: UploadFile = File(...),
    estudiante_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Evaluate student pronunciation for a specific dialogue line.
    
    Args:
        dialogue_id: ID of the dialogue
        line_id: ID of the specific line being practiced
        audio: Audio file uploaded by student
        estudiante_id: Optional student ID for progress tracking
    """
    # Get dialogue and line
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    
    # Find the specific line
    target_line = db.query(DialogueLine).filter(
        DialogueLine.id == line_id,
        DialogueLine.dialogue_id == dialogue_id
    ).first()
    
    if not target_line:
        raise HTTPException(status_code=404, detail="Line not found in this dialogue")
    
    expected_text = target_line.text
    
    # Save uploaded audio
    audio_filename = f"dialogue_{dialogue_id}_line_{target_line.id}_{estudiante_id or 'anon'}.wav"
    audio_path = os.path.join(STUDENT_AUDIO_DIR, audio_filename)
    
    with open(audio_path, "wb") as f:
        content = await audio.read()
        f.write(content)
    
    logger.info(f"Saved student audio: {audio_path} (Size: {len(content)} bytes)")
    
    # Evaluate pronunciation
    try:
        result = await pronunciation_service.evaluate(audio_path, expected_text)
        logger.info(f"Evaluation result - Score: {result.score}, Transcribed: '{result.transcription}'")
    except Exception as e:
        logger.error(f"Pronunciation evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
    
    # Save attempt if student ID provided
    if estudiante_id:
        import json
        attempt = StudentDialogueAttempt(
            estudiante_id=estudiante_id,
            dialogue_id=dialogue_id,
            line_id=target_line.id,
            audio_path=audio_path,
            transcription=result.transcription,
            alignment_result=json.dumps(result.alignment_data) if result.alignment_data else None,
            score=result.score,
            feedback=result.feedback
        )
        db.add(attempt)
        db.commit()
    
    # Build response
    return EvaluationResponse(
        score=result.score,
        transcription=result.transcription,
        expected_text=result.expected_text,
        matched_words=result.matched_words,
        total_words=result.word_count,
        missed_words=result.missed_words,
        word_evaluations=[
            WordEvaluation(**w) for w in result.word_evaluations
        ],
        feedback=result.feedback
    )


# =====================================================
# Student Progress
# =====================================================

@router.get("/{dialogue_id}/progress/{estudiante_id}", response_model=StudentDialogueProgress)
def get_student_progress(
    dialogue_id: int,
    estudiante_id: int,
    db: Session = Depends(get_db)
):
    """Get student's progress for a specific dialogue"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    
    # Get all attempts
    attempts = db.query(StudentDialogueAttempt).filter(
        StudentDialogueAttempt.dialogue_id == dialogue_id,
        StudentDialogueAttempt.estudiante_id == estudiante_id
    ).order_by(StudentDialogueAttempt.created_at.desc()).all()
    
    # Calculate stats
    student_lines = [l for l in dialogue.lines if l.role == dialogue.student_role]
    completed_line_ids = set(a.line_id for a in attempts if a.score and a.score >= 50)
    
    best_score = None
    if attempts:
        scores = [a.score for a in attempts if a.score is not None]
        best_score = max(scores) if scores else None
    
    return StudentDialogueProgress(
        dialogue_id=dialogue_id,
        dialogue_title=dialogue.title,
        total_lines=len(student_lines),
        completed_lines=len(completed_line_ids),
        best_score=best_score,
        last_attempt=attempts[0].created_at if attempts else None,
        attempts=[StudentAttemptResponse.model_validate(a) for a in attempts[:10]]
    )
