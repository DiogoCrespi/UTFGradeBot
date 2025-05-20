import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def init_database():
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database='utfgradebot',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Ler o arquivo schema.sql
        with open('db/schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Executar o schema
        cur.execute(schema)
        print("Schema do banco de dados criado com sucesso!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {str(e)}")

if __name__ == "__main__":
    init_database() 