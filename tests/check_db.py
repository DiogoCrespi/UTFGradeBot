from db.db import Database

def check_database():
    db = Database()
    
    # Verifica cursos
    cursos = db.execute_query("SELECT COUNT(*) as count FROM cursos")
    print(f"\nCursos: {cursos[0]['count']}")
    cursos_detalhes = db.execute_query("SELECT id, codigo, nome, campus FROM cursos")
    print("Detalhes dos cursos:")
    for curso in cursos_detalhes:
        print(f"ID: {curso['id']}, Código: {curso['codigo']}, Nome: {curso['nome']}, Campus: {curso['campus']}")
    
    # Verifica disciplinas
    disciplinas = db.execute_query("SELECT COUNT(*) as count FROM disciplinas")
    print(f"\nDisciplinas: {disciplinas[0]['count']}")
    disciplinas_detalhes = db.execute_query("SELECT id, codigo, nome FROM disciplinas")
    print("Detalhes das disciplinas:")
    for disciplina in disciplinas_detalhes:
        print(f"ID: {disciplina['id']}, Código: {disciplina['codigo']}, Nome: {disciplina['nome']}")
    
    # Verifica turmas
    turmas = db.execute_query("SELECT COUNT(*) as count FROM turmas")
    print(f"\nTurmas: {turmas[0]['count']}")
    turmas_detalhes = db.execute_query("SELECT id, codigo, professor FROM turmas")
    print("Detalhes das turmas:")
    for turma in turmas_detalhes:
        print(f"ID: {turma['id']}, Código: {turma['codigo']}, Professor: {turma['professor']}")
    
    # Consulta para listar disciplinas com professores e horários
    disciplinas_info = db.execute_query("""
        SELECT d.codigo, d.nome, t.codigo as turma_codigo, t.professor, h.dia_semana, h.aula_inicio, h.aula_fim
        FROM disciplinas d
        LEFT JOIN turmas t ON d.id = t.disciplina_id
        LEFT JOIN horarios h ON t.id = h.turma_id
        ORDER BY d.codigo, t.codigo
    """)
    print("\nDisciplinas com professores e horários:")
    for info in disciplinas_info:
        print(f"[{info['codigo']}] {info['nome']} - {info['turma_codigo']} — {info['professor']} [{info['dia_semana']} {info['aula_inicio']}-{info['aula_fim']}]")

if __name__ == "__main__":
    check_database() 