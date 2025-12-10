from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TipoProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: Optional[bool] = True


class TipoProductoCreate(TipoProductoBase):
    pass


class TipoProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class TipoProductoResponse(TipoProductoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
