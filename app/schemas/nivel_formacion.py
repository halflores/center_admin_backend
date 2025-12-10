from pydantic import BaseModel
from typing import Optional

# Shared properties
class NivelFormacionBase(BaseModel):
    nombre: str

# Properties to receive via API on creation
class NivelFormacionCreate(NivelFormacionBase):
    pass

# Properties to receive via API on update
class NivelFormacionUpdate(NivelFormacionBase):
    pass

class NivelFormacionInDBBase(NivelFormacionBase):
    id: int

    class Config:
        from_attributes = True

# Additional properties to return via API
class NivelFormacionResponse(NivelFormacionInDBBase):
    pass
