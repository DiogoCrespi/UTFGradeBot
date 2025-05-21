import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from selenium.common.exceptions import NoAlertPresentException

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Arquivo para armazenar a data da última atualização global
LAST_GLOBAL_UPDATE_FILE = 'last_global_update.txt'

def read_last_global_update():
    """Lê a data da última atualização global salva em arquivo"""
    if os.path.exists(LAST_GLOBAL_UPDATE_FILE):
        try:
            with open(LAST_GLOBAL_UPDATE_FILE, 'r') as f:
                timestamp_str = f.read().strip()
                if timestamp_str:
                    return datetime.fromisoformat(timestamp_str)
        except Exception as e:
            logger.error(f"Erro ao ler data de atualização global do arquivo: {str(e)}")
    return None

def write_last_global_update(timestamp: datetime):
    """Salva a data da última atualização global em arquivo"""
    try:
        with open(LAST_GLOBAL_UPDATE_FILE, 'w') as f:
            f.write(timestamp.isoformat())
        logger.info(f"Data de atualização global salva: {timestamp}")
    except Exception as e:
        logger.error(f"Erro ao salvar data de atualização global no arquivo: {str(e)}")

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
                    "turno": str(dia[-1]),  # Pega o M/T/N e garante que é string
                    "aula_inicio": int(num),
                    "aula_fim": int(num),
                    "sala": str(sala.strip("()"))  # Garante que é string
                })
    except Exception as e:
        logger.error(f"Erro ao processar horários: {str(e)}")
    return horarios

def parse_disciplina(disciplina_text):
    """Extrai informações da disciplina do texto"""
    try:
        # Exemplo: [MAT1004] Álgebra Linear (3 aulas/sem)
        # Atualizado para capturar códigos de qualquer tamanho
        match = re.match(r'\[([A-Z0-9]+)\]\s+(.*?)\s+\((\d+)\s+aulas/sem\)', disciplina_text)
        if match:
            codigo, nome, aulas = match.groups()
            return {
                "codigo": str(codigo),  # Garante que é string
                "nome": str(nome),      # Garante que é string
                "carga_horaria": int(aulas) * 15,  # 15 semanas por semestre
                "tipo": "OBRIGATORIA" if not str(codigo).startswith("OP") else "OPTATIVA"
            }
        else:
            logger.warning(f"Formato inválido de disciplina: {disciplina_text}")
            return None
    except Exception as e:
        logger.error(f"Erro ao processar disciplina: {str(e)}")
        return None

def parse_turmas_html(html):
    """Extrai disciplinas e suas turmas do HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    current_disciplina = None
    for elem in soup.find_all(['span']):
        if 'class' in elem.attrs:
            if 'disc' in elem['class']:
                # Nova disciplina
                disc_text = elem.get_text(separator=' ', strip=True)
                # Exemplo: [MAT1004] Álgebra Linear (3 aulas/sem)
                m = re.match(r'\[([A-Z0-9]+)\]\s+(.*?)\s+\((\d+) aulas/sem\)', disc_text)
                if m:
                    codigo, nome, aulas = m.groups()
                    current_disciplina = {
                        "codigo": codigo.strip(),
                        "nome": nome.strip(),
                        "carga_horaria": int(aulas) * 15,  # 15 semanas por semestre
                        "turmas": []
                    }
                    results.append(current_disciplina)
                else:
                    current_disciplina = None
            elif 'tur' in elem['class'] and current_disciplina is not None:
                # Turma associada à disciplina atual
                label = elem.find('label')
                if not label:
                    continue
                texto = label.get_text(separator=' ', strip=True)
                # Exemplo: "ALI2 — Franciele Buss Frescki Kestring [ 4M3(I11) - 4M4(I11) - 4M5(I11) ]"
                match = re.match(r'([A-Z0-9]+)\s*—\s*([^\[]+)\s*\[\s*(.*?)\s*\]', texto)
                if not match:
                    continue
                codigo, professor, horarios_str = match.groups()
                horarios = []
                for h in horarios_str.split(' - '):
                    h_match = re.match(r'(\d)([MTN])(\d)\((.*?)\)', h.strip())
                    if h_match:
                        dia, turno, aula, sala = h_match.groups()
                        horarios.append({
                            "dia": int(dia),
                            "turno": turno,
                            "aula_inicio": int(aula),
                            "aula_fim": int(aula),
                            "sala": sala
                        })
                turma = {
                    "codigo": codigo.strip(),
                    "professor": professor.strip(),
                    "horarios": horarios
                }
                current_disciplina["turmas"].append(turma)
    return results

def handle_popup(driver):
    """Lida com popups do navegador"""
    try:
        # Aguarda um curto período para o popup aparecer
        time.sleep(1)
        
        # Tenta encontrar e aceitar o popup
        alert = driver.switch_to.alert
        alert.accept()
        return True
    except:
        return False

def process_curso(driver, curso_codigo, curso_nome, cur, campus_nome):
    """Processa um curso específico"""
    try:
        logger.info(f"Processando curso: {curso_codigo} - {curso_nome}")
        
        # Tenta clicar no botão do curso usando JavaScript
        script = f"""
            var links = document.getElementsByTagName('a');
            for(var i = 0; i < links.length; i++) {{
                if(links[i].href && links[i].href.includes('CODIGO_CURSO={curso_codigo}')) {{
                    links[i].click();
                    return true;
                }}
            }}
            return false;
        """
        clicked = driver.execute_script(script)
        time.sleep(1)

        # Verifica se há popup de erro
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            logger.warning(f"Alerta encontrado: {alert_text}")
            if "não está disponível no GNH" in alert_text:
                logger.warning(f"Curso {curso_codigo} não está disponível no momento")
                alert.accept()
                return False
            alert.accept()
        except:
            pass

        if not clicked:
            logger.error(f"Não foi possível encontrar o botão para o curso {curso_codigo}")
            return False

        time.sleep(5)
        
        # Verifica se há mensagem de erro
        try:
            error_message = driver.find_element(By.XPATH, "//*[contains(text(), 'este curso não está disponível no GNH')]")
            if error_message:
                logger.warning(f"Curso {curso_codigo} não está disponível no GNH")
                return False
        except:
            pass
        
        # Aguarda o carregamento da página
        try:
            WebDriverWait(driver, SELENIUM_CONFIG['timeout']).until(
                EC.presence_of_element_located((By.ID, "resultado"))
            )
        except:
            logger.error(f"Timeout ao carregar página do curso {curso_codigo}")
            return False

        # Extrai a data da última atualização
        try:
            last_update_text = driver.find_element(By.XPATH, "//strong[contains(text(), '/')]").text
            last_update = datetime.strptime(last_update_text, "%d/%m/%Y %H:%M:%S")
            
            # Verifica se o curso já existe e compara a data de atualização
            cur.execute("SELECT last_update FROM cursos WHERE codigo = %s", (curso_codigo,))
            result = cur.fetchone()
            
            if result and result[0] and last_update <= result[0]:
                logger.info(f"Curso {curso_codigo} já está atualizado. Última atualização: {result[0]}")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao verificar data de atualização: {str(e)}")
        
        # Inicia uma transação para o curso
        cur.execute("BEGIN")
        
        try:
            # Insere ou atualiza o curso
            cur.execute("""
                INSERT INTO cursos (codigo, nome, modalidade, campus, turno, duracao, carga_horaria, carga_horaria_total, periodo_atual, last_update)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (codigo) DO UPDATE
                SET nome = EXCLUDED.nome,
                    modalidade = EXCLUDED.modalidade,
                    campus = EXCLUDED.campus,
                    turno = EXCLUDED.turno,
                    duracao = EXCLUDED.duracao,
                    carga_horaria = EXCLUDED.carga_horaria,
                    carga_horaria_total = EXCLUDED.carga_horaria_total,
                    periodo_atual = EXCLUDED.periodo_atual,
                    last_update = EXCLUDED.last_update
                RETURNING id
            """, (
                curso_codigo,
                curso_nome,
                'PRESENCIAL',
                campus_nome,
                'INTEGRAL',
                8,
                0,
                0,
                1,
                last_update
            ))
            
            curso_id = cur.fetchone()[0]
            
            # Processa as disciplinas e turmas
            disciplinas = driver.find_elements(By.CLASS_NAME, "disc")
            carga_horaria_total = 0
            
            disciplinas.sort(key=lambda x: x.text.split(']')[0].strip('['))
            
            disciplinas_processadas = []
            disciplinas_com_erro = []
            
            for disciplina in disciplinas:
                try:
                    cur.execute("SAVEPOINT disciplina")
                    
                    disciplina_text = disciplina.text
                    disciplina_info = parse_disciplina(disciplina_text)
                    
                    if disciplina_info:
                        codigo_disciplina = disciplina_info['codigo']
                        logger.info(f"Processando disciplina: {codigo_disciplina} - {disciplina_info['nome']}")
                        
                        if codigo_disciplina in disciplinas_processadas:
                            logger.warning(f"Disciplina {codigo_disciplina} já foi processada anteriormente")
                            cur.execute("ROLLBACK TO SAVEPOINT disciplina")
                            continue
                        
                        disciplinas_processadas.append(codigo_disciplina)
                        
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
                        
                        carga_horaria_total += disciplina_info['carga_horaria']
                        
                        cur.execute("""
                            INSERT INTO curso_disciplinas (curso_id, disciplina_id, periodo)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (curso_id, disciplina_id, periodo) DO NOTHING
                        """, (curso_id, disciplina_id, 0))
                        
                        # Get the full HTML of the 'resultado' div
                        resultado_div = driver.find_element(By.ID, "resultado")
                        resultado_html = resultado_div.get_attribute('outerHTML')
                        parsed_disciplinas = parse_turmas_html(resultado_html)
                        # Find the parsed disciplina matching this code
                        parsed_disc = next((d for d in parsed_disciplinas if d["codigo"] == codigo_disciplina), None)
                        if parsed_disc:
                            for turma_info in parsed_disc["turmas"]:
                                logger.info(f"  Turma: {turma_info['codigo']} - Prof: {turma_info['professor']}")
                                cur.execute("""
                                    INSERT INTO turmas (disciplina_id, codigo, professor)
                                    VALUES (%s, %s, %s)
                                    ON CONFLICT (disciplina_id, codigo) DO UPDATE
                                    SET professor = EXCLUDED.professor
                                    RETURNING id
                                """, (
                                    disciplina_id,
                                    turma_info['codigo'],
                                    turma_info['professor']
                                ))
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
                        
                        cur.execute("RELEASE SAVEPOINT disciplina")
                        
                    else:
                        logger.warning(f"Não foi possível extrair informações da disciplina: {disciplina_text}")
                        disciplinas_com_erro.append(disciplina_text)
                        cur.execute("ROLLBACK TO SAVEPOINT disciplina")
                
                except Exception as e:
                    logger.error(f"Erro ao processar disciplina: {str(e)}")
                    disciplinas_com_erro.append(disciplina.text)
                    cur.execute("ROLLBACK TO SAVEPOINT disciplina")
            
            cur.execute("""
                UPDATE cursos 
                SET carga_horaria_total = %s,
                    carga_horaria = %s
                WHERE id = %s
            """, (carga_horaria_total, carga_horaria_total, curso_id))
            
            cur.execute("COMMIT")
            
            logger.info(f"Curso {curso_codigo} processado com sucesso")
            if disciplinas_com_erro:
                logger.warning(f"Disciplinas com erro: {len(disciplinas_com_erro)}")
                for disc in disciplinas_com_erro:
                    logger.warning(f"  - {disc}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar curso {curso_codigo}: {str(e)}")
            cur.execute("ROLLBACK")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao processar curso {curso_codigo}: {str(e)}")
        return False

def process_campus(driver, campus_id, campus_nome, cur):
    """Processa todos os cursos de um campus específico"""
    try:
        logger.info(f"Processando campus: {campus_nome}")
        
        # Clica no botão do campus
        script = f"""
            var h3 = document.querySelector('h3[onclick="treeView(\\'{campus_id}\\');"]');
            if (h3) {{
                h3.click();
                return true;
            }}
            return false;
        """
        clicked = driver.execute_script(script)
        
        if not clicked:
            logger.error(f"Não foi possível encontrar o botão para o campus {campus_nome}")
            return False
        
        time.sleep(5)  # Aguarda o carregamento do campus
        
        # Extrai todos os cursos do campus
        cursos = driver.find_elements(By.CSS_SELECTOR, f"#{campus_id} a")
        cursos_processados = 0
        
        # Armazena os links dos cursos antes de processá-los
        curso_links = []
        for curso_element in cursos:
            try:
                href = curso_element.get_attribute('href')
                if 'CODIGO_CURSO=' in href:
                    curso_codigo = href.split('CODIGO_CURSO=')[1]
                    curso_nome = curso_element.text.strip()
                    curso_links.append((curso_codigo, curso_nome))
            except Exception as e:
                logger.error(f"Erro ao extrair informações do curso: {str(e)}")
                continue
        
        # Processa cada curso usando os links armazenados
        for curso_codigo, curso_nome in curso_links:
            try:
                # Processa o curso
                success = process_curso(driver, curso_codigo, curso_nome, cur, campus_nome)
                if success:
                    cursos_processados += 1
                    logger.info(f"Curso {curso_codigo} processado com sucesso")
                else:
                    logger.warning(f"Falha ao processar curso {curso_codigo}")
                
                # Volta para a página inicial
                driver.get(SCRAPING_CONFIG['url'])
                time.sleep(5)
                
                # Clica no campus novamente
                driver.execute_script(script)
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Erro ao processar curso do campus {campus_nome}: {str(e)}")
                continue
        
        logger.info(f"Campus {campus_nome} processado. {cursos_processados} cursos processados com sucesso.")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao processar campus {campus_nome}: {str(e)}")
        return False

def check_global_update(driver):
    """Verifica a última atualização global do sistema comparando com a data salva em arquivo"""
    try:
        last_update_element = driver.find_element(By.ID, "last_update")
        if last_update_element:
            last_update_text = last_update_element.text
            # Convert the string from the webpage to a datetime object
            # The format seems to be "Mon Mar 17 12:26:42 UTC 2025"
            # The format code for UTC is %Z, but strptime might not handle it directly.
            # Let's try parsing without %Z and assume UTC based on the string.
            try:
                last_update_web = datetime.strptime(last_update_text, "%a %b %d %H:%M:%S UTC %Y")
            except ValueError:
                 # Fallback if UTC is not handled, try without it
                last_update_web = datetime.strptime(last_update_text.replace(' UTC', ''), "%a %b %d %H:%M:%S %Y")

            # Lê a data da última atualização salva em arquivo
            last_update_saved = read_last_global_update()
            
            logger.info(f"Última atualização detectada na web: {last_update_web}")
            if last_update_saved:
                logger.info(f"Última atualização salva em arquivo: {last_update_saved}")
            else:
                logger.info("Nenhuma data de atualização global salva em arquivo.")

            # Compara a data da web com a data salva
            if last_update_saved and last_update_web <= last_update_saved:
                logger.info("Banco de dados já está atualizado globalmente.")
                return False  # Não precisa atualizar se a data da web for menor ou igual à salva
            
            logger.info("Nova atualização global detectada ou nenhuma data salva. Iniciando raspagem completa.")
            return True  # Precisa atualizar se a data da web for mais nova ou se não houver data salva
            
    except Exception as e:
        logger.error(f"Erro ao verificar atualização global: {str(e)}")
        return True  # Em caso de erro, assume que precisa atualizar

def main():
    driver = None
    conn = None
    cur = None
    
    try:
        logger.info("Iniciando o scraper...")
        driver = setup_driver()
        
        # Carrega a página inicial
        logger.info("Acessando a página inicial...")
        driver.get(SCRAPING_CONFIG['url'])
        time.sleep(5)  # Aguarda o carregamento inicial
        
        # Verifica a última atualização global
        needs_update = check_global_update(driver)

        if not needs_update:
            logger.info("Nenhuma atualização necessária.")
            return

        # Se precisa atualizar, conecta ao banco e processa
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Processa cada campus
        for campus_id, campus_nome in SCRAPING_CONFIG['campus'].items():
            try:
                success = process_campus(driver, campus_id, campus_nome, cur)
                if success:
                    logger.info(f"Campus {campus_nome} processado com sucesso")
                else:
                    logger.warning(f"Falha ao processar campus {campus_nome}")
                
                # Volta para a página inicial após processar o campus
                driver.get(SCRAPING_CONFIG['url'])
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Erro ao processar campus {campus_nome}: {str(e)}")
                continue
        
        # Após processar todos os campus (se chegou até aqui), salva a nova data de atualização global
        # É importante pegar a data da página novamente para garantir que seja a mesma que disparou a atualização
        last_update_element = driver.find_element(By.ID, "last_update")
        if last_update_element:
            last_update_text = last_update_element.text
            try:
                last_update_web = datetime.strptime(last_update_text, "%a %b %d %H:%M:%S UTC %Y")
            except ValueError:
                last_update_web = datetime.strptime(last_update_text.replace(' UTC', ''), "%a %b %d %H:%M:%S %Y")
            
            write_last_global_update(last_update_web)
            logger.info("Raspagem completa concluída e data de atualização global salva.")

        
    except Exception as e:
        logger.error(f"Erro durante a execução do scraper: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        if driver:
            driver.quit()

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