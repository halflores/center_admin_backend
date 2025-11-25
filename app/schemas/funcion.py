from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class FuncionBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None

class FuncionCreate(FuncionBase):
    pass

class FuncionUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None

class FuncionResponse(FuncionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
