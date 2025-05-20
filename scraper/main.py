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

def parse_turma(turma_text):
    """Extrai informações da turma do texto"""
    try:
        # Exemplo: ALI2 — Franciele Buss Frescki Kestring [ 4M3(I11) - 4M4(I11) - 4M5(I11) ]
        match = re.match(r'([A-Z0-9]+)\s*—\s*([^[]+)\s*\[(.*?)\]', turma_text)
        if match:
            codigo, professor, horarios = match.groups()
            horarios_list = parse_horarios(horarios)
            return {
                "codigo": str(codigo.strip()),
                "professor": str(professor.strip()),
                "horarios": horarios_list
            }
        else:
            logger.warning(f"Formato inválido de turma: {turma_text}")
            return None
    except Exception as e:
        logger.error(f"Erro ao processar turma: {str(e)}")
        return None

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

        # Adicionar um pequeno delay após o clique antes de verificar alertas
        time.sleep(1) # Pequeno delay para o alerta aparecer

        # Verifica se há popup de erro (MOVIDO PARA CÁ)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            logger.warning(f"Alerta encontrado: {alert_text}")

            # Verifica se é um alerta de curso não disponível e lida com ele
            if "não está disponível no GNH" in alert_text:
                logger.warning(f"Curso {curso_codigo} não está disponível no momento (via alerta)")
                alert.accept()
                return False # Sai da função se o curso não está disponível

            # Se não for um alerta de curso não disponível, aceita e continua (ou decide outra ação)
            alert.accept()
            logger.info("Alerta aceito.")

        except NoAlertPresentException: # Importar NoAlertPresentException do selenium.common.exceptions
            pass  # Se não houver alerta, continua normalmente
        except Exception as e:
            logger.error(f"Erro ao lidar com alerta: {str(e)}")
            # Decide se continua ou para após um erro inesperado com o alerta
            # Neste caso, vamos logar e continuar, mas pode ser ajustado

        if not clicked:
            logger.error(f"Não foi possível encontrar o botão para o curso {curso_codigo}")
            return False

        time.sleep(5)  # Mantém o aguardo para o carregamento da página após o clique e tratamento do alerta
        
        # Verifica se há mensagem de erro "este curso não está disponível no GNH"
        try:
            error_message = driver.find_element(By.XPATH, "//*[contains(text(), 'este curso não está disponível no GNH')]")
            if error_message:
                logger.warning(f"Curso {curso_codigo} não está disponível no GNH")
                return False
        except:
            pass  # Se não encontrar a mensagem de erro, continua normalmente
        
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
            
            # Verifica se o curso já existe e compara as datas
            cur.execute("SELECT last_update FROM cursos WHERE codigo = %s", (curso_codigo,))
            result = cur.fetchone()
            
            if result and result[0]:
                stored_last_update = result[0]
                if stored_last_update >= last_update:
                    logger.info(f"Curso {curso_codigo} já está atualizado. Última atualização: {stored_last_update}")
                    return True
        except Exception as e:
            logger.error(f"Erro ao verificar data de atualização: {str(e)}")
            # Se houver erro ao verificar a data, continua com o processamento
        
        # Inicia uma transação para o curso
        cur.execute("BEGIN")
        
        try:
            # Insere ou atualiza o curso
            logger.info(f"Tentando inserir curso: codigo={curso_codigo}, nome={curso_nome}, campus={campus_nome}")
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
                campus_nome,  # Corrigido para garantir que é string
                'INTEGRAL',  # valor padrão
                8,  # valor padrão
                0,  # será atualizado depois
                0,  # será atualizado depois
                1,  # valor padrão
                last_update
            ))
            
            curso_id = cur.fetchone()[0]
            
            # Processa as disciplinas e turmas
            disciplinas = driver.find_elements(By.CLASS_NAME, "disc")
            carga_horaria_total = 0
            
            # Ordena as disciplinas pelo código
            disciplinas.sort(key=lambda x: x.text.split(']')[0].strip('['))
            
            # Lista para armazenar os códigos das disciplinas processadas
            disciplinas_processadas = []
            disciplinas_com_erro = []
            
            for disciplina in disciplinas:
                try:
                    # Inicia uma transação para cada disciplina
                    cur.execute("SAVEPOINT disciplina")
                    
                    # Extrai informações da disciplina
                    disciplina_text = disciplina.text
                    disciplina_info = parse_disciplina(disciplina_text)
                    
                    if disciplina_info:
                        codigo_disciplina = disciplina_info['codigo']
                        logger.info(f"Processando disciplina: {codigo_disciplina} - {disciplina_info['nome']}")
                        
                        # Verifica se a disciplina já foi processada
                        if codigo_disciplina in disciplinas_processadas:
                            logger.warning(f"Disciplina {codigo_disciplina} já foi processada anteriormente")
                            cur.execute("ROLLBACK TO SAVEPOINT disciplina")
                            continue
                        
                        disciplinas_processadas.append(codigo_disciplina)
                        
                        # Insere ou atualiza a disciplina
                        logger.info(f"Tentando inserir disciplina: {disciplina_info}")
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
                        
                        # Atualiza a carga horária total
                        carga_horaria_total += disciplina_info['carga_horaria']
                        
                        # Relaciona a disciplina com o curso
                        logger.info(f"Relacionando disciplina {disciplina_id} com curso {curso_id}")
                        cur.execute("""
                            INSERT INTO curso_disciplinas (curso_id, disciplina_id, periodo)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (curso_id, disciplina_id, periodo) DO NOTHING
                        """, (curso_id, disciplina_id, 0))
                        
                        # Processa as turmas da disciplina
                        # Encontra todas as turmas que seguem esta disciplina
                        turmas = driver.find_elements(By.XPATH, f"//span[@class='disc'][contains(text(), '{codigo_disciplina}')]/following-sibling::span[@class='tur']")
                        
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
                                """, (
                                    disciplina_id,
                                    turma_info['codigo'],
                                    turma_info['professor']
                                ))
                                turma_id = cur.fetchone()[0]
                                
                                # Insere os horários da turma
                                for horario in turma_info['horarios']:
                                    if not isinstance(horario, dict):
                                        logger.error(f"Horário não é dict! Tipo: {type(horario)}, Valor: {horario}")
                                        continue
                                    logger.info(f"Inserindo horário: {horario}")
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
                        
                        # Commit da transação da disciplina
                        cur.execute("RELEASE SAVEPOINT disciplina")
                        
                    else:
                        logger.warning(f"Não foi possível extrair informações da disciplina: {disciplina_text}")
                        disciplinas_com_erro.append(disciplina_text)
                        cur.execute("ROLLBACK TO SAVEPOINT disciplina")
                
                except Exception as e:
                    logger.error(f"Erro ao processar disciplina: {str(e)}")
                    disciplinas_com_erro.append(disciplina.text)
                    cur.execute("ROLLBACK TO SAVEPOINT disciplina")
            
            # Atualiza a carga horária total do curso
            cur.execute("""
                UPDATE cursos 
                SET carga_horaria_total = %s,
                    carga_horaria = %s
                WHERE id = %s
            """, (carga_horaria_total, carga_horaria_total, curso_id))
            
            # Commit da transação do curso
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
    """Verifica a última atualização global do sistema"""
    try:
        last_update_element = driver.find_element(By.ID, "last_update")
        if last_update_element:
            last_update_text = last_update_element.text
            last_update = datetime.strptime(last_update_text, "%a %b %d %H:%M:%S UTC %Y")
            
            # Verifica se já temos essa atualização no banco
            cur = get_db_connection().cursor()
            cur.execute("SELECT last_update FROM global_updates ORDER BY last_update DESC LIMIT 1")
            result = cur.fetchone()
            
            if result and result[0] >= last_update:
                logger.info(f"Sistema já está atualizado. Última atualização: {result[0]}")
                return False
            
            # Registra a nova atualização
            cur.execute("""
                INSERT INTO global_updates (last_update)
                VALUES (%s)
            """, (last_update,))
            cur.connection.commit()
            logger.info(f"Nova atualização detectada: {last_update}")
            return True
            
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
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Carrega a página inicial
        logger.info("Acessando a página inicial...")
        driver.get(SCRAPING_CONFIG['url'])
        time.sleep(5)  # Aguarda o carregamento inicial
        
        # Verifica a última atualização global
        # if not check_global_update(driver):
        #     logger.info("Nenhuma atualização necessária.")
        #     return
        
        # Processa cada campus
        for campus_id, campus_nome in SCRAPING_CONFIG['campus'].items():
            try:
                success = process_campus(driver, campus_id, campus_nome, cur)
                if success:
                    logger.info(f"Campus {campus_nome} processado com sucesso")
                else:
                    logger.warning(f"Falha ao processar campus {campus_nome}")
                
                # Volta para a página inicial
                driver.get(SCRAPING_CONFIG['url'])
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Erro ao processar campus {campus_nome}: {str(e)}")
                continue
        
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