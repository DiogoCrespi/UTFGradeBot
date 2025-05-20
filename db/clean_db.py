import os
import sys
import psycopg2

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_CONFIG

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'migrations')

def clean_db():
    """Remove e recria as tabelas do banco de dados"""
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
        
        # Remove as tabelas existentes
        cur.execute("""
            DROP TABLE IF EXISTS horarios CASCADE;
            DROP TABLE IF EXISTS turmas CASCADE;
            DROP TABLE IF EXISTS curso_disciplinas CASCADE;
            DROP TABLE IF EXISTS disciplinas CASCADE;
            DROP TABLE IF EXISTS cursos CASCADE;
        """)
        conn.commit()
        print('Tabelas removidas com sucesso.')
        
        # Recria as tabelas usando o schema.sql
        print('Criando tabelas usando schema.sql...')
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cur.execute(schema_sql)
            conn.commit()
        print('Tabelas criadas com sucesso usando schema.sql.')
        
        # # Aplica as migrações incrementais - Removido para evitar conflito
        # print('Aplicando migrações incrementais...')
        # migrations = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')])
        # for migration in migrations:
        #     path = os.path.join(MIGRATIONS_DIR, migration)
        #     print(f'Executando migração: {migration}')
        #     with open(path, 'r', encoding='utf-8') as f:
        #         sql = f.read()
        #         cur.execute(sql)
        #         conn.commit()
        # print('Migrações incrementais aplicadas com sucesso.')
        
    except Exception as e:
        print(f'Erro ao limpar/recriar banco: {e}')
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    clean_db() 