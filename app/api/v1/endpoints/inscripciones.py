from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.inscripcion import InscripcionCreate, InscripcionUpdate, InscripcionResponse, InscripcionWithDetailsResponse
from app.services import inscripcion as inscripcion_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=InscripcionWithDetailsResponse)
def create_inscripcion(inscripcion: InscripcionCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return inscripcion_service.create_inscripcion(db=db, inscripcion=inscripcion)

@router.get("/", response_model=List[InscripcionWithDetailsResponse])
def read_inscripciones(
    skip: int = 0, 
    limit: int = 100, 
    estudiante_id: Optional[int] = None, 
    curso_id: Optional[int] = None, 
    gestion_id: Optional[int] = None,
    estado: Optional[str] = None, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(deps.get_current_user)
):
    return inscripcion_service.get_inscripciones(db, skip=skip, limit=limit, estudiante_id=estudiante_id, 
                                                  curso_id=curso_id, gestion_id=gestion_id, estado=estado)

@router.get("/{inscripcion_id}", response_model=InscripcionWithDetailsResponse)
def read_inscripcion(inscripcion_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_inscripcion = inscripcion_service.get_inscripcion(db, inscripcion_id=inscripcion_id)
    if db_inscripcion is None:
        raise HTTPException(status_code=404, detail="Inscripcion not found")
    return db_inscripcion

@router.put("/{inscripcion_id}", response_model=InscripcionWithDetailsResponse)
def update_inscripcion(inscripcion_id: int, inscripcion: InscripcionUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_inscripcion = inscripcion_service.update_inscripcion(db, inscripcion_id=inscripcion_id, inscripcion=inscripcion)
    if db_inscripcion is None:
        raise HTTPException(status_code=404, detail="Inscripcion not found")
    return db_inscripcion

@router.delete("/{inscripcion_id}", response_model=InscripcionResponse)
def delete_inscripcion(inscripcion_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_inscripcion = inscripcion_service.delete_inscripcion(db, inscripcion_id=inscripcion_id)
    if db_inscripcion is None:
        raise HTTPException(status_code=404, detail="Inscripcion not found")
    return db_inscripcion
