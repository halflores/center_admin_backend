from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TipoTransaccionBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: Optional[bool] = True


class TipoTransaccionCreate(TipoTransaccionBase):
    pass


class TipoTransaccionUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class TipoTransaccionResponse(TipoTransaccionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
