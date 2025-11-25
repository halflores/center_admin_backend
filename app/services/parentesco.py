from sqlalchemy.orm import Session
from app.models.models import Parentesco
from app.schemas.parentesco import ParentescoCreate, ParentescoUpdate

def get_parentesco(db: Session, parentesco_id: int):
    return db.query(Parentesco).filter(Parentesco.id == parentesco_id).first()

def get_parentescos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Parentesco).offset(skip).limit(limit).all()

def create_parentesco(db: Session, parentesco: ParentescoCreate):
    db_parentesco = Parentesco(**parentesco.model_dump())
    db.add(db_parentesco)
    db.commit()
    db.refresh(db_parentesco)
    return db_parentesco

def update_parentesco(db: Session, parentesco_id: int, parentesco: ParentescoUpdate):
    db_parentesco = get_parentesco(db, parentesco_id)
    if not db_parentesco:
        return None
    
    update_data = parentesco.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_parentesco, key, value)
    
    db.add(db_parentesco)
    db.commit()
    db.refresh(db_parentesco)
    return db_parentesco

def delete_parentesco(db: Session, parentesco_id: int):
    db_parentesco = get_parentesco(db, parentesco_id)
    if db_parentesco:
        db.delete(db_parentesco)
        db.commit()
    return db_parentesco
