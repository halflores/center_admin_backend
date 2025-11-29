from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class PrecioProductoBase(BaseModel):
    producto_id: int
    lista_precios_id: int
    precio: Decimal

class PrecioProductoCreate(PrecioProductoBase):
    pass

class PrecioProductoUpdate(BaseModel):
    precio: Decimal

class PrecioProductoResponse(PrecioProductoBase):
    id: int

    class Config:
        from_attributes = True
