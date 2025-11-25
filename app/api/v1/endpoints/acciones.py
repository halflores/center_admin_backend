from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.accion import AccionCreate, AccionUpdate, AccionResponse
from app.services import accion as accion_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=AccionResponse)
def create_accion(
    accion: AccionCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_accion = accion_service.get_accion_by_name(db, name=accion.nombre)
    if db_accion:
        raise HTTPException(status_code=400, detail="Action already exists")
    return accion_service.create_accion(db=db, accion=accion)

@router.get("/", response_model=List[AccionResponse])
def read_acciones(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    acciones = accion_service.get_acciones(db, skip=skip, limit=limit)
    return acciones

@router.get("/{accion_id}", response_model=AccionResponse)
def read_accion(
    accion_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_accion = accion_service.get_accion(db, accion_id=accion_id)
    if db_accion is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return db_accion

@router.put("/{accion_id}", response_model=AccionResponse)
def update_accion(
    accion_id: int, 
    accion: AccionUpdate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_accion = accion_service.update_accion(db, accion_id=accion_id, accion_update=accion)
    if db_accion is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return db_accion

@router.delete("/{accion_id}", response_model=AccionResponse)
def delete_accion(
    accion_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_accion = accion_service.delete_accion(db, accion_id=accion_id)
    if db_accion is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return db_accion
