from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.curso import CursoCreate, CursoUpdate, CursoResponse, CursoWithDetailsResponse
from app.services import curso as curso_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=CursoWithDetailsResponse)
def create_curso(curso: CursoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return curso_service.create_curso(db=db, curso=curso)

@router.get("/", response_model=List[CursoWithDetailsResponse])
def read_cursos(
    skip: int = 0, 
    limit: int = 100, 
    modulo_id: Optional[int] = None, 
    profesor_id: Optional[int] = None, 
    campus_id: Optional[int] = None, 
    estado: Optional[str] = None, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(deps.get_current_user)
):
    return curso_service.get_cursos(db, skip=skip, limit=limit, modulo_id=modulo_id, 
                                     profesor_id=profesor_id, campus_id=campus_id, estado=estado)

@router.get("/{curso_id}", response_model=CursoWithDetailsResponse)
def read_curso(curso_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_curso = curso_service.get_curso(db, curso_id=curso_id)
    if db_curso is None:
        raise HTTPException(status_code=404, detail="Curso not found")
    return db_curso

@router.put("/{curso_id}", response_model=CursoWithDetailsResponse)
def update_curso(curso_id: int, curso: CursoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_curso = curso_service.update_curso(db, curso_id=curso_id, curso=curso)
    if db_curso is None:
        raise HTTPException(status_code=404, detail="Curso not found")
    return db_curso

@router.delete("/{curso_id}", response_model=CursoResponse)
def delete_curso(curso_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_curso = curso_service.delete_curso(db, curso_id=curso_id)
    if db_curso is None:
        raise HTTPException(status_code=404, detail="Curso not found")
    return db_curso
