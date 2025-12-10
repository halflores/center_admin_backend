-- Add comentarios column to profesores table
ALTER TABLE profesores ADD COLUMN IF NOT EXISTS comentarios TEXT;
