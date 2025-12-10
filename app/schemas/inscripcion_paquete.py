from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InscripcionPaqueteBase(BaseModel):
    estudiante_id: int
    paquete_id: int
    gestion_id: Optional[int] = None
    venta_id: Optional[int] = None


class InscripcionPaqueteCreate(InscripcionPaqueteBase):
    pass


class InscripcionPaqueteUpdate(BaseModel):
    estado_academico: Optional[str] = None  # INSCRITO, APROBADO, REPROBADO
    observaciones: Optional[str] = None
    profesor_id: Optional[int] = None


class InscripcionPaqueteResultado(BaseModel):
    """Schema for professor to set student result"""
    estado_academico: str  # APROBADO, REPROBADO
    observaciones: Optional[str] = None


class InscripcionPaqueteResponse(InscripcionPaqueteBase):
    id: int
    estado_academico: str
    fecha_inscripcion: datetime
    fecha_resultado: Optional[datetime] = None
    profesor_id: Optional[int] = None
    observaciones: Optional[str] = None
    created_at: datetime
    # Enriched fields
    estudiante_nombres: Optional[str] = None
    estudiante_apellidos: Optional[str] = None
    paquete_nombre: Optional[str] = None
    programa_nombre: Optional[str] = None
    nivel_nombre: Optional[str] = None
    modulo_nombre: Optional[str] = None
    profesor_nombres: Optional[str] = None
    profesor_apellidos: Optional[str] = None

    class Config:
        from_attributes = True


class SiguientePaqueteResponse(BaseModel):
    """Response for suggested next package based on student progress"""
    estudiante_id: int
    ultimo_aprobado: Optional[InscripcionPaqueteResponse] = None
    siguiente_paquete: Optional[dict] = None
    mensaje: str
