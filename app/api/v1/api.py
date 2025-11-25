from fastapi import APIRouter
from app.api.v1.endpoints import roles, users, login, funciones, acciones, permisos, rol_permisos, campus, estudiantes, gestion, parentesco, responsables

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(funciones.router, prefix="/funciones", tags=["funciones"])
api_router.include_router(acciones.router, prefix="/acciones", tags=["acciones"])
api_router.include_router(permisos.router, prefix="/permisos", tags=["permisos"])
api_router.include_router(rol_permisos.router, prefix="/rol_permisos", tags=["rol_permisos"])
api_router.include_router(campus.router, prefix="/campus", tags=["campus"])
api_router.include_router(estudiantes.router, prefix="/estudiantes", tags=["estudiantes"])
api_router.include_router(gestion.router, prefix="/gestion", tags=["gestion"])
api_router.include_router(parentesco.router, prefix="/parentesco", tags=["parentesco"])
api_router.include_router(responsables.router, prefix="/responsables", tags=["responsables"])
