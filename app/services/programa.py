from sqlalchemy.orm import Session
from app.models.models import Programa
from app.schemas.programa import ProgramaCreate, ProgramaUpdate

def get_programa(db: Session, programa_id: int):
    return db.query(Programa).filter(Programa.id == programa_id).first()

def get_programas(db: Session, skip: int = 0, limit: int = 100, activo: bool = None):
    query = db.query(Programa)
    if activo is not None:
        query = query.filter(Programa.activo == activo)
    return query.offset(skip).limit(limit).all()

def create_programa(db: Session, programa: ProgramaCreate):
    db_programa = Programa(**programa.model_dump())
    db.add(db_programa)
    db.commit()
    db.refresh(db_programa)
    return db_programa

def update_programa(db: Session, programa_id: int, programa: ProgramaUpdate):
    db_programa = get_programa(db, programa_id)
    if not db_programa:
        return None
    
    update_data = programa.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_programa, key, value)
    
    db.add(db_programa)
    db.commit()
    db.refresh(db_programa)
    return db_programa

def delete_programa(db: Session, programa_id: int):
    db_programa = get_programa(db, programa_id)
    if db_programa:
        db.delete(db_programa)
        db.commit()
    return db_programa
