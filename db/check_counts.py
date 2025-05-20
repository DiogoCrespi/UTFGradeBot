from db.db import Database
import sys

def check_counts():
    try:
        print("Tentando conectar ao banco de dados...")
        db = Database()
        print("Conexão bem sucedida.")
        
        # Configura a codificação para UTF-8
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
        
        print("\n=== Contagem de Registros ===")
        print("-" * 30)
        
        # Verifica cursos
        cursos = db.execute_query("SELECT COUNT(*) as count FROM cursos")
        print(f"Cursos: {cursos[0]['count']}")
        
        # Verifica disciplinas
        disciplinas = db.execute_query("SELECT COUNT(*) as count FROM disciplinas")
        print(f"Disciplinas: {disciplinas[0]['count']}")
        
        # Verifica turmas
        turmas = db.execute_query("SELECT COUNT(*) as count FROM turmas")
        print(f"Turmas: {turmas[0]['count']}")
        
        # Verifica horários
        horarios = db.execute_query("SELECT COUNT(*) as count FROM horarios")
        print(f"Horários: {horarios[0]['count']}")
        
        # Verifica curso_disciplinas
        curso_disc = db.execute_query("SELECT COUNT(*) as count FROM curso_disciplinas")
        print(f"Relações Curso-Disciplina: {curso_disc[0]['count']}")
        
        print("\n=== Últimas Atualizações ===")
        print("-" * 30)
        
        # Verifica última atualização de cursos
        ultima_atualizacao = db.execute_query("""
            SELECT MAX(last_update) as ultima 
            FROM cursos
        """)
        if ultima_atualizacao[0]['ultima']:
            print(f"Última atualização de cursos: {ultima_atualizacao[0]['ultima']}")
        
        print("\nVerificação concluída com sucesso.")
        
    except Exception as e:
        print(f"Erro ao verificar contagens: {str(e)}")

if __name__ == "__main__":
    check_counts() 