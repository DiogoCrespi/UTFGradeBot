from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.settings import SCRAPING_CONFIG

class Navegador:
    def __init__(self):
        self.options = Options()
        if SCRAPING_CONFIG['headless']:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.wait = WebDriverWait(self.driver, SCRAPING_CONFIG['timeout'])
    
    def acessar_url(self, url):
        """Acessa uma URL e aguarda o carregamento da página"""
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located(('tag name', 'body')))
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fechar() 