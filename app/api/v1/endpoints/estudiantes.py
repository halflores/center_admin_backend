from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse
from app.services import estudiante as estudiante_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

from sqlalchemy.exc import IntegrityError

@router.get("/check-email")
def check_email_exists(email: str, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    estudiante = estudiante_service.get_estudiante_by_email(db, email=email)
    if estudiante:
        return {"exists": True, "detail": "El correo electrónico ya está registrado."}
    return {"exists": False, "detail": "El correo electrónico está disponible."}

@router.post("/", response_model=EstudianteResponse)
def create_estudiante(estudiante: EstudianteCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    try:
        return estudiante_service.create_estudiante(db=db, estudiante=estudiante, usuario_id=current_user.id)
    except IntegrityError as e:
        db.rollback()
        error_str = str(e).lower()
        if hasattr(e, 'orig') and e.orig:
            error_str += " " + str(e.orig).lower()
            
        if "unique" in error_str or "duplicate" in error_str:
            if "correo" in error_str or "email" in error_str:
                raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
            raise HTTPException(status_code=400, detail="Ya existe un registro con estos datos (posible duplicado).")
        
        if "foreign key" in error_str:
            raise HTTPException(status_code=400, detail="Referencia inválida (Campus o Usuario no existe).")
            
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e.orig) if hasattr(e, 'orig') else str(e)}")
    except Exception as e:
        db.rollback()
        print(f"ERROR CREATING STUDENT: {type(e)} - {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/", response_model=List[EstudianteResponse])
def read_estudiantes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return estudiante_service.get_estudiantes(db, skip=skip, limit=limit)

@router.get("/{estudiante_id}", response_model=EstudianteResponse)
def read_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_estudiante = estudiante_service.get_estudiante(db, estudiante_id=estudiante_id)
    if db_estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return db_estudiante

@router.put("/{estudiante_id}", response_model=EstudianteResponse)
def update_estudiante(estudiante_id: int, estudiante: EstudianteUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_estudiante = estudiante_service.update_estudiante(db, estudiante_id=estudiante_id, estudiante=estudiante)
    if db_estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return db_estudiante

@router.delete("/{estudiante_id}", response_model=EstudianteResponse)
def delete_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_estudiante = estudiante_service.delete_estudiante(db, estudiante_id=estudiante_id)
    if db_estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return db_estudiante
