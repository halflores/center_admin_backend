from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.horario import HorarioCreate, HorarioUpdate, HorarioResponse, HorarioWithAulaResponse
from app.services import horario as horario_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=HorarioResponse)
def create_horario(horario: HorarioCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return horario_service.create_horario(db=db, horario=horario)

@router.get("/", response_model=List[HorarioWithAulaResponse])
def read_horarios(skip: int = 0, limit: int = 100, curso_id: Optional[int] = None, campus_id: Optional[int] = None, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return horario_service.get_horarios(db, skip=skip, limit=limit, curso_id=curso_id, campus_id=campus_id)

@router.get("/{horario_id}", response_model=HorarioWithAulaResponse)
def read_horario(horario_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_horario = horario_service.get_horario(db, horario_id=horario_id)
    if db_horario is None:
        raise HTTPException(status_code=404, detail="Horario not found")
    return db_horario

@router.put("/{horario_id}", response_model=HorarioWithAulaResponse)
def update_horario(horario_id: int, horario: HorarioUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_horario = horario_service.update_horario(db, horario_id=horario_id, horario=horario)
    if db_horario is None:
        raise HTTPException(status_code=404, detail="Horario not found")
    return db_horario

@router.delete("/{horario_id}", response_model=HorarioResponse)
def delete_horario(horario_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_horario = horario_service.delete_horario(db, horario_id=horario_id)
    if db_horario is None:
        raise HTTPException(status_code=404, detail="Horario not found")
    return db_horario
