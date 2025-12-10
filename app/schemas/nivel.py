from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NivelBase(BaseModel):
    programa_id: int
    codigo: Optional[str] = None
    nombre: str
    nombre_comercial: Optional[str] = None
    orden: Optional[int] = 0
    duracion_sugerida: Optional[str] = None
    enfoque_principal: Optional[str] = None
    duracion_meses: Optional[int] = None
    activo: Optional[bool] = True

class NivelCreate(NivelBase):
    pass

class NivelUpdate(BaseModel):
    programa_id: Optional[int] = None
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    nombre_comercial: Optional[str] = None
    orden: Optional[int] = None
    duracion_sugerida: Optional[str] = None
    enfoque_principal: Optional[str] = None
    duracion_meses: Optional[int] = None
    activo: Optional[bool] = None

class NivelResponse(NivelBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Response with program info
from app.schemas.programa import ProgramaResponse

class NivelWithProgramaResponse(NivelResponse):
    programa: Optional[ProgramaResponse] = None
