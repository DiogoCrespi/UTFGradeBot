-- Remove a foreign key antiga de turmas para disciplinas(codigo)
ALTER TABLE turmas DROP CONSTRAINT IF EXISTS turmas_disciplina_codigo_fkey;

-- Adiciona a coluna 'id' em disciplinas, se não existir
ALTER TABLE disciplinas ADD COLUMN IF NOT EXISTS id SERIAL;

-- Remove a constraint de chave primária antiga
ALTER TABLE disciplinas DROP CONSTRAINT IF EXISTS disciplinas_pkey CASCADE;

-- Define 'id' como chave primária
ALTER TABLE disciplinas ADD PRIMARY KEY (id);

-- Garante que o par (codigo, nome) seja único
CREATE UNIQUE INDEX IF NOT EXISTS idx_disciplina_codigo_nome ON disciplinas(codigo, nome);

-- Adiciona nova coluna disciplina_id em turmas, se não existir
ALTER TABLE turmas ADD COLUMN IF NOT EXISTS disciplina_id INTEGER;

-- Atualiza disciplina_id em turmas com base no código
UPDATE turmas t SET disciplina_id = d.id FROM disciplinas d WHERE t.disciplina_codigo = d.codigo;

-- Remove a coluna antiga disciplina_codigo, se não for mais necessária
ALTER TABLE turmas DROP COLUMN IF EXISTS disciplina_codigo;

-- Cria nova foreign key de turmas para disciplinas(id)
ALTER TABLE turmas ADD CONSTRAINT turmas_disciplina_id_fkey FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id); 