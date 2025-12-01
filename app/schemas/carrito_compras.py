from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class CarritoItemBase(BaseModel):
    producto_id: int
    cantidad: int
    descuento: Optional[float] = 0.0

    @validator('cantidad')
    def validate_cantidad(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class CarritoItemCreate(CarritoItemBase):
    pass

class CarritoItemUpdate(BaseModel):
    cantidad: Optional[int] = None
    descuento: Optional[float] = None

    @validator('cantidad')
    def validate_cantidad(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class CarritoItemResponse(CarritoItemBase):
    id: int
    usuario_id: int
    created_at: datetime

    class Config:
        from_attributes = True
