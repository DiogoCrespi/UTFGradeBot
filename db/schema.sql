-- Criação das tabelas para o Turing Bot

-- Tabela de cursos
CREATE TABLE IF NOT EXISTS cursos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    campus VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de disciplinas
CREATE TABLE IF NOT EXISTS disciplinas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL,
    nome VARCHAR(255) NOT NULL,
    carga_horaria INTEGER NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- 'OBRIGATORIA' ou 'ELETIVA'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(codigo, nome)
);

-- Tabela de relação entre cursos e disciplinas
CREATE TABLE IF NOT EXISTS curso_disciplinas (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER REFERENCES cursos(id),
    disciplina_id INTEGER REFERENCES disciplinas(id),
    periodo INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(curso_id, disciplina_id, periodo)
);

-- Índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_curso_codigo ON cursos(codigo);
CREATE INDEX IF NOT EXISTS idx_disciplina_codigo ON disciplinas(codigo);
CREATE INDEX IF NOT EXISTS idx_curso_disciplinas_periodo ON curso_disciplinas(periodo); 