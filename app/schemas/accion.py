from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class AccionBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)

class AccionCreate(AccionBase):
    pass

class AccionUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)

class AccionResponse(AccionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
