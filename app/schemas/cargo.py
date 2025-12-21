from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CargoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: Optional[bool] = True

class CargoCreate(CargoBase):
    pass

class CargoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class CargoResponse(CargoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
