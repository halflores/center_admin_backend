from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime


class ModuloLibroBase(BaseModel):
    """Base schema for ModuloLibro"""
    modulo_id: int = Field(..., description="ID del módulo")
    libro_id: int = Field(..., description="ID del libro")
    tipo_asignacion: Literal["obligatorio", "recomendado"] = Field(
        default="recomendado", 
        description="Tipo de asignación: obligatorio o recomendado"
    )


class ModuloLibroCreate(ModuloLibroBase):
    """Schema for creating a new ModuloLibro association"""
    activo: bool = Field(default=True, description="Estado de la asociación")
    orden: int = Field(default=1, description="Orden de prioridad")
    descripcion: Optional[str] = Field(None, description="Descripción adicional")


class ModuloLibroUpdate(BaseModel):
    """Schema for updating an existing ModuloLibro association"""
    tipo_asignacion: Optional[Literal["obligatorio", "recomendado"]] = Field(
        None, 
        description="Tipo de asignación"
    )
    activo: Optional[bool] = Field(None, description="Estado de la asociación")
    orden: Optional[int] = Field(None, description="Orden de prioridad")
    descripcion: Optional[str] = Field(None, description="Descripción adicional")


class LibroSimple(BaseModel):
    """Simplified book schema for nested responses"""
    id: int
    titulo: str
    isbn: Optional[str] = None
    autor: Optional[str] = None
    editorial: Optional[str] = None
    
    class Config:
        from_attributes = True

    @validator('editorial', pre=True, check_fields=False)
    def extract_editorial_name(cls, v):
        if hasattr(v, 'nombre'):
            return v.nombre
        return str(v) if v else None

    @validator('autor', pre=True, check_fields=False)
    def extract_autor_names(cls, v, values):
        # Si 'autor' no viene directo, intentamos obtenerlo de libro_autores si existe en el objeto origen
        # Nota: 'v' aquí será el valor del atributo 'autor' si existe, o lo que pydantic decida.
        # En from_attributes=True, si el atributo no existe, pasa None.
        # Pero para computed fields necesitamos acceder al objeto original (root).
        # En Pydantic v1 es difícil acceder al root en validator de campo.
        # Sin embargo, si el modelo Libro no tiene atributo 'autor', v será None.
        return v
    
    @validator('autor', pre=True, always=True, check_fields=False)
    def extract_autor_from_orm(cls, v, values):
        # Esta estrategia es limitada en Pydantic v1 simple.
        # Vamos a asumir que autor devuelve None si no existe, y lo dejamos así por ahora
        # para no complicar con root_validator que cambia la estructura.
        # Si queremos autores, deberíamos agregar una property en el modelo Libro.
        return v


class ModuloSimple(BaseModel):
    """Simplified module schema for nested responses"""
    id: int
    nombre: str
    codigo: Optional[str] = None
    
    class Config:
        from_attributes = True


class ModuloLibroResponse(BaseModel):
    """Schema for ModuloLibro response with nested data"""
    id: int
    modulo_id: int
    libro_id: int
    tipo_asignacion: str
    activo: bool
    orden: int
    descripcion: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    libro: Optional[LibroSimple] = None
    modulo: Optional[ModuloSimple] = None
    
    class Config:
        from_attributes = True


class LibroSugerido(BaseModel):
    """Libro con información de sugerencia para el estudiante"""
    id: int
    titulo: str
    isbn: Optional[str] = None
    autor: Optional[str] = None
    editorial: Optional[str] = None
    disponible: bool
    copias_disponibles: int
    tipo_asignacion: str  # 'obligatorio' o 'recomendado'
    orden: int  # Para ordenar las sugerencias
    
    class Config:
        from_attributes = True
