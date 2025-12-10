from sqlalchemy.orm import Session
from app.models.models import TipoProducto
from app.schemas.tipo_producto import TipoProductoCreate, TipoProductoUpdate


def get_tipos_producto(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TipoProducto).offset(skip).limit(limit).all()


def get_tipo_producto(db: Session, tipo_producto_id: int):
    return db.query(TipoProducto).filter(TipoProducto.id == tipo_producto_id).first()


def get_tipo_producto_by_nombre(db: Session, nombre: str):
    return db.query(TipoProducto).filter(TipoProducto.nombre == nombre).first()


def create_tipo_producto(db: Session, tipo_producto: TipoProductoCreate):
    db_tipo = TipoProducto(**tipo_producto.model_dump())
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo


def update_tipo_producto(db: Session, tipo_producto_id: int, tipo_producto: TipoProductoUpdate):
    db_tipo = db.query(TipoProducto).filter(TipoProducto.id == tipo_producto_id).first()
    if not db_tipo:
        return None
    
    update_data = tipo_producto.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tipo, key, value)
    
    db.commit()
    db.refresh(db_tipo)
    return db_tipo


def delete_tipo_producto(db: Session, tipo_producto_id: int):
    db_tipo = db.query(TipoProducto).filter(TipoProducto.id == tipo_producto_id).first()
    if not db_tipo:
        return None
    
    db.delete(db_tipo)
    db.commit()
    return db_tipo
