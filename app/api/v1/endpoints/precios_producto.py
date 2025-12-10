from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.precio_producto import PrecioProductoCreate, PrecioProductoUpdate, PrecioProductoResponse
from app.services import precio_producto as precio_producto_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=PrecioProductoResponse)
def create_precio_producto(precio_producto: PrecioProductoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_precio = precio_producto_service.get_precio_by_producto_and_lista(
        db, 
        producto_id=precio_producto.producto_id, 
        lista_precios_id=precio_producto.lista_precios_id
    )
    if db_precio:
        raise HTTPException(status_code=400, detail="El precio para este producto en esta lista de precios ya existe")
    return precio_producto_service.create_precio_producto(db=db, precio_producto=precio_producto)

@router.get("/", response_model=List[PrecioProductoResponse])
def read_precios_producto(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    precios = precio_producto_service.get_precios_producto(db, skip=skip, limit=limit)
    return precios

@router.get("/{precio_producto_id}", response_model=PrecioProductoResponse)
def read_precio_producto(precio_producto_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_precio = precio_producto_service.get_precio_producto(db, precio_producto_id=precio_producto_id)
    if db_precio is None:
        raise HTTPException(status_code=404, detail="Price not found")
    return db_precio

@router.put("/{precio_producto_id}", response_model=PrecioProductoResponse)
def update_precio_producto(precio_producto_id: int, precio_producto: PrecioProductoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_precio = precio_producto_service.update_precio_producto(db, precio_producto_id=precio_producto_id, precio_producto=precio_producto)
    if db_precio is None:
        raise HTTPException(status_code=404, detail="Price not found")
    return db_precio

@router.delete("/{precio_producto_id}", response_model=PrecioProductoResponse)
def delete_precio_producto(precio_producto_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_precio = precio_producto_service.delete_precio_producto(db, precio_producto_id=precio_producto_id)
    if db_precio is None:
        raise HTTPException(status_code=404, detail="Price not found")
    return db_precio
