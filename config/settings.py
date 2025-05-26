import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Banco de Dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),  # Usa 'db' como padrão para ambiente Docker
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'utfgradebot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '1597')
}

# Configurações do Web Scraping
SCRAPING_CONFIG = {
    'url': os.getenv('SCRAPING_URL', 'https://gradenahora.com.br/utfpr/grade_na_hora.html'),
    'campus': {
        'apucarana': 'Apucarana',
        'campo_mourao': 'Campo Mourão',
        'cornelio_procopio': 'Cornélio Procópio',
        'curitiba': 'Curitiba',
        'dois_vizinhos': 'Dois Vizinhos',
        'francisco_beltrao': 'Francisco Beltrão',
        'guarapuava': 'Guarapuava',
        'londrina': 'Londrina',
        'medianeira': 'Medianeira',
        'pato_branco': 'Pato Branco',
        'ponta_grossa': 'Ponta Grossa',
        'santa_helena': 'Santa Helena',
        'toledo': 'Toledo'
    },
    'cursos': {
        # Os cursos serão carregados dinamicamente para cada campus
    }
}

# Configurações do Selenium
SELENIUM_CONFIG = {
    'headless': os.getenv('SELENIUM_HEADLESS', 'True').lower() == 'true',
    'timeout': int(os.getenv('SELENIUM_TIMEOUT', '30')),
    'wait_time': int(os.getenv('SELENIUM_WAIT_TIME', '5'))
}

# Configurações do Bot (futuro)
BOT_CONFIG = {
    'enabled': False,  # Será implementado posteriormente
    'token': os.getenv('BOT_TOKEN', '')
} 