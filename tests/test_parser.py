import pytest
from bs4 import BeautifulSoup
from core.models import Disciplina

def test_extrair_disciplina():
    """Testa a extração de uma disciplina do HTML"""
    # HTML de exemplo
    html = """
    <table class="grade-curricular">
        <tr>
            <th>Código</th>
            <th>Nome</th>
            <th>CH</th>
            <th>Tipo</th>
        </tr>
        <tr>
            <td>AS34A</td>
            <td>Algoritmos e Programação</td>
            <td>80</td>
            <td>Obrigatória</td>
        </tr>
    </table>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    tabela = soup.find('table', {'class': 'grade-curricular'})
    row = tabela.find_all('tr')[1]  # Pega a primeira linha de dados
    cols = row.find_all('td')
    
    disciplina = Disciplina(
        codigo=cols[0].text.strip(),
        nome=cols[1].text.strip(),
        carga_horaria=int(cols[2].text.strip()),
        tipo='OBRIGATORIA' if 'Obrigatória' in cols[3].text else 'ELETIVA'
    )
    
    assert disciplina.codigo == 'AS34A'
    assert disciplina.nome == 'Algoritmos e Programação'
    assert disciplina.carga_horaria == 80
    assert disciplina.tipo == 'OBRIGATORIA'

def test_extrair_disciplina_eletiva():
    """Testa a extração de uma disciplina eletiva"""
    html = """
    <table class="grade-curricular">
        <tr>
            <th>Código</th>
            <th>Nome</th>
            <th>CH</th>
            <th>Tipo</th>
        </tr>
        <tr>
            <td>AS34B</td>
            <td>Programação Web</td>
            <td>60</td>
            <td>Eletiva</td>
        </tr>
    </table>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    tabela = soup.find('table', {'class': 'grade-curricular'})
    row = tabela.find_all('tr')[1]
    cols = row.find_all('td')
    
    disciplina = Disciplina(
        codigo=cols[0].text.strip(),
        nome=cols[1].text.strip(),
        carga_horaria=int(cols[2].text.strip()),
        tipo='OBRIGATORIA' if 'Obrigatória' in cols[3].text else 'ELETIVA'
    )
    
    assert disciplina.codigo == 'AS34B'
    assert disciplina.nome == 'Programação Web'
    assert disciplina.carga_horaria == 60
    assert disciplina.tipo == 'ELETIVA' 