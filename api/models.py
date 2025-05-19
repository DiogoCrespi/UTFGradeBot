from pydantic import BaseModel
from typing import List, Optional
from datetime import time

class Curso(BaseModel):
    id: int
    codigo: str
    nome: str
    modalidade: str
    campus: str
    turno: str
    duracao: int
    carga_horaria: int

class Disciplina(BaseModel):
    id: int
    codigo: str
    nome: str
    carga_horaria: int
    periodo: Optional[int] = None

class Horario(BaseModel):
    dia_semana: str
    turno: str
    aula_inicio: time
    aula_fim: time
    sala: str

class Turma(BaseModel):
    id: int
    codigo: str
    professor: str
    horarios: List[Horario]

class CargaHorariaPeriodo(BaseModel):
    periodo: int
    carga_horaria: int

class CursoDetalhado(Curso):
    disciplinas: List[Disciplina]
    carga_horaria_por_periodo: List[CargaHorariaPeriodo] 