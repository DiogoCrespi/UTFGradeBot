-- Adiciona a coluna 'id' como chave primária na tabela cursos
ALTER TABLE cursos
ADD COLUMN IF NOT EXISTS id SERIAL;

-- Remove a constraint de chave primária antiga, se existir
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'cursos' AND constraint_type = 'PRIMARY KEY'
    ) THEN
        ALTER TABLE cursos DROP CONSTRAINT IF EXISTS cursos_pkey;
    END IF;
END$$;

-- Define 'id' como chave primária
ALTER TABLE cursos ADD PRIMARY KEY (id);

-- Garante que o campo 'codigo' seja único
CREATE UNIQUE INDEX IF NOT EXISTS idx_curso_codigo ON cursos(codigo); 