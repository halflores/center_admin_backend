from sqlalchemy.orm import Session, joinedload
from app.models.models import Venta, DetalleVenta, Producto, MovimientoInventario, Estudiante, InscripcionPaquete, Gestion
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
            producto = db.query(Producto).options(joinedload(Producto.tipo_producto)).filter(Producto.id == detalle.producto_id).first()
            if not producto:
                raise Exception(f"Product {detalle.producto_id} not found")

            es_servicio = producto.tipo_producto and producto.tipo_producto.nombre == 'SERVICIO'

            if not es_servicio:
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

            # Update Stock only if not service
            if not es_servicio:
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

        # Create InscripcionPaquete if paquete_id is present
        if venta.paquete_id and venta.estudiante_id:
            # Get active gestion (term) based on current year and max nro
            # Since 'activo' column doesn't exist, we assume the latest term of the current year is active
            gestion_activa = db.query(Gestion).filter(Gestion.anio == now_bolivia.year).order_by(Gestion.nro.desc()).first()
            if not gestion_activa:
                # Fallback: try to find any gestion
                gestion_activa = db.query(Gestion).order_by(Gestion.anio.desc(), Gestion.nro.desc()).first()
            
            gestion_id = gestion_activa.id if gestion_activa else None

            inscripcion = InscripcionPaquete(
                estudiante_id=venta.estudiante_id,
                paquete_id=venta.paquete_id,
                venta_id=db_venta.id,
                gestion_id=gestion_id,
                estado_academico='INSCRITO',
                fecha_inscripcion=now_bolivia
            )
            db.add(inscripcion)

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
            producto = db.query(Producto).options(joinedload(Producto.tipo_producto)).filter(Producto.id == detalle.producto_id).first()
            if producto:
                es_servicio = producto.tipo_producto and producto.tipo_producto.nombre == 'SERVICIO'
                
                if not es_servicio:
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
