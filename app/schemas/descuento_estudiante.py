from pydantic import BaseModel, validator
from typing import Optional
from decimal import Decimal
from datetime import datetime

class DescuentoEstudianteBase(BaseModel):
    estudiante_id: int
    producto_id: int
    lista_precios_id: Optional[int] = None
    porcentaje_descuento: Optional[Decimal] = None
    monto_descuento: Optional[Decimal] = None
    activo: Optional[bool] = True

    @validator('porcentaje_descuento')
    def validate_porcentaje(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Percentage must be between 0 and 100')
        return v

    @validator('monto_descuento')
    def validate_monto(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount must be non-negative')
        return v

class DescuentoEstudianteCreate(DescuentoEstudianteBase):
    pass

class DescuentoEstudianteUpdate(BaseModel):
    porcentaje_descuento: Optional[Decimal] = None
    monto_descuento: Optional[Decimal] = None
    activo: Optional[bool] = None

    @validator('porcentaje_descuento')
    def validate_porcentaje(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Percentage must be between 0 and 100')
        return v

    @validator('monto_descuento')
    def validate_monto(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount must be non-negative')
        return v

class DescuentoEstudianteResponse(DescuentoEstudianteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
