from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.movimiento_inventario import MovimientoInventarioResponse
from app.services import movimientos as movimiento_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.get("/", response_model=List[MovimientoInventarioResponse])
def read_movimientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return movimiento_service.get_movimientos(db, skip=skip, limit=limit)
