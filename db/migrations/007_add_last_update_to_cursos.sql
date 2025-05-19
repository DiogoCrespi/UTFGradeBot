-- Adiciona a coluna 'last_update' na tabela cursos
ALTER TABLE cursos
ADD COLUMN IF NOT EXISTS last_update TIMESTAMP;

-- Atualiza os registros existentes com a data atual
UPDATE cursos
SET last_update = CURRENT_TIMESTAMP
WHERE last_update IS NULL; 