-- Adiciona campos faltantes na tabela de cursos
ALTER TABLE cursos
ADD COLUMN IF NOT EXISTS modalidade VARCHAR(50) NOT NULL DEFAULT 'PRESENCIAL',
ADD COLUMN IF NOT EXISTS turno VARCHAR(50) NOT NULL DEFAULT 'INTEGRAL',
ADD COLUMN IF NOT EXISTS duracao INTEGER NOT NULL DEFAULT 8,
ADD COLUMN IF NOT EXISTS carga_horaria INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS carga_horaria_total INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS periodo_atual INTEGER NOT NULL DEFAULT 1;

-- Atualiza os valores padrão para cursos existentes
UPDATE cursos
SET modalidade = 'PRESENCIAL',
    turno = 'INTEGRAL',
    duracao = 8,
    carga_horaria = 0,
    carga_horaria_total = 0,
    periodo_atual = 1
WHERE modalidade IS NULL
   OR turno IS NULL
   OR duracao IS NULL
   OR carga_horaria IS NULL
   OR carga_horaria_total IS NULL
   OR periodo_atual IS NULL; 