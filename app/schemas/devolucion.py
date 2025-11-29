from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

class DetalleDevolucionBase(BaseModel):
    producto_id: int
    cantidad: int

    @validator('cantidad')
    def validate_cantidad(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class DetalleDevolucionCreate(DetalleDevolucionBase):
    pass

class DetalleDevolucionResponse(DetalleDevolucionBase):
    id: int

    class Config:
        from_attributes = True

class DevolucionBase(BaseModel):
    tipo: str
    referencia_id: Optional[int] = None
    motivo: Optional[str] = None

    @validator('tipo')
    def validate_tipo(cls, v):
        if v not in ('PROVEEDOR', 'ESTUDIANTE'):
            raise ValueError('Type must be PROVEEDOR or ESTUDIANTE')
        return v

class DevolucionCreate(DevolucionBase):
    detalles: List[DetalleDevolucionCreate]

class DevolucionResponse(DevolucionBase):
    id: int
    fecha: datetime
    usuario_id: Optional[int]
    estado: str
    detalles: List[DetalleDevolucionResponse]

    class Config:
        from_attributes = True
