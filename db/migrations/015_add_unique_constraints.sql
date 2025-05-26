-- Add unique constraint to disciplinas
ALTER TABLE disciplinas 
    ADD CONSTRAINT unique_disciplina_codigo_nome 
    UNIQUE (codigo, nome);

-- Add unique constraint to turmas
ALTER TABLE turmas 
    ADD CONSTRAINT unique_turma_disciplina_codigo 
    UNIQUE (disciplina_id, codigo);

-- Add unique constraint to horarios
ALTER TABLE horarios 
    ADD CONSTRAINT unique_horario_turma_dia_turno_aula 
    UNIQUE (turma_id, dia_semana, turno, aula_inicio); 