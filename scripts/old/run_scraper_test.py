#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import logging
import re
from bs4 import BeautifulSoup

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações hardcoded para teste
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
    """Configura e retorna o driver do Chrome"""
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
        
        # Determina o caminho do ChromeDriver baseado no sistema operacional
        if os.name == 'nt':  # Windows
            driver_path = os.path.join(os.getcwd(), 'chromedriver', 'chromedriver.exe')
        else:  # Linux/Mac
            driver_path = os.getenv('CHROMEDRIVER_PATH', '/app/chromedriver/chromedriver')
        
        if not os.path.exists(driver_path):
            logger.error(f"ChromeDriver não encontrado em: {driver_path}")
            raise FileNotFoundError(f"ChromeDriver não encontrado em: {driver_path}")
        
        driver = uc.Chrome(
            options=options,
            driver_executable_path=driver_path,
            version_main=136  # Versão específica do Chrome
        )
        return driver
    except Exception as e:
        logger.error(f"Erro ao configurar o ChromeDriver: {str(e)}")
        raise

def test_navigation():
    """Testa a navegação básica"""
    driver = None
    try:
        logger.info("🚀 Iniciando teste de navegação...")
        
        driver = setup_driver()
        logger.info("✅ ChromeDriver configurado com sucesso!")
        
        # Carrega a página inicial
        logger.info("🌐 Acessando a página do Grade na Hora...")
        driver.get(SCRAPING_CONFIG['url'])
        time.sleep(5)
        
        # Verifica se a página carregou
        title = driver.title
        logger.info(f"✅ Página carregada! Título: {title}")
        
        # Tenta encontrar elementos da página
        try:
            # Procura por elementos típicos da página
            campus_elements = driver.find_elements(By.TAG_NAME, "h3")
            logger.info(f"✅ Encontrados {len(campus_elements)} elementos de campus")
            
            # Procura por links de cursos
            curso_links = driver.find_elements(By.TAG_NAME, "a")
            logger.info(f"✅ Encontrados {len(curso_links)} links de cursos")
            
            # Procura pelo campus de Medianeira
            medianeira_found = False
            for element in campus_elements:
                if "medianeira" in element.text.lower():
                    medianeira_found = True
                    logger.info(f"✅ Campus Medianeira encontrado: {element.text}")
                    break
            
            if not medianeira_found:
                logger.warning("⚠️ Campus Medianeira não encontrado na página")
            
            logger.info("🎉 Teste de navegação concluído com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a navegação: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {str(e)}")
        return False
    finally:
        if driver:
            driver.quit()
            logger.info("🔒 ChromeDriver fechado")

def main():
    """Função principal do teste"""
    try:
        logger.info("🚀 Iniciando teste do scraper UTFGradeBot...")
        
        # Testa a navegação
        success = test_navigation()
        
        if success:
            logger.info("🎉 Teste concluído com sucesso! O ChromeDriver está funcionando perfeitamente.")
        else:
            logger.error("💥 Teste falhou. Verifique os logs acima.")
            
    except Exception as e:
        logger.error(f"❌ Erro durante a execução: {str(e)}")

if __name__ == "__main__":
    main() 