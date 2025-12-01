from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MovimientoInventarioBase(BaseModel):
    producto_id: int
    tipo_movimiento: str
    cantidad: int
    referencia_tabla: Optional[str] = None
    referencia_id: Optional[int] = None

class MovimientoInventarioCreate(MovimientoInventarioBase):
    pass

class MovimientoInventarioResponse(MovimientoInventarioBase):
    id: int
    fecha: datetime
    usuario_id: Optional[int]
    usuario_nombre: Optional[str] = None
    producto_nombre: Optional[str] = None
    cliente: Optional[str] = None
    proveedor: Optional[str] = None
    anulado: bool = False
    total: Optional[float] = None

    class Config:
        from_attributes = True
