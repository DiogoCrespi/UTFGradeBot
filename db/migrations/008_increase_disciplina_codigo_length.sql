-- Aumenta o tamanho da coluna codigo na tabela disciplinas
ALTER TABLE disciplinas ALTER COLUMN codigo TYPE VARCHAR(20);
 
-- Atualiza o índice único para refletir o novo tamanho
DROP INDEX IF EXISTS idx_disciplina_codigo_nome;
CREATE UNIQUE INDEX idx_disciplina_codigo_nome ON disciplinas(codigo, nome); 