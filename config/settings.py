import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Banco de Dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'turing_bot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Configurações do Web Scraping
SCRAPING_CONFIG = {
    'url': os.getenv('UTFPR_URL', 'https://gradenahora.com.br/utfpr/grade_na_hora.html'),
    'curso_codigo': os.getenv('CURSO_CODIGO', '04219'),
    'headless': os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true',
    'timeout': int(os.getenv('SELENIUM_TIMEOUT', '30'))
}

# Configurações do Bot (futuro)
BOT_CONFIG = {
    'enabled': False,  # Será implementado posteriormente
    'token': os.getenv('BOT_TOKEN', '')
} 