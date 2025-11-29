from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.venta import VentaCreate, VentaResponse
from app.services import ventas as venta_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=VentaResponse)
def create_venta(venta: VentaCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    try:
        return venta_service.create_venta(db=db, venta=venta, usuario_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[VentaResponse])
def read_ventas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return venta_service.get_ventas(db, skip=skip, limit=limit)

@router.get("/{venta_id}", response_model=VentaResponse)
def read_venta(venta_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_venta = venta_service.get_venta(db, venta_id=venta_id)
    if db_venta is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return db_venta
