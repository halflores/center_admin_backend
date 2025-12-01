from sqlalchemy.orm import Session, joinedload
from app.models.models import MovimientoInventario, Usuario, Producto, Ingreso, Venta, Proveedor, Estudiante, Gestion, EstudianteGestion
from fastapi import HTTPException, status
from datetime import datetime, timedelta

def get_movimientos(db: Session, skip: int = 0, limit: int = 100):
    # Use joinedload to eagerly load related entities
    movimientos = db.query(MovimientoInventario)\
        .options(joinedload(MovimientoInventario.usuario), joinedload(MovimientoInventario.producto))\
        .order_by(MovimientoInventario.fecha.desc())\
        .offset(skip).limit(limit).all()
    
    result = []
    for mov in movimientos:
        # Explicitly build dictionary to ensure all fields are present and correct
        mov_data = {
            "id": mov.id,
            "producto_id": mov.producto_id,
            "tipo_movimiento": mov.tipo_movimiento,
            "cantidad": mov.cantidad,
            "fecha": mov.fecha,
            "referencia_tabla": mov.referencia_tabla,
            "referencia_id": mov.referencia_id,
            "usuario_id": mov.usuario_id,
            "usuario_nombre": None,
            "producto_nombre": None,
            "cliente": None,
            "proveedor": None,
            "anulado": mov.anulado,
            "total": None
        }
        
        # Get User Name from relationship
        if mov.usuario:
            mov_data['usuario_nombre'] = f"{mov.usuario.nombre} {mov.usuario.apellido}"
        
        # Get Product Name from relationship
        if mov.producto:
            mov_data['producto_nombre'] = mov.producto.nombre

        # Get Reference Info (Client/Provider/Total)
        if mov.referencia_tabla == 'ingresos' and mov.referencia_id:
            ingreso = db.query(Ingreso).filter(Ingreso.id == mov.referencia_id).first()
            if ingreso:
                mov_data['total'] = float(ingreso.total) if ingreso.total else None
                if ingreso.proveedor_id:
                    proveedor = db.query(Proveedor).filter(Proveedor.id == ingreso.proveedor_id).first()
                    if proveedor:
                        mov_data['proveedor'] = proveedor.nombre
                elif ingreso.proveedor: # Fallback for old string field
                    mov_data['proveedor'] = ingreso.proveedor
                
        elif mov.referencia_tabla == 'ventas' and mov.referencia_id:
            venta = db.query(Venta).filter(Venta.id == mov.referencia_id).first()
            if venta:
                mov_data['total'] = float(venta.total) if venta.total else None
                if venta.cliente_nombre:
                    mov_data['cliente'] = venta.cliente_nombre
                elif venta.estudiante_id:
                    estudiante = db.query(Estudiante).filter(Estudiante.id == venta.estudiante_id).first()
                    if estudiante:
                        mov_data['cliente'] = f"{estudiante.nombres} {estudiante.apellidos}"

        result.append(mov_data)
        
    return result

def anular_movimiento(db: Session, movimiento_id: int, usuario_id: int):
    # 1. Get original movement
    original_mov = db.query(MovimientoInventario).filter(MovimientoInventario.id == movimiento_id).first()
    if not original_mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        
    if "ANULACION" in original_mov.tipo_movimiento:
        raise HTTPException(status_code=400, detail="Este movimiento ya es una anulación")
        
    if original_mov.anulado:
        raise HTTPException(status_code=400, detail="Este movimiento ya ha sido anulado")

    # 2. Create counter-movement
    new_tipo = f"ANULACION_{original_mov.tipo_movimiento}"
    # Invert quantity: if original was +10, new is -10. If original was -5, new is +5.
    new_cantidad = -original_mov.cantidad 
    
    # Use Bolivia time (UTC-4)
    fecha_bolivia = datetime.utcnow() - timedelta(hours=4)
    
    new_mov = MovimientoInventario(
        producto_id=original_mov.producto_id,
        tipo_movimiento=new_tipo,
        cantidad=new_cantidad,
        fecha=fecha_bolivia,
        referencia_tabla=original_mov.referencia_tabla,
        referencia_id=original_mov.referencia_id,
        usuario_id=usuario_id
    )
    
    # 3. Update stock
    producto = db.query(Producto).filter(Producto.id == original_mov.producto_id).first()
    if producto:
        producto.stock_actual += new_cantidad
        
    # 4. Mark original as annulled
    original_mov.anulado = True
        
    db.add(new_mov)
    db.commit()
    db.refresh(new_mov)
    
    # Return enriched response for the new movement
    # We need to construct the response manually or re-fetch to get the enriched data
    # For simplicity, we return the basic object and let the frontend refresh or handle it
    # Ideally, we should reuse the enrichment logic, but for now this is sufficient as the list refreshes
    return new_mov
