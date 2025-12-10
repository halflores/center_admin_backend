from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InscripcionBase(BaseModel):
    estudiante_id: int
    curso_id: int
    gestion_id: int
    estado: Optional[str] = 'ACTIVO'
    monto_pagado: Optional[float] = None
    observaciones: Optional[str] = None

class InscripcionCreate(InscripcionBase):
    pass

class InscripcionUpdate(BaseModel):
    estado: Optional[str] = None
    monto_pagado: Optional[float] = None
    observaciones: Optional[str] = None

class InscripcionResponse(InscripcionBase):
    id: int
    fecha_inscripcion: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Response with related data
from app.schemas.estudiante import EstudianteResponse
from app.schemas.curso import CursoResponse
from app.schemas.gestion import GestionResponse

class InscripcionWithDetailsResponse(InscripcionResponse):
    estudiante: Optional[EstudianteResponse] = None
    curso: Optional[CursoResponse] = None
    gestion: Optional[GestionResponse] = None
