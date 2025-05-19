from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db.db import Database
from db.queries import (
    SELECT_CURSO_POR_CODIGO,
    SELECT_DISCIPLINA_POR_CODIGO,
    SELECT_DISCIPLINAS_POR_CURSO_PERIODO,
    SELECT_CARGA_HORARIA_TOTAL_POR_PERIODO
)
from .models import (
    Curso,
    Disciplina,
    Turma,
    CargaHorariaPeriodo,
    CursoDetalhado
)
from typing import List

app = FastAPI(
    title="Turing Bot API",
    description="API para consulta de dados do currículo da UTFPR",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância do banco de dados
db = Database()

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Bem-vindo à API do Turing Bot",
        "version": "1.0.0",
        "endpoints": {
            "cursos": "/api/cursos",
            "disciplinas": "/api/disciplinas",
            "turmas": "/api/turmas"
        }
    }

@app.get("/api/cursos", response_model=List[Curso])
async def listar_cursos():
    """Lista todos os cursos"""
    query = "SELECT * FROM cursos ORDER BY nome"
    return db.execute_query(query)

@app.get("/api/cursos/{codigo}", response_model=CursoDetalhado)
async def get_curso(codigo: str):
    """Retorna detalhes de um curso específico"""
    # Busca informações do curso
    curso = db.execute_query(SELECT_CURSO_POR_CODIGO, {"codigo": codigo})
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    
    # Busca disciplinas do curso
    disciplinas = db.execute_query(
        SELECT_DISCIPLINAS_POR_CURSO_PERIODO,
        {"codigo": codigo}
    )
    
    # Busca carga horária por período
    carga_horaria = db.execute_query(
        SELECT_CARGA_HORARIA_TOTAL_POR_PERIODO,
        {"codigo": codigo}
    )
    
    return {
        **curso[0],
        "disciplinas": disciplinas,
        "carga_horaria_por_periodo": carga_horaria
    }

@app.get("/api/cursos/{codigo}/disciplinas", response_model=List[Disciplina])
async def listar_disciplinas_curso(codigo: str):
    """Lista todas as disciplinas de um curso"""
    query = """
        SELECT DISTINCT d.*, cd.periodo
        FROM disciplinas d
        JOIN curso_disciplinas cd ON d.id = cd.disciplina_id
        JOIN cursos c ON c.id = cd.curso_id
        WHERE c.codigo = %(codigo)s
        ORDER BY cd.periodo, d.nome
    """
    return db.execute_query(query, {"codigo": codigo})

@app.get("/api/cursos/{codigo}/disciplinas/{periodo}", response_model=List[Disciplina])
async def listar_disciplinas_periodo(codigo: str, periodo: int):
    """Lista disciplinas de um período específico"""
    disciplinas = db.execute_query(
        SELECT_DISCIPLINAS_POR_CURSO_PERIODO,
        {"codigo": codigo, "periodo": periodo}
    )
    if not disciplinas:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhuma disciplina encontrada para o período {periodo}"
        )
    return disciplinas

@app.get("/api/cursos/{codigo}/carga-horaria", response_model=List[CargaHorariaPeriodo])
async def get_carga_horaria_curso(codigo: str):
    """Retorna a carga horária total por período"""
    return db.execute_query(
        SELECT_CARGA_HORARIA_TOTAL_POR_PERIODO,
        {"codigo": codigo}
    )

@app.get("/api/disciplinas/{codigo}", response_model=Disciplina)
async def get_disciplina(codigo: str):
    """Retorna detalhes de uma disciplina"""
    disciplina = db.execute_query(
        SELECT_DISCIPLINA_POR_CODIGO,
        {"codigo": codigo}
    )
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    return disciplina[0]

@app.get("/api/disciplinas/{codigo}/turmas", response_model=List[Turma])
async def listar_turmas_disciplina(codigo: str):
    """Lista todas as turmas de uma disciplina"""
    query = """
        SELECT 
            t.id,
            t.codigo,
            t.professor,
            json_agg(
                json_build_object(
                    'dia_semana', h.dia_semana,
                    'turno', h.turno,
                    'aula_inicio', h.aula_inicio,
                    'aula_fim', h.aula_fim,
                    'sala', h.sala
                )
            ) as horarios
        FROM turmas t
        JOIN disciplinas d ON d.id = t.disciplina_id
        LEFT JOIN horarios h ON h.turma_id = t.id
        WHERE d.codigo = %(codigo)s
        GROUP BY t.id, t.codigo, t.professor
        ORDER BY t.codigo
    """
    return db.execute_query(query, {"codigo": codigo})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 