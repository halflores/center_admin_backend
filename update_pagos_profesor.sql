-- Script to update pagos_profesor table

-- 1. Remove the 'periodo' column if it exists
ALTER TABLE pagos_profesor DROP COLUMN IF EXISTS periodo;

-- 2. Add the 'usuario_id' column
ALTER TABLE pagos_profesor ADD COLUMN usuario_id INTEGER;

-- 3. Add the foreign key constraint referencing the usuarios table
-- Note: Assuming 'usuarios' table exists and has 'id' as primary key
ALTER TABLE pagos_profesor 
ADD CONSTRAINT fk_pagos_profesor_usuario_id 
FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
