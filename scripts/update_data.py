import schedule
import time
import logging
from datetime import datetime
from scraper.main import Scraper

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def atualizar_dados():
    """Atualiza os dados da grade curricular"""
    try:
        logger.info("Iniciando atualização dos dados...")
        scraper = Scraper()
        scraper.extrair_dados()
        logger.info("Atualização concluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao atualizar dados: {str(e)}")

def main():
    """Função principal que agenda a atualização diária"""
    # Agenda a atualização para rodar todos os dias às 3h da manhã
    schedule.every().day.at("03:00").do(atualizar_dados)
    
    logger.info("Serviço de atualização iniciado")
    logger.info("Próxima atualização agendada para 03:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main() 