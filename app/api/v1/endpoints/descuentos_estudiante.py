from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.descuento_estudiante import DescuentoEstudianteCreate, DescuentoEstudianteUpdate, DescuentoEstudianteResponse
from app.services import descuento_estudiante as descuento_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=DescuentoEstudianteResponse)
def create_descuento(descuento: DescuentoEstudianteCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_descuento = descuento_service.get_descuento_by_student_and_product(
        db, 
        estudiante_id=descuento.estudiante_id, 
        producto_id=descuento.producto_id
    )
    if db_descuento:
        raise HTTPException(status_code=400, detail="Discount for this student and product already exists")
    return descuento_service.create_descuento(db=db, descuento=descuento)

@router.get("/", response_model=List[DescuentoEstudianteResponse])
def read_descuentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    descuentos = descuento_service.get_descuentos(db, skip=skip, limit=limit)
    return descuentos

@router.get("/{descuento_id}", response_model=DescuentoEstudianteResponse)
def read_descuento(descuento_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_descuento = descuento_service.get_descuento(db, descuento_id=descuento_id)
    if db_descuento is None:
        raise HTTPException(status_code=404, detail="Discount not found")
    return db_descuento

@router.put("/{descuento_id}", response_model=DescuentoEstudianteResponse)
def update_descuento(descuento_id: int, descuento: DescuentoEstudianteUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_descuento = descuento_service.update_descuento(db, descuento_id=descuento_id, descuento=descuento)
    if db_descuento is None:
        raise HTTPException(status_code=404, detail="Discount not found")
    return db_descuento

@router.delete("/{descuento_id}", response_model=DescuentoEstudianteResponse)
def delete_descuento(descuento_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_descuento = descuento_service.delete_descuento(db, descuento_id=descuento_id)
    if db_descuento is None:
        raise HTTPException(status_code=404, detail="Discount not found")
    return db_descuento
