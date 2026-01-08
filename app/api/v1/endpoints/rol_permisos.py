from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.rol_permiso import RolPermisoCreate, RolPermisoResponse
from app.services import rol_permiso as rol_permiso_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=RolPermisoResponse)
def create_rol_permiso(
    rol_permiso: RolPermisoCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    db_rol_permiso = rol_permiso_service.get_rol_permiso(
        db, rol_id=rol_permiso.rol_id, permiso_id=rol_permiso.permiso_id
    )
    if db_rol_permiso:
        raise HTTPException(status_code=400, detail="Role Permission assignment already exists")
    
    try:
        return rol_permiso_service.create_rol_permiso(db=db, rol_permiso=rol_permiso)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not assign permission to role. Ensure Role and Permission IDs exist. Error: {str(e)}")

@router.get("/", response_model=List[RolPermisoResponse])
def read_rol_permisos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    rol_permisos = rol_permiso_service.get_rol_permisos(db, skip=skip, limit=limit)
    return rol_permisos

@router.get("/rol/{rol_id}", response_model=List[RolPermisoResponse])
def read_permisos_by_rol(
    rol_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    rol_permisos = rol_permiso_service.get_permisos_by_rol(db, rol_id=rol_id)
    return rol_permisos

@router.delete("/{rol_id}/{permiso_id}")
def delete_rol_permiso(
    rol_id: int, 
    permiso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    # Get it first to check existence
    db_rol_permiso = rol_permiso_service.get_rol_permiso(db, rol_id=rol_id, permiso_id=permiso_id)
    if not db_rol_permiso:
        raise HTTPException(status_code=404, detail="Role Permission assignment not found")
    
    # Perform deletion
    rol_permiso_service.delete_rol_permiso(db, rol_id=rol_id, permiso_id=permiso_id)
    
    return {"message": "Permission successfully removed from role", "rol_id": rol_id, "permiso_id": permiso_id}
