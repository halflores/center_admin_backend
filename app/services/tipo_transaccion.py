from sqlalchemy.orm import Session
from app.models.models import TipoTransaccion
from app.schemas.tipo_transaccion import TipoTransaccionCreate, TipoTransaccionUpdate


def get_tipo_transaccion(db: Session, tipo_id: int):
    return db.query(TipoTransaccion).filter(TipoTransaccion.id == tipo_id).first()


def get_tipo_transaccion_by_name(db: Session, name: str):
    return db.query(TipoTransaccion).filter(TipoTransaccion.nombre == name).first()


def get_tipos_transaccion(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TipoTransaccion).offset(skip).limit(limit).all()


def create_tipo_transaccion(db: Session, tipo: TipoTransaccionCreate):
    db_tipo = TipoTransaccion(
        nombre=tipo.nombre,
        descripcion=tipo.descripcion,
        activo=tipo.activo if tipo.activo is not None else True
    )
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo


def update_tipo_transaccion(db: Session, tipo_id: int, tipo: TipoTransaccionUpdate):
    db_tipo = get_tipo_transaccion(db, tipo_id)
    if not db_tipo:
        return None
    
    update_data = tipo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tipo, key, value)
    
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo


def delete_tipo_transaccion(db: Session, tipo_id: int):
    db_tipo = get_tipo_transaccion(db, tipo_id)
    if db_tipo:
        db.delete(db_tipo)
        db.commit()
    return db_tipo
