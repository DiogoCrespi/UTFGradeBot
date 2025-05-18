# Queries para manipulação de cursos
INSERT_CURSO = """
    INSERT INTO cursos (codigo, nome, campus)
    VALUES (%(codigo)s, %(nome)s, %(campus)s)
    ON CONFLICT (codigo) DO UPDATE
    SET nome = EXCLUDED.nome,
        campus = EXCLUDED.campus,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id;
"""

SELECT_CURSO_POR_CODIGO = """
    SELECT id, codigo, nome, campus
    FROM cursos
    WHERE codigo = %(codigo)s;
"""

# Queries para manipulação de disciplinas
INSERT_DISCIPLINA = """
    INSERT INTO disciplinas (codigo, nome, carga_horaria, tipo)
    VALUES (%(codigo)s, %(nome)s, %(carga_horaria)s, %(tipo)s)
    ON CONFLICT (codigo, nome) DO UPDATE
    SET carga_horaria = EXCLUDED.carga_horaria,
        tipo = EXCLUDED.tipo,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id;
"""

SELECT_DISCIPLINA_POR_CODIGO = """
    SELECT * FROM disciplinas
    WHERE codigo = %(codigo)s
"""

# Queries para manipulação de curso_disciplinas
INSERT_CURSO_DISCIPLINA = """
    INSERT INTO curso_disciplinas (curso_id, disciplina_id, periodo)
    VALUES (%(curso_id)s, %(disciplina_id)s, %(periodo)s)
    ON CONFLICT (curso_id, disciplina_id, periodo) DO UPDATE
    SET updated_at = CURRENT_TIMESTAMP
    RETURNING id;
"""

SELECT_DISCIPLINAS_POR_CURSO_PERIODO = """
    SELECT d.*, cd.periodo
    FROM disciplinas d
    JOIN curso_disciplinas cd ON d.id = cd.disciplina_id
    WHERE cd.curso_id = %(curso_id)s
    AND cd.periodo = %(periodo)s
    ORDER BY d.nome
"""

SELECT_CARGA_HORARIA_TOTAL_POR_PERIODO = """
    SELECT cd.periodo, SUM(d.carga_horaria) as total_horas
    FROM disciplinas d
    JOIN curso_disciplinas cd ON d.id = cd.disciplina_id
    WHERE cd.curso_id = %(curso_id)s
    GROUP BY cd.periodo
    ORDER BY cd.periodo
"""

# Queries para manipulação de turmas
INSERT_TURMA = """
    INSERT INTO turmas (disciplina_id, codigo, professor, vagas_totais, vagas_ocupadas)
    VALUES (%(disciplina_id)s, %(codigo)s, %(professor)s, %(vagas_totais)s, %(vagas_ocupadas)s)
    ON CONFLICT (disciplina_id, codigo) DO UPDATE
    SET professor = EXCLUDED.professor,
        vagas_totais = EXCLUDED.vagas_totais,
        vagas_ocupadas = EXCLUDED.vagas_ocupadas,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id;
"""

# Queries para manipulação de horários
INSERT_HORARIO = """
    INSERT INTO horarios (turma_id, dia_semana, turno, aula_inicio, aula_fim, sala)
    VALUES (%(turma_id)s, %(dia_semana)s, %(turno)s, %(aula_inicio)s, %(aula_fim)s, %(sala)s)
    ON CONFLICT (turma_id, dia_semana, turno, aula_inicio) DO UPDATE
    SET aula_fim = EXCLUDED.aula_fim,
        sala = EXCLUDED.sala,
        updated_at = CURRENT_TIMESTAMP;
""" 