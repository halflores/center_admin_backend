from sqlalchemy.orm import Session
from app.models.models import Responsable
from app.schemas.responsable import ResponsableCreate, ResponsableUpdate

def get_responsable(db: Session, responsable_id: int):
    return db.query(Responsable).filter(Responsable.id == responsable_id).first()

def get_responsables(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Responsable).offset(skip).limit(limit).all()

def create_responsable(db: Session, responsable: ResponsableCreate):
    db_responsable = Responsable(**responsable.model_dump())
    db.add(db_responsable)
    db.commit()
    db.refresh(db_responsable)
    return db_responsable

def update_responsable(db: Session, responsable_id: int, responsable: ResponsableUpdate):
    db_responsable = get_responsable(db, responsable_id)
    if not db_responsable:
        return None
    
    update_data = responsable.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_responsable, key, value)
    
    db.add(db_responsable)
    db.commit()
    db.refresh(db_responsable)
    return db_responsable

def delete_responsable(db: Session, responsable_id: int):
    db_responsable = get_responsable(db, responsable_id)
    if db_responsable:
        db.delete(db_responsable)
        db.commit()
    return db_responsable
