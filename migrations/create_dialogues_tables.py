"""
Migration: Create Dialogues Tables for Conversation Practice
============================================================

This migration creates the following tables:
- dialogues: Pre-defined conversation dialogues
- dialogue_lines: Individual lines of each dialogue
- student_dialogue_attempts: Student practice attempts with scores

Run: python migrations/create_dialogues_tables.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

# SQL Migration
MIGRATION_SQL = """
-- =====================================================
-- DIALOGUES - Práctica de Conversación
-- =====================================================

-- Main dialogues table
CREATE TABLE IF NOT EXISTS dialogues (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    difficulty_level VARCHAR(50) DEFAULT 'beginner',
    student_role VARCHAR(100) NOT NULL,
    tutor_role VARCHAR(100) NOT NULL,
    voice_gender VARCHAR(10) DEFAULT 'female',
    voice_accent VARCHAR(20) DEFAULT 'en-US',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Dialogue lines table
CREATE TABLE IF NOT EXISTS dialogue_lines (
    id SERIAL PRIMARY KEY,
    dialogue_id INTEGER NOT NULL REFERENCES dialogues(id) ON DELETE CASCADE,
    role VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    audio_url VARCHAR(500)
);

-- Student attempts table
CREATE TABLE IF NOT EXISTS student_dialogue_attempts (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    dialogue_id INTEGER NOT NULL REFERENCES dialogues(id) ON DELETE CASCADE,
    line_id INTEGER NOT NULL REFERENCES dialogue_lines(id) ON DELETE CASCADE,
    audio_path VARCHAR(500),
    transcription TEXT,
    alignment_result TEXT,
    score NUMERIC(5, 2),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_dialogue_lines_dialogue_id ON dialogue_lines(dialogue_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_lines_order ON dialogue_lines(dialogue_id, order_index);
CREATE INDEX IF NOT EXISTS idx_student_dialogue_attempts_student ON student_dialogue_attempts(estudiante_id);
CREATE INDEX IF NOT EXISTS idx_student_dialogue_attempts_dialogue ON student_dialogue_attempts(dialogue_id);

-- Comments
COMMENT ON TABLE dialogues IS 'Pre-defined conversation dialogues for speaking practice';
COMMENT ON TABLE dialogue_lines IS 'Individual lines of each dialogue with role assignment';
COMMENT ON TABLE student_dialogue_attempts IS 'Student practice attempts with transcription and scores';
"""

def run_migration():
    """Execute the migration"""
    print("=" * 60)
    print("Running migration: Create Dialogues Tables")
    print("=" * 60)
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Execute migration
            conn.execute(text(MIGRATION_SQL))
            conn.commit()
            
        print("Migration completed successfully!")
        print("   - Created table: dialogues")
        print("   - Created table: dialogue_lines")
        print("   - Created table: student_dialogue_attempts")
        print("   - Created indexes for performance")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        # In case of failure, we raise to exit with error code if needed
        # raise

if __name__ == "__main__":
    run_migration()
