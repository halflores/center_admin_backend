from sqlalchemy.orm import Session
from app.models.models import ListaPrecio
from app.schemas.lista_precio import ListaPrecioCreate, ListaPrecioUpdate

def get_lista_precio(db: Session, lista_precio_id: int):
    return db.query(ListaPrecio).filter(ListaPrecio.id == lista_precio_id).first()

def get_lista_precio_by_name(db: Session, name: str):
    return db.query(ListaPrecio).filter(ListaPrecio.nombre == name).first()

def get_listas_precios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ListaPrecio).offset(skip).limit(limit).all()

def create_lista_precio(db: Session, lista_precio: ListaPrecioCreate):
    db_lista_precio = ListaPrecio(nombre=lista_precio.nombre, descripcion=lista_precio.descripcion)
    db.add(db_lista_precio)
    db.commit()
    db.refresh(db_lista_precio)
    return db_lista_precio

def update_lista_precio(db: Session, lista_precio_id: int, lista_precio: ListaPrecioUpdate):
    db_lista_precio = get_lista_precio(db, lista_precio_id)
    if not db_lista_precio:
        return None
    
    update_data = lista_precio.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lista_precio, key, value)
    
    db.add(db_lista_precio)
    db.commit()
    db.refresh(db_lista_precio)
    return db_lista_precio

def delete_lista_precio(db: Session, lista_precio_id: int):
    db_lista_precio = get_lista_precio(db, lista_precio_id)
    if db_lista_precio:
        db.delete(db_lista_precio)
        db.commit()
    return db_lista_precio
