from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.carrito_compras import CarritoItemCreate, CarritoItemUpdate, CarritoItemResponse
from app.services import carrito as carrito_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.get("/", response_model=List[CarritoItemResponse])
def read_cart(db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return carrito_service.get_cart(db, usuario_id=current_user.id)

@router.post("/", response_model=CarritoItemResponse)
def add_to_cart(item: CarritoItemCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return carrito_service.add_to_cart(db=db, item=item, usuario_id=current_user.id)

@router.put("/{item_id}", response_model=CarritoItemResponse)
def update_cart_item(item_id: int, item: CarritoItemUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_item = carrito_service.update_cart_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return db_item

@router.delete("/{item_id}", response_model=CarritoItemResponse)
def remove_from_cart(item_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_item = carrito_service.remove_from_cart(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return db_item

@router.delete("/")
def clear_cart(db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    carrito_service.clear_cart(db, usuario_id=current_user.id)
    return {"message": "Cart cleared"}
