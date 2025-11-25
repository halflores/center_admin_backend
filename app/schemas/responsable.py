from pydantic import BaseModel
from typing import Optional

class ResponsableBase(BaseModel):
    estudiante_id: int
    parentesco_id: Optional[int] = None
    nombres: str
    apellidos: str
    direccion: Optional[str] = None
    correo: Optional[str] = None
    celular: Optional[str] = None

class ResponsableCreate(ResponsableBase):
    pass

class ResponsableUpdate(ResponsableBase):
    estudiante_id: Optional[int] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None

class ResponsableResponse(ResponsableBase):
    id: int

    class Config:
        from_attributes = True
