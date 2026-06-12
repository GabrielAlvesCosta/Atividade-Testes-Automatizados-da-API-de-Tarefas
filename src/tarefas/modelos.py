from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class StatusTarefa(str, Enum):
    pendente = 'pendente'
    em_andamento = 'em_andamento'
    concluido = 'concluido'

class TarefaCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descricao: Optional[str] = None

class TarefaResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    status: StatusTarefa = StatusTarefa.pendente