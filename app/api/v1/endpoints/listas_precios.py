from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.lista_precio import ListaPrecioCreate, ListaPrecioUpdate, ListaPrecioResponse
from app.services import lista_precio as lista_precio_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=ListaPrecioResponse)
def create_lista_precio(lista_precio: ListaPrecioCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_lista_precio = lista_precio_service.get_lista_precio_by_name(db, name=lista_precio.nombre)
    if db_lista_precio:
        raise HTTPException(status_code=400, detail="Price list already exists")
    return lista_precio_service.create_lista_precio(db=db, lista_precio=lista_precio)

@router.get("/", response_model=List[ListaPrecioResponse])
def read_listas_precios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    listas_precios = lista_precio_service.get_listas_precios(db, skip=skip, limit=limit)
    return listas_precios

@router.get("/{lista_precio_id}", response_model=ListaPrecioResponse)
def read_lista_precio(lista_precio_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_lista_precio = lista_precio_service.get_lista_precio(db, lista_precio_id=lista_precio_id)
    if db_lista_precio is None:
        raise HTTPException(status_code=404, detail="Price list not found")
    return db_lista_precio

@router.put("/{lista_precio_id}", response_model=ListaPrecioResponse)
def update_lista_precio(lista_precio_id: int, lista_precio: ListaPrecioUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_lista_precio = lista_precio_service.update_lista_precio(db, lista_precio_id=lista_precio_id, lista_precio=lista_precio)
    if db_lista_precio is None:
        raise HTTPException(status_code=404, detail="Price list not found")
    return db_lista_precio

@router.delete("/{lista_precio_id}", response_model=ListaPrecioResponse)
def delete_lista_precio(lista_precio_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_lista_precio = lista_precio_service.delete_lista_precio(db, lista_precio_id=lista_precio_id)
    if db_lista_precio is None:
        raise HTTPException(status_code=404, detail="Price list not found")
    return db_lista_precio
