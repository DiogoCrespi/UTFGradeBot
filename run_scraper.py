from db.clean_db import clean_database
# from db.init_db import init_database # Não precisamos mais chamar init_database separadamente
from scraper.main import main as run_scraper

if __name__ == "__main__":
    print("Limpando e inicializando banco de dados...")
    clean_database() # Chama clean_db para dropar e recriar tabelas com migrações
    
    print("\nIniciando scraper...")
    run_scraper() 