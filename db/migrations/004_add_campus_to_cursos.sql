-- Adiciona o campo 'campus' na tabela de cursos
ALTER TABLE cursos
ADD COLUMN IF NOT EXISTS campus VARCHAR(100) NOT NULL DEFAULT 'N/A'; 