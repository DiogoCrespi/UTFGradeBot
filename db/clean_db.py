import os
import sys
import psycopg2
from dotenv import load_dotenv

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_CONFIG

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'migrations')

def clean_database():
    """Limpa o banco de dados e recria as tabelas"""
    conn = None
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Comenta o comando de limpar o banco
        # cur.execute("DROP SCHEMA public CASCADE;")
        # cur.execute("CREATE SCHEMA public;")
        # cur.execute("GRANT ALL ON SCHEMA public TO postgres;")
        # cur.execute("GRANT ALL ON SCHEMA public TO public;")
        
        # Executa o schema
        with open('db/schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
            cur.execute(schema)
        
        print("Banco de dados limpo e recriado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao limpar banco de dados: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    clean_database() 