from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.funcion import FuncionCreate, FuncionUpdate, FuncionResponse
from app.services import funcion as funcion_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=FuncionResponse)
def create_funcion(
    funcion: FuncionCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_funcion = funcion_service.get_funcion_by_name(db, name=funcion.nombre)
    if db_funcion:
        raise HTTPException(status_code=400, detail="Function already exists")
    return funcion_service.create_funcion(db=db, funcion=funcion)

@router.get("/", response_model=List[FuncionResponse])
def read_funciones(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    funciones = funcion_service.get_funciones(db, skip=skip, limit=limit)
    return funciones

@router.get("/{funcion_id}", response_model=FuncionResponse)
def read_funcion(
    funcion_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_funcion = funcion_service.get_funcion(db, funcion_id=funcion_id)
    if db_funcion is None:
        raise HTTPException(status_code=404, detail="Function not found")
    return db_funcion

@router.put("/{funcion_id}", response_model=FuncionResponse)
def update_funcion(
    funcion_id: int, 
    funcion: FuncionUpdate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_funcion = funcion_service.update_funcion(db, funcion_id=funcion_id, funcion_update=funcion)
    if db_funcion is None:
        raise HTTPException(status_code=404, detail="Function not found")
    return db_funcion

@router.delete("/{funcion_id}", response_model=FuncionResponse)
def delete_funcion(
    funcion_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_funcion = funcion_service.delete_funcion(db, funcion_id=funcion_id)
    if db_funcion is None:
        raise HTTPException(status_code=404, detail="Function not found")
    return db_funcion
