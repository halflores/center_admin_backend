from sqlalchemy.orm import Session, joinedload
from app.models.models import PagoProfesor
from app.schemas.pago_profesor import PagoProfesorCreate, PagoProfesorUpdate

def get_pago_profesor(db: Session, pago_id: int):
    return db.query(PagoProfesor).options(
        joinedload(PagoProfesor.profesor),
        joinedload(PagoProfesor.gestion)
    ).filter(PagoProfesor.id == pago_id).first()

def get_pagos_profesor(db: Session, skip: int = 0, limit: int = 100, 
                       profesor_id: int = None, gestion_id: int = None, estado: str = None):
    query = db.query(PagoProfesor).options(
        joinedload(PagoProfesor.profesor),
        joinedload(PagoProfesor.gestion)
    )
    if profesor_id:
        query = query.filter(PagoProfesor.profesor_id == profesor_id)
    if gestion_id:
        query = query.filter(PagoProfesor.gestion_id == gestion_id)
    if estado:
        query = query.filter(PagoProfesor.estado == estado)
    return query.order_by(PagoProfesor.created_at.desc()).offset(skip).limit(limit).all()

def create_pago_profesor(db: Session, pago: PagoProfesorCreate, usuario_id: int):
    pago_data = pago.model_dump()
    if 'periodo' in pago_data:
        del pago_data['periodo']
    
    db_pago = PagoProfesor(**pago_data, usuario_id=usuario_id)
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return get_pago_profesor(db, db_pago.id)

def update_pago_profesor(db: Session, pago_id: int, pago: PagoProfesorUpdate):
    db_pago = db.query(PagoProfesor).filter(PagoProfesor.id == pago_id).first()
    if not db_pago:
        return None
    
    update_data = pago.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pago, key, value)
    
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return get_pago_profesor(db, pago_id)

def delete_pago_profesor(db: Session, pago_id: int):
    db_pago = get_pago_profesor(db, pago_id)
    if db_pago:
        db.delete(db_pago)
        db.commit()
    return db_pago
