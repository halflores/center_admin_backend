from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.gestion import GestionCreate, GestionUpdate, GestionResponse
from app.services import gestion as gestion_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=GestionResponse)
def create_gestion(gestion: GestionCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return gestion_service.create_gestion(db=db, gestion=gestion)

@router.get("/", response_model=List[GestionResponse])
def read_gestiones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return gestion_service.get_gestiones(db, skip=skip, limit=limit)

@router.get("/{gestion_id}", response_model=GestionResponse)
def read_gestion(gestion_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_gestion = gestion_service.get_gestion(db, gestion_id=gestion_id)
    if db_gestion is None:
        raise HTTPException(status_code=404, detail="Gestion not found")
    return db_gestion

@router.put("/{gestion_id}", response_model=GestionResponse)
def update_gestion(gestion_id: int, gestion: GestionUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_gestion = gestion_service.update_gestion(db, gestion_id=gestion_id, gestion=gestion)
    if db_gestion is None:
        raise HTTPException(status_code=404, detail="Gestion not found")
    return db_gestion

@router.delete("/{gestion_id}", response_model=GestionResponse)
def delete_gestion(gestion_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_gestion = gestion_service.delete_gestion(db, gestion_id=gestion_id)
    if db_gestion is None:
        raise HTTPException(status_code=404, detail="Gestion not found")
    return db_gestion
