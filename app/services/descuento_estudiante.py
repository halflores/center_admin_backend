from sqlalchemy.orm import Session
from app.models.models import DescuentoEstudiante
from app.schemas.descuento_estudiante import DescuentoEstudianteCreate, DescuentoEstudianteUpdate

def get_descuento(db: Session, descuento_id: int):
    return db.query(DescuentoEstudiante).filter(DescuentoEstudiante.id == descuento_id).first()

def get_descuento_by_student_and_product(db: Session, estudiante_id: int, producto_id: int):
    return db.query(DescuentoEstudiante).filter(
        DescuentoEstudiante.estudiante_id == estudiante_id,
        DescuentoEstudiante.producto_id == producto_id
    ).first()

def get_descuentos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DescuentoEstudiante).offset(skip).limit(limit).all()

def create_descuento(db: Session, descuento: DescuentoEstudianteCreate):
    db_descuento = DescuentoEstudiante(
        estudiante_id=descuento.estudiante_id,
        producto_id=descuento.producto_id,
        lista_precios_id=descuento.lista_precios_id,
        porcentaje_descuento=descuento.porcentaje_descuento,
        monto_descuento=descuento.monto_descuento,
        activo=descuento.activo
    )
    db.add(db_descuento)
    db.commit()
    db.refresh(db_descuento)
    return db_descuento

def update_descuento(db: Session, descuento_id: int, descuento: DescuentoEstudianteUpdate):
    db_descuento = get_descuento(db, descuento_id)
    if not db_descuento:
        return None
    
    update_data = descuento.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_descuento, key, value)
    
    db.add(db_descuento)
    db.commit()
    db.refresh(db_descuento)
    return db_descuento

def delete_descuento(db: Session, descuento_id: int):
    db_descuento = get_descuento(db, descuento_id)
    if db_descuento:
        db.delete(db_descuento)
        db.commit()
    return db_descuento
