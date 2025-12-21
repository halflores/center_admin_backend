from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class EmpleadoBase(BaseModel):
    nombres: str
    apellidos: str
    ci: str
    fecha_nacimiento: Optional[date] = None
    
    cargo_id: Optional[int] = None
    
    fecha_ingreso: Optional[date] = None
    salario: Optional[float] = None
    bonificaciones: Optional[float] = 0.00
    
    correo: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None
    
    activo: Optional[bool] = True

class EmpleadoCreate(EmpleadoBase):
    crear_usuario: Optional[bool] = False
    rol_usuario_id: Optional[int] = None
    contrasena: Optional[str] = None # Optional, defaults to CI if generated

class EmpleadoUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    ci: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    
    cargo_id: Optional[int] = None
    
    fecha_ingreso: Optional[date] = None
    salario: Optional[float] = None
    bonificaciones: Optional[float] = None
    
    correo: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None
    
    activo: Optional[bool] = None
    usuario_id: Optional[int] = None

class EmpleadoResponse(EmpleadoBase):
    id: int
    usuario_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Include cargo info
    # cargo_nombre: Optional[str] = None

    class Config:
        from_attributes = True

from app.schemas.cargo import CargoResponse
class EmpleadoDetailResponse(EmpleadoResponse):
    cargo: Optional[CargoResponse] = None
