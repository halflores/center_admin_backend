from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.role import RoleResponse
from app.schemas.permiso import PermisoResponse

class RolPermisoBase(BaseModel):
    rol_id: int
    permiso_id: int

class RolPermisoCreate(RolPermisoBase):
    pass

class RolPermisoUpdate(BaseModel):
    # Typically you don't update a composite key directly, you delete and create.
    # But if we had extra fields, we would update them here.
    pass

class RolPermisoResponse(RolPermisoBase):
    rol: Optional[RoleResponse] = None
    permiso: Optional[PermisoResponse] = None

    model_config = ConfigDict(from_attributes=True)
