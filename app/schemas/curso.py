from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime, time

class HorarioInCurso(BaseModel):
    dia_semana: str
    hora_inicio: time
    hora_fin: time
    aula: Optional[str] = None

class CursoBase(BaseModel):
    modulo_id: int
    profesor_id: Optional[int] = None
    campus_id: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    cupo_maximo: Optional[int] = None
    estado: Optional[str] = 'ACTIVO'

class CursoCreate(CursoBase):
    horarios: Optional[List[HorarioInCurso]] = None  # Create horarios with curso

class CursoUpdate(BaseModel):
    modulo_id: Optional[int] = None
    profesor_id: Optional[int] = None
    campus_id: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    cupo_maximo: Optional[int] = None
    estado: Optional[str] = None

class HorarioResponse(BaseModel):
    id: int
    dia_semana: str
    hora_inicio: time
    hora_fin: time
    aula: Optional[str] = None
    
    # Import locally to avoid circular deps if needed, 
    # but usually Pydantic handles simple forward refs or we can just define a simple schema here.
    # For now, let's use a simple dict or define a minimal Aula schema right above if strictly needed,
    # or rely on the service returning the object and Pydantic dumping it if configured.
    # Actually, let's just use the definition from implementation plan: import AulaResponse.
    # Wait, circular import risk with app.schemas.aula if that imports this.
    # Let's try adding a minimal valid schema directly here if possible or just use existing structure using "from attributes".
    # Just adding the field that we populated in service (aula_rel).
    
    # Let's define a nested AulaSimple helper to be safe.
    
class AulaSimple(BaseModel):
    id: int
    nombre: str
    ubicacion: Optional[str] = None
    class Config:
        from_attributes = True

class HorarioResponse(BaseModel):
    id: int
    dia_semana: str
    hora_inicio: time
    hora_fin: time
    aula: Optional[str] = None
    aula_rel: Optional[AulaSimple] = None

    class Config:
        from_attributes = True

class CursoResponse(CursoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Response with related data
from app.schemas.modulo import ModuloResponse
from app.schemas.profesor import ProfesorResponse
from app.schemas.campus import CampusResponse

class CursoWithDetailsResponse(CursoResponse):
    modulo: Optional[ModuloResponse] = None
    profesor: Optional[ProfesorResponse] = None
    campus: Optional[CampusResponse] = None
    horarios: List[HorarioResponse] = []
