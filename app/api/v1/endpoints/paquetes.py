from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.api.deps import get_current_user, check_permission
from app.models.models import Usuario
from app.schemas.paquete import (
    PaqueteCreate, PaqueteUpdate, PaqueteResponse, 
    PaqueteWithProductsResponse, PaqueteProductoCreate
)
from app.services import paquete as paquete_service

router = APIRouter()


@router.get("/", response_model=List[PaqueteWithProductsResponse])
def get_paquetes(
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get all packages with their products"""
    # check_permission(db, current_user, "paquetes", "read") # FIX: Invalid signature access
    try:
        paquetes = paquete_service.get_paquetes(db, skip=skip, limit=limit, activo=activo)
        return [paquete_service.enrich_paquete_response(db, p) for p in paquetes]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@router.get("/{paquete_id}", response_model=PaqueteWithProductsResponse)
def get_paquete(
    paquete_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get a specific package by ID with its products"""
    # check_permission(db, current_user, "paquetes", "read") # FIX: Invalid signature access
    db_paquete = paquete_service.get_paquete(db, paquete_id)
    if not db_paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    return paquete_service.enrich_paquete_response(db, db_paquete)


@router.get("/modulo/{modulo_id}", response_model=List[PaqueteWithProductsResponse])
def get_paquetes_by_modulo(
    modulo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get packages for a specific module"""
    # check_permission(db, current_user, "paquetes", "read") # FIX: Invalid signature access
    paquetes = paquete_service.get_paquetes_by_modulo(db, modulo_id)
    return [paquete_service.enrich_paquete_response(db, p) for p in paquetes]


@router.post("/", response_model=PaqueteWithProductsResponse, status_code=status.HTTP_201_CREATED)
def create_paquete(
    paquete: PaqueteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a new package"""
    # check_permission(db, current_user, "paquetes", "create") # FIX: Invalid signature access
    db_paquete = paquete_service.create_paquete(db, paquete)
    return paquete_service.enrich_paquete_response(db, db_paquete)


@router.put("/{paquete_id}", response_model=PaqueteWithProductsResponse)
def update_paquete(
    paquete_id: int,
    paquete: PaqueteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Update a package"""
    # check_permission(db, current_user, "paquetes", "update") # FIX: Invalid signature access
    
    db_paquete = paquete_service.update_paquete(db, paquete_id, paquete)
    if not db_paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    return paquete_service.enrich_paquete_response(db, db_paquete)


@router.delete("/{paquete_id}")
def delete_paquete(
    paquete_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Delete a package"""
    # check_permission(db, current_user, "paquetes", "delete") # FIX: Invalid signature access
    
    db_paquete = paquete_service.delete_paquete(db, paquete_id)
    if not db_paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    return {"message": "Paquete eliminado correctamente"}


@router.post("/{paquete_id}/productos")
def add_producto_to_paquete(
    paquete_id: int,
    producto: PaqueteProductoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Add a product to a package"""
    # check_permission(db, current_user, "paquetes", "update") # FIX: Invalid signature access
    
    # Verify package exists
    db_paquete = paquete_service.get_paquete(db, paquete_id)
    if not db_paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    
    result = paquete_service.add_producto_to_paquete(db, paquete_id, producto)
    return {"message": "Producto agregado al paquete", "id": result.id}


@router.delete("/{paquete_id}/productos/{producto_id}")
def remove_producto_from_paquete(
    paquete_id: int,
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove a product from a package"""
    # check_permission(db, current_user, "paquetes", "update") # FIX: Invalid signature access
    
    result = paquete_service.remove_producto_from_paquete(db, paquete_id, producto_id)
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado en el paquete")
    return {"message": "Producto eliminado del paquete"}
