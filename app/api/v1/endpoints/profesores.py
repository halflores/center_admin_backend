from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.profesor import ProfesorCreate, ProfesorUpdate, ProfesorResponse, ProfesorWithCampusResponse
from app.services import profesor as profesor_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=ProfesorResponse)
def create_profesor(profesor: ProfesorCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return profesor_service.create_profesor(db=db, profesor=profesor)

@router.get("/", response_model=List[ProfesorWithCampusResponse])
def read_profesores(skip: int = 0, limit: int = 100, activo: Optional[bool] = None, campus_id: Optional[int] = None, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return profesor_service.get_profesores(db, skip=skip, limit=limit, activo=activo, campus_id=campus_id)

@router.get("/{profesor_id}", response_model=ProfesorWithCampusResponse)
def read_profesor(profesor_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_profesor = profesor_service.get_profesor(db, profesor_id=profesor_id)
    if db_profesor is None:
        raise HTTPException(status_code=404, detail="Profesor not found")
    return db_profesor

@router.put("/{profesor_id}", response_model=ProfesorWithCampusResponse)
def update_profesor(profesor_id: int, profesor: ProfesorUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_profesor = profesor_service.update_profesor(db, profesor_id=profesor_id, profesor=profesor)
    if db_profesor is None:
        raise HTTPException(status_code=404, detail="Profesor not found")
    return db_profesor

@router.delete("/{profesor_id}", response_model=ProfesorResponse)
def delete_profesor(profesor_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_profesor = profesor_service.delete_profesor(db, profesor_id=profesor_id)
    if db_profesor is None:
        raise HTTPException(status_code=404, detail="Profesor not found")
    return db_profesor
