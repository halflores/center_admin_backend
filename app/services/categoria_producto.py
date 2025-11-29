from sqlalchemy.orm import Session
from app.models.models import CategoriaProducto
from app.schemas.categoria_producto import CategoriaProductoCreate, CategoriaProductoUpdate

def get_categoria(db: Session, categoria_id: int):
    return db.query(CategoriaProducto).filter(CategoriaProducto.id == categoria_id).first()

def get_categoria_by_name(db: Session, name: str):
    return db.query(CategoriaProducto).filter(CategoriaProducto.nombre == name).first()

def get_categorias(db: Session, skip: int = 0, limit: int = 100):
    return db.query(CategoriaProducto).offset(skip).limit(limit).all()

def create_categoria(db: Session, categoria: CategoriaProductoCreate):
    db_categoria = CategoriaProducto(nombre=categoria.nombre, descripcion=categoria.descripcion)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def update_categoria(db: Session, categoria_id: int, categoria: CategoriaProductoUpdate):
    db_categoria = get_categoria(db, categoria_id)
    if not db_categoria:
        return None
    
    update_data = categoria.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_categoria, key, value)
    
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def delete_categoria(db: Session, categoria_id: int):
    db_categoria = get_categoria(db, categoria_id)
    if db_categoria:
        db.delete(db_categoria)
        db.commit()
    return db_categoria
