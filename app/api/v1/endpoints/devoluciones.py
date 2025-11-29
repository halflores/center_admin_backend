from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.devolucion import DevolucionCreate, DevolucionResponse
from app.services import devoluciones as devolucion_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=DevolucionResponse)
def create_devolucion(devolucion: DevolucionCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    try:
        return devolucion_service.create_devolucion(db=db, devolucion=devolucion, usuario_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
