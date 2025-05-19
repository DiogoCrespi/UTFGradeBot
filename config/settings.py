import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Banco de Dados
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'turing_bot',
    'user': 'postgres',
    'password': '1597'
}

# Configurações do Web Scraping
SCRAPING_CONFIG = {
    'url': 'https://gradenahora.com.br/utfpr/grade_na_hora.html',
    'campus': 'Medianeira',
    'cursos': {
        '04219': 'Ciência da Computação',
        '04105': 'Tecnologia em Informática',
        '04158': 'Tecnologia em Desenvolvimento de Sistemas',
        '04176': 'Tecnologia em Análise e Desenvolvimento de Sistemas'
    }
}

# Configurações do Selenium
SELENIUM_CONFIG = {
    'headless': False,  # Desabilitado para debug
    'timeout': 30,
    'wait_time': 5
}

# Configurações do Bot (futuro)
BOT_CONFIG = {
    'enabled': False,  # Será implementado posteriormente
    'token': os.getenv('BOT_TOKEN', '')
} 