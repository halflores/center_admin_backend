from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class EstudianteBase(BaseModel):
    nombres: str
    apellidos: str
    direccion: Optional[str] = None
    correo: Optional[str] = None
    celular: Optional[str] = None
    campus_id: Optional[int] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None


class EstudianteCreate(EstudianteBase):
    crear_usuario: Optional[bool] = False
    rol_usuario_id: Optional[int] = None
    contrasena: Optional[str] = None


class EstudianteUpdate(EstudianteBase):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None

from app.schemas.campus import CampusResponse
from app.schemas.responsable import ResponsableResponse
from typing import List

class EstudianteResponse(EstudianteBase):
    id: int
    usuario_id: Optional[int] = None
    created_at: datetime
    campus: Optional[CampusResponse] = None
    responsables: List[ResponsableResponse] = []

    class Config:
        from_attributes = True
