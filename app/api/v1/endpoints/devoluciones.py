from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.devolucion import DevolucionCreate, DevolucionResponse
from app.services import devoluciones as devolucion_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.get("/", response_model=List[DevolucionResponse])
def get_devoluciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tipo: Optional[str] = Query(None, regex="^(PROVEEDOR|ESTUDIANTE)$"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Get list of devoluciones with optional tipo filter"""
    return devolucion_service.get_devoluciones(db=db, skip=skip, limit=limit, tipo=tipo)

@router.get("/{devolucion_id}", response_model=DevolucionResponse)
def get_devolucion(
    devolucion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Get a specific devolucion by ID"""
    devolucion = devolucion_service.get_devolucion_by_id(db=db, devolucion_id=devolucion_id)
    if not devolucion:
        raise HTTPException(status_code=404, detail="Devolucion not found")
    return devolucion

@router.post("/", response_model=DevolucionResponse)
def create_devolucion(devolucion: DevolucionCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    try:
        return devolucion_service.create_devolucion(db=db, devolucion=devolucion, usuario_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
