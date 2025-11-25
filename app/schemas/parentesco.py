from pydantic import BaseModel
from typing import Optional

class ParentescoBase(BaseModel):
    nombre: str

class ParentescoCreate(ParentescoBase):
    pass

class ParentescoUpdate(ParentescoBase):
    nombre: Optional[str] = None

class ParentescoResponse(ParentescoBase):
    id: int

    class Config:
        from_attributes = True
