from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ModuloBase(BaseModel):
    nivel_id: int
    codigo: Optional[str] = None
    nombre: str
    duracion_semanas: Optional[int] = None
    horas_presenciales: Optional[int] = None
    horas_totales: Optional[int] = None
    orden: Optional[int] = 0
    activo: Optional[bool] = True

class ModuloCreate(ModuloBase):
    pass

class ModuloUpdate(BaseModel):
    nivel_id: Optional[int] = None
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    duracion_semanas: Optional[int] = None
    horas_presenciales: Optional[int] = None
    horas_totales: Optional[int] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None

class ModuloResponse(ModuloBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Response with nivel info
from app.schemas.nivel import NivelResponse

class ModuloWithNivelResponse(ModuloResponse):
    nivel: Optional[NivelResponse] = None
