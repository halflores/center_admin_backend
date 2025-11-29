from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse
from app.services import producto as producto_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=ProductoResponse)
def create_producto(producto: ProductoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("productos.create"))):
    if producto.codigo:
        db_producto = producto_service.get_producto_by_codigo(db, codigo=producto.codigo)
        if db_producto:
            raise HTTPException(status_code=400, detail="Product with this code already exists")
    return producto_service.create_producto(db=db, producto=producto)

@router.get("/", response_model=List[ProductoResponse])
def read_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("productos.read"))):
    productos = producto_service.get_productos(db, skip=skip, limit=limit)
    return productos

@router.get("/{producto_id}", response_model=ProductoResponse)
def read_producto(producto_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("productos.read"))):
    db_producto = producto_service.get_producto(db, producto_id=producto_id)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_producto

@router.put("/{producto_id}", response_model=ProductoResponse)
def update_producto(producto_id: int, producto: ProductoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("productos.update"))):
    if producto.codigo:
         existing_prod = producto_service.get_producto_by_codigo(db, codigo=producto.codigo)
         if existing_prod and existing_prod.id != producto_id:
             raise HTTPException(status_code=400, detail="Product with this code already exists")

    db_producto = producto_service.update_producto(db, producto_id=producto_id, producto=producto)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_producto

@router.delete("/{producto_id}", response_model=ProductoResponse)
def delete_producto(producto_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("productos.delete"))):
    db_producto = producto_service.delete_producto(db, producto_id=producto_id)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_producto
