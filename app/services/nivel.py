from sqlalchemy.orm import Session, joinedload
from app.models.models import Nivel
from app.schemas.nivel import NivelCreate, NivelUpdate

def get_nivel(db: Session, nivel_id: int):
    return db.query(Nivel).options(joinedload(Nivel.programa)).filter(Nivel.id == nivel_id).first()

def get_niveles(db: Session, skip: int = 0, limit: int = 100, programa_id: int = None, activo: bool = None):
    query = db.query(Nivel).options(joinedload(Nivel.programa))
    if programa_id:
        query = query.filter(Nivel.programa_id == programa_id)
    if activo is not None:
        query = query.filter(Nivel.activo == activo)
    return query.order_by(Nivel.orden).offset(skip).limit(limit).all()

def create_nivel(db: Session, nivel: NivelCreate):
    db_nivel = Nivel(**nivel.model_dump())
    db.add(db_nivel)
    db.commit()
    db.refresh(db_nivel)
    return db_nivel

def update_nivel(db: Session, nivel_id: int, nivel: NivelUpdate):
    db_nivel = get_nivel(db, nivel_id)
    if not db_nivel:
        return None
    
    update_data = nivel.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_nivel, key, value)
    
    db.add(db_nivel)
    db.commit()
    db.refresh(db_nivel)
    return db_nivel

def delete_nivel(db: Session, nivel_id: int):
    db_nivel = get_nivel(db, nivel_id)
    if db_nivel:
        db.delete(db_nivel)
        db.commit()
    return db_nivel
