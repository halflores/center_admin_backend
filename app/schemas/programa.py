from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProgramaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: Optional[bool] = True

class ProgramaCreate(ProgramaBase):
    pass

class ProgramaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class ProgramaResponse(ProgramaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
