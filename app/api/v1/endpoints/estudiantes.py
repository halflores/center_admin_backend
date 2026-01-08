from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse
from app.services import estudiante as estudiante_service
from app.api import deps
from app.models.models import Usuario, Role
from app.core.security import get_password_hash


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
        # Check if email exists if provided
        if estudiante.correo:
             existing_email = estudiante_service.get_estudiante_by_email(db, email=estudiante.correo)
             if existing_email:
                 raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado en estudiantes.")

        estudiante_data = estudiante.model_dump(exclude={"crear_usuario", "rol_usuario_id", "contrasena"})
        
        # Prepare Create DTO for service (hacky if service expects Pydantic model)
        # Service expects EstudianteCreate. But EstudianteCreate now has extra fields.
        # Servicio uses `**estudiante.model_dump(), usuario_id=usuario_id`.
        # `model_dump()` will include the new fields unless validation excludes them or we handle it.
        # `Estudiante` SQLA model won't accept extra fields in `**kwargs` probably, or it might ignore them? 
        # SQLA model constructor accepts kwargs for column names. It will ERROR on unknown columns.
        # So we MUST exclude them before creating the model.
        # The service implementation: `db_estudiante = Estudiante(**estudiante.model_dump(), usuario_id=usuario_id)`
        # This will ERROR if model_dump() contains `crear_usuario`.
        # I should probably update the SERVICE to gracefully handle this OR instantiate Estudiante manually here OR update service to exclude.

        # Let's handle logic here and use the service OR update logic here completely.
        # To avoid modifying service signature which might be used elsewhere (though unlikely), 
        # I will instantiate Estudiante here or modify the object passed to service.
        
        # Actually easier: I'll do the logic here and use `estudiante_service.create_estudiante` ONLY if I can strip the fields.
        # But `estudiante` argument to service checks Pydantic type `EstudianteCreate`.
        
        # Let's manually create the user here first.
        new_usuario_id = None
        
        if estudiante.crear_usuario:
            if not estudiante.correo:
                 raise HTTPException(status_code=400, detail="El correo es obligatorio para crear un usuario.")
            
            # Check if user email exists (in Usuarios table)
            if db.query(Usuario).filter(Usuario.correo == estudiante.correo).first():
                 raise HTTPException(status_code=400, detail="Ya existe un usuario de sistema con este correo.")

            rol_id = estudiante.rol_usuario_id
            if not rol_id:
                # Default role 'Estudiante'
                rol = db.query(Role).filter(Role.nombre == 'Estudiante').first()
                if rol:
                    rol_id = rol.id
                else:
                    raise HTTPException(status_code=400, detail="Debe seleccionar un rol para el usuario.")

            # Password
            raw_password = estudiante.contrasena if estudiante.contrasena else (estudiante.celular if estudiante.celular else "123456") 
            # Default password fallback if no CI (Student doesn't have CI field in schema? Wait. Estudiante schema doesn't have CI. Empleados do.
            # Student has `celular` or I can use generic. Let's use `celular` or generic.
            
            hashed_password = get_password_hash(raw_password)
            
            nuevo_usuario = Usuario(
                nombre=estudiante.nombres,
                apellido=estudiante.apellidos,
                correo=estudiante.correo,
                contrasena=hashed_password,
                rol_id=rol_id,
                activo=True
            )
            db.add(nuevo_usuario)
            db.flush() # Get ID
            new_usuario_id = nuevo_usuario.id

        # Now create student. 
        # Refactored: Call service but we need to ensure service doesn't crash on extra fields.
        # Service does: `db_estudiante = Estudiante(**estudiante.model_dump(), usuario_id=usuario_id)`
        # `model_dump()` on `EstudianteCreate` WILL include 'crear_usuario'.
        # This WILL fail because `Estudiante` model doesn't have `crear_usuario`.
        # I MUST update the service or perform the creation here. 
        # I'll update the endpoint to NOT use the service for creation, or I'll patch the input.
        
        # Let's create `Estudiante` directly here to avoid issues and since we are overriding behavior.
        # OR better: Update the SERVICE to `exclude_unset=True` or specific exclusion? No, service uses `model_dump()`.
        
        # I will Create a pure dictionary for the model
        db_estudiante_data = estudiante.model_dump(exclude={"crear_usuario", "rol_usuario_id", "contrasena"})
        
        # We need to pass this to DB.
        from app.models.models import Estudiante
        
        # If we didn't create a user, do we link the creator? PREVIOUSLY it did `usuario_id=current_user.id`.
        # Unlikely that was correct for "linked user". Maybe it was "created_by"?
        # But since I am implementing "Linked User", I will set it to `new_usuario_id`.
        # If `new_usuario_id` is None, `usuario_id` will be None.
        
        db_estudiante = Estudiante(**db_estudiante_data, usuario_id=new_usuario_id)
        db.add(db_estudiante)
        db.commit()
        db.refresh(db_estudiante)
        return db_estudiante

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
    except HTTPException as he:
        raise he
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

@router.delete("/{estudiante_id}")
def delete_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    try:
        db_estudiante = estudiante_service.get_estudiante(db, estudiante_id=estudiante_id)
        if db_estudiante is None:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        # Capture data before deletion to avoid issues with detached/deleted objects during serialization
        # We manually build the response to ensure all relationships are already loaded or ignored.
        result = {
            "id": db_estudiante.id,
            "nombres": db_estudiante.nombres,
            "apellidos": db_estudiante.apellidos,
            "mensaje": "Estudiante eliminado exitosamente"
        }
        
        # Perform deletion
        estudiante_service.delete_estudiante(db, estudiante_id=estudiante_id)
        
        return result
    except IntegrityError as e:
        db.rollback()
        error_str = str(e).lower()
        if "foreign key" in error_str or "conflicto" in error_str:
            raise HTTPException(
                status_code=400, 
                detail="No se puede eliminar el estudiante porque tiene registros asociados (ej. Ventas, Pagos)."
            )
        raise HTTPException(status_code=400, detail=f"Error de integridad al eliminar: {str(e)}")
    except Exception as e:
        db.rollback()
        print(f"Error deleting student {estudiante_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al eliminar: {str(e)}")
