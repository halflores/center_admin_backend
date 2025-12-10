from sqlalchemy.orm import Session, joinedload
from app.models.models import Modulo
from app.schemas.modulo import ModuloCreate, ModuloUpdate

def get_modulo(db: Session, modulo_id: int):
    return db.query(Modulo).options(joinedload(Modulo.nivel)).filter(Modulo.id == modulo_id).first()

def get_modulos(db: Session, skip: int = 0, limit: int = 100, nivel_id: int = None, activo: bool = None):
    query = db.query(Modulo).options(joinedload(Modulo.nivel))
    if nivel_id:
        query = query.filter(Modulo.nivel_id == nivel_id)
    if activo is not None:
        query = query.filter(Modulo.activo == activo)
    return query.order_by(Modulo.orden).offset(skip).limit(limit).all()

def create_modulo(db: Session, modulo: ModuloCreate):
    db_modulo = Modulo(**modulo.model_dump())
    db.add(db_modulo)
    db.commit()
    db.refresh(db_modulo)
    return db_modulo

def update_modulo(db: Session, modulo_id: int, modulo: ModuloUpdate):
    db_modulo = get_modulo(db, modulo_id)
    if not db_modulo:
        return None
    
    update_data = modulo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_modulo, key, value)
    
    db.add(db_modulo)
    db.commit()
    db.refresh(db_modulo)
    return db_modulo

def delete_modulo(db: Session, modulo_id: int):
    db_modulo = get_modulo(db, modulo_id)
    if db_modulo:
        db.delete(db_modulo)
        db.commit()
    return db_modulo
