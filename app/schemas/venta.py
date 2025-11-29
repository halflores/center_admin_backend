from pydantic import BaseModel, validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class DetalleVentaBase(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: Decimal

    @validator('cantidad')
    def validate_cantidad(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class DetalleVentaCreate(DetalleVentaBase):
    pass

class DetalleVentaResponse(DetalleVentaBase):
    id: int
    subtotal: Decimal

    class Config:
        from_attributes = True

class VentaBase(BaseModel):
    estudiante_id: Optional[int] = None
    cliente_nombre: Optional[str] = None
    metodo_pago: Optional[str] = None

class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate]

class VentaResponse(VentaBase):
    id: int
    fecha: datetime
    usuario_id: Optional[int]
    total: Decimal
    estado: str
    detalles: List[DetalleVentaResponse]

    class Config:
        from_attributes = True
