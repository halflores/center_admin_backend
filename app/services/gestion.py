from sqlalchemy.orm import Session
from app.models.models import Gestion
from app.schemas.gestion import GestionCreate, GestionUpdate

def get_gestion(db: Session, gestion_id: int):
    return db.query(Gestion).filter(Gestion.id == gestion_id).first()

def get_gestiones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Gestion).offset(skip).limit(limit).all()

def create_gestion(db: Session, gestion: GestionCreate):
    db_gestion = Gestion(**gestion.model_dump())
    db.add(db_gestion)
    db.commit()
    db.refresh(db_gestion)
    return db_gestion

def update_gestion(db: Session, gestion_id: int, gestion: GestionUpdate):
    db_gestion = get_gestion(db, gestion_id)
    if not db_gestion:
        return None
    
    update_data = gestion.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_gestion, key, value)
    
    db.add(db_gestion)
    db.commit()
    db.refresh(db_gestion)
    return db_gestion

def delete_gestion(db: Session, gestion_id: int):
    db_gestion = get_gestion(db, gestion_id)
    if db_gestion:
        db.delete(db_gestion)
        db.commit()
    return db_gestion
