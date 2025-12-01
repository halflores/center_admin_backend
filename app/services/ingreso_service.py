from sqlalchemy.orm import Session
from app.models.models import Ingreso, DetalleIngreso, Producto, MovimientoInventario, Usuario
from app.schemas.ingreso import IngresoCreate
from datetime import datetime
from zoneinfo import ZoneInfo

def create_ingreso(db: Session, ingreso_in: IngresoCreate, current_user: Usuario):
    # 1. Calculate total and prepare details
    total_ingreso = 0
    
    bolivia_tz = ZoneInfo("America/La_Paz")
    now_bolivia = datetime.now(bolivia_tz).replace(tzinfo=None)
    
    # Create Ingreso record first to get ID
    db_ingreso = Ingreso(
        proveedor_id=ingreso_in.proveedor_id,
        nro_factura=ingreso_in.nro_factura,
        usuario_id=current_user.id,
        total=0, # Will update later
        estado='COMPLETADO',
        fecha=now_bolivia
    )
    db.add(db_ingreso)
    db.flush() # Get ID

    for detalle in ingreso_in.detalles:
        subtotal = detalle.cantidad * detalle.costo_unitario
        total_ingreso += float(subtotal)
        
        # Create DetalleIngreso
        db_detalle = DetalleIngreso(
            ingreso_id=db_ingreso.id,
            producto_id=detalle.producto_id,
            cantidad=detalle.cantidad,
            costo_unitario=detalle.costo_unitario,
            subtotal=subtotal
        )
        db.add(db_detalle)
        
        # Update Stock
        producto = db.query(Producto).filter(Producto.id == detalle.producto_id).first()
        if producto:
            producto.stock_actual += detalle.cantidad
            db.add(producto)
            
            # Create MovimientoInventario
            movimiento = MovimientoInventario(
                producto_id=detalle.producto_id,
                tipo_movimiento='INGRESO_COMPRA',
                cantidad=detalle.cantidad,
                fecha=now_bolivia,
                referencia_tabla='ingresos',
                referencia_id=db_ingreso.id,
                usuario_id=current_user.id
            )
            db.add(movimiento)
            
    # Update total
    db_ingreso.total = total_ingreso
    db.add(db_ingreso)
    
    db.commit()
    db.refresh(db_ingreso)
    return db_ingreso


def cancel_ingreso(db: Session, ingreso_id: int, current_user: Usuario):
    # 1. Get Ingreso
    ingreso = get_ingreso(db, ingreso_id)
    if not ingreso:
        raise Exception("Ingreso not found")
    
    if ingreso.estado == 'ANULADO':
        raise Exception("Ingreso already cancelled")

    # 2. Reverse Stock
    for detalle in ingreso.detalles:
        producto = db.query(Producto).filter(Producto.id == detalle.producto_id).first()
        if producto:
            producto.stock_actual -= detalle.cantidad
            db.add(producto)

            # 3. Log Movement (Reversal)
            movimiento = MovimientoInventario(
                producto_id=detalle.producto_id,
                tipo_movimiento='ANULACION_INGRESO',
                cantidad=-detalle.cantidad, # Negative because we are removing the previously added stock
                fecha=datetime.utcnow(),
                referencia_tabla='ingresos',
                referencia_id=ingreso.id,
                usuario_id=current_user.id
            )
            db.add(movimiento)

    # 4. Update State
    ingreso.estado = 'ANULADO'
    db.add(ingreso)
    
    db.commit()
    db.refresh(ingreso)
    return ingreso


def get_ingreso(db: Session, ingreso_id: int):
    return db.query(Ingreso).filter(Ingreso.id == ingreso_id).first()

def get_ingresos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Ingreso).offset(skip).limit(limit).all()

