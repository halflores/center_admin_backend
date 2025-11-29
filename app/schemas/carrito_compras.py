from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class CarritoItemBase(BaseModel):
    producto_id: int
    cantidad: int

    @validator('cantidad')
    def validate_cantidad(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class CarritoItemCreate(CarritoItemBase):
    pass

class CarritoItemUpdate(BaseModel):
    cantidad: int

    @validator('cantidad')
    def validate_cantidad(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class CarritoItemResponse(CarritoItemBase):
    id: int
    usuario_id: int
    created_at: datetime

    class Config:
        from_attributes = True
