from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.models import Funcion
from app.schemas.funcion import FuncionCreate, FuncionUpdate

def get_funcion(db: Session, funcion_id: int) -> Optional[Funcion]:
    return db.query(Funcion).filter(Funcion.id == funcion_id).first()

def get_funcion_by_name(db: Session, name: str) -> Optional[Funcion]:
    return db.query(Funcion).filter(Funcion.nombre == name).first()

def get_funciones(db: Session, skip: int = 0, limit: int = 100) -> List[Funcion]:
    return db.query(Funcion).offset(skip).limit(limit).all()

def create_funcion(db: Session, funcion: FuncionCreate) -> Funcion:
    db_funcion = Funcion(
        nombre=funcion.nombre,
        descripcion=funcion.descripcion
    )
    db.add(db_funcion)
    db.commit()
    db.refresh(db_funcion)
    return db_funcion

def update_funcion(db: Session, funcion_id: int, funcion_update: FuncionUpdate) -> Optional[Funcion]:
    db_funcion = get_funcion(db, funcion_id)
    if not db_funcion:
        return None
    
    update_data = funcion_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_funcion, key, value)
        
    db.add(db_funcion)
    db.commit()
    db.refresh(db_funcion)
    return db_funcion

def delete_funcion(db: Session, funcion_id: int) -> Optional[Funcion]:
    db_funcion = get_funcion(db, funcion_id)
    if not db_funcion:
        return None
    
    db.delete(db_funcion)
    db.commit()
    return db_funcion
