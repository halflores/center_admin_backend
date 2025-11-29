from sqlalchemy.orm import Session
from app.models.models import Venta, DetalleVenta, Producto, MovimientoInventario
from app.schemas.venta import VentaCreate
from datetime import datetime

def create_venta(db: Session, venta: VentaCreate, usuario_id: int):
    # Start transaction implicitly by using db session
    try:
        # Create Venta
        db_venta = Venta(
            usuario_id=usuario_id,
            estudiante_id=venta.estudiante_id,
            cliente_nombre=venta.cliente_nombre,
            metodo_pago=venta.metodo_pago,
            total=0, # Will calculate
            fecha=datetime.utcnow()
        )
        db.add(db_venta)
        db.flush() # Get ID

        total = 0
        for detalle in venta.detalles:
            # Check stock
            producto = db.query(Producto).filter(Producto.id == detalle.producto_id).first()
            if not producto:
                raise Exception(f"Product {detalle.producto_id} not found")
            if producto.stock_actual < detalle.cantidad:
                raise Exception(f"Insufficient stock for product {producto.nombre}")

            # Calculate subtotal
            subtotal = detalle.cantidad * detalle.precio_unitario
            total += subtotal

            # Create DetalleVenta
            db_detalle = DetalleVenta(
                venta_id=db_venta.id,
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=subtotal
            )
            db.add(db_detalle)

            # Update Stock
            producto.stock_actual -= detalle.cantidad
            db.add(producto)

            # Create MovimientoInventario
            movimiento = MovimientoInventario(
                producto_id=detalle.producto_id,
                tipo_movimiento="VENTA",
                cantidad=-detalle.cantidad,
                fecha=datetime.utcnow(),
                referencia_tabla="ventas",
                referencia_id=db_venta.id,
                usuario_id=usuario_id
            )
            db.add(movimiento)

        db_venta.total = total
        db.add(db_venta)
        db.commit()
        db.refresh(db_venta)
        return db_venta
    except Exception as e:
        db.rollback()
        raise e

def get_ventas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Venta).offset(skip).limit(limit).all()

def get_venta(db: Session, venta_id: int):
    return db.query(Venta).filter(Venta.id == venta_id).first()
