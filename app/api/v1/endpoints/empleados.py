from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext

from app.api.deps import get_db
from app.models.models import Empleado, Usuario, Role
from app.schemas.empleado import EmpleadoCreate, EmpleadoUpdate, EmpleadoResponse, EmpleadoDetailResponse

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@router.get("/", response_model=List[EmpleadoDetailResponse])
def read_empleados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    empleados = db.query(Empleado).offset(skip).limit(limit).all()
    return empleados

@router.post("/", response_model=EmpleadoDetailResponse)
def create_empleado(empleado: EmpleadoCreate, db: Session = Depends(get_db)):
    try:
        # Check if CI exists
        if db.query(Empleado).filter(Empleado.ci == empleado.ci).first():
            raise HTTPException(status_code=400, detail="Empleado with this CI already exists")
        
        empleado_data = empleado.dict(exclude={"crear_usuario", "rol_usuario_id", "contrasena"})
        nuevo_empleado = Empleado(**empleado_data)
        
        # Handle optional User creation
        if empleado.crear_usuario:
            if not empleado.correo:
                 raise HTTPException(status_code=400, detail="Email is required to create a user")
            
            # Check if user email exists
            if db.query(Usuario).filter(Usuario.correo == empleado.correo).first():
                 raise HTTPException(status_code=400, detail="User with this email already exists")
    
            # Determine password
            raw_password = empleado.contrasena if empleado.contrasena else empleado.ci
            hashed_password = get_password_hash(raw_password)
            
            rol_id = empleado.rol_usuario_id
            if not rol_id:
                # Fallback: Find role 'Empleado' or use first available just to be safe (though risky)
                 rol = db.query(Role).filter(Role.nombre.in_(['Empleado', 'Usuario', 'User'])).first()
                 if rol:
                     rol_id = rol.id
                 else:
                     # If no suitable role, raise error
                     if not rol_id:
                          raise HTTPException(status_code=400, detail="Role ID required for user creation and no default found")
            
            nuevo_usuario = Usuario(
                nombre=empleado.nombres,
                apellido=empleado.apellidos,
                correo=empleado.correo,
                contrasena=hashed_password,
                rol_id=rol_id,
                activo=True
            )
            db.add(nuevo_usuario)
            db.flush() # Get ID
            
            nuevo_empleado.usuario_id = nuevo_usuario.id
    
        db.add(nuevo_empleado)
        db.commit()
        db.refresh(nuevo_empleado)
        return nuevo_empleado
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc() # Log to docker console
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/{empleado_id}", response_model=EmpleadoDetailResponse)
def read_empleado(empleado_id: int, db: Session = Depends(get_db)):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado not found")
    return empleado

@router.put("/{empleado_id}", response_model=EmpleadoDetailResponse)
def update_empleado(empleado_id: int, empleado: EmpleadoUpdate, db: Session = Depends(get_db)):
    db_empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if db_empleado is None:
        raise HTTPException(status_code=404, detail="Empleado not found")
    
    update_data = empleado.dict(exclude_unset=True)
    
    # Logic to update user if needed could go here, but usually kept separate except for maybe email/name sync.
    # We will just update empleado fields for now.
    
    for key, value in update_data.items():
        setattr(db_empleado, key, value)
    
    db.commit()
    db.refresh(db_empleado)
    return db_empleado

@router.delete("/{empleado_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_empleado(empleado_id: int, db: Session = Depends(get_db)):
    db_empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if db_empleado is None:
        raise HTTPException(status_code=404, detail="Empleado not found")
    
    db.delete(db_empleado)
    db.commit()
    return None
