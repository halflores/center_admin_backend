from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.tipo_transaccion import TipoTransaccionCreate, TipoTransaccionUpdate, TipoTransaccionResponse
from app.services import tipo_transaccion as tipo_transaccion_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()


@router.post("/", response_model=TipoTransaccionResponse)
def create_tipo_transaccion(
    tipo: TipoTransaccionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_tipo = tipo_transaccion_service.get_tipo_transaccion_by_name(db, name=tipo.nombre)
    if db_tipo:
        raise HTTPException(status_code=400, detail="Tipo de transacción ya existe")
    return tipo_transaccion_service.create_tipo_transaccion(db=db, tipo=tipo)


@router.get("/", response_model=List[TipoTransaccionResponse])
def read_tipos_transaccion(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    tipos = tipo_transaccion_service.get_tipos_transaccion(db, skip=skip, limit=limit)
    return tipos


@router.get("/{tipo_id}", response_model=TipoTransaccionResponse)
def read_tipo_transaccion(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_tipo = tipo_transaccion_service.get_tipo_transaccion(db, tipo_id=tipo_id)
    if db_tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de transacción no encontrado")
    return db_tipo


@router.put("/{tipo_id}", response_model=TipoTransaccionResponse)
def update_tipo_transaccion(
    tipo_id: int,
    tipo: TipoTransaccionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_tipo = tipo_transaccion_service.update_tipo_transaccion(db, tipo_id=tipo_id, tipo=tipo)
    if db_tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de transacción no encontrado")
    return db_tipo


@router.delete("/{tipo_id}", response_model=TipoTransaccionResponse)
def delete_tipo_transaccion(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_tipo = tipo_transaccion_service.delete_tipo_transaccion(db, tipo_id=tipo_id)
    if db_tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de transacción no encontrado")
    return db_tipo
