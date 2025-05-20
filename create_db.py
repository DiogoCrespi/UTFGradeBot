import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def create_database():
    try:
        # Conectar ao banco de dados postgres para criar o novo banco
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Criar o banco de dados se não existir
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'utfgradebot'")
        exists = cur.fetchone()
        if not exists:
            cur.execute('CREATE DATABASE utfgradebot')
            print("Banco de dados 'utfgradebot' criado com sucesso!")
        else:
            print("Banco de dados 'utfgradebot' já existe.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao criar banco de dados: {str(e)}")

if __name__ == "__main__":
    create_database() 