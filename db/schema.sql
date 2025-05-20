-- Criação das tabelas para o Turing Bot

-- Tabela de cursos
CREATE TABLE IF NOT EXISTS cursos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    modalidade VARCHAR(50) NOT NULL,
    campus VARCHAR(100) NOT NULL,
    turno VARCHAR(50) NOT NULL,
    duracao INTEGER NOT NULL,
    carga_horaria INTEGER NOT NULL,
    carga_horaria_total INTEGER NOT NULL,
    periodo_atual INTEGER NOT NULL,
    last_update TIMESTAMP,
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

-- Tabela de turmas
CREATE TABLE IF NOT EXISTS turmas (
    id SERIAL PRIMARY KEY,
    disciplina_id INTEGER REFERENCES disciplinas(id),
    codigo VARCHAR(10) NOT NULL,
    professor VARCHAR(255),
    vagas_totais INTEGER,
    vagas_ocupadas INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(disciplina_id, codigo)
);

-- Tabela de horários
CREATE TABLE IF NOT EXISTS horarios (
    id SERIAL PRIMARY KEY,
    turma_id INTEGER REFERENCES turmas(id),
    dia_semana INTEGER NOT NULL, -- 1=Segunda, 2=Terça, etc.
    turno VARCHAR(1) NOT NULL, -- 'M'=Manhã, 'T'=Tarde, 'N'=Noite
    aula_inicio INTEGER NOT NULL, -- Número da primeira aula
    aula_fim INTEGER NOT NULL, -- Número da última aula
    sala VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(turma_id, dia_semana, turno, aula_inicio)
);

-- Índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_curso_codigo ON cursos(codigo);
CREATE INDEX IF NOT EXISTS idx_disciplina_codigo ON disciplinas(codigo);
CREATE INDEX IF NOT EXISTS idx_curso_disciplinas_periodo ON curso_disciplinas(periodo);
CREATE INDEX IF NOT EXISTS idx_turma_codigo ON turmas(codigo);
CREATE INDEX IF NOT EXISTS idx_horario_dia_turno ON horarios(dia_semana, turno); 