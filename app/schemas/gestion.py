from pydantic import BaseModel
from typing import Optional

class GestionBase(BaseModel):
    nro: int
    anio: int

class GestionCreate(GestionBase):
    pass

class GestionUpdate(GestionBase):
    nro: Optional[int] = None
    anio: Optional[int] = None

class GestionResponse(GestionBase):
    id: int

    class Config:
        from_attributes = True
