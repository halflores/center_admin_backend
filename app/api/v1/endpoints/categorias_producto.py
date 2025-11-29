from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.categoria_producto import CategoriaProductoCreate, CategoriaProductoUpdate, CategoriaProductoResponse
from app.services import categoria_producto as categoria_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=CategoriaProductoResponse)
def create_categoria(categoria: CategoriaProductoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("categorias_producto.create"))):
    db_categoria = categoria_service.get_categoria_by_name(db, name=categoria.nombre)
    if db_categoria:
        raise HTTPException(status_code=400, detail="Category already exists")
    return categoria_service.create_categoria(db=db, categoria=categoria)

@router.get("/", response_model=List[CategoriaProductoResponse])
def read_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("categorias_producto.read"))):
    categorias = categoria_service.get_categorias(db, skip=skip, limit=limit)
    return categorias

@router.get("/{categoria_id}", response_model=CategoriaProductoResponse)
def read_categoria(categoria_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("categorias_producto.read"))):
    db_categoria = categoria_service.get_categoria(db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_categoria

@router.put("/{categoria_id}", response_model=CategoriaProductoResponse)
def update_categoria(categoria_id: int, categoria: CategoriaProductoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("categorias_producto.update"))):
    db_categoria = categoria_service.update_categoria(db, categoria_id=categoria_id, categoria=categoria)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_categoria

@router.delete("/{categoria_id}", response_model=CategoriaProductoResponse)
def delete_categoria(categoria_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("categorias_producto.delete"))):
    db_categoria = categoria_service.delete_categoria(db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_categoria
