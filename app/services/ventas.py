from sqlalchemy.orm import Session, joinedload
from app.models.models import Venta, DetalleVenta, Producto, MovimientoInventario, Estudiante
from app.schemas.venta import VentaCreate
from datetime import datetime
from zoneinfo import ZoneInfo

def create_venta(db: Session, venta: VentaCreate, usuario_id: int):
    # Start transaction implicitly by using db session
    try:
        bolivia_tz = ZoneInfo("America/La_Paz")
        now_bolivia = datetime.now(bolivia_tz).replace(tzinfo=None)

        # Create Venta
        db_venta = Venta(
            usuario_id=usuario_id,
            estudiante_id=venta.estudiante_id,
            cliente_nombre=venta.cliente_nombre,
            metodo_pago=venta.metodo_pago,
            total=0, # Will calculate
            fecha=now_bolivia
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

            # Calculate subtotal with discount
            descuento = detalle.descuento if hasattr(detalle, 'descuento') and detalle.descuento else 0
            precio_con_descuento = detalle.precio_unitario - descuento
            subtotal = detalle.cantidad * precio_con_descuento
            total += subtotal

            # Create DetalleVenta
            db_detalle = DetalleVenta(
                venta_id=db_venta.id,
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                descuento=descuento,
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
                fecha=now_bolivia,
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

def cancel_venta(db: Session, venta_id: int, usuario_id: int):
    try:
        # 1. Get Venta
        venta = get_venta(db, venta_id)
        if not venta:
            raise Exception("Venta not found")
        
        if venta.estado == 'ANULADA':
            raise Exception("Venta already cancelled")

        # 2. Reverse Stock
        for detalle in venta.detalles:
            producto = db.query(Producto).filter(Producto.id == detalle.producto_id).first()
            if producto:
                producto.stock_actual += detalle.cantidad # Add back the sold quantity
                db.add(producto)

                # 3. Log Movement (Reversal)
                movimiento = MovimientoInventario(
                    producto_id=detalle.producto_id,
                    tipo_movimiento="ANULACION_VENTA",
                    cantidad=detalle.cantidad, # Positive because we are adding back to stock
                    fecha=datetime.utcnow(),
                    referencia_tabla="ventas",
                    referencia_id=venta.id,
                    usuario_id=usuario_id
                )
                db.add(movimiento)

        # 4. Update State
        venta.estado = 'ANULADA'
        db.add(venta)
        
        db.commit()
        db.refresh(venta)
        return venta
    except Exception as e:
        db.rollback()
        raise e

def get_ventas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Venta).options(
        joinedload(Venta.usuario),
        joinedload(Venta.estudiante).joinedload(Estudiante.campus),
        joinedload(Venta.detalles).joinedload(DetalleVenta.producto)
    ).offset(skip).limit(limit).all()

def get_venta(db: Session, venta_id: int):
    return db.query(Venta).options(
        joinedload(Venta.usuario),
        joinedload(Venta.estudiante).joinedload(Estudiante.campus),
        joinedload(Venta.detalles).joinedload(DetalleVenta.producto)
    ).filter(Venta.id == venta_id).first()
