from sqlalchemy.orm import Session
from app.models.models import CarritoCompras, Producto
from app.schemas.carrito_compras import CarritoItemCreate, CarritoItemUpdate

def get_cart(db: Session, usuario_id: int):
    return db.query(CarritoCompras).filter(CarritoCompras.usuario_id == usuario_id).all()

def add_to_cart(db: Session, item: CarritoItemCreate, usuario_id: int):
    # Check if item exists
    db_item = db.query(CarritoCompras).filter(
        CarritoCompras.usuario_id == usuario_id,
        CarritoCompras.producto_id == item.producto_id
    ).first()

    if db_item:
        db_item.cantidad += item.cantidad
        # Update discount if provided
        if item.descuento is not None:
            db_item.descuento = item.descuento
    else:
        db_item = CarritoCompras(
            usuario_id=usuario_id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            descuento=item.descuento if item.descuento is not None else 0.0
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def update_cart_item(db: Session, item_id: int, item: CarritoItemUpdate):
    db_item = db.query(CarritoCompras).filter(CarritoCompras.id == item_id).first()
    if db_item:
        if item.cantidad is not None:
            db_item.cantidad = item.cantidad
        if item.descuento is not None:
            db_item.descuento = item.descuento
        db.commit()
        db.refresh(db_item)
    return db_item

def remove_from_cart(db: Session, item_id: int):
    db_item = db.query(CarritoCompras).filter(CarritoCompras.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

def clear_cart(db: Session, usuario_id: int):
    db.query(CarritoCompras).filter(CarritoCompras.usuario_id == usuario_id).delete()
    db.commit()
