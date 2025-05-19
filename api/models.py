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
    tipo: str = Field(..., description="Tipo da disciplina (OBRIGATORIA ou OPTATIVA)")
    periodo: Optional[int] = Field(None, description="Período em que a disciplina é oferecida")

class Horario(BaseModel):
    id: int
    turma_id: int
    dia_semana: int = Field(..., description="Dia da semana (1-7)")
    turno: str = Field(..., description="Turno (M, T, N)")
    aula_inicio: int = Field(..., description="Número da aula de início")
    aula_fim: int = Field(..., description="Número da aula de fim")
    sala: str = Field(..., description="Sala")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Turma(BaseModel):
    id: int
    codigo: str = Field(..., description="Código da turma")
    professor: str = Field(..., description="Nome do professor")
    disciplina_id: int = Field(..., description="ID da disciplina")
    horarios: List[Horario] = Field(default_factory=list, description="Lista de horários da turma")

class CargaHorariaPeriodo(BaseModel):
    periodo: int = Field(..., description="Número do período")
    carga_horaria: int = Field(..., description="Carga horária total do período")
    disciplinas: List[Disciplina] = Field(..., description="Lista de disciplinas do período")

class CursoDetalhado(Curso):
    disciplinas: List[Disciplina] = Field(..., description="Lista de disciplinas do curso")
    carga_horaria_por_periodo: List[dict] = Field(..., description="Carga horária por período") 