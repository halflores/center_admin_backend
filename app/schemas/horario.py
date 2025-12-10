from pydantic import BaseModel
from typing import Optional
from datetime import time

class HorarioBase(BaseModel):
    curso_id: int
    dia_semana: str
    hora_inicio: time
    hora_fin: time
    aula_id: Optional[int] = None

class HorarioCreate(HorarioBase):
    pass

class HorarioUpdate(BaseModel):
    curso_id: Optional[int] = None
    dia_semana: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    aula_id: Optional[int] = None

class HorarioResponse(HorarioBase):
    id: int

    class Config:
        from_attributes = True

from app.schemas.aula import AulaResponse

class ProfesorSimpleResponse(BaseModel):
    id: int
    nombres: str
    apellidos: str
    class Config:
        from_attributes = True

class ModuloSimpleResponse(BaseModel):
    id: int
    nombre: str
    class Config:
        from_attributes = True

class CursoSimpleResponse(BaseModel):
    id: int
    modulo_id: int
    modulo: Optional[ModuloSimpleResponse] = None
    profesor: Optional[ProfesorSimpleResponse] = None
    class Config:
        from_attributes = True

class HorarioWithAulaResponse(HorarioResponse):
    aula_rel: Optional[AulaResponse] = None
    curso: Optional[CursoSimpleResponse] = None
