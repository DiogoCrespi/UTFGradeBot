-- Adiciona constraint UNIQUE para (disciplina_id, codigo) em turmas
ALTER TABLE turmas ADD CONSTRAINT turmas_disciplina_id_codigo_unique UNIQUE (disciplina_id, codigo); 