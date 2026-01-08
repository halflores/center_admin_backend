from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Usuario
from app.db.session import get_db
from app.schemas.user import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/login/access-token")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Usuario:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
        if token_data is None:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(Usuario).filter(Usuario.id == int(token_data)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    # if not current_user.activo:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def check_permission(required_permission: str):
    def permission_checker(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
        # Check if user is superadmin or has Administrador role
        if current_user.rol and current_user.rol.nombre == "Administrador":
            return current_user
        
        # Check if user has the specific permission via their role
        has_perm = False
        if current_user.rol:
            for rol_permiso in current_user.rol.permisos:
                permiso = rol_permiso.permiso
                permission_str = f"{permiso.funcion.nombre}.{permiso.accion.nombre}"
                if permission_str.lower() == required_permission.lower():
                    has_perm = True
                    break
        
        if not has_perm:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {required_permission}",
            )
        return current_user
    return permission_checker
