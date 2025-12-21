from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# --- Género Literario ---
class GeneroLiterarioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: Optional[bool] = True

class GeneroLiterarioCreate(GeneroLiterarioBase):
    pass

class GeneroLiterarioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class GeneroLiterarioOut(GeneroLiterarioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Editorial ---
class EditorialBase(BaseModel):
    nombre: str
    pais: Optional[str] = None
    sitio_web: Optional[str] = None
    activo: Optional[bool] = True

class EditorialCreate(EditorialBase):
    pass

class EditorialUpdate(BaseModel):
    nombre: Optional[str] = None
    pais: Optional[str] = None
    sitio_web: Optional[str] = None
    activo: Optional[bool] = None

class EditorialOut(EditorialBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Autor ---
class AutorBase(BaseModel):
    nombres: str
    apellidos: str
    nacionalidad: Optional[str] = None
    biografia: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    activo: Optional[bool] = True

class AutorCreate(AutorBase):
    pass

class AutorUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    nacionalidad: Optional[str] = None
    biografia: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    activo: Optional[bool] = None

class AutorOut(AutorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Libro ---
class LibroBase(BaseModel):
    isbn: str
    titulo: str
    subtitulo: Optional[str] = None
    genero_id: int
    editorial_id: int
    anio_publicacion: Optional[int] = None
    numero_paginas: Optional[int] = None
    idioma: Optional[str] = 'Español'
    cantidad_total: int = 1
    cantidad_disponible: int = 1
    ubicacion_fisica: Optional[str] = None
    descripcion: Optional[str] = None
    imagen_portada: Optional[str] = None
    estado: Optional[str] = 'DISPONIBLE'

class LibroCreate(LibroBase):
    autores_ids: List[int]  # Lista de IDs de autores

class LibroUpdate(BaseModel):
    isbn: Optional[str] = None
    titulo: Optional[str] = None
    subtitulo: Optional[str] = None
    genero_id: Optional[int] = None
    editorial_id: Optional[int] = None
    anio_publicacion: Optional[int] = None
    numero_paginas: Optional[int] = None
    idioma: Optional[str] = None
    cantidad_total: Optional[int] = None
    # cantidad_disponible se maneja internamente generalmente
    ubicacion_fisica: Optional[str] = None
    descripcion: Optional[str] = None
    imagen_portada: Optional[str] = None
    estado: Optional[str] = None
    autores_ids: Optional[List[int]] = None

class LibroAutorOut(BaseModel):
    autor: AutorOut
    orden: int

    class Config:
        from_attributes = True

class LibroOut(LibroBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # Relaciones simples para listas
    
    class Config:
        from_attributes = True

class LibroOutDetailed(LibroOut):
    genero: GeneroLiterarioOut
    editorial: EditorialOut
    libro_autores: List[LibroAutorOut] = []

# --- Préstamo ---
class PrestamoBase(BaseModel):
    libro_id: int
    usuario_id: int
    tipo_prestamo: Optional[str] = "PERSONAL"  # PERSONAL, ACADEMICO
    modulo_id: Optional[int] = None
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    observaciones: Optional[str] = None

class PrestamoCreate(PrestamoBase):
    pass

class PrestamoUpdate(BaseModel):
    estado: Optional[str] = None
    fecha_devolucion: Optional[date] = None
    observaciones: Optional[str] = None

class PrestamoOut(PrestamoBase):
    id: int
    fecha_devolucion: Optional[date] = None
    estado: str
    dias_retraso: int
    monto_multa: Decimal
    multa_pagada: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PrestamoOutDetailed(PrestamoOut):
    libro: LibroOut

# --- Multa Préstamo ---
class MultaPrestamoBase(BaseModel):
    prestamo_id: int
    dias_retraso: int
    monto_por_dia: Decimal = Decimal("1.00")
    monto_total: Decimal

class MultaPrestamoCreate(MultaPrestamoBase):
    pass

class MultaPrestamoUpdate(BaseModel):
    pagado: Optional[bool] = None
    fecha_pago: Optional[datetime] = None
    metodo_pago: Optional[str] = None
    observaciones: Optional[str] = None

class MultaPrestamoOut(MultaPrestamoBase):
    id: int
    fecha_calculo: datetime
    pagado: bool
    fecha_pago: Optional[datetime] = None
    metodo_pago: Optional[str] = None
    observaciones: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Reserva ---
class ReservaBase(BaseModel):
    libro_id: int
    usuario_id: int

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    estado: Optional[str] = None
    notificado: Optional[bool] = None
    fecha_notificacion: Optional[datetime] = None

class ReservaOut(ReservaBase):
    id: int
    fecha_reserva: datetime
    estado: str
    fecha_notificacion: Optional[datetime] = None
    fecha_expiracion: Optional[datetime] = None
    notificado: bool
    observaciones: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReservaOutDetailed(ReservaOut):
    libro: LibroOut

# --- Módulo Libro ---
class ModuloLibroBase(BaseModel):
    modulo_id: int
    libro_id: int
    orden: Optional[int] = 1
    obligatorio: Optional[bool] = True
    descripcion: Optional[str] = None

class ModuloLibroCreate(ModuloLibroBase):
    pass

class ModuloLibroUpdate(BaseModel):
    orden: Optional[int] = None
    obligatorio: Optional[bool] = None
    descripcion: Optional[str] = None

class ModuloLibroOut(ModuloLibroBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ModuloLibroDetailed(ModuloLibroOut):
    libro: LibroOut

# --- Calendar Views ---
class PrestamoCalendar(BaseModel):
    """Schema for calendar view of loans"""
    id: int
    libro_titulo: str
    usuario_nombre: str
    tipo_prestamo: str
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    fecha_devolucion: Optional[date] = None
    estado: str
    dias_retraso: int
    monto_multa: Decimal

    class Config:
        from_attributes = True
