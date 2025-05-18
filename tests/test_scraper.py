import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from scraper.main import Scraper
from core.models import Curso, Disciplina, Turma, Horario

# HTML de exemplo para testes
HTML_CURSO = """
<div class="curso-info">
    <h1 class="curso-nome">Engenharia de Computação</h1>
</div>
"""

HTML_DISCIPLINAS = """
<table class="grade-curricular">
    <tr>
        <th>Código</th>
        <th>Nome</th>
        <th>CH</th>
        <th>Tipo</th>
    </tr>
    <tr>
        <td>MAT1004</td>
        <td>Álgebra Linear</td>
        <td>60</td>
        <td>Obrigatória</td>
    </tr>
    <tr>
        <td>MAT1005</td>
        <td>Cálculo I</td>
        <td>80</td>
        <td>Obrigatória</td>
    </tr>
</table>
"""

HTML_TURMAS = """
<table class="turmas">
    <tr>
        <th>Código</th>
        <th>Professor</th>
        <th>Vagas</th>
        <th>Ocupadas</th>
        <th>Horários</th>
    </tr>
    <tr>
        <td>ALI2</td>
        <td>João Silva</td>
        <td>40</td>
        <td>35</td>
        <td>
            <span class="horario">Segunda 13:00-14:40 (Sala I11)</span>
            <span class="horario">Quarta 13:00-14:40 (Sala I11)</span>
        </td>
    </tr>
</table>
"""

@pytest.fixture
def mock_db():
    """Fixture para mock do banco de dados"""
    with patch('scraper.main.Database') as mock:
        db = Mock()
        db.execute_query.return_value = [{'id': 1}]
        mock.return_value = db
        yield db

@pytest.fixture
def mock_navegador():
    """Fixture para mock do navegador"""
    with patch('scraper.main.Navegador') as mock:
        navegador = Mock()
        navegador.driver.page_source = HTML_CURSO + HTML_DISCIPLINAS
        mock.return_value.__enter__.return_value = navegador
        yield navegador

def test_extrair_curso(mock_db, mock_navegador):
    """Testa a extração de informações do curso"""
    scraper = Scraper()
    soup = BeautifulSoup(HTML_CURSO, 'html.parser')
    curso = scraper._extrair_curso(soup)
    
    assert isinstance(curso, Curso)
    assert curso.nome == "Engenharia de Computação"
    assert curso.codigo == scraper.url.split('=')[-1]

def test_extrair_disciplinas(mock_db, mock_navegador):
    """Testa a extração de disciplinas"""
    scraper = Scraper()
    soup = BeautifulSoup(HTML_DISCIPLINAS, 'html.parser')
    disciplinas = scraper._extrair_disciplinas(soup)
    
    assert len(disciplinas) == 2
    assert isinstance(disciplinas[0], Disciplina)
    assert disciplinas[0].codigo == "MAT1004"
    assert disciplinas[0].nome == "Álgebra Linear"
    assert disciplinas[0].carga_horaria == 60
    assert disciplinas[0].tipo == "OBRIGATORIA"

def test_extrair_turmas(mock_db, mock_navegador):
    """Testa a extração de turmas e horários"""
    scraper = Scraper()
    mock_navegador.driver.page_source = HTML_TURMAS
    soup = BeautifulSoup(HTML_TURMAS, 'html.parser')
    turmas = scraper._extrair_turmas(mock_navegador, "MAT1004")
    
    assert len(turmas) == 1
    assert isinstance(turmas[0], Turma)
    assert turmas[0].codigo == "ALI2"
    assert turmas[0].professor == "João Silva"
    assert turmas[0].vagas_totais == 40
    assert turmas[0].vagas_ocupadas == 35
    
    # Verifica horários
    assert len(turmas[0].horarios) == 2
    assert isinstance(turmas[0].horarios[0], Horario)
    assert turmas[0].horarios[0].dia_semana == 1  # Segunda
    assert turmas[0].horarios[0].turno == "T"  # Tarde
    assert turmas[0].horarios[0].sala == "I11"

def test_converter_dia_semana():
    """Testa a conversão de dias da semana"""
    scraper = Scraper()
    assert scraper._converter_dia_semana("Segunda") == 1
    assert scraper._converter_dia_semana("Terça") == 2
    assert scraper._converter_dia_semana("Quarta") == 3
    assert scraper._converter_dia_semana("Quinta") == 4
    assert scraper._converter_dia_semana("Sexta") == 5
    assert scraper._converter_dia_semana("Sábado") == 6
    assert scraper._converter_dia_semana("Domingo") == 1  # Valor padrão

def test_determinar_turno():
    """Testa a determinação do turno baseado no horário"""
    scraper = Scraper()
    assert scraper._determinar_turno("08:00") == "M"  # Manhã
    assert scraper._determinar_turno("13:00") == "T"  # Tarde
    assert scraper._determinar_turno("19:00") == "N"  # Noite

def test_extrair_dados_completo(mock_db, mock_navegador):
    """Testa o fluxo completo de extração de dados"""
    scraper = Scraper()
    scraper.extrair_dados()
    
    # Verifica se as queries foram executadas
    assert mock_db.execute_query.call_count >= 5  # Curso + 2 disciplinas + turma + horários 