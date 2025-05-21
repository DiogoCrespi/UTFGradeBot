-- Adiciona constraint UNIQUE para codigo em cursos
ALTER TABLE cursos ADD CONSTRAINT cursos_codigo_unique UNIQUE (codigo); 