import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config.settings import DB_CONFIG

class Database:
    def __init__(self):
        self.config = DB_CONFIG
    
    @contextmanager
    def get_connection(self):
        """Cria uma conexão com o banco de dados"""
        conn = psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password']
        )
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_cursor(self):
        """Cria um cursor para executar queries"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def execute_query(self, query, params=None):
        """Executa uma query e retorna os resultados"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or {})
            return cursor.fetchall()
    
    def execute_update(self, query, params=None):
        """Executa uma query de atualização e retorna o número de linhas afetadas"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or {})
            return cursor.rowcount 