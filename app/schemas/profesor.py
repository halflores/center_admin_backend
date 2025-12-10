from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class ProfesorBase(BaseModel):
    ci: Optional[str] = None
    nombres: str
    apellidos: str
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[str] = None
    comentarios: Optional[str] = None
    nivel_formacion_id: Optional[int] = None
    experiencia_anios: Optional[int] = None
    fecha_ingreso: Optional[date] = None
    fecha_salida: Optional[date] = None
    tipo_contrato: Optional[str] = None
    salario_hora: Optional[float] = None
    activo: Optional[bool] = True

class ProfesorCreate(ProfesorBase):
    usuario_id: Optional[int] = None
    campus_ids: Optional[List[int]] = None  # List of campus IDs to associate

class ProfesorUpdate(BaseModel):
    ci: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[str] = None
    comentarios: Optional[str] = None
    nivel_formacion_id: Optional[int] = None
    experiencia_anios: Optional[int] = None
    fecha_ingreso: Optional[date] = None
    fecha_salida: Optional[date] = None
    tipo_contrato: Optional[str] = None
    salario_hora: Optional[float] = None
    activo: Optional[bool] = None
    usuario_id: Optional[int] = None
    campus_ids: Optional[List[int]] = None

class ProfesorCampusResponse(BaseModel):
    campus_id: int
    principal: bool
    
    class Config:
        from_attributes = True

class ProfesorResponse(ProfesorBase):
    id: int
    usuario_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Response with campus list
from app.schemas.campus import CampusResponse
from app.schemas.nivel_formacion import NivelFormacionResponse

class ProfesorCampusDetailResponse(BaseModel):
    campus: CampusResponse
    principal: bool
    
    class Config:
        from_attributes = True

class ProfesorWithCampusResponse(ProfesorResponse):
    campus_list: List[ProfesorCampusDetailResponse] = []
    nivel_formacion_rel: Optional[NivelFormacionResponse] = None
