from db.db import Database

def check_database():
    db = Database()
    
    # Verifica cursos
    cursos = db.execute_query("SELECT COUNT(*) as count FROM cursos")
    print(f"\nCursos: {cursos[0]['count']}")
    
    # Verifica disciplinas
    disciplinas = db.execute_query("SELECT COUNT(*) as count FROM disciplinas")
    print(f"Disciplinas: {disciplinas[0]['count']}")
    
    # Verifica turmas
    turmas = db.execute_query("SELECT COUNT(*) as count FROM turmas")
    print(f"Turmas: {turmas[0]['count']}")

if __name__ == "__main__":
    check_database() 