from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.modulo import ModuloCreate, ModuloUpdate, ModuloResponse, ModuloWithNivelResponse
from app.services import modulo as modulo_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=ModuloResponse)
def create_modulo(modulo: ModuloCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return modulo_service.create_modulo(db=db, modulo=modulo)

@router.get("/", response_model=List[ModuloWithNivelResponse])
def read_modulos(skip: int = 0, limit: int = 100, nivel_id: Optional[int] = None, activo: Optional[bool] = None, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return modulo_service.get_modulos(db, skip=skip, limit=limit, nivel_id=nivel_id, activo=activo)

@router.get("/{modulo_id}", response_model=ModuloWithNivelResponse)
def read_modulo(modulo_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_modulo = modulo_service.get_modulo(db, modulo_id=modulo_id)
    if db_modulo is None:
        raise HTTPException(status_code=404, detail="Modulo not found")
    return db_modulo

@router.put("/{modulo_id}", response_model=ModuloResponse)
def update_modulo(modulo_id: int, modulo: ModuloUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_modulo = modulo_service.update_modulo(db, modulo_id=modulo_id, modulo=modulo)
    if db_modulo is None:
        raise HTTPException(status_code=404, detail="Modulo not found")
    return db_modulo

@router.delete("/{modulo_id}", response_model=ModuloResponse)
def delete_modulo(modulo_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_modulo = modulo_service.delete_modulo(db, modulo_id=modulo_id)
    if db_modulo is None:
        raise HTTPException(status_code=404, detail="Modulo not found")
    return db_modulo
