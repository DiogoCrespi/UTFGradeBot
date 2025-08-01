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
from webdriver_manager.chrome import ChromeDriverManager

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_driver():
    """Configura e retorna o driver do Chrome usando webdriver-manager"""
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
        
        # Usa webdriver-manager para baixar automaticamente o ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        # Cria o driver
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.info("✅ ChromeDriver configurado com sucesso!")
        return driver
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar o ChromeDriver: {str(e)}")
        raise

def test_navigation():
    """Testa a navegação básica"""
    driver = None
    try:
        logger.info("🚀 Iniciando teste de navegação...")
        
        driver = setup_driver()
        
        # Carrega a página inicial
        logger.info("🌐 Acessando a página do Grade na Hora...")
        driver.get("https://gradenahora.com.br/utfpr/grade_na_hora.html")
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