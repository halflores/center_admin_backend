from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, check_permission
from app.models.models import Usuario
from app.schemas.tipo_producto import TipoProductoCreate, TipoProductoUpdate, TipoProductoResponse
from app.services import tipo_producto as tipo_producto_service

router = APIRouter()


@router.get("/", response_model=List[TipoProductoResponse])
def get_tipos_producto(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("tipos_producto.read"))
):
    """Get all product types"""
    return tipo_producto_service.get_tipos_producto(db, skip=skip, limit=limit)


@router.get("/{tipo_producto_id}", response_model=TipoProductoResponse)
def get_tipo_producto(
    tipo_producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("tipos_producto.read"))
):
    """Get a specific product type by ID"""
    db_tipo = tipo_producto_service.get_tipo_producto(db, tipo_producto_id)
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo de producto no encontrado")
    return db_tipo


@router.post("/", response_model=TipoProductoResponse, status_code=status.HTTP_201_CREATED)
def create_tipo_producto(
    tipo_producto: TipoProductoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("tipos_producto.create"))
):
    """Create a new product type"""
    # Check if name already exists
    existing = tipo_producto_service.get_tipo_producto_by_nombre(db, tipo_producto.nombre)
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un tipo de producto con ese nombre")
    
    return tipo_producto_service.create_tipo_producto(db, tipo_producto)


@router.put("/{tipo_producto_id}", response_model=TipoProductoResponse)
def update_tipo_producto(
    tipo_producto_id: int,
    tipo_producto: TipoProductoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("tipos_producto.update"))
):
    """Update a product type"""
    db_tipo = tipo_producto_service.update_tipo_producto(db, tipo_producto_id, tipo_producto)
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo de producto no encontrado")
    return db_tipo


@router.delete("/{tipo_producto_id}")
def delete_tipo_producto(
    tipo_producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("tipos_producto.delete"))
):
    """Delete a product type"""
    db_tipo = tipo_producto_service.delete_tipo_producto(db, tipo_producto_id)
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo de producto no encontrado")
    return {"message": "Tipo de producto eliminado correctamente"}
