import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import psycopg2
from config.settings import DB_CONFIG

if len(sys.argv) < 2:
    print("Uso: python db/run_single_migration.py <nome_arquivo_migracao.sql> [--inspect] <sql>")
    sys.exit(1)

if sys.argv[1] == '--inspect':
    sql = sys.argv[2]
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cur = conn.cursor()
        cur.execute(sql)
        for row in cur.fetchall():
            print(row)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao executar inspeção: {e}")
        sys.exit(1)
    sys.exit(0)

migration_file = sys.argv[1]

migration_path = os.path.join(os.path.dirname(__file__), 'migrations', migration_file)

if not os.path.exists(migration_path):
    print(f"Arquivo de migração não encontrado: {migration_path}")
    sys.exit(1)

try:
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cur = conn.cursor()
    with open(migration_path, 'r', encoding='utf-8') as f:
        sql = f.read()
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()
    print(f"Migração {migration_file} aplicada com sucesso.")
except Exception as e:
    print(f"Erro ao aplicar migração: {e}")
    sys.exit(1) 