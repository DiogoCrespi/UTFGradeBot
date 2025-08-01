#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Configura a codificação para UTF-8 no Windows
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')

# Configurações hardcoded para teste
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'utfgradebot',
    'user': 'postgres',
    'password': '1597'
}

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        print("🔧 Testando conexão com o banco de dados...")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        print("✅ Conexão com o banco de dados estabelecida!")
        
        # Testa uma query simples
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM cursos")
        count = cur.fetchone()[0]
        print(f"✅ Encontrados {count} cursos no banco de dados")
        
        # Testa query específica do curso
        cur.execute("""
            SELECT COUNT(*) 
            FROM cursos c
            JOIN curso_disciplinas cd ON c.id = cd.curso_id
            JOIN disciplinas d ON cd.disciplina_id = d.id
            WHERE c.nome = '219Ciência Computação'
            AND c.campus = 'Medianeira'
        """)
        count_disciplinas = cur.fetchone()[0]
        print(f"✅ Encontradas {count_disciplinas} disciplinas do curso de Ciência da Computação")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {str(e)}")
        return False

def test_query():
    """Testa a query principal do filtrador"""
    try:
        print("\n🔧 Testando query do filtrador...")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query do filtrador
        query = """
            SELECT 
                d.codigo,
                d.nome as disciplina,
                t.codigo as turma,
                t.professor,
                h.dia_semana,
                h.turno,
                h.aula_inicio,
                h.aula_fim,
                h.sala
            FROM cursos c
            JOIN curso_disciplinas cd ON c.id = cd.curso_id
            JOIN disciplinas d ON cd.disciplina_id = d.id
            JOIN turmas t ON d.id = t.disciplina_id
            JOIN horarios h ON t.id = h.turma_id
            WHERE c.nome = '219Ciência Computação'
            AND c.campus = 'Medianeira'
            ORDER BY d.codigo, t.codigo, h.dia_semana, h.turno, h.aula_inicio
            LIMIT 10;
        """
        
        cur.execute(query)
        resultados = cur.fetchall()
        
        print(f"✅ Query executada com sucesso! Encontrados {len(resultados)} registros")
        
        if resultados:
            print("\n📋 Primeiros 5 registros:")
            for i, row in enumerate(resultados[:5]):
                print(f"  {i+1}. {row['codigo']} - {row['disciplina']} - Turma: {row['turma']} - Prof: {row['professor']}")
                print(f"     Horário: {row['dia_semana']}{row['turno']}{row['aula_inicio']}({row['sala']})")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar query: {str(e)}")
        return False

def main():
    """Função principal do teste"""
    print("🚀 Iniciando teste do Filtrador de Horários...")
    
    # Testa conexão
    if not test_connection():
        print("❌ Falha no teste de conexão")
        return
    
    # Testa query
    if not test_query():
        print("❌ Falha no teste de query")
        return
    
    print("\n🎉 Todos os testes passaram! O filtrador está pronto para uso.")
    print("\nPara usar o filtrador completo, execute:")
    print("python run_filtro_horarios_simple.py")

if __name__ == "__main__":
    main() 