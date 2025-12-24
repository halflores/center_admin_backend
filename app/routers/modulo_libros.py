from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.api.deps import get_db
from app.models.models import ModuloLibro, Modulo, Libro
from app.schemas.modulo_libro import (
    ModuloLibroCreate, 
    ModuloLibroUpdate, 
    ModuloLibroResponse
)

router = APIRouter(prefix="/modulos", tags=["modulo-libros"])


@router.get("/{modulo_id}/libros", response_model=List[ModuloLibroResponse])
async def get_libros_by_modulo(
    modulo_id: int,
    activo_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Obtener todos los libros asociados a un módulo.
    
    Args:
        modulo_id: ID del módulo
        activo_only: Si es True, solo devuelve asociaciones activas
    """
    # Verificar que el módulo existe
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
    
    # Construir query
    query = db.query(ModuloLibro).options(
        joinedload(ModuloLibro.libro),
        joinedload(ModuloLibro.modulo)
    ).filter(ModuloLibro.modulo_id == modulo_id)
    
    if activo_only:
        query = query.filter(ModuloLibro.activo == True)
    
    asociaciones = query.order_by(
        ModuloLibro.tipo_asignacion.desc(),  # obligatorio primero
        ModuloLibro.orden.asc()
    ).all()
    
    return asociaciones


@router.post("/{modulo_id}/libros", response_model=ModuloLibroResponse, status_code=status.HTTP_201_CREATED)
async def create_modulo_libro(
    modulo_id: int,
    data: ModuloLibroCreate,
    db: Session = Depends(get_db)
):
    """
    Asociar un libro a un módulo.
    
    Args:
        modulo_id: ID del módulo
        data: Datos de la asociación
    """
    # Verificar que el módulo existe
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
    
    # Verificar que el libro existe
    libro = db.query(Libro).filter(Libro.id == data.libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Verificar que no exista ya la asociación
    existing = db.query(ModuloLibro).filter(
        ModuloLibro.modulo_id == modulo_id,
        ModuloLibro.libro_id == data.libro_id
    ).first()
    
    if existing:
        if not existing.activo:
            # Reactivar registro existente
            existing.activo = data.activo
            existing.tipo_asignacion = data.tipo_asignacion
            existing.orden = data.orden
            existing.descripcion = data.descripcion
            existing.obligatorio = (data.tipo_asignacion == "obligatorio")
            
            db.commit()
            db.refresh(existing)
            db.refresh(existing, ['libro', 'modulo'])
            return existing

        raise HTTPException(
            status_code=400, 
            detail="Este libro ya está asociado al módulo"
        )
    
    # Crear asociación
    nueva_asociacion = ModuloLibro(
        modulo_id=modulo_id,
        libro_id=data.libro_id,
        tipo_asignacion=data.tipo_asignacion,
        activo=data.activo,
        orden=data.orden,
        descripcion=data.descripcion,
        # Mantener compatibilidad con campo obligatorio
        obligatorio=(data.tipo_asignacion == "obligatorio")
    )
    
    db.add(nueva_asociacion)
    db.commit()
    db.refresh(nueva_asociacion)
    
    # Cargar relaciones
    db.refresh(nueva_asociacion, ['libro', 'modulo'])
    
    return nueva_asociacion


@router.put("/{modulo_id}/libros/{libro_id}", response_model=ModuloLibroResponse)
async def update_modulo_libro(
    modulo_id: int,
    libro_id: int,
    data: ModuloLibroUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar asociación módulo-libro.
    
    Args:
        modulo_id: ID del módulo
        libro_id: ID del libro
        data: Datos a actualizar
    """
    asociacion = db.query(ModuloLibro).filter(
        ModuloLibro.modulo_id == modulo_id,
        ModuloLibro.libro_id == libro_id
    ).first()
    
    if not asociacion:
        raise HTTPException(status_code=404, detail="Asociación no encontrada")
    
    # Actualizar campos si se proporcionan
    if data.tipo_asignacion is not None:
        asociacion.tipo_asignacion = data.tipo_asignacion
        # Mantener sincronizado el campo obligatorio
        asociacion.obligatorio = (data.tipo_asignacion == "obligatorio")
    
    if data.activo is not None:
        asociacion.activo = data.activo
    
    if data.orden is not None:
        asociacion.orden = data.orden
    
    if data.descripcion is not None:
        asociacion.descripcion = data.descripcion
    
    db.commit()
    db.refresh(asociacion, ['libro', 'modulo'])
    
    return asociacion


@router.delete("/{modulo_id}/libros/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_modulo_libro(
    modulo_id: int,
    libro_id: int,
    soft_delete: bool = True,
    db: Session = Depends(get_db)
):
    """
    Eliminar asociación módulo-libro.
    
    Args:
        modulo_id: ID del módulo
        libro_id: ID del libro
        soft_delete: Si es True, solo marca como inactivo. Si es False, elimina el registro.
    """
    asociacion = db.query(ModuloLibro).filter(
        ModuloLibro.modulo_id == modulo_id,
        ModuloLibro.libro_id == libro_id
    ).first()
    
    if not asociacion:
        raise HTTPException(status_code=404, detail="Asociación no encontrada")
    
    if soft_delete:
        # Soft delete: marcar como inactivo
        asociacion.activo = False
        db.commit()
    else:
        # Hard delete: eliminar registro
        db.delete(asociacion)
        db.commit()
    
    return None


@router.get("", response_model=List[ModuloLibroResponse])
async def get_all_modulo_libros(
    activo_only: bool = True,
    tipo_asignacion: str = None,
    db: Session = Depends(get_db)
):
    """
    Obtener todas las asociaciones módulo-libro.
    
    Args:
        activo_only: Si es True, solo devuelve asociaciones activas
        tipo_asignacion: Filtrar por tipo ('obligatorio' o 'recomendado')
    """
    query = db.query(ModuloLibro).options(
        joinedload(ModuloLibro.libro),
        joinedload(ModuloLibro.modulo)
    )
    
    if activo_only:
        query = query.filter(ModuloLibro.activo == True)
    
    if tipo_asignacion:
        query = query.filter(ModuloLibro.tipo_asignacion == tipo_asignacion)
    
    asociaciones = query.order_by(
        ModuloLibro.modulo_id.asc(),
        ModuloLibro.tipo_asignacion.desc(),
        ModuloLibro.orden.asc()
    ).all()
    
    return asociaciones
