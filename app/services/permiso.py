from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.models import Permiso
from app.schemas.permiso import PermisoCreate, PermisoUpdate

def get_permiso(db: Session, permiso_id: int) -> Optional[Permiso]:
    return db.query(Permiso).filter(Permiso.id == permiso_id).first()

def get_permiso_by_pair(db: Session, funcion_id: int, accion_id: int) -> Optional[Permiso]:
    return db.query(Permiso).filter(
        Permiso.funcion_id == funcion_id, 
        Permiso.accion_id == accion_id
    ).first()

def get_permisos(db: Session, skip: int = 0, limit: int = 100) -> List[Permiso]:
    return db.query(Permiso).offset(skip).limit(limit).all()

def create_permiso(db: Session, permiso: PermisoCreate) -> Permiso:
    db_permiso = Permiso(
        funcion_id=permiso.funcion_id,
        accion_id=permiso.accion_id
    )
    db.add(db_permiso)
    db.commit()
    db.refresh(db_permiso)
    return db_permiso

def update_permiso(db: Session, permiso_id: int, permiso_update: PermisoUpdate) -> Optional[Permiso]:
    db_permiso = get_permiso(db, permiso_id)
    if not db_permiso:
        return None
    
    update_data = permiso_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_permiso, key, value)
        
    db.add(db_permiso)
    db.commit()
    db.refresh(db_permiso)
    return db_permiso

def delete_permiso(db: Session, permiso_id: int) -> Optional[Permiso]:
    db_permiso = get_permiso(db, permiso_id)
    if not db_permiso:
        return None
    
    db.delete(db_permiso)
    db.commit()
    return db_permiso
