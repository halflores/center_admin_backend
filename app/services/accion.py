from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.models import Accion
from app.schemas.accion import AccionCreate, AccionUpdate

def get_accion(db: Session, accion_id: int) -> Optional[Accion]:
    return db.query(Accion).filter(Accion.id == accion_id).first()

def get_accion_by_name(db: Session, name: str) -> Optional[Accion]:
    return db.query(Accion).filter(Accion.nombre == name).first()

def get_acciones(db: Session, skip: int = 0, limit: int = 100) -> List[Accion]:
    return db.query(Accion).offset(skip).limit(limit).all()

def create_accion(db: Session, accion: AccionCreate) -> Accion:
    db_accion = Accion(
        nombre=accion.nombre
    )
    db.add(db_accion)
    db.commit()
    db.refresh(db_accion)
    return db_accion

def update_accion(db: Session, accion_id: int, accion_update: AccionUpdate) -> Optional[Accion]:
    db_accion = get_accion(db, accion_id)
    if not db_accion:
        return None
    
    update_data = accion_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_accion, key, value)
        
    db.add(db_accion)
    db.commit()
    db.refresh(db_accion)
    return db_accion

def delete_accion(db: Session, accion_id: int) -> Optional[Accion]:
    db_accion = get_accion(db, accion_id)
    if not db_accion:
        return None
    
    db.delete(db_accion)
    db.commit()
    return db_accion
