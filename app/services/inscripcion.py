from sqlalchemy.orm import Session, joinedload
from app.models.models import Inscripcion
from app.schemas.inscripcion import InscripcionCreate, InscripcionUpdate

def get_inscripcion(db: Session, inscripcion_id: int):
    return db.query(Inscripcion).options(
        joinedload(Inscripcion.estudiante),
        joinedload(Inscripcion.curso),
        joinedload(Inscripcion.gestion)
    ).filter(Inscripcion.id == inscripcion_id).first()

def get_inscripciones(db: Session, skip: int = 0, limit: int = 100, 
                      estudiante_id: int = None, curso_id: int = None, 
                      gestion_id: int = None, estado: str = None):
    query = db.query(Inscripcion).options(
        joinedload(Inscripcion.estudiante),
        joinedload(Inscripcion.curso),
        joinedload(Inscripcion.gestion)
    )
    if estudiante_id:
        query = query.filter(Inscripcion.estudiante_id == estudiante_id)
    if curso_id:
        query = query.filter(Inscripcion.curso_id == curso_id)
    if gestion_id:
        query = query.filter(Inscripcion.gestion_id == gestion_id)
    if estado:
        query = query.filter(Inscripcion.estado == estado)
    return query.offset(skip).limit(limit).all()

def create_inscripcion(db: Session, inscripcion: InscripcionCreate):
    db_inscripcion = Inscripcion(**inscripcion.model_dump())
    db.add(db_inscripcion)
    db.commit()
    db.refresh(db_inscripcion)
    return get_inscripcion(db, db_inscripcion.id)

def update_inscripcion(db: Session, inscripcion_id: int, inscripcion: InscripcionUpdate):
    db_inscripcion = db.query(Inscripcion).filter(Inscripcion.id == inscripcion_id).first()
    if not db_inscripcion:
        return None
    
    update_data = inscripcion.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_inscripcion, key, value)
    
    db.add(db_inscripcion)
    db.commit()
    db.refresh(db_inscripcion)
    return get_inscripcion(db, inscripcion_id)

def delete_inscripcion(db: Session, inscripcion_id: int):
    db_inscripcion = get_inscripcion(db, inscripcion_id)
    if db_inscripcion:
        db.delete(db_inscripcion)
        db.commit()
    return db_inscripcion
