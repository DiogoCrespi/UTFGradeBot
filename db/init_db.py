import psycopg2
from config.settings import DB_CONFIG

def init_database():
    """Inicializa o banco de dados com o schema correto"""
    # Conecta ao banco de dados postgres para criar o banco turing_bot
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database='postgres',
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Cria o banco de dados se não existir
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"Banco de dados {DB_CONFIG['database']} criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar banco de dados: {str(e)}")
    finally:
        cur.close()
        conn.close()
    
    # Conecta ao banco turing_bot para criar as tabelas
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Garante que a coluna last_update exista
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='cursos' AND column_name='last_update'
                ) THEN
                    ALTER TABLE cursos ADD COLUMN last_update TIMESTAMP;
                END IF;
            END$$;
        """)

        # Criação das tabelas
        cur.execute("""
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
        """)
        print("Tabelas criadas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar tabelas: {str(e)}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_database() 