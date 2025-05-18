import pytest
import os
from db.db import Database

@pytest.fixture(scope="session")
def test_db():
    """Configura o banco de dados de teste"""
    # Configura variáveis de ambiente para teste
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '5432'
    os.environ['DB_NAME'] = 'turing_bot_test'
    os.environ['DB_USER'] = 'postgres'
    os.environ['DB_PASSWORD'] = '1597'
    
    # Cria o banco de teste
    db = Database()
    
    # Executa o schema
    with open('db/schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
        db.execute_query(schema)
    
    yield db
    
    # Limpa o banco após os testes
    db.execute_query("DROP SCHEMA public CASCADE;")
    db.execute_query("CREATE SCHEMA public;")
    db.execute_query("GRANT ALL ON SCHEMA public TO postgres;")
    db.execute_query("GRANT ALL ON SCHEMA public TO public;")

@pytest.fixture(autouse=True)
def setup_teardown(test_db):
    """Setup e teardown para cada teste"""
    # Setup: limpa as tabelas
    test_db.execute_query("TRUNCATE cursos, disciplinas, curso_disciplinas, turmas, horarios CASCADE;")
    
    yield
    
    # Teardown: limpa as tabelas novamente
    test_db.execute_query("TRUNCATE cursos, disciplinas, curso_disciplinas, turmas, horarios CASCADE;") 