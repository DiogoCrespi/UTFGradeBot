import os
import sys
import psycopg2

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_CONFIG

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'migrations')

# Lista todas as migrações .sql em ordem
migrations = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')])

def run_migrations():
    """Executa todas as migrações do banco de dados"""
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
        for migration in migrations:
            path = os.path.join(MIGRATIONS_DIR, migration)
            print(f'Executando migração: {migration}')
            with open(path, 'r', encoding='utf-8') as f:
                sql = f.read()
                cur.execute(sql)
                conn.commit()
        cur.close()
        print('Todas as migrações foram aplicadas com sucesso.')
    except Exception as e:
        print(f'Erro ao executar migrações: {e}')
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migrations() 