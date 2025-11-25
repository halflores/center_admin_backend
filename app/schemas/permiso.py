from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.funcion import FuncionResponse
from app.schemas.accion import AccionResponse

class PermisoBase(BaseModel):
    funcion_id: int
    accion_id: int

class PermisoCreate(PermisoBase):
    pass

class PermisoUpdate(BaseModel):
    funcion_id: Optional[int] = None
    accion_id: Optional[int] = None

class PermisoResponse(PermisoBase):
    id: int
    funcion: Optional[FuncionResponse] = None
    accion: Optional[AccionResponse] = None

    model_config = ConfigDict(from_attributes=True)
