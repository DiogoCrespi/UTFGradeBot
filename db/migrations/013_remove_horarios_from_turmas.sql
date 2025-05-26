-- Create horarios table if it doesn't exist
CREATE TABLE IF NOT EXISTS horarios (
    id SERIAL PRIMARY KEY,
    turma_id INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    turno CHAR(1) NOT NULL,
    aula_inicio INTEGER NOT NULL,
    aula_fim INTEGER NOT NULL,
    sala VARCHAR(20) NOT NULL
);

-- Add foreign key constraint if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_horarios_turma'
    ) THEN
        ALTER TABLE horarios 
        ADD CONSTRAINT fk_horarios_turma 
        FOREIGN KEY (turma_id) 
        REFERENCES turmas(id) 
        ON DELETE CASCADE;
    END IF;
END $$;

-- Remove horarios column from turmas table
ALTER TABLE turmas DROP COLUMN IF EXISTS horarios; 