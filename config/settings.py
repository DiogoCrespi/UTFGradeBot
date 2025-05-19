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
        '04103': 'Tecnologia Ambiental',
        '04104': 'Tecnologia Eletromecânica',
        '04105': 'Tecnologia em Informática',
        '04154': 'Tecnologia em Gestão Ambiental',
        '04155': 'Tecnologia em Manutenção Eletromecânica',
        '04156': 'Tecnologia em Laticínios',
        '04157': 'Tecnologia em Indústria de Carnes',
        '04158': 'Tecnologia em Desenvolvimento de Sistemas',
        '04168': 'Tecnologia em Gestão Ambiental',
        '04169': 'Tecnologia em Alimentos',
        '04170': 'Engenharia de Produção Agroindustrial',
        '04175': 'Tecnologia em Manutenção Industrial',
        '04176': 'Tecnologia em Análise e Desenvolvimento de Sistemas',
        '04200': 'Engenharia de Produção',
        '04201': 'Engenharia de Alimentos',
        '04202': 'Engenharia Ambiental',
        '04219': 'Ciência da Computação',
        '04220': 'Engenharia Elétrica',
        '04262': 'Licenciatura em Química',
        '04280': 'Engenharia Ambiental e Sanitária',
        '04282': 'Química Industrial',
        '04286': 'Gestão do Agronegócio'
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