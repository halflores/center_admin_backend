from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.models.models import Cargo
from app.schemas.cargo import CargoCreate, CargoUpdate, CargoResponse

router = APIRouter()

@router.get("/", response_model=List[CargoResponse])
def read_cargos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cargos = db.query(Cargo).offset(skip).limit(limit).all()
    return cargos

@router.post("/", response_model=CargoResponse)
def create_cargo(cargo: CargoCreate, db: Session = Depends(get_db)):
    db_cargo = db.query(Cargo).filter(Cargo.nombre == cargo.nombre).first()
    if db_cargo:
        raise HTTPException(status_code=400, detail="Cargo already exists")
    
    nuevo_cargo = Cargo(**cargo.dict())
    db.add(nuevo_cargo)
    db.commit()
    db.refresh(nuevo_cargo)
    return nuevo_cargo

@router.get("/{cargo_id}", response_model=CargoResponse)
def read_cargo(cargo_id: int, db: Session = Depends(get_db)):
    db_cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if db_cargo is None:
        raise HTTPException(status_code=404, detail="Cargo not found")
    return db_cargo

@router.put("/{cargo_id}", response_model=CargoResponse)
def update_cargo(cargo_id: int, cargo: CargoUpdate, db: Session = Depends(get_db)):
    db_cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if db_cargo is None:
        raise HTTPException(status_code=404, detail="Cargo not found")
    
    update_data = cargo.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cargo, key, value)
    
    db.commit()
    db.refresh(db_cargo)
    return db_cargo

@router.delete("/{cargo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cargo(cargo_id: int, db: Session = Depends(get_db)):
    db_cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if db_cargo is None:
        raise HTTPException(status_code=404, detail="Cargo not found")
    
    db.delete(db_cargo)
    db.commit()
    return None
