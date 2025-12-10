from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PaqueteProductoBase(BaseModel):
    producto_id: int
    cantidad: Optional[int] = 1


class PaqueteProductoCreate(PaqueteProductoBase):
    pass


class PaqueteProductoResponse(PaqueteProductoBase):
    id: int
    paquete_id: int
    producto_nombre: Optional[str] = None
    producto_codigo: Optional[str] = None

    class Config:
        from_attributes = True


class PaqueteBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    programa_id: Optional[int] = None
    nivel_id: Optional[int] = None
    modulo_id: Optional[int] = None
    precio_total: Optional[Decimal] = None
    activo: Optional[bool] = True


class PaqueteCreate(PaqueteBase):
    productos: Optional[List[PaqueteProductoCreate]] = []


class PaqueteUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    programa_id: Optional[int] = None
    nivel_id: Optional[int] = None
    modulo_id: Optional[int] = None
    precio_total: Optional[Decimal] = None
    activo: Optional[bool] = None
    productos: Optional[List[PaqueteProductoCreate]] = None


class PaqueteResponse(PaqueteBase):
    id: int
    created_at: datetime
    programa_nombre: Optional[str] = None
    nivel_nombre: Optional[str] = None
    modulo_nombre: Optional[str] = None

    class Config:
        from_attributes = True


class PaqueteWithProductsResponse(PaqueteResponse):
    productos: List[PaqueteProductoResponse] = []
