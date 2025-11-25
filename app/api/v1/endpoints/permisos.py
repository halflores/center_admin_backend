from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.permiso import PermisoCreate, PermisoUpdate, PermisoResponse
from app.services import permiso as permiso_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=PermisoResponse)
def create_permiso(
    permiso: PermisoCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_permiso = permiso_service.get_permiso_by_pair(db, funcion_id=permiso.funcion_id, accion_id=permiso.accion_id)
    if db_permiso:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    # Optional: Check if funcion_id and accion_id exist in their respective tables
    # This is enforced by foreign keys in DB, but we could handle it gracefully here.
    try:
        return permiso_service.create_permiso(db=db, permiso=permiso)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not create permission. Ensure Function and Action IDs exist. Error: {str(e)}")

@router.get("/", response_model=List[PermisoResponse])
def read_permisos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    permisos = permiso_service.get_permisos(db, skip=skip, limit=limit)
    return permisos

@router.get("/{permiso_id}", response_model=PermisoResponse)
def read_permiso(
    permiso_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_permiso = permiso_service.get_permiso(db, permiso_id=permiso_id)
    if db_permiso is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    return db_permiso

@router.put("/{permiso_id}", response_model=PermisoResponse)
def update_permiso(
    permiso_id: int, 
    permiso: PermisoUpdate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_permiso = permiso_service.update_permiso(db, permiso_id=permiso_id, permiso_update=permiso)
    if db_permiso is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    return db_permiso

@router.delete("/{permiso_id}", response_model=PermisoResponse)
def delete_permiso(
    permiso_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_permiso = permiso_service.delete_permiso(db, permiso_id=permiso_id)
    if db_permiso is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    return db_permiso
