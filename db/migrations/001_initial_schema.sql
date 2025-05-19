-- Criação da tabela de cursos
CREATE TABLE IF NOT EXISTS cursos (
    codigo VARCHAR(10) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    carga_horaria_total INTEGER NOT NULL,
    periodo_atual INTEGER NOT NULL
);

-- Criação da tabela de disciplinas
CREATE TABLE IF NOT EXISTS disciplinas (
    codigo VARCHAR(10) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    carga_horaria INTEGER NOT NULL,
    periodo INTEGER NOT NULL,
    aulas_por_semana INTEGER NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('OBRIGATORIA', 'OPTATIVA')),
    curso_codigo VARCHAR(10) REFERENCES cursos(codigo)
);

-- Criação da tabela de turmas
CREATE TABLE IF NOT EXISTS turmas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL,
    professor VARCHAR(255) NOT NULL,
    disciplina_codigo VARCHAR(10) REFERENCES disciplinas(codigo),
    horarios JSONB NOT NULL -- Formato: [{"dia": "2M", "horario": "M1", "sala": "L22"}, ...]
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_disciplinas_curso ON disciplinas(curso_codigo);
CREATE INDEX IF NOT EXISTS idx_turmas_disciplina ON turmas(disciplina_codigo);
CREATE INDEX IF NOT EXISTS idx_disciplinas_periodo ON disciplinas(periodo); 