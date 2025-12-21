from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

# Shared properties
from app.schemas.estudiante import EstudianteResponse

# Simple user schema for displaying user information
class UsuarioSimple(BaseModel):
    id: int
    nombre: str
    apellido: str
    correo: str
    class Config:
        from_attributes = True

class CategoriaGastoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: Optional[bool] = True

class CategoriaGastoCreate(CategoriaGastoBase):
    pass

class CategoriaGastoUpdate(CategoriaGastoBase):
    nombre: Optional[str] = None

class CategoriaGastoOut(CategoriaGastoBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


class GastoBase(BaseModel):
    categoria_id: int
    monto: Decimal
    descripcion: str
    fecha_gasto: Optional[datetime] = None
    comprobante_referencia: Optional[str] = None
    metodo_pago: Optional[str] = None

class GastoCreate(GastoBase):
    pass

class GastoUpdate(BaseModel):
    categoria_id: Optional[int] = None
    monto: Optional[Decimal] = None
    descripcion: Optional[str] = None
    fecha_gasto: Optional[datetime] = None
    comprobante_referencia: Optional[str] = None
    metodo_pago: Optional[str] = None

class GastoOut(GastoBase):
    id: int
    usuario_id: Optional[int]
    created_at: datetime
    categoria: CategoriaGastoOut
    class Config:
        from_attributes = True


class CajaSesionBase(BaseModel):
    monto_inicial: Decimal = 0.00
    observaciones: Optional[str] = None

class CajaSesionCreate(CajaSesionBase):
    pass

class CajaArqueoBase(BaseModel):
    billetes_200: int = 0
    billetes_100: int = 0
    billetes_50: int = 0
    billetes_20: int = 0
    billetes_10: int = 0
    monedas_5: int = 0
    monedas_2: int = 0
    monedas_1: int = 0
    monedas_050: int = 0
    monedas_020: int = 0
    monedas_010: int = 0
    monto_total: Decimal

class CajaArqueoCreate(CajaArqueoBase):
    pass

class CajaArqueoOut(CajaArqueoBase):
    id: int
    caja_sesion_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class CajaSesionClose(BaseModel):
    monto_final_real: Decimal
    observaciones: Optional[str] = None
    arqueo: Optional[CajaArqueoCreate] = None

class CajaSesionOut(CajaSesionBase):
    id: int
    usuario_id: int
    fecha_apertura: datetime
    fecha_cierre: Optional[datetime]
    monto_final_esperado: Optional[Decimal]
    monto_final_real: Optional[Decimal]
    diferencia: Optional[Decimal]
    estado: str
    class Config:
        from_attributes = True

class CajaMovimientoOut(BaseModel):
    id: int
    sesion_id: Optional[int]
    tipo: str
    categoria: str
    monto: Decimal
    descripcion: Optional[str]
    fecha: datetime
    referencia_tabla: Optional[str]
    referencia_id: Optional[int]
    usuario_id: Optional[int]
    # Payment tracking fields
    metodo_pago: Optional[str] = None
    numero_voucher: Optional[str] = None
    # User details
    usuario: Optional[UsuarioSimple] = None
    class Config:
        from_attributes = True


class PlanPagoBase(BaseModel):
    estudiante_id: int
    monto_total: Decimal
    fecha_vencimiento: date
    observaciones: Optional[str] = None

class PlanPagoCreate(PlanPagoBase):
    inscripcion_id: Optional[int] = None
    inscripcion_paquete_id: Optional[int] = None

class PlanPagoOut(PlanPagoBase):
    id: int
    monto_pagado: Decimal
    saldo_pendiente: Decimal
    fecha_emision: date
    estado: str
    estudiante: Optional[EstudianteResponse] = None
    created_at: datetime
    class Config:
        from_attributes = True

class PagoCuotaCreate(BaseModel):
    monto: Decimal
    metodo_pago: str
    referencia_pago: Optional[str] = None

class PagoNominaBase(BaseModel):
    usuario_empleado_id: int
    monto: Decimal
    tipo_pago: str = 'SUELDO'
    descripcion: Optional[str] = None
    periodo: Optional[str] = None
    metodo_pago: Optional[str] = None
    nro_transaccion: Optional[str] = None
    fecha_pago: Optional[date] = None


class PagoNominaCreate(PagoNominaBase):
    pass

class PagoNominaUpdate(BaseModel):
    monto: Optional[Decimal] = None
    descripcion: Optional[str] = None
    periodo: Optional[str] = None
    metodo_pago: Optional[str] = None
    nro_transaccion: Optional[str] = None
    fecha_pago: Optional[date] = None
# ... (rest of the file)
class PagoNominaOut(PagoNominaBase):
    id: int
    usuario_admin_id: Optional[int]
    fecha_pago: date
    estado: str
    created_at: datetime
    class Config:
        from_attributes = True
