-- Cria a tabela de atualizações globais
CREATE TABLE IF NOT EXISTS global_updates (
    id SERIAL PRIMARY KEY,
    last_update TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cria um índice para melhorar a performance das consultas
CREATE INDEX IF NOT EXISTS idx_global_updates_last_update ON global_updates(last_update); 