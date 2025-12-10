from sqlalchemy.orm import Session, joinedload
from app.models.models import Horario, Curso
from app.schemas.horario import HorarioCreate, HorarioUpdate

def get_horario(db: Session, horario_id: int):
    return db.query(Horario).options(
        joinedload(Horario.aula_rel),
        joinedload(Horario.curso).joinedload(Curso.modulo),
        joinedload(Horario.curso).joinedload(Curso.profesor)
    ).filter(Horario.id == horario_id).first()

def get_horarios(db: Session, skip: int = 0, limit: int = 100, curso_id: int = None, campus_id: int = None):
    query = db.query(Horario).options(
        joinedload(Horario.aula_rel),
        joinedload(Horario.curso).joinedload(Curso.modulo),
        joinedload(Horario.curso).joinedload(Curso.profesor)
    )
    if curso_id:
        query = query.filter(Horario.curso_id == curso_id)
    if campus_id:
        query = query.join(Horario.curso).filter(Curso.campus_id == campus_id)
    return query.offset(skip).limit(limit).all()

def create_horario(db: Session, horario: HorarioCreate):
    db_horario = Horario(**horario.model_dump())
    db.add(db_horario)
    db.commit()
    db.refresh(db_horario)
    return db_horario

def update_horario(db: Session, horario_id: int, horario: HorarioUpdate):
    db_horario = get_horario(db, horario_id)
    if not db_horario:
        return None
    
    update_data = horario.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_horario, key, value)
    
    db.add(db_horario)
    db.commit()
    db.refresh(db_horario)
    return db_horario

def delete_horario(db: Session, horario_id: int):
    db_horario = get_horario(db, horario_id)
    if db_horario:
        db.delete(db_horario)
        db.commit()
    return db_horario
