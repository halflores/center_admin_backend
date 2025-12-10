from sqlalchemy.orm import Session
from app.models.models import Devolucion, DetalleDevolucion, Producto, MovimientoInventario
from app.schemas.devolucion import DevolucionCreate
from datetime import datetime
from typing import Optional

def get_devoluciones(db: Session, skip: int = 0, limit: int = 100, tipo: Optional[str] = None):
    """Get list of devoluciones with optional tipo filter"""
    query = db.query(Devolucion)
    if tipo:
        query = query.filter(Devolucion.tipo == tipo)
    return query.order_by(Devolucion.fecha.desc()).offset(skip).limit(limit).all()

def get_devolucion_by_id(db: Session, devolucion_id: int):
    """Get a specific devolucion by ID"""
    return db.query(Devolucion).filter(Devolucion.id == devolucion_id).first()

def create_devolucion(db: Session, devolucion: DevolucionCreate, usuario_id: int):
    try:
        db_devolucion = Devolucion(
            tipo=devolucion.tipo,
            referencia_id=devolucion.referencia_id,
            motivo=devolucion.motivo,
            usuario_id=usuario_id,
            fecha=datetime.utcnow()
        )
        db.add(db_devolucion)
        db.flush()

        for detalle in devolucion.detalles:
            producto = db.query(Producto).filter(Producto.id == detalle.producto_id).first()
            if not producto:
                raise Exception(f"Product {detalle.producto_id} not found")

            # Create DetalleDevolucion
            db_detalle = DetalleDevolucion(
                devolucion_id=db_devolucion.id,
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad
            )
            db.add(db_detalle)

            # Update Stock (Add back to inventory for customer returns, subtract for supplier returns)
            if devolucion.tipo == "ESTUDIANTE":
                producto.stock_actual += detalle.cantidad
            else:  # PROVEEDOR
                producto.stock_actual -= detalle.cantidad
            db.add(producto)

            # Create MovimientoInventario
            tipo_mov = "DEVOLUCION_PROVEEDOR" if devolucion.tipo == "PROVEEDOR" else "DEVOLUCION_ESTUDIANTE"
            movimiento = MovimientoInventario(
                producto_id=detalle.producto_id,
                tipo_movimiento=tipo_mov,
                cantidad=detalle.cantidad,
                fecha=datetime.utcnow(),
                referencia_tabla="devoluciones",
                referencia_id=db_devolucion.id,
                usuario_id=usuario_id
            )
            db.add(movimiento)

        db.commit()
        db.refresh(db_devolucion)
        return db_devolucion
    except Exception as e:
        db.rollback()
        raise e
