from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from config.settings import SCRAPING_CONFIG
from scraper.navegador import Navegador
from db.db import Database
from db.queries import (
    INSERT_CURSO,
    INSERT_DISCIPLINA,
    INSERT_CURSO_DISCIPLINA,
    SELECT_CURSO_POR_CODIGO
)
from core.models import Curso, Disciplina, CursoDisciplina

class Scraper:
    def __init__(self):
        self.db = Database()
        self.url = f"{SCRAPING_CONFIG['url']}#CODIGO_CURSO={SCRAPING_CONFIG['curso_codigo']}"
    
    def extrair_dados(self):
        """Extrai os dados da grade curricular"""
        with Navegador() as navegador:
            navegador.acessar_url(self.url)
            time.sleep(5)  # Aguarda o carregamento dinâmico
            
            # Extrai o HTML da página
            html = navegador.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extrai informações do curso
            curso = self._extrair_curso(soup)
            curso_id = self._salvar_curso(curso)
            
            # Extrai disciplinas
            disciplinas = self._extrair_disciplinas(soup)
            self._salvar_disciplinas(disciplinas, curso_id)
    
    def _extrair_curso(self, soup):
        """Extrai informações do curso da página"""
        nome_curso = soup.find('h1', {'class': 'curso-nome'}).text.strip()
        return Curso(
            codigo=SCRAPING_CONFIG['curso_codigo'],
            nome=nome_curso,
            campus='Cornélio Procópio'  # Pode ser extraído da página se necessário
        )
    
    def _extrair_disciplinas(self, soup):
        """Extrai as disciplinas da grade curricular"""
        disciplinas = []
        tabela = soup.find('table', {'class': 'grade-curricular'})
        
        if not tabela:
            return disciplinas
        
        for row in tabela.find_all('tr')[1:]:  # Pula o cabeçalho
            cols = row.find_all('td')
            if len(cols) >= 4:
                disciplina = Disciplina(
                    codigo=cols[0].text.strip(),
                    nome=cols[1].text.strip(),
                    carga_horaria=int(cols[2].text.strip()),
                    tipo='OBRIGATORIA' if 'Obrigatória' in cols[3].text else 'ELETIVA'
                )
                disciplinas.append(disciplina)
        
        return disciplinas
    
    def _salvar_curso(self, curso):
        """Salva ou atualiza o curso no banco de dados"""
        result = self.db.execute_query(
            INSERT_CURSO,
            {
                'codigo': curso.codigo,
                'nome': curso.nome,
                'campus': curso.campus
            }
        )
        return result[0]['id']
    
    def _salvar_disciplinas(self, disciplinas, curso_id):
        """Salva as disciplinas e suas relações com o curso"""
        for disciplina in disciplinas:
            # Salva a disciplina
            result = self.db.execute_query(
                INSERT_DISCIPLINA,
                {
                    'codigo': disciplina.codigo,
                    'nome': disciplina.nome,
                    'carga_horaria': disciplina.carga_horaria,
                    'tipo': disciplina.tipo
                }
            )
            disciplina_id = result[0]['id']
            
            # Salva a relação curso-disciplina
            self.db.execute_query(
                INSERT_CURSO_DISCIPLINA,
                {
                    'curso_id': curso_id,
                    'disciplina_id': disciplina_id,
                    'periodo': 1  # Será implementado a extração do período
                }
            )

if __name__ == '__main__':
    scraper = Scraper()
    scraper.extrair_dados() 