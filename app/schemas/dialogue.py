"""
Pydantic schemas for Dialogue/Conversation Practice
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


# =====================================================
# Dialogue Line Schemas
# =====================================================

class DialogueLineBase(BaseModel):
    role: str = Field(..., description="Role name (e.g., 'Alex' or 'Maria')")
    text: str = Field(..., description="Line text to speak")
    order_index: int = Field(..., description="Order in dialogue sequence")


class DialogueLineCreate(DialogueLineBase):
    audio_url: Optional[str] = None
    alignment_json: Optional[str] = None


class DialogueLineUpdate(BaseModel):
    role: Optional[str] = None
    text: Optional[str] = None
    order_index: Optional[int] = None


class DialogueLineResponse(DialogueLineBase):
    id: int
    dialogue_id: int
    audio_url: Optional[str] = None
    alignment_json: Optional[str] = None
    
    class Config:
        from_attributes = True



# =====================================================
# Dialogue Role Schemas
# =====================================================

class DialogueRoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    voice_gender: str = Field("female")
    voice_accent: str = Field("en-US")

class DialogueRoleCreate(DialogueRoleBase):
    pass

class DialogueRoleResponse(DialogueRoleBase):
    id: int
    dialogue_id: int
    
    class Config:
        from_attributes = True

# =====================================================
# Dialogue Schemas
# =====================================================

class DialogueBase(BaseModel):
    title: str = Field(..., max_length=200, description="Dialogue title")
    description: Optional[str] = Field(None, description="Dialogue description")
    difficulty_level: str = Field("beginner", description="beginner, intermediate, advanced")
    modulo_id: Optional[int] = Field(None, description="Linked module ID")


class DialogueCreate(DialogueBase):
    roles: List[DialogueRoleCreate] = Field(..., description="List of roles in the dialogue")
    lines: Optional[List[DialogueLineCreate]] = Field(default=[], description="Dialogue lines")
    
    # Optional backward compatibility fields (ignored in processing but kept for valid Pydantic models from old clients if any)
    student_role: Optional[str] = None
    tutor_role: Optional[str] = None


class DialogueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    activo: Optional[bool] = None
    roles: Optional[List[DialogueRoleCreate]] = None
    modulo_id: Optional[int] = None


class DialogueListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    difficulty_level: str
    difficulty_level: str
    student_role: Optional[str] = None
    tutor_role: Optional[str] = None
    roles: List[DialogueRoleResponse] = []
    line_count: int = 0

    activo: bool
    modulo_id: Optional[int] = None
    modulo_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True


class DialogueDetailResponse(DialogueBase):
    id: int
    activo: bool
    created_at: datetime
    student_role: Optional[str] = None
    tutor_role: Optional[str] = None
    voice_gender: Optional[str] = "female"
    voice_accent: Optional[str] = "en-US"
    lines: List[DialogueLineResponse] = []
    roles: List[DialogueRoleResponse] = []
    
    class Config:
        from_attributes = True


# =====================================================
# Evaluation Schemas
# =====================================================

class WordEvaluation(BaseModel):
    word: str
    matched: bool
    confidence: float
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None


class EvaluationRequest(BaseModel):
    line_index: int = Field(..., description="Index of the line being evaluated (0-based)")


class EvaluationResponse(BaseModel):
    score: float = Field(..., description="Pronunciation score 0-100")
    transcription: str = Field(..., description="What the student said (STT result)")
    expected_text: str = Field(..., description="What student was supposed to say")
    matched_words: int
    total_words: int
    missed_words: List[str] = []
    word_evaluations: List[WordEvaluation] = []
    feedback: str = Field(..., description="Human-readable feedback")


# =====================================================
# Student Progress Schemas
# =====================================================

class StudentAttemptResponse(BaseModel):
    id: int
    dialogue_id: int
    line_id: int
    score: Optional[float]
    feedback: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentDialogueProgress(BaseModel):
    dialogue_id: int
    dialogue_title: str
    total_lines: int
    completed_lines: int
    best_score: Optional[float]
    last_attempt: Optional[datetime]
    attempts: List[StudentAttemptResponse] = []


# =====================================================
# Bulk Operations
# =====================================================

class DialogueLinesUpdate(BaseModel):
    lines: List[DialogueLineCreate] = Field(..., description="Complete list of lines (replaces existing)")
