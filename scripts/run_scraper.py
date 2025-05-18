import os
import sys
from pathlib import Path
from scraper.main import Scraper

def executar_scraper():
    """Executa o scraper para extrair os dados"""
    try:
        # Adiciona o diretório raiz ao PYTHONPATH
        root_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(root_dir))
        
        print("Iniciando extração dos dados...")
        scraper = Scraper()
        scraper.extrair_dados()
        print("Extração concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro ao executar scraper: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    executar_scraper() 