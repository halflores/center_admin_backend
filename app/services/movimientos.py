from sqlalchemy.orm import Session
from app.models.models import MovimientoInventario

def get_movimientos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(MovimientoInventario).offset(skip).limit(limit).all()
