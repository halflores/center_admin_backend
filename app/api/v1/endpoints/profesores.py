from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.profesor import ProfesorCreate, ProfesorUpdate, ProfesorResponse, ProfesorWithCampusResponse
from app.services import profesor as profesor_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=ProfesorResponse)
def create_profesor(profesor: ProfesorCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    from app.core.security import get_password_hash
    from app.models.models import Role, Usuario as UsuarioModel
    from sqlalchemy.exc import IntegrityError
    
    try:
        new_usuario_id = None
        
        if profesor.crear_usuario:
            if not profesor.correo:
                raise HTTPException(status_code=400, detail="El correo es obligatorio para crear un usuario.")
            
            # Check if user email exists
            if db.query(UsuarioModel).filter(UsuarioModel.correo == profesor.correo).first():
                raise HTTPException(status_code=400, detail="Ya existe un usuario de sistema con este correo.")

            rol_id = profesor.rol_usuario_id
            if not rol_id:
                # Default role 'Profesor'
                rol = db.query(Role).filter(Role.nombre == 'Profesor').first()
                if rol:
                    rol_id = rol.id
                else:
                    raise HTTPException(status_code=400, detail="Debe seleccionar un rol para el usuario.")

            # Password: use provided or default to CI (Profesor has CI)
            raw_password = profesor.contrasena if profesor.contrasena else (profesor.ci if profesor.ci else "123456")
            
            hashed_password = get_password_hash(raw_password)
            
            nuevo_usuario = UsuarioModel(
                nombre=profesor.nombres,
                apellido=profesor.apellidos,
                correo=profesor.correo,
                contrasena=hashed_password,
                rol_id=rol_id,
                activo=True
            )
            db.add(nuevo_usuario)
            db.flush()
            new_usuario_id = nuevo_usuario.id

        # Add the newly created user_id to the professor data if created
        if new_usuario_id:
            profesor.usuario_id = new_usuario_id

        return profesor_service.create_profesor(db=db, profesor=profesor)
        
    except IntegrityError as e:
        db.rollback()
        error_str = str(e.orig).lower()
        if "profesores_ci_key" in error_str or "ci" in error_str:
            raise HTTPException(status_code=400, detail="El CI ingresado ya existe en la base de datos.")
        if "correo" in error_str:
            raise HTTPException(status_code=400, detail="El correo ingresado ya existe en la base de datos.")
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e.orig)}")

@router.get("/", response_model=List[ProfesorWithCampusResponse])
def read_profesores(skip: int = 0, limit: int = 100, activo: Optional[bool] = None, campus_id: Optional[int] = None, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return profesor_service.get_profesores(db, skip=skip, limit=limit, activo=activo, campus_id=campus_id)

@router.get("/{profesor_id}", response_model=ProfesorWithCampusResponse)
def read_profesor(profesor_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_profesor = profesor_service.get_profesor(db, profesor_id=profesor_id)
    if db_profesor is None:
        raise HTTPException(status_code=404, detail="Profesor not found")
    return db_profesor

@router.put("/{profesor_id}", response_model=ProfesorWithCampusResponse)
def update_profesor(profesor_id: int, profesor: ProfesorUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    from sqlalchemy.exc import IntegrityError
    try:
        db_profesor = profesor_service.update_profesor(db, profesor_id=profesor_id, profesor=profesor)
        if db_profesor is None:
            raise HTTPException(status_code=404, detail="Profesor not found")
        return db_profesor
    except IntegrityError as e:
        db.rollback()
        error_str = str(e.orig).lower()
        if "profesores_ci_key" in error_str or "ci" in error_str:
            raise HTTPException(status_code=400, detail="El CI ingresado ya existe en la base de datos.")
        if "correo" in error_str:
            raise HTTPException(status_code=400, detail="El correo ingresado ya existe en la base de datos.")
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e.orig)}")

@router.delete("/{profesor_id}", response_model=ProfesorResponse)
def delete_profesor(profesor_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_profesor = profesor_service.delete_profesor(db, profesor_id=profesor_id)
    if db_profesor is None:
        raise HTTPException(status_code=404, detail="Profesor not found")
    return db_profesor
