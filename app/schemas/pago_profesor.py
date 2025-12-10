from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class PagoProfesorBase(BaseModel):
    profesor_id: int
    gestion_id: Optional[int] = None
    tipo_transaccion_id: Optional[int] = None
    nro_voucher: Optional[str] = None
    horas_trabajadas: Optional[int] = None
    monto_hora: Optional[float] = None
    monto_total: float
    estado: Optional[str] = 'PENDIENTE'
    fecha_pago: Optional[date] = None
    observaciones: Optional[str] = None

class PagoProfesorCreate(PagoProfesorBase):
    pass

class PagoProfesorUpdate(BaseModel):
    gestion_id: Optional[int] = None
    tipo_transaccion_id: Optional[int] = None
    nro_voucher: Optional[str] = None
    horas_trabajadas: Optional[int] = None
    monto_hora: Optional[float] = None
    monto_total: Optional[float] = None
    estado: Optional[str] = None
    fecha_pago: Optional[date] = None
    observaciones: Optional[str] = None

class PagoProfesorResponse(PagoProfesorBase):
    id: int
    usuario_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Response with related data
from app.schemas.profesor import ProfesorResponse
from app.schemas.gestion import GestionResponse
from app.schemas.tipo_transaccion import TipoTransaccionResponse

class PagoProfesorWithDetailsResponse(PagoProfesorResponse):
    profesor: Optional[ProfesorResponse] = None
    gestion: Optional[GestionResponse] = None
    tipo_transaccion: Optional[TipoTransaccionResponse] = None
