import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json
import re
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import time
from config.settings import SCRAPING_CONFIG, DB_CONFIG, SELENIUM_CONFIG
import logging
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

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def get_db_connection():
    try:
        return psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        raise

def setup_driver():
    try:
        options = uc.ChromeOptions()
        if SELENIUM_CONFIG['headless']:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Configura o caminho do ChromeDriver
        driver_path = os.path.join(os.getcwd(), 'chromedriver', 'chromedriver.exe')
        if not os.path.exists(driver_path):
            logger.error(f"ChromeDriver não encontrado em: {driver_path}")
            raise FileNotFoundError(f"ChromeDriver não encontrado em: {driver_path}")
        
        driver = uc.Chrome(
            options=options,
            driver_executable_path=driver_path,
            version_main=120  # Especifica a versão do Chrome
        )
        return driver
    except Exception as e:
        logger.error(f"Erro ao configurar o ChromeDriver: {str(e)}")
        raise

def parse_horarios(horarios_str):
    """Converte string de horários para lista de dicionários"""
    horarios = []
    try:
        # Remove o "+info" do final
        horarios_str = horarios_str.replace("+info", "").strip()
        
        # Divide os horários
        for horario in horarios_str.split(" - "):
            # Extrai dia, horário e sala usando regex
            match = re.match(r'(\d+[MTN])(\d+)(\([A-Z]\d+\))', horario.strip())
            if match:
                dia, num, sala = match.groups()
                horarios.append({
                    "dia": int(dia[:-1]),  # Remove o M/T/N do final
                    "turno": dia[-1],      # Pega o M/T/N
                    "aula_inicio": int(num),
                    "aula_fim": int(num),
                    "sala": sala.strip("()")
                })
    except Exception as e:
        logger.error(f"Erro ao processar horários: {str(e)}")
    return horarios

def parse_disciplina(disciplina_text):
    """Extrai informações da disciplina do texto"""
    try:
        # Exemplo: [MAT1004] Álgebra Linear (3 aulas/sem)
        match = re.match(r'\[([A-Z0-9]+)\]\s+(.*?)\s+\((\d+)\s+aulas/sem\)', disciplina_text)
        if match:
            codigo, nome, aulas = match.groups()
            return {
                "codigo": codigo,
                "nome": nome,
                "carga_horaria": int(aulas) * 15,  # 15 semanas por semestre
                "tipo": "OBRIGATORIA" if not codigo.startswith("OP") else "OPTATIVA"
            }
    except Exception as e:
        logger.error(f"Erro ao processar disciplina: {str(e)}")
    return None

def parse_turma(turma_text):
    """Extrai informações da turma do texto"""
    try:
        # Exemplo: ALI2 — Franciele Buss Frescki Kestring [ 4M3(I11) - 4M4(I11) - 4M5(I11) ]
        match = re.match(r'([A-Z0-9]+)\s*—\s*([^[]+)\s*\[(.*?)\]', turma_text)
        if match:
            codigo, professor, horarios = match.groups()
            return {
                "codigo": codigo.strip(),
                "professor": professor.strip(),
                "horarios": parse_horarios(horarios)
            }
    except Exception as e:
        logger.error(f"Erro ao processar turma: {str(e)}")
    return None

def main():
    driver = None
    conn = None
    cur = None
    
    try:
        logger.info("Iniciando o scraper...")
        driver = setup_driver()
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Carrega a página inicial
        logger.info("Acessando a página inicial...")
        driver.get(SCRAPING_CONFIG['url'])
        time.sleep(5)  # Aguarda o carregamento inicial
        
        # Foca apenas no curso de Ciência da Computação
        curso_codigo = '04219'
        curso_nome = 'Ciência da Computação'
        
        logger.info(f"Processando curso: {curso_codigo} - {curso_nome}")
        
        # Tenta clicar no botão do curso usando JavaScript
        script = f"""
            var links = document.getElementsByTagName('a');
            for(var i = 0; i < links.length; i++) {{
                if(links[i].href.includes('CODIGO_CURSO={curso_codigo}')) {{
                    links[i].click();
                    return true;
                }}
            }}
            return false;
        """
        clicked = driver.execute_script(script)
        
        if not clicked:
            logger.error(f"Não foi possível encontrar o botão para o curso {curso_codigo}")
            return
        
        time.sleep(5)  # Aguarda o carregamento do curso
        
        # Aguarda o carregamento da página
        WebDriverWait(driver, SELENIUM_CONFIG['timeout']).until(
            EC.presence_of_element_located((By.ID, "resultado"))
        )
        
        # Insere ou atualiza o curso em uma transação separada
        try:
            cur.execute("""
                INSERT INTO cursos (codigo, nome, modalidade, campus, turno, duracao, carga_horaria, carga_horaria_total, periodo_atual)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (codigo) DO UPDATE
                SET nome = EXCLUDED.nome,
                    modalidade = EXCLUDED.modalidade,
                    campus = EXCLUDED.campus,
                    turno = EXCLUDED.turno,
                    duracao = EXCLUDED.duracao,
                    carga_horaria = EXCLUDED.carga_horaria,
                    carga_horaria_total = EXCLUDED.carga_horaria_total,
                    periodo_atual = EXCLUDED.periodo_atual
                RETURNING id
            """, (
                curso_codigo,
                curso_nome,
                'PRESENCIAL',  # valor padrão
                SCRAPING_CONFIG['campus'],
                'INTEGRAL',    # valor padrão
                8,             # valor padrão
                0,             # valor padrão
                0,             # valor padrão
                1              # valor padrão
            ))
            curso_id = cur.fetchone()[0]
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao inserir curso: {str(e)}")
            raise
        
        # Processa cada disciplina em transações separadas
        disciplinas = driver.find_elements(By.CLASS_NAME, "disc")
        for disciplina in disciplinas:
            try:
                # Extrai informações da disciplina
                disciplina_text = disciplina.text
                disciplina_info = parse_disciplina(disciplina_text)
                
                if disciplina_info:
                    logger.info(f"Processando disciplina: {disciplina_info['codigo']} - {disciplina_info['nome']}")
                    
                    # Insere ou atualiza a disciplina em uma transação separada
                    try:
                        cur.execute("""
                            INSERT INTO disciplinas (codigo, nome, carga_horaria, tipo)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (codigo, nome) DO UPDATE SET
                                carga_horaria = EXCLUDED.carga_horaria,
                                tipo = EXCLUDED.tipo
                            RETURNING id
                        """, (
                            disciplina_info['codigo'],
                            disciplina_info['nome'],
                            disciplina_info['carga_horaria'],
                            disciplina_info['tipo']
                        ))
                        disciplina_id = cur.fetchone()[0]
                        
                        # Relaciona a disciplina com o curso
                        cur.execute("""
                            INSERT INTO curso_disciplinas (curso_id, disciplina_id, periodo)
                            VALUES (%s, %s, 0)
                            ON CONFLICT (curso_id, disciplina_id, periodo) DO NOTHING
                        """, (curso_id, disciplina_id))
                        
                        # Processa as turmas da disciplina
                        # Procura as turmas que seguem esta disciplina
                        turmas = disciplina.find_elements(By.XPATH, "following-sibling::span[@class='tur']")
                        for turma in turmas:
                            turma_info = parse_turma(turma.text)
                            if turma_info:
                                logger.info(f"  Turma: {turma_info['codigo']} - Prof: {turma_info['professor']}")
                                
                                # Insere ou atualiza a turma
                                cur.execute("""
                                    INSERT INTO turmas (disciplina_id, codigo, professor)
                                    VALUES (%s, %s, %s)
                                    ON CONFLICT (disciplina_id, codigo) DO UPDATE
                                    SET professor = EXCLUDED.professor
                                    RETURNING id
                                """, (disciplina_id, turma_info['codigo'], turma_info['professor']))
                                turma_id = cur.fetchone()[0]
                                
                                # Insere os horários da turma
                                for horario in turma_info['horarios']:
                                    cur.execute("""
                                        INSERT INTO horarios 
                                        (turma_id, dia_semana, turno, aula_inicio, aula_fim, sala)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                        ON CONFLICT (turma_id, dia_semana, turno, aula_inicio) DO NOTHING
                                    """, (
                                        turma_id,
                                        horario['dia'],
                                        horario['turno'],
                                        horario['aula_inicio'],
                                        horario['aula_fim'],
                                        horario['sala']
                                    ))
                        
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        logger.error(f"Erro ao processar disciplina {disciplina_info['codigo']}: {str(e)}")
                        continue
            except Exception as e:
                logger.error(f"Erro ao processar disciplina: {str(e)}")
                continue
        
        logger.info("Curso processado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante a extração: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        if driver:
            try:
                driver.quit()
            except:
                pass

def count_cursos():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM cursos;")
        count = cur.fetchone()[0]
        print(f"Número de cursos na tabela: {count}")
    except Exception as e:
        print(f"Erro ao contar cursos: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()

# --- Classe Scraper desativada pois depende de 'curso_codigo' e não é usada no fluxo principal ---
'''
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
''' 