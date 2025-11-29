from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductoBase(BaseModel):
    nombre: str
    categoria_id: Optional[int] = None
    codigo: Optional[str] = None
    stock_actual: Optional[int] = 0
    activo: Optional[bool] = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    codigo: Optional[str] = None
    stock_actual: Optional[int] = None
    activo: Optional[bool] = None

class ProductoResponse(ProductoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
