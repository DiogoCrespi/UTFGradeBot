import pytest
from db.db import Database
from db.queries import (
    INSERT_CURSO,
    INSERT_DISCIPLINA,
    INSERT_CURSO_DISCIPLINA,
    INSERT_TURMA,
    INSERT_HORARIO,
    SELECT_CURSO_POR_CODIGO,
    SELECT_DISCIPLINA_POR_CODIGO,
    SELECT_DISCIPLINAS_POR_CURSO_PERIODO
)

@pytest.fixture
def db():
    """Fixture para conexão com o banco de dados de teste"""
    return Database()

def test_insert_curso(db):
    """Testa a inserção de um curso"""
    curso_data = {
        'codigo': 'TEST001',
        'nome': 'Curso de Teste',
        'campus': 'Campus Teste'
    }
    
    result = db.execute_query(INSERT_CURSO, curso_data)
    assert result[0]['id'] is not None
    
    # Verifica se o curso foi inserido
    curso = db.execute_query(SELECT_CURSO_POR_CODIGO, {'codigo': 'TEST001'})
    assert len(curso) == 1
    assert curso[0]['nome'] == 'Curso de Teste'

def test_insert_disciplina(db):
    """Testa a inserção de uma disciplina"""
    disciplina_data = {
        'codigo': 'DISC001',
        'nome': 'Disciplina de Teste',
        'carga_horaria': 60,
        'tipo': 'OBRIGATORIA'
    }
    
    result = db.execute_query(INSERT_DISCIPLINA, disciplina_data)
    assert result[0]['id'] is not None
    
    # Verifica se a disciplina foi inserida
    disciplina = db.execute_query(SELECT_DISCIPLINA_POR_CODIGO, {'codigo': 'DISC001'})
    assert len(disciplina) == 1
    assert disciplina[0]['nome'] == 'Disciplina de Teste'

def test_insert_curso_disciplina(db):
    """Testa a inserção da relação curso-disciplina"""
    # Primeiro insere um curso
    curso_data = {
        'codigo': 'TEST002',
        'nome': 'Curso de Teste 2',
        'campus': 'Campus Teste'
    }
    curso_result = db.execute_query(INSERT_CURSO, curso_data)
    curso_id = curso_result[0]['id']
    
    # Depois insere uma disciplina
    disciplina_data = {
        'codigo': 'DISC002',
        'nome': 'Disciplina de Teste 2',
        'carga_horaria': 80,
        'tipo': 'ELETIVA'
    }
    disciplina_result = db.execute_query(INSERT_DISCIPLINA, disciplina_data)
    disciplina_id = disciplina_result[0]['id']
    
    # Insere a relação
    relacao_data = {
        'curso_id': curso_id,
        'disciplina_id': disciplina_id,
        'periodo': 1
    }
    db.execute_query(INSERT_CURSO_DISCIPLINA, relacao_data)
    
    # Verifica se a relação foi criada
    disciplinas = db.execute_query(
        SELECT_DISCIPLINAS_POR_CURSO_PERIODO,
        {'curso_id': curso_id, 'periodo': 1}
    )
    assert len(disciplinas) == 1
    assert disciplinas[0]['codigo'] == 'DISC002'

def test_insert_turma_horario(db):
    """Testa a inserção de turma e horário"""
    # Primeiro insere uma disciplina
    disciplina_data = {
        'codigo': 'DISC003',
        'nome': 'Disciplina de Teste 3',
        'carga_horaria': 60,
        'tipo': 'OBRIGATORIA'
    }
    disciplina_result = db.execute_query(INSERT_DISCIPLINA, disciplina_data)
    disciplina_id = disciplina_result[0]['id']
    
    # Insere a turma
    turma_data = {
        'disciplina_id': disciplina_id,
        'codigo': 'TURM001',
        'professor': 'Professor Teste',
        'vagas_totais': 40,
        'vagas_ocupadas': 30
    }
    turma_result = db.execute_query(INSERT_TURMA, turma_data)
    turma_id = turma_result[0]['id']
    
    # Insere o horário
    horario_data = {
        'turma_id': turma_id,
        'dia_semana': 1,
        'turno': 'M',
        'aula_inicio': 1,
        'aula_fim': 2,
        'sala': 'SALA001'
    }
    db.execute_query(INSERT_HORARIO, horario_data)
    
    # Verifica se a turma e o horário foram inseridos
    # (Aqui você pode adicionar queries de SELECT para verificar)

def test_duplicate_insert(db):
    """Testa a inserção de registros duplicados"""
    # Insere um curso
    curso_data = {
        'codigo': 'TEST003',
        'nome': 'Curso de Teste 3',
        'campus': 'Campus Teste'
    }
    db.execute_query(INSERT_CURSO, curso_data)
    
    # Tenta inserir o mesmo curso novamente
    curso_data['nome'] = 'Nome Alterado'
    result = db.execute_query(INSERT_CURSO, curso_data)
    
    # Verifica se o nome foi atualizado
    curso = db.execute_query(SELECT_CURSO_POR_CODIGO, {'codigo': 'TEST003'})
    assert curso[0]['nome'] == 'Nome Alterado' 