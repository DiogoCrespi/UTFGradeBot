#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import re
from bs4 import BeautifulSoup

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações hardcoded
SCRAPING_CONFIG = {
    'url': 'https://gradenahora.com.br/utfpr/grade_na_hora.html',
    'campus': {
        'medianeira': 'Medianeira'
    }
}

SELENIUM_CONFIG = {
    'headless': True,
    'timeout': 30,
    'wait_time': 5
}

def setup_driver():
    """Configura e retorna o driver do Chrome usando Selenium padrão"""
    try:
        logger.info("🔧 Configurando ChromeDriver...")
        
        # Configura as opções do Chrome
        options = Options()
        options.add_argument('--headless=new')  # Modo headless
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Usa o ChromeDriver local
        driver_path = os.path.join(os.getcwd(), 'chromedriver', 'chromedriver.exe')
        
        if not os.path.exists(driver_path):
            logger.error(f"ChromeDriver não encontrado em: {driver_path}")
            raise FileNotFoundError(f"ChromeDriver não encontrado em: {driver_path}")
        
        logger.info(f"✅ ChromeDriver encontrado em: {driver_path}")
        
        # Cria o service com o ChromeDriver local
        service = Service(executable_path=driver_path)
        
        # Cria o driver
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.info("✅ ChromeDriver configurado com sucesso!")
        return driver
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar o ChromeDriver: {str(e)}")
        raise

def parse_disciplina(disciplina_text):
    """Extrai informações da disciplina do texto"""
    try:
        # Remove o código da disciplina do início do texto
        match = re.match(r'\[([A-Z0-9]+)\]\s+(.*?)\s+\((\d+)\s+aulas/sem\)', disciplina_text)
        if match:
            codigo, nome, aulas = match.groups()
            return {
                "codigo": str(codigo),
                "nome": str(nome),
                "carga_horaria": int(aulas) * 15,  # 15 horas por aula
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

def process_curso(driver, curso_codigo, curso_nome, campus_nome):
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
            logger.info(f"Data de última atualização: {last_update}")
        except Exception as e:
            logger.error(f"Erro ao verificar data de atualização: {str(e)}")
        
        # Processa as disciplinas
        disciplinas = driver.find_elements(By.CLASS_NAME, "disc")
        carga_horaria_total = 0
        
        disciplinas.sort(key=lambda x: x.text.split(']')[0].strip('['))
        
        disciplinas_processadas = []
        disciplinas_com_erro = []
        
        logger.info(f"Encontradas {len(disciplinas)} disciplinas")
        
        for disciplina in disciplinas:
            try:
                disciplina_text = disciplina.text
                disciplina_info = parse_disciplina(disciplina_text)
                
                if disciplina_info:
                    codigo_disciplina = disciplina_info['codigo']
                    logger.info(f"Processando disciplina: {codigo_disciplina} - {disciplina_info['nome']}")
                    
                    if codigo_disciplina in disciplinas_processadas:
                        logger.warning(f"Disciplina {codigo_disciplina} já foi processada anteriormente")
                        continue
                    
                    disciplinas_processadas.append(codigo_disciplina)
                    carga_horaria_total += disciplina_info['carga_horaria']
                    
                    # Get the full HTML of the 'resultado' div
                    resultado_div = driver.find_element(By.ID, "resultado")
                    resultado_html = resultado_div.get_attribute('outerHTML')
                    parsed_disciplinas = parse_turmas_html(resultado_html)
                    # Find the parsed disciplina matching this code
                    parsed_disc = next((d for d in parsed_disciplinas if d["codigo"] == codigo_disciplina), None)
                    if parsed_disc:
                        logger.info(f"  Encontradas {len(parsed_disc['turmas'])} turmas")
                        for turma_info in parsed_disc["turmas"]:
                            logger.info(f"    Turma: {turma_info['codigo']} - Prof: {turma_info['professor']}")
                            logger.info(f"      Horários: {len(turma_info['horarios'])} horários")
                    
                else:
                    logger.warning(f"Não foi possível extrair informações da disciplina: {disciplina_text}")
                    disciplinas_com_erro.append(disciplina_text)
            
            except Exception as e:
                logger.error(f"Erro ao processar disciplina: {str(e)}")
                disciplinas_com_erro.append(disciplina.text)
        
        logger.info(f"Curso {curso_codigo} processado com sucesso")
        logger.info(f"Carga horária total: {carga_horaria_total} horas")
        logger.info(f"Disciplinas processadas: {len(disciplinas_processadas)}")
        if disciplinas_com_erro:
            logger.warning(f"Disciplinas com erro: {len(disciplinas_com_erro)}")
            for disc in disciplinas_com_erro:
                logger.warning(f"  - {disc}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao processar curso {curso_codigo}: {str(e)}")
        return False

def main():
    """Função principal do programa"""
    driver = None
    
    try:
        logger.info("🚀 Iniciando o scraper para Ciência da Computação em Medianeira...")
        
        # Configura a codificação para UTF-8
        if os.name == 'nt':  # Windows
            import sys
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stdin.reconfigure(encoding='utf-8')
        
        driver = setup_driver()
        
        # Carrega a página inicial
        logger.info("🌐 Acessando a página inicial...")
        driver.get(SCRAPING_CONFIG['url'])
        time.sleep(5)
        
        # Processa apenas o curso de Ciência da Computação em Medianeira
        campus_id = None
        campus_nome = "Medianeira"
        
        # Encontra o ID do campus de Medianeira
        for cid, cname in SCRAPING_CONFIG['campus'].items():
            if cname == campus_nome:
                campus_id = cid
                break
        
        if not campus_id:
            logger.error("Campus Medianeira não encontrado na configuração")
            return
        
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
            return
        
        time.sleep(5)
        
        # Procura o curso de Ciência da Computação
        curso_links = driver.find_elements(By.CSS_SELECTOR, f"#{campus_id} a")
        curso_encontrado = False
        
        for curso_element in curso_links:
            try:
                href = curso_element.get_attribute('href')
                if 'CODIGO_CURSO=' in href:
                    curso_codigo = href.split('CODIGO_CURSO=')[1]
                    curso_nome = curso_element.text.strip()
                    
                    # Verifica se é o curso de Ciência da Computação
                    if "CIÊNCIA COMPUTAÇÃO" in curso_nome.upper():
                        curso_encontrado = True
                        success = process_curso(driver, curso_codigo, curso_nome, campus_nome)
                        if success:
                            logger.info(f"✅ Curso {curso_codigo} processado com sucesso")
                        else:
                            logger.warning(f"⚠️ Falha ao processar curso {curso_codigo}")
                        break
            except Exception as e:
                logger.error(f"Erro ao processar link do curso: {str(e)}")
                continue
        
        if not curso_encontrado:
            logger.error("❌ Curso de Ciência da Computação não encontrado em Medianeira")
        
    except Exception as e:
        logger.error(f"❌ Erro durante a execução do scraper: {str(e)}")
    finally:
        if driver:
            driver.quit()
            logger.info("🔒 ChromeDriver fechado")

if __name__ == "__main__":
    main() 