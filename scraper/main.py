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
    INSERT_TURMA,
    INSERT_HORARIO,
    SELECT_CURSO_POR_CODIGO
)
from core.models import Curso, Disciplina, CursoDisciplina, Turma, Horario

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
            
            # Extrai turmas e horários
            for disciplina in disciplinas:
                turmas = self._extrair_turmas(navegador, disciplina.codigo)
                self._salvar_turmas(turmas, disciplina.id)
    
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
    
    def _extrair_turmas(self, navegador, codigo_disciplina):
        """Extrai as turmas de uma disciplina"""
        turmas = []
        
        # Navega para a página de turmas da disciplina
        url_turmas = f"{SCRAPING_CONFIG['url']}/turmas/{codigo_disciplina}"
        navegador.acessar_url(url_turmas)
        time.sleep(3)
        
        # Extrai o HTML da página de turmas
        html = navegador.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Encontra a tabela de turmas
        tabela = soup.find('table', {'class': 'turmas'})
        if not tabela:
            return turmas
        
        for row in tabela.find_all('tr')[1:]:  # Pula o cabeçalho
            cols = row.find_all('td')
            if len(cols) >= 4:
                turma = Turma(
                    codigo=cols[0].text.strip(),
                    professor=cols[1].text.strip(),
                    vagas_totais=int(cols[2].text.strip()),
                    vagas_ocupadas=int(cols[3].text.strip())
                )
                
                # Extrai horários da turma
                horarios = self._extrair_horarios(cols[4])
                turma.horarios = horarios
                
                turmas.append(turma)
        
        return turmas
    
    def _extrair_horarios(self, col_horarios):
        """Extrai os horários de uma turma"""
        horarios = []
        spans = col_horarios.find_all('span', {'class': 'horario'})
        
        for span in spans:
            texto = span.text.strip()
            # Exemplo: "Segunda 13:00-14:40 (Sala I11)"
            dia = self._converter_dia_semana(texto.split()[0])
            turno = self._determinar_turno(texto.split()[1])
            sala = texto.split('(')[1].replace(')', '').replace('Sala ', '') if '(' in texto else None
            
            horario = Horario(
                dia_semana=dia,
                turno=turno,
                aula_inicio=1,  # Será calculado baseado no horário
                aula_fim=2,     # Será calculado baseado no horário
                sala=sala
            )
            horarios.append(horario)
        
        return horarios
    
    def _converter_dia_semana(self, dia):
        """Converte nome do dia para número"""
        dias = {
            'Segunda': 1, 'Terça': 2, 'Quarta': 3,
            'Quinta': 4, 'Sexta': 5, 'Sábado': 6
        }
        return dias.get(dia, 1)
    
    def _determinar_turno(self, horario):
        """Determina o turno baseado no horário"""
        hora = int(horario.split(':')[0])
        if 7 <= hora < 12:
            return 'M'
        elif 12 <= hora < 18:
            return 'T'
        else:
            return 'N'
    
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
            disciplina.id = result[0]['id']
            
            # Salva a relação curso-disciplina
            self.db.execute_query(
                INSERT_CURSO_DISCIPLINA,
                {
                    'curso_id': curso_id,
                    'disciplina_id': disciplina.id,
                    'periodo': 1  # Será implementado a extração do período
                }
            )
    
    def _salvar_turmas(self, turmas, disciplina_id):
        """Salva as turmas e seus horários"""
        for turma in turmas:
            # Salva a turma
            result = self.db.execute_query(
                INSERT_TURMA,
                {
                    'disciplina_id': disciplina_id,
                    'codigo': turma.codigo,
                    'professor': turma.professor,
                    'vagas_totais': turma.vagas_totais,
                    'vagas_ocupadas': turma.vagas_ocupadas
                }
            )
            turma_id = result[0]['id']
            
            # Salva os horários da turma
            for horario in turma.horarios:
                self.db.execute_query(
                    INSERT_HORARIO,
                    {
                        'turma_id': turma_id,
                        'dia_semana': horario.dia_semana,
                        'turno': horario.turno,
                        'aula_inicio': horario.aula_inicio,
                        'aula_fim': horario.aula_fim,
                        'sala': horario.sala
                    }
                )

if __name__ == '__main__':
    scraper = Scraper()
    scraper.extrair_dados() 