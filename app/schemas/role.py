from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoleBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    nombre: Optional[str] = None

class RoleResponse(RoleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
