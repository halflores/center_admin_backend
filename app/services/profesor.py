from sqlalchemy.orm import Session, joinedload
from app.models.models import Profesor, ProfesorCampus
from app.schemas.profesor import ProfesorCreate, ProfesorUpdate

def get_profesor(db: Session, profesor_id: int):
    return db.query(Profesor).options(
        joinedload(Profesor.campus_list).joinedload(ProfesorCampus.campus)
    ).filter(Profesor.id == profesor_id).first()

def get_profesores(db: Session, skip: int = 0, limit: int = 100, activo: bool = None, campus_id: int = None):
    query = db.query(Profesor).options(
        joinedload(Profesor.campus_list).joinedload(ProfesorCampus.campus)
    )
    if activo is not None:
        query = query.filter(Profesor.activo == activo)
    if campus_id:
        query = query.join(ProfesorCampus).filter(ProfesorCampus.campus_id == campus_id)
    return query.offset(skip).limit(limit).all()

def create_profesor(db: Session, profesor: ProfesorCreate):
    profesor_data = profesor.model_dump(exclude={'campus_ids', 'crear_usuario', 'rol_usuario_id', 'contrasena'})
    db_profesor = Profesor(**profesor_data)
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    
    # Add campus relationships
    if profesor.campus_ids:
        for i, campus_id in enumerate(profesor.campus_ids):
            profesor_campus = ProfesorCampus(
                profesor_id=db_profesor.id,
                campus_id=campus_id,
                principal=(i == 0)  # First campus is principal
            )
            db.add(profesor_campus)
        db.commit()
        db.refresh(db_profesor)
    
    return db_profesor

def update_profesor(db: Session, profesor_id: int, profesor: ProfesorUpdate):
    db_profesor = db.query(Profesor).filter(Profesor.id == profesor_id).first()
    if not db_profesor:
        return None
    
    update_data = profesor.model_dump(exclude_unset=True, exclude={'campus_ids'})
    for key, value in update_data.items():
        setattr(db_profesor, key, value)
    
    # Update campus relationships if provided
    if profesor.campus_ids is not None:
        # Remove existing relationships
        db.query(ProfesorCampus).filter(ProfesorCampus.profesor_id == profesor_id).delete()
        
        # Add new relationships
        for i, campus_id in enumerate(profesor.campus_ids):
            profesor_campus = ProfesorCampus(
                profesor_id=profesor_id,
                campus_id=campus_id,
                principal=(i == 0)
            )
            db.add(profesor_campus)
    
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    return get_profesor(db, profesor_id)

def delete_profesor(db: Session, profesor_id: int):
    db_profesor = get_profesor(db, profesor_id)
    if db_profesor:
        db.delete(db_profesor)
        db.commit()
    return db_profesor
