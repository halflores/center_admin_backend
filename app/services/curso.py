from sqlalchemy.orm import Session, joinedload
from app.models.models import Curso, Horario
from app.schemas.curso import CursoCreate, CursoUpdate

def get_curso(db: Session, curso_id: int):
    return db.query(Curso).options(
        joinedload(Curso.modulo),
        joinedload(Curso.profesor),
        joinedload(Curso.campus),
        joinedload(Curso.horarios).joinedload(Horario.aula_rel)
    ).filter(Curso.id == curso_id).first()

def get_cursos(db: Session, skip: int = 0, limit: int = 100, modulo_id: int = None, 
               profesor_id: int = None, campus_id: int = None, estado: str = None):
    query = db.query(Curso).options(
        joinedload(Curso.modulo),
        joinedload(Curso.profesor),
        joinedload(Curso.campus),
        joinedload(Curso.horarios).joinedload(Horario.aula_rel)
    )
    if modulo_id:
        query = query.filter(Curso.modulo_id == modulo_id)
    if profesor_id:
        query = query.filter(Curso.profesor_id == profesor_id)
    if campus_id:
        query = query.filter(Curso.campus_id == campus_id)
    if estado:
        query = query.filter(Curso.estado == estado)
    return query.offset(skip).limit(limit).all()

def create_curso(db: Session, curso: CursoCreate):
    curso_data = curso.model_dump(exclude={'horarios'})
    db_curso = Curso(**curso_data)
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)
    
    # Create horarios if provided
    if curso.horarios:
        for horario_data in curso.horarios:
            horario = Horario(
                curso_id=db_curso.id,
                **horario_data.model_dump()
            )
            db.add(horario)
        db.commit()
        db.refresh(db_curso)
    
    return get_curso(db, db_curso.id)

def update_curso(db: Session, curso_id: int, curso: CursoUpdate):
    db_curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not db_curso:
        return None
    
    update_data = curso.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_curso, key, value)
    
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)
    return get_curso(db, curso_id)

def delete_curso(db: Session, curso_id: int):
    db_curso = get_curso(db, curso_id)
    if db_curso:
        db.delete(db_curso)
        db.commit()
    return db_curso
