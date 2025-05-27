import os
import sys
import psycopg2

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_CONFIG

def run_migrations():
    """Executa o schema do banco de dados"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cur = conn.cursor()
        
        # Lê e executa o arquivo schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql = f.read()
            cur.execute(sql)
            conn.commit()
        
        cur.close()
        print('Schema do banco de dados aplicado com sucesso.')
    except Exception as e:
        print(f'Erro ao executar schema: {e}')
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    run_migrations() 