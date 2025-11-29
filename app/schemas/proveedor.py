from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProveedorBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    celular: Optional[str] = None
    nombre_responsable: Optional[str] = None

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    celular: Optional[str] = None
    nombre_responsable: Optional[str] = None

class ProveedorResponse(ProveedorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
