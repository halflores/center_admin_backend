from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.models import RolPermiso
from app.schemas.rol_permiso import RolPermisoCreate

def get_rol_permiso(db: Session, rol_id: int, permiso_id: int) -> Optional[RolPermiso]:
    return db.query(RolPermiso).filter(
        RolPermiso.rol_id == rol_id,
        RolPermiso.permiso_id == permiso_id
    ).first()

def get_rol_permisos(db: Session, skip: int = 0, limit: int = 100) -> List[RolPermiso]:
    return db.query(RolPermiso).offset(skip).limit(limit).all()

def get_permisos_by_rol(db: Session, rol_id: int) -> List[RolPermiso]:
    return db.query(RolPermiso).filter(RolPermiso.rol_id == rol_id).all()

def create_rol_permiso(db: Session, rol_permiso: RolPermisoCreate) -> RolPermiso:
    db_rol_permiso = RolPermiso(
        rol_id=rol_permiso.rol_id,
        permiso_id=rol_permiso.permiso_id
    )
    db.add(db_rol_permiso)
    db.commit()
    db.refresh(db_rol_permiso)
    return db_rol_permiso

def delete_rol_permiso(db: Session, rol_id: int, permiso_id: int) -> Optional[RolPermiso]:
    db_rol_permiso = get_rol_permiso(db, rol_id, permiso_id)
    if not db_rol_permiso:
        return None
    
    db.delete(db_rol_permiso)
    db.commit()
    return db_rol_permiso
