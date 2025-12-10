from sqlalchemy.orm import Session
from app.models.models import NivelAcademicoEstudiante
from app.schemas.nivel_academico_estudiante import NivelAcademicoEstudianteCreate, NivelAcademicoEstudianteUpdate


def get_nivel_academico(db: Session, nivel_id: int):
    return db.query(NivelAcademicoEstudiante).filter(NivelAcademicoEstudiante.id == nivel_id).first()


def get_niveles_academicos_by_estudiante(db: Session, estudiante_id: int):
    return db.query(NivelAcademicoEstudiante).filter(
        NivelAcademicoEstudiante.estudiante_id == estudiante_id
    ).order_by(NivelAcademicoEstudiante.created_at.desc()).all()


def get_niveles_academicos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(NivelAcademicoEstudiante).offset(skip).limit(limit).all()


def create_nivel_academico(db: Session, nivel: NivelAcademicoEstudianteCreate):
    db_nivel = NivelAcademicoEstudiante(
        estudiante_id=nivel.estudiante_id,
        gestion_id=nivel.gestion_id,
        programa_id=nivel.programa_id,
        nivel_id=nivel.nivel_id,
        modulo_id=nivel.modulo_id,
        comentario_evaluacion=nivel.comentario_evaluacion
    )
    db.add(db_nivel)
    db.commit()
    db.refresh(db_nivel)
    return db_nivel


def update_nivel_academico(db: Session, nivel_id: int, nivel: NivelAcademicoEstudianteUpdate):
    db_nivel = get_nivel_academico(db, nivel_id)
    if not db_nivel:
        return None
    
    update_data = nivel.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_nivel, key, value)
    
    db.add(db_nivel)
    db.commit()
    db.refresh(db_nivel)
    return db_nivel


def delete_nivel_academico(db: Session, nivel_id: int):
    db_nivel = get_nivel_academico(db, nivel_id)
    if db_nivel:
        db.delete(db_nivel)
        db.commit()
    return db_nivel
