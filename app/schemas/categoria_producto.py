from pydantic import BaseModel
from typing import Optional

class CategoriaProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaProductoCreate(CategoriaProductoBase):
    pass

class CategoriaProductoUpdate(CategoriaProductoBase):
    nombre: Optional[str] = None

class CategoriaProductoResponse(CategoriaProductoBase):
    id: int

    class Config:
        from_attributes = True
