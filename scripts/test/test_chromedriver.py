#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import undetected_chromedriver as uc
import time

def test_chromedriver():
    """Testa se o ChromeDriver está funcionando"""
    try:
        print("🚀 Iniciando teste do ChromeDriver...")
        
        # Configura as opções do Chrome
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')  # Modo headless
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Caminho do ChromeDriver no Windows
        driver_path = os.path.join(os.getcwd(), 'chromedriver', 'chromedriver.exe')
        
        print(f"📁 Verificando ChromeDriver em: {driver_path}")
        
        if not os.path.exists(driver_path):
            print(f"❌ ChromeDriver não encontrado em: {driver_path}")
            return False
        
        print("✅ ChromeDriver encontrado!")
        
        # Inicializa o driver
        print("🔧 Inicializando ChromeDriver...")
        driver = uc.Chrome(
            options=options,
            driver_executable_path=driver_path,
            version_main=136
        )
        
        print("✅ ChromeDriver inicializado com sucesso!")
        
        # Testa navegação
        print("🌐 Testando navegação...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        title = driver.title
        print(f"✅ Navegação bem-sucedida! Título da página: {title}")
        
        # Fecha o driver
        driver.quit()
        print("✅ Teste concluído com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_chromedriver()
    if success:
        print("\n🎉 ChromeDriver está funcionando perfeitamente!")
    else:
        print("\n💥 ChromeDriver não está funcionando corretamente.") 