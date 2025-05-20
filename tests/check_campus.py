from db.db import Database

def check_campus():
    try:
        db = Database()
        result = db.execute_query("SELECT DISTINCT campus FROM cursos ORDER BY campus;")
        
        print("\nCampus encontrados no banco de dados:")
        print("-" * 30)
        for row in result:
            print(f"- {row[0]}")
        print("-" * 30)
        
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")

if __name__ == "__main__":
    check_campus() 