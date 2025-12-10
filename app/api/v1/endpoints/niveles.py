from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.nivel import NivelCreate, NivelUpdate, NivelResponse, NivelWithProgramaResponse
from app.services import nivel as nivel_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=NivelResponse)
def create_nivel(nivel: NivelCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return nivel_service.create_nivel(db=db, nivel=nivel)

@router.get("/", response_model=List[NivelWithProgramaResponse])
def read_niveles(skip: int = 0, limit: int = 100, programa_id: Optional[int] = None, activo: Optional[bool] = None, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return nivel_service.get_niveles(db, skip=skip, limit=limit, programa_id=programa_id, activo=activo)

@router.get("/{nivel_id}", response_model=NivelWithProgramaResponse)
def read_nivel(nivel_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_nivel = nivel_service.get_nivel(db, nivel_id=nivel_id)
    if db_nivel is None:
        raise HTTPException(status_code=404, detail="Nivel not found")
    return db_nivel

@router.put("/{nivel_id}", response_model=NivelResponse)
def update_nivel(nivel_id: int, nivel: NivelUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_nivel = nivel_service.update_nivel(db, nivel_id=nivel_id, nivel=nivel)
    if db_nivel is None:
        raise HTTPException(status_code=404, detail="Nivel not found")
    return db_nivel

@router.delete("/{nivel_id}", response_model=NivelResponse)
def delete_nivel(nivel_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_nivel = nivel_service.delete_nivel(db, nivel_id=nivel_id)
    if db_nivel is None:
        raise HTTPException(status_code=404, detail="Nivel not found")
    return db_nivel
