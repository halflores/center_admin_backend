from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.nivel_academico_estudiante import (
    NivelAcademicoEstudianteCreate, 
    NivelAcademicoEstudianteUpdate, 
    NivelAcademicoEstudianteWithDetailsResponse
)
from app.services import nivel_academico_estudiante as nivel_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()


@router.post("/", response_model=NivelAcademicoEstudianteWithDetailsResponse)
def create_nivel_academico(
    nivel: NivelAcademicoEstudianteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    return nivel_service.create_nivel_academico(db=db, nivel=nivel)


@router.get("/", response_model=List[NivelAcademicoEstudianteWithDetailsResponse])
def read_niveles_academicos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    return nivel_service.get_niveles_academicos(db, skip=skip, limit=limit)


@router.get("/estudiante/{estudiante_id}", response_model=List[NivelAcademicoEstudianteWithDetailsResponse])
def read_niveles_by_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    return nivel_service.get_niveles_academicos_by_estudiante(db, estudiante_id=estudiante_id)


@router.get("/{nivel_id}", response_model=NivelAcademicoEstudianteWithDetailsResponse)
def read_nivel_academico(
    nivel_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_nivel = nivel_service.get_nivel_academico(db, nivel_id=nivel_id)
    if db_nivel is None:
        raise HTTPException(status_code=404, detail="Nivel académico no encontrado")
    return db_nivel


@router.put("/{nivel_id}", response_model=NivelAcademicoEstudianteWithDetailsResponse)
def update_nivel_academico(
    nivel_id: int,
    nivel: NivelAcademicoEstudianteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_nivel = nivel_service.update_nivel_academico(db, nivel_id=nivel_id, nivel=nivel)
    if db_nivel is None:
        raise HTTPException(status_code=404, detail="Nivel académico no encontrado")
    return db_nivel


@router.delete("/{nivel_id}", response_model=NivelAcademicoEstudianteWithDetailsResponse)
def delete_nivel_academico(
    nivel_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_nivel = nivel_service.delete_nivel_academico(db, nivel_id=nivel_id)
    if db_nivel is None:
        raise HTTPException(status_code=404, detail="Nivel académico no encontrado")
    return db_nivel
