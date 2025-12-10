from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import Aula
from app.schemas.aula import AulaCreate, AulaUpdate, AulaResponse

router = APIRouter()

@router.get("/", response_model=List[AulaResponse])
def read_aulas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_user),
):
    """
    Retrieve aulas.
    """
    aulas = db.query(Aula).offset(skip).limit(limit).all()
    return aulas

@router.post("/", response_model=AulaResponse)
def create_aula(
    *,
    db: Session = Depends(deps.get_db),
    aula_in: AulaCreate,
    current_user: Any = Depends(deps.get_current_user),
):
    """
    Create new aula.
    """
    if db.query(Aula).filter(Aula.nombre == aula_in.nombre).first():
        raise HTTPException(status_code=400, detail="El aula ya existe")
        
    aula = Aula(
        nombre=aula_in.nombre,
        capacidad=aula_in.capacidad,
        ubicacion=aula_in.ubicacion
    )
    db.add(aula)
    db.commit()
    db.refresh(aula)
    return aula

@router.put("/{id}", response_model=AulaResponse)
def update_aula(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    aula_in: AulaUpdate,
    current_user: Any = Depends(deps.get_current_user),
):
    """
    Update an aula.
    """
    aula = db.query(Aula).filter(Aula.id == id).first()
    if not aula:
        raise HTTPException(status_code=404, detail="Aula no encontrada")
        
    if aula_in.nombre != aula.nombre:
        if db.query(Aula).filter(Aula.nombre == aula_in.nombre).first():
            raise HTTPException(status_code=400, detail="El nombre del aula ya existe")

    aula_data = aula_in.model_dump(exclude_unset=True)
    for field, value in aula_data.items():
        setattr(aula, field, value)

    db.commit()
    db.refresh(aula)
    return aula

@router.delete("/{id}", response_model=AulaResponse)
def delete_aula(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: Any = Depends(deps.get_current_user),
):
    """
    Delete an aula.
    """
    aula = db.query(Aula).filter(Aula.id == id).first()
    if not aula:
        raise HTTPException(status_code=404, detail="Aula no encontrada")
        
    db.delete(aula)
    db.commit()
    return aula
