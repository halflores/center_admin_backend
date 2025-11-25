from sqlalchemy.orm import Session
from app.models.models import Usuario
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(Usuario).filter(Usuario.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.correo == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.contrasena)
    db_user = Usuario(
        nombre=user.nombre,
        apellido=user.apellido,
        correo=user.correo,
        contrasena=hashed_password,
        rol_id=user.rol_id,
        activo=user.activo
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: Usuario, user_update: UserUpdate):
    update_data = user_update.model_dump(exclude_unset=True)
    if "contrasena" in update_data:
        update_data["contrasena"] = get_password_hash(update_data["contrasena"])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
