from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.pago_profesor import PagoProfesorCreate, PagoProfesorUpdate, PagoProfesorResponse, PagoProfesorWithDetailsResponse
from app.services import pago_profesor as pago_profesor_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=PagoProfesorWithDetailsResponse)
def create_pago_profesor(pago: PagoProfesorCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return pago_profesor_service.create_pago_profesor(db=db, pago=pago, usuario_id=current_user.id)

@router.get("/", response_model=List[PagoProfesorWithDetailsResponse])
def read_pagos_profesor(
    skip: int = 0, 
    limit: int = 100, 
    profesor_id: Optional[int] = None, 
    gestion_id: Optional[int] = None,
    estado: Optional[str] = None, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(deps.get_current_user)
):
    return pago_profesor_service.get_pagos_profesor(db, skip=skip, limit=limit, profesor_id=profesor_id, 
                                                     gestion_id=gestion_id, estado=estado)

@router.get("/{pago_id}", response_model=PagoProfesorWithDetailsResponse)
def read_pago_profesor(pago_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_pago = pago_profesor_service.get_pago_profesor(db, pago_id=pago_id)
    if db_pago is None:
        raise HTTPException(status_code=404, detail="Pago not found")
    return db_pago

@router.put("/{pago_id}", response_model=PagoProfesorWithDetailsResponse)
def update_pago_profesor(pago_id: int, pago: PagoProfesorUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_pago = pago_profesor_service.update_pago_profesor(db, pago_id=pago_id, pago=pago)
    if db_pago is None:
        raise HTTPException(status_code=404, detail="Pago not found")
    return db_pago

@router.delete("/{pago_id}", response_model=PagoProfesorResponse)
def delete_pago_profesor(pago_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_pago = pago_profesor_service.delete_pago_profesor(db, pago_id=pago_id)
    if db_pago is None:
        raise HTTPException(status_code=404, detail="Pago not found")
    return db_pago
