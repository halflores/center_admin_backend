from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.models import Paquete, PaqueteProducto, Producto, Programa, Nivel, Modulo
from app.schemas.paquete import PaqueteCreate, PaqueteUpdate, PaqueteProductoCreate


def get_paquetes(db: Session, skip: int = 0, limit: int = 100, activo: Optional[bool] = None):
    query = db.query(Paquete)
    if activo is not None:
        query = query.filter(Paquete.activo == activo)
    return query.offset(skip).limit(limit).all()


def get_paquete(db: Session, paquete_id: int):
    return db.query(Paquete).filter(Paquete.id == paquete_id).first()


def get_paquetes_by_modulo(db: Session, modulo_id: int):
    """Get packages for a specific module"""
    return db.query(Paquete).filter(
        Paquete.modulo_id == modulo_id,
        Paquete.activo == True
    ).all()


def get_siguiente_paquete(db: Session, programa_id: int, nivel_id: int, modulo_id: int):
    """
    Get the next package based on current module.
    Logic: Find the next module in order, then find its package.
    """
    # Get current module
    current_modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not current_modulo:
        return None
    
    # Try to find next module in same level
    next_modulo = db.query(Modulo).filter(
        Modulo.nivel_id == nivel_id,
        Modulo.orden > current_modulo.orden,
        Modulo.activo == True
    ).order_by(Modulo.orden).first()
    
    if next_modulo:
        # Found next module in same level
        paquete = db.query(Paquete).filter(
            Paquete.modulo_id == next_modulo.id,
            Paquete.activo == True
        ).first()
        return paquete
    
    # No more modules in this level, try next level
    current_nivel = db.query(Nivel).filter(Nivel.id == nivel_id).first()
    if not current_nivel:
        return None
    
    next_nivel = db.query(Nivel).filter(
        Nivel.programa_id == programa_id,
        Nivel.orden > current_nivel.orden,
        Nivel.activo == True
    ).order_by(Nivel.orden).first()
    
    if next_nivel:
        # Get first module of next level
        first_modulo = db.query(Modulo).filter(
            Modulo.nivel_id == next_nivel.id,
            Modulo.activo == True
        ).order_by(Modulo.orden).first()
        
        if first_modulo:
            paquete = db.query(Paquete).filter(
                Paquete.modulo_id == first_modulo.id,
                Paquete.activo == True
            ).first()
            return paquete
    
    return None


def create_paquete(db: Session, paquete: PaqueteCreate):
    # Extract productos from paquete data
    productos_data = paquete.productos if paquete.productos else []
    paquete_dict = paquete.model_dump(exclude={'productos'})
    
    db_paquete = Paquete(**paquete_dict)
    db.add(db_paquete)
    db.commit()
    db.refresh(db_paquete)
    
    # Add products to package
    for prod in productos_data:
        db_paquete_producto = PaqueteProducto(
            paquete_id=db_paquete.id,
            producto_id=prod.producto_id,
            cantidad=prod.cantidad
        )
        db.add(db_paquete_producto)
    
    db.commit()
    db.refresh(db_paquete)
    return db_paquete


def update_paquete(db: Session, paquete_id: int, paquete: PaqueteUpdate):
    db_paquete = db.query(Paquete).filter(Paquete.id == paquete_id).first()
    if not db_paquete:
        return None
    
    # Handle productos separately
    productos_data = paquete.productos
    update_data = paquete.model_dump(exclude_unset=True, exclude={'productos'})
    
    for key, value in update_data.items():
        setattr(db_paquete, key, value)
    
    # Update products if provided
    if productos_data is not None:
        # Delete existing products
        db.query(PaqueteProducto).filter(PaqueteProducto.paquete_id == paquete_id).delete()
        
        # Add new products
        for prod in productos_data:
            db_paquete_producto = PaqueteProducto(
                paquete_id=paquete_id,
                producto_id=prod.producto_id,
                cantidad=prod.cantidad
            )
            db.add(db_paquete_producto)
    
    db.commit()
    db.refresh(db_paquete)
    return db_paquete


def delete_paquete(db: Session, paquete_id: int):
    db_paquete = db.query(Paquete).filter(Paquete.id == paquete_id).first()
    if not db_paquete:
        return None
    
    db.delete(db_paquete)
    db.commit()
    return db_paquete


def add_producto_to_paquete(db: Session, paquete_id: int, producto: PaqueteProductoCreate):
    # Check if already exists
    existing = db.query(PaqueteProducto).filter(
        PaqueteProducto.paquete_id == paquete_id,
        PaqueteProducto.producto_id == producto.producto_id
    ).first()
    
    if existing:
        # Update quantity
        existing.cantidad = producto.cantidad
        db.commit()
        db.refresh(existing)
        return existing
    
    db_item = PaqueteProducto(
        paquete_id=paquete_id,
        producto_id=producto.producto_id,
        cantidad=producto.cantidad
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def remove_producto_from_paquete(db: Session, paquete_id: int, producto_id: int):
    db_item = db.query(PaqueteProducto).filter(
        PaqueteProducto.paquete_id == paquete_id,
        PaqueteProducto.producto_id == producto_id
    ).first()
    
    if not db_item:
        return None
    
    db.delete(db_item)
    db.commit()
    return db_item


def enrich_paquete_response(db: Session, paquete: Paquete) -> dict:
    """Add related names to paquete response"""
    result = {
        "id": paquete.id,
        "nombre": paquete.nombre,
        "descripcion": paquete.descripcion,
        "programa_id": paquete.programa_id,
        "nivel_id": paquete.nivel_id,
        "modulo_id": paquete.modulo_id,
        "precio_total": paquete.precio_total,
        "activo": paquete.activo,
        "created_at": paquete.created_at,
        "programa_nombre": paquete.programa.nombre if paquete.programa else None,
        "nivel_nombre": paquete.nivel.nombre if paquete.nivel else None,
        "modulo_nombre": paquete.modulo.nombre if paquete.modulo else None,
        "productos": []
    }
    
    for pp in paquete.productos:
        result["productos"].append({
            "id": pp.id,
            "paquete_id": pp.paquete_id,
            "producto_id": pp.producto_id,
            "cantidad": pp.cantidad,
            "producto_nombre": pp.producto.nombre if pp.producto else None,
            "producto_codigo": pp.producto.codigo if pp.producto else None
        })
    
    return result
