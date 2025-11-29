from sqlalchemy.orm import Session
from app.models.models import Proveedor
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate

def get_proveedor(db: Session, proveedor_id: int):
    return db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

def get_proveedores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Proveedor).offset(skip).limit(limit).all()

def create_proveedor(db: Session, proveedor: ProveedorCreate):
    db_proveedor = Proveedor(
        nombre=proveedor.nombre,
        direccion=proveedor.direccion,
        celular=proveedor.celular,
        nombre_responsable=proveedor.nombre_responsable
    )
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

def update_proveedor(db: Session, proveedor_id: int, proveedor: ProveedorUpdate):
    db_proveedor = get_proveedor(db, proveedor_id)
    if not db_proveedor:
        return None
    
    update_data = proveedor.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_proveedor, key, value)
    
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

def delete_proveedor(db: Session, proveedor_id: int):
    db_proveedor = get_proveedor(db, proveedor_id)
    if db_proveedor:
        db.delete(db_proveedor)
        db.commit()
    return db_proveedor
