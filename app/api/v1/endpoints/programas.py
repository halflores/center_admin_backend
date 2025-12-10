from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.programa import ProgramaCreate, ProgramaUpdate, ProgramaResponse
from app.services import programa as programa_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=ProgramaResponse)
def create_programa(programa: ProgramaCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return programa_service.create_programa(db=db, programa=programa)

@router.get("/", response_model=List[ProgramaResponse])
def read_programas(skip: int = 0, limit: int = 100, activo: Optional[bool] = None, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return programa_service.get_programas(db, skip=skip, limit=limit, activo=activo)

@router.get("/{programa_id}", response_model=ProgramaResponse)
def read_programa(programa_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_programa = programa_service.get_programa(db, programa_id=programa_id)
    if db_programa is None:
        raise HTTPException(status_code=404, detail="Programa not found")
    return db_programa

@router.put("/{programa_id}", response_model=ProgramaResponse)
def update_programa(programa_id: int, programa: ProgramaUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_programa = programa_service.update_programa(db, programa_id=programa_id, programa=programa)
    if db_programa is None:
        raise HTTPException(status_code=404, detail="Programa not found")
    return db_programa

@router.delete("/{programa_id}", response_model=ProgramaResponse)
def delete_programa(programa_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_programa = programa_service.delete_programa(db, programa_id=programa_id)
    if db_programa is None:
        raise HTTPException(status_code=404, detail="Programa not found")
    return db_programa
