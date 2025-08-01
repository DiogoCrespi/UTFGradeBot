import os
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def criar_banco():
    """Cria o banco de dados se não existir"""
    try:
        # Conecta ao PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="1597"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verifica se o banco existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'turing_bot'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Criando banco de dados 'turing_bot'...")
            cursor.execute("CREATE DATABASE turing_bot")
            print("Banco de dados criado com sucesso!")
        else:
            print("Banco de dados 'turing_bot' já existe.")
        
        cursor.close()
        conn.close()
        
        # Executa o script SQL
        print("Executando script de criação das tabelas...")
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="turing_bot",
            user="postgres",
            password="1597"
        )
        cursor = conn.cursor()
        
        # Lê e executa o arquivo schema.sql
        with open('db/schema.sql', 'r') as f:
            cursor.execute(f.read())
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Tabelas criadas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar banco de dados: {str(e)}")
        raise

if __name__ == '__main__':
    criar_banco() 