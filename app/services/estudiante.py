from sqlalchemy.orm import Session
from app.models.models import Estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate

def get_estudiante(db: Session, estudiante_id: int):
    return db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()

def get_estudiantes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Estudiante).offset(skip).limit(limit).all()

def create_estudiante(db: Session, estudiante: EstudianteCreate, usuario_id: int):
    db_estudiante = Estudiante(**estudiante.model_dump(), usuario_id=usuario_id)
    db.add(db_estudiante)
    db.commit()
    db.refresh(db_estudiante)
    return db_estudiante

def update_estudiante(db: Session, estudiante_id: int, estudiante: EstudianteUpdate):
    db_estudiante = get_estudiante(db, estudiante_id)
    if not db_estudiante:
        return None
    
    update_data = estudiante.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_estudiante, key, value)
    
    db.add(db_estudiante)
    db.commit()
    db.refresh(db_estudiante)
    return db_estudiante

def delete_estudiante(db: Session, estudiante_id: int):
    db_estudiante = get_estudiante(db, estudiante_id)
    if db_estudiante:
        db.delete(db_estudiante)
        db.commit()
    return db_estudiante
