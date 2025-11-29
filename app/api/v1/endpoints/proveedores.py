from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse
from app.services import proveedor_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=ProveedorResponse)
def create_proveedor(
    proveedor: ProveedorCreate, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(deps.get_current_user)
):
    return proveedor_service.create_proveedor(db=db, proveedor=proveedor)

@router.get("/", response_model=List[ProveedorResponse])
def read_proveedores(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(deps.get_current_user)
):
    return proveedor_service.get_proveedores(db, skip=skip, limit=limit)

@router.get("/{proveedor_id}", response_model=ProveedorResponse)
def read_proveedor(
    proveedor_id: int, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_proveedor = proveedor_service.get_proveedor(db, proveedor_id=proveedor_id)
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return db_proveedor

@router.put("/{proveedor_id}", response_model=ProveedorResponse)
def update_proveedor(
    proveedor_id: int, 
    proveedor: ProveedorUpdate, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_proveedor = proveedor_service.update_proveedor(db, proveedor_id=proveedor_id, proveedor=proveedor)
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return db_proveedor

@router.delete("/{proveedor_id}", response_model=ProveedorResponse)
def delete_proveedor(
    proveedor_id: int, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_proveedor = proveedor_service.delete_proveedor(db, proveedor_id=proveedor_id)
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return db_proveedor
