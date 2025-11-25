from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse
from app.services import estudiante as estudiante_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=EstudianteResponse)
def create_estudiante(estudiante: EstudianteCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return estudiante_service.create_estudiante(db=db, estudiante=estudiante, usuario_id=current_user.id)

@router.get("/", response_model=List[EstudianteResponse])
def read_estudiantes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return estudiante_service.get_estudiantes(db, skip=skip, limit=limit)

@router.get("/{estudiante_id}", response_model=EstudianteResponse)
def read_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_estudiante = estudiante_service.get_estudiante(db, estudiante_id=estudiante_id)
    if db_estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return db_estudiante

@router.put("/{estudiante_id}", response_model=EstudianteResponse)
def update_estudiante(estudiante_id: int, estudiante: EstudianteUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_estudiante = estudiante_service.update_estudiante(db, estudiante_id=estudiante_id, estudiante=estudiante)
    if db_estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return db_estudiante

@router.delete("/{estudiante_id}", response_model=EstudianteResponse)
def delete_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_estudiante = estudiante_service.delete_estudiante(db, estudiante_id=estudiante_id)
    if db_estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return db_estudiante
