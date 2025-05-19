-- Adiciona constraint UNIQUE para (codigo, nome) em disciplinas
ALTER TABLE disciplinas ADD CONSTRAINT disciplinas_codigo_nome_unique UNIQUE (codigo, nome); 