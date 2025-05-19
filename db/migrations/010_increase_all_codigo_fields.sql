-- Aumenta o tamanho de todos os campos codigo para VARCHAR(20)
ALTER TABLE cursos ALTER COLUMN codigo TYPE VARCHAR(20);
ALTER TABLE disciplinas ALTER COLUMN codigo TYPE VARCHAR(20);
ALTER TABLE turmas ALTER COLUMN codigo TYPE VARCHAR(20);

-- Atualiza os índices para refletir o novo tamanho
DROP INDEX IF EXISTS idx_curso_codigo;
DROP INDEX IF EXISTS idx_disciplina_codigo;
DROP INDEX IF EXISTS idx_turma_codigo;

CREATE INDEX idx_curso_codigo ON cursos(codigo);
CREATE INDEX idx_disciplina_codigo ON disciplinas(codigo);
CREATE INDEX idx_turma_codigo ON turmas(codigo); 