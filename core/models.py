from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Curso:
    codigo: str
    nome: str
    campus: Optional[str] = None
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