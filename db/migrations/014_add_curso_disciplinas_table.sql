-- Create curso_disciplinas table for many-to-many relationship
CREATE TABLE IF NOT EXISTS curso_disciplinas (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER NOT NULL,
    disciplina_id INTEGER NOT NULL,
    periodo INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT fk_curso_disciplinas_curso FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
    CONSTRAINT fk_curso_disciplinas_disciplina FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE,
    CONSTRAINT unique_curso_disciplina_periodo UNIQUE (curso_id, disciplina_id, periodo)
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_curso_disciplinas_curso ON curso_disciplinas(curso_id);
CREATE INDEX IF NOT EXISTS idx_curso_disciplinas_disciplina ON curso_disciplinas(disciplina_id); 