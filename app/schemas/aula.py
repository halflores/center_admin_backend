from pydantic import BaseModel
from typing import Optional

# Shared properties
class AulaBase(BaseModel):
    nombre: str
    capacidad: Optional[int] = None
    ubicacion: Optional[str] = None

# Properties to receive via API on creation
class AulaCreate(AulaBase):
    pass

# Properties to receive via API on update
class AulaUpdate(AulaBase):
    pass

class AulaInDBBase(AulaBase):
    id: int

    class Config:
        from_attributes = True

# Additional properties to return via API
class AulaResponse(AulaInDBBase):
    pass
