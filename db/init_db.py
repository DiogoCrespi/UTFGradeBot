import os
import psycopg2
from dotenv import load_dotenv
from config.settings import DB_CONFIG

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
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
        
        # Executa as migrações em ordem
        migrations = [
            '001_create_tables.sql',
            '002_add_campus_to_cursos.sql',
            '003_add_turno_to_cursos.sql',
            '004_add_duracao_to_cursos.sql',
            '005_add_carga_horaria_to_cursos.sql',
            '006_add_id_to_disciplinas.sql',
            '007_add_global_updates.sql'
        ]
        
        for migration in migrations:
            migration_path = os.path.join('db', 'migrations', migration)
            if os.path.exists(migration_path):
                with open(migration_path, 'r') as f:
                    sql = f.read()
                    cur.execute(sql)
                print(f"Migração {migration} executada com sucesso")
            else:
                print(f"Arquivo de migração {migration} não encontrado")
        
        print("Tabelas criadas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_database() 