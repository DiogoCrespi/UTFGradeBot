from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Curso:
    codigo: str
    nome: str
    campus: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Disciplina:
    codigo: str
    nome: str
    carga_horaria: int
    tipo: str  # 'OBRIGATORIA' ou 'ELETIVA'
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class CursoDisciplina:
    curso_id: int
    disciplina_id: int
    periodo: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Turma:
    codigo: str
    professor: str
    vagas_totais: int
    vagas_ocupadas: int
    disciplina_id: Optional[int] = None
    id: Optional[int] = None
    horarios: List['Horario'] = None

    def __post_init__(self):
        if self.horarios is None:
            self.horarios = []

@dataclass
class Horario:
    dia_semana: int  # 1=Segunda, 2=Terça, etc.
    turno: str  # 'M'=Manhã, 'T'=Tarde, 'N'=Noite
    aula_inicio: int
    aula_fim: int
    sala: Optional[str] = None
    turma_id: Optional[int] = None
    id: Optional[int] = None 