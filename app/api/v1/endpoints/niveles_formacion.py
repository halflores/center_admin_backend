from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import NivelFormacion
from app.schemas.nivel_formacion import NivelFormacionCreate, NivelFormacionUpdate, NivelFormacionResponse

router = APIRouter()

@router.get("/", response_model=List[NivelFormacionResponse])
def read_niveles_formacion(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_user),
):
    """
    Retrieve niveles de formación.
    """
    niveles = db.query(NivelFormacion).offset(skip).limit(limit).all()
    return niveles

@router.post("/", response_model=NivelFormacionResponse)
def create_nivel_formacion(
    *,
    db: Session = Depends(deps.get_db),
    nivel_in: NivelFormacionCreate,
    current_user: Any = Depends(deps.get_current_user),
):
    """
    Create new nivel de formación.
    """
    # Check if name already exists
    if db.query(NivelFormacion).filter(NivelFormacion.nombre == nivel_in.nombre).first():
        raise HTTPException(status_code=400, detail="El nivel de formación ya existe")
        
    nivel = NivelFormacion(nombre=nivel_in.nombre)
    db.add(nivel)
    db.commit()
    db.refresh(nivel)
    return nivel

@router.put("/{id}", response_model=NivelFormacionResponse)
def update_nivel_formacion(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    nivel_in: NivelFormacionUpdate,
    current_user: Any = Depends(deps.get_current_user),
):
    """
    Update a nivel de formación.
    """
    nivel = db.query(NivelFormacion).filter(NivelFormacion.id == id).first()
    if not nivel:
        raise HTTPException(status_code=404, detail="Nivel de formación no encontrado")
        
    # Check if name already exists (if changed)
    if nivel_in.nombre != nivel.nombre:
        if db.query(NivelFormacion).filter(NivelFormacion.nombre == nivel_in.nombre).first():
            raise HTTPException(status_code=400, detail="El nombre del nivel de formación ya existe")

    nivel.nombre = nivel_in.nombre
    db.commit()
    db.refresh(nivel)
    return nivel

@router.delete("/{id}", response_model=NivelFormacionResponse)
def delete_nivel_formacion(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: Any = Depends(deps.get_current_user),
):
    """
    Delete a nivel de formación.
    """
    nivel = db.query(NivelFormacion).filter(NivelFormacion.id == id).first()
    if not nivel:
        raise HTTPException(status_code=404, detail="Nivel de formación no encontrado")
        
    db.delete(nivel)
    db.commit()
    return nivel
