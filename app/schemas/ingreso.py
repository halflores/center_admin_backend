from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from app.schemas.proveedor import ProveedorResponse
from app.schemas.producto import ProductoResponse

class DetalleIngresoBase(BaseModel):
    producto_id: int
    cantidad: int
    costo_unitario: Decimal

class DetalleIngresoCreate(DetalleIngresoBase):
    pass

class DetalleIngresoResponse(DetalleIngresoBase):
    id: int
    ingreso_id: int
    subtotal: Decimal
    producto: Optional[ProductoResponse] = None
    
    class Config:
        from_attributes = True

class IngresoBase(BaseModel):
    proveedor_id: Optional[int] = None
    nro_factura: Optional[str] = None

class IngresoCreate(IngresoBase):
    detalles: List[DetalleIngresoCreate]

# Simple user response for ingreso
class UsuarioSimple(BaseModel):
    nombre: str
    apellido: str
    
    class Config:
        from_attributes = True

class IngresoResponse(IngresoBase):
    id: int
    fecha: datetime
    usuario_id: Optional[int]
    total: Decimal
    estado: str
    proveedor: Optional[ProveedorResponse] = None
    usuario: Optional[UsuarioSimple] = None
    detalles: List[DetalleIngresoResponse] = []

    class Config:
        from_attributes = True

