from sqlalchemy.orm import Session
from app.models.models import PrecioProducto
from app.schemas.precio_producto import PrecioProductoCreate, PrecioProductoUpdate

def get_precio_producto(db: Session, precio_producto_id: int):
    return db.query(PrecioProducto).filter(PrecioProducto.id == precio_producto_id).first()

def get_precio_by_producto_and_lista(db: Session, producto_id: int, lista_precios_id: int):
    return db.query(PrecioProducto).filter(
        PrecioProducto.producto_id == producto_id,
        PrecioProducto.lista_precios_id == lista_precios_id
    ).first()

def get_precios_producto(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PrecioProducto).offset(skip).limit(limit).all()

def create_precio_producto(db: Session, precio_producto: PrecioProductoCreate):
    db_precio_producto = PrecioProducto(
        producto_id=precio_producto.producto_id,
        lista_precios_id=precio_producto.lista_precios_id,
        precio=precio_producto.precio
    )
    db.add(db_precio_producto)
    db.commit()
    db.refresh(db_precio_producto)
    return db_precio_producto

def update_precio_producto(db: Session, precio_producto_id: int, precio_producto: PrecioProductoUpdate):
    db_precio_producto = get_precio_producto(db, precio_producto_id)
    if not db_precio_producto:
        return None
    
    update_data = precio_producto.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_precio_producto, key, value)
    
    db.add(db_precio_producto)
    db.commit()
    db.refresh(db_precio_producto)
    return db_precio_producto

def delete_precio_producto(db: Session, precio_producto_id: int):
    db_precio_producto = get_precio_producto(db, precio_producto_id)
    if db_precio_producto:
        db.delete(db_precio_producto)
        db.commit()
    return db_precio_producto
