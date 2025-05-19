from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import time, datetime

class Curso(BaseModel):
    id: int
    codigo: str = Field(..., description="Código do curso")
    nome: str = Field(..., description="Nome do curso")
    modalidade: str
    campus: str
    turno: str
    duracao: int
    carga_horaria: int
    carga_horaria_total: int = Field(..., description="Carga horária total do curso")
    periodo_atual: int = Field(..., description="Período atual do curso")

class Disciplina(BaseModel):
    id: int
    codigo: str = Field(..., description="Código da disciplina")
    nome: str = Field(..., description="Nome da disciplina")
    carga_horaria: int = Field(..., description="Carga horária total")
    periodo: int = Field(..., description="Período em que a disciplina é oferecida")
    aulas_por_semana: int = Field(..., description="Número de aulas por semana")
    tipo: str = Field(..., description="Tipo da disciplina (OBRIGATORIA ou OPTATIVA)")
    curso_codigo: str = Field(..., description="Código do curso")

class Horario(BaseModel):
    dia: str = Field(..., description="Dia da semana (ex: 2M, 3T, 4N)")
    horario: str = Field(..., description="Horário (ex: M1, M2, T3)")
    sala: str = Field(..., description="Sala (ex: L22, I11, H610)")

class Turma(BaseModel):
    id: int
    codigo: str = Field(..., description="Código da turma")
    professor: str = Field(..., description="Nome do professor")
    horarios: List[Horario] = Field(..., description="Lista de horários da turma")

class CargaHorariaPeriodo(BaseModel):
    periodo: int = Field(..., description="Número do período")
    carga_horaria: int = Field(..., description="Carga horária total do período")
    disciplinas: List[Disciplina] = Field(..., description="Lista de disciplinas do período")

class CursoDetalhado(Curso):
    disciplinas: List[Disciplina] = Field(..., description="Lista de disciplinas do curso")
    carga_horaria_por_periodo: List[dict] = Field(..., description="Carga horária por período") 