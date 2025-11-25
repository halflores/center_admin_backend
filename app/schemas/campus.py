from pydantic import BaseModel
from typing import Optional

class CampusBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    celular: Optional[str] = None

class CampusCreate(CampusBase):
    pass

class CampusUpdate(CampusBase):
    nombre: Optional[str] = None

class CampusResponse(CampusBase):
    id: int

    class Config:
        from_attributes = True
