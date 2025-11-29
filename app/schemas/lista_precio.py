from pydantic import BaseModel
from typing import Optional

class ListaPrecioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class ListaPrecioCreate(ListaPrecioBase):
    pass

class ListaPrecioUpdate(ListaPrecioBase):
    nombre: Optional[str] = None

class ListaPrecioResponse(ListaPrecioBase):
    id: int

    class Config:
        from_attributes = True
