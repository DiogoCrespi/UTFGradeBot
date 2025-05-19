from db.init_db import init_database
from scraper.main import main as run_scraper

if __name__ == "__main__":
    print("Inicializando banco de dados...")
    init_database()
    
    print("\nIniciando scraper...")
    run_scraper() 