import argparse
from db.db import Database
from db.queries import (
    SELECT_DISCIPLINAS_POR_CURSO_PERIODO,
    SELECT_CARGA_HORARIA_TOTAL_POR_PERIODO
)

def consultar_disciplinas(periodo):
    """Consulta as disciplinas de um período específico"""
    db = Database()
    
    # Consulta as disciplinas
    disciplinas = db.execute_query(
        SELECT_DISCIPLINAS_POR_CURSO_PERIODO,
        {'curso_id': 1, 'periodo': periodo}  # curso_id 1 é o curso de Engenharia de Software
    )
    
    # Consulta a carga horária total
    carga_horaria = db.execute_query(
        SELECT_CARGA_HORARIA_TOTAL_POR_PERIODO,
        {'curso_id': 1}
    )
    
    # Exibe as disciplinas
    print(f"\nDisciplinas do {periodo}º período:")
    print("-" * 80)
    print(f"{'Código':<10} {'Nome':<50} {'CH':<5} {'Tipo':<15}")
    print("-" * 80)
    
    for disc in disciplinas:
        print(f"{disc['codigo']:<10} {disc['nome']:<50} {disc['carga_horaria']:<5} {disc['tipo']:<15}")
    
    # Exibe a carga horária total
    total = next((ch['total_horas'] for ch in carga_horaria if ch['periodo'] == periodo), 0)
    print("-" * 80)
    print(f"Carga horária total: {total} horas")

def main():
    parser = argparse.ArgumentParser(description='Consulta disciplinas por período')
    parser.add_argument('--periodo', type=int, required=True, help='Número do período')
    args = parser.parse_args()
    
    consultar_disciplinas(args.periodo)

if __name__ == '__main__':
    main() 