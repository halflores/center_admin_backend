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
def read_movimientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("movimientos.read"))):
    return movimiento_service.get_movimientos(db, skip=skip, limit=limit)

@router.post("/{id}/anular", response_model=MovimientoInventarioResponse)
def anular_movimiento(id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.check_permission("movimientos.create"))): # Using create permission for now, or could be a specific 'anular' permission
    return movimiento_service.anular_movimiento(db, movimiento_id=id, usuario_id=current_user.id)
