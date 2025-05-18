import pytest
from db.db import Database
from db.queries import (
    INSERT_CURSO,
    INSERT_DISCIPLINA,
    INSERT_CURSO_DISCIPLINA,
    SELECT_DISCIPLINAS_POR_CURSO_PERIODO
)

@pytest.fixture
def db():
    """Fixture que fornece uma instância do banco de dados"""
    return Database()

def test_insert_curso(db):
    """Testa a inserção de um curso"""
    result = db.execute_query(
        INSERT_CURSO,
        {
            'codigo': 'TEST001',
            'nome': 'Curso de Teste',
            'campus': 'Campus Teste'
        }
    )
    
    assert len(result) == 1
    assert result[0]['id'] is not None

def test_insert_disciplina(db):
    """Testa a inserção de uma disciplina"""
    result = db.execute_query(
        INSERT_DISCIPLINA,
        {
            'codigo': 'DISC001',
            'nome': 'Disciplina de Teste',
            'carga_horaria': 60,
            'tipo': 'OBRIGATORIA'
        }
    )
    
    assert len(result) == 1
    assert result[0]['id'] is not None

def test_insert_curso_disciplina(db):
    """Testa a inserção da relação curso-disciplina"""
    # Primeiro insere um curso
    curso_result = db.execute_query(
        INSERT_CURSO,
        {
            'codigo': 'TEST002',
            'nome': 'Curso de Teste 2',
            'campus': 'Campus Teste'
        }
    )
    curso_id = curso_result[0]['id']
    
    # Depois insere uma disciplina
    disciplina_result = db.execute_query(
        INSERT_DISCIPLINA,
        {
            'codigo': 'DISC002',
            'nome': 'Disciplina de Teste 2',
            'carga_horaria': 80,
            'tipo': 'ELETIVA'
        }
    )
    disciplina_id = disciplina_result[0]['id']
    
    # Por fim, insere a relação
    result = db.execute_query(
        INSERT_CURSO_DISCIPLINA,
        {
            'curso_id': curso_id,
            'disciplina_id': disciplina_id,
            'periodo': 1
        }
    )
    
    assert len(result) == 1
    assert result[0]['id'] is not None

def test_select_disciplinas_por_periodo(db):
    """Testa a consulta de disciplinas por período"""
    # Primeiro insere os dados necessários
    curso_result = db.execute_query(
        INSERT_CURSO,
        {
            'codigo': 'TEST003',
            'nome': 'Curso de Teste 3',
            'campus': 'Campus Teste'
        }
    )
    curso_id = curso_result[0]['id']
    
    disciplina_result = db.execute_query(
        INSERT_DISCIPLINA,
        {
            'codigo': 'DISC003',
            'nome': 'Disciplina de Teste 3',
            'carga_horaria': 90,
            'tipo': 'OBRIGATORIA'
        }
    )
    disciplina_id = disciplina_result[0]['id']
    
    db.execute_query(
        INSERT_CURSO_DISCIPLINA,
        {
            'curso_id': curso_id,
            'disciplina_id': disciplina_id,
            'periodo': 1
        }
    )
    
    # Agora testa a consulta
    disciplinas = db.execute_query(
        SELECT_DISCIPLINAS_POR_CURSO_PERIODO,
        {
            'curso_id': curso_id,
            'periodo': 1
        }
    )
    
    assert len(disciplinas) == 1
    assert disciplinas[0]['codigo'] == 'DISC003'
    assert disciplinas[0]['nome'] == 'Disciplina de Teste 3'
    assert disciplinas[0]['carga_horaria'] == 90
    assert disciplinas[0]['tipo'] == 'OBRIGATORIA' 