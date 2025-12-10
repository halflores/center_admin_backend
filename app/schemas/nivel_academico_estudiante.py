from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NivelAcademicoEstudianteBase(BaseModel):
    gestion_id: Optional[int] = None
    programa_id: Optional[int] = None
    nivel_id: Optional[int] = None
    modulo_id: Optional[int] = None
    comentario_evaluacion: Optional[str] = None


class NivelAcademicoEstudianteCreate(NivelAcademicoEstudianteBase):
    estudiante_id: int


class NivelAcademicoEstudianteUpdate(NivelAcademicoEstudianteBase):
    pass


class NivelAcademicoEstudianteResponse(NivelAcademicoEstudianteBase):
    id: int
    estudiante_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Response with related data
from app.schemas.gestion import GestionResponse
from app.schemas.programa import ProgramaResponse
from app.schemas.nivel import NivelResponse
from app.schemas.modulo import ModuloResponse

class NivelAcademicoEstudianteWithDetailsResponse(NivelAcademicoEstudianteResponse):
    gestion: Optional[GestionResponse] = None
    programa: Optional[ProgramaResponse] = None
    nivel: Optional[NivelResponse] = None
    modulo: Optional[ModuloResponse] = None
