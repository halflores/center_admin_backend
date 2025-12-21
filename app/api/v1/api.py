from fastapi import APIRouter
from app.api.v1.endpoints import roles, users, login, funciones, acciones, permisos, rol_permisos, campus, estudiantes, gestion, parentesco, responsables, categorias_producto, productos, listas_precios, precios_producto, descuentos_estudiante, ventas, devoluciones, movimientos, carrito, ingresos, proveedores
from app.api.v1.endpoints import programas, niveles, modulos, profesores, cursos, horarios, inscripciones, pagos_profesores, niveles_formacion, aulas, tipos_transaccion, niveles_academicos_estudiante
from app.api.v1.endpoints import tipos_producto, paquetes, inscripciones_paquete, financial, cargos, empleados, library

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
api_router.include_router(categorias_producto.router, prefix="/categorias_producto", tags=["categorias_producto"])
api_router.include_router(productos.router, prefix="/productos", tags=["productos"])
api_router.include_router(listas_precios.router, prefix="/listas_precios", tags=["listas_precios"])
api_router.include_router(precios_producto.router, prefix="/precios_producto", tags=["precios_producto"])
api_router.include_router(descuentos_estudiante.router, prefix="/descuentos_estudiante", tags=["descuentos_estudiante"])
api_router.include_router(ventas.router, prefix="/ventas", tags=["ventas"])
api_router.include_router(devoluciones.router, prefix="/devoluciones", tags=["devoluciones"])
api_router.include_router(movimientos.router, prefix="/movimientos", tags=["movimientos"])
api_router.include_router(carrito.router, prefix="/carrito", tags=["carrito"])
api_router.include_router(ingresos.router, prefix="/ingresos", tags=["ingresos"])
api_router.include_router(proveedores.router, prefix="/proveedores", tags=["proveedores"])
api_router.include_router(tipos_transaccion.router, prefix="/tipos-transaccion", tags=["tipos_transaccion"])

# HR Module
api_router.include_router(cargos.router, prefix="/cargos", tags=["cargos"])
api_router.include_router(empleados.router, prefix="/empleados", tags=["empleados"])

# Academic Structure Endpoints
api_router.include_router(programas.router, prefix="/programas", tags=["programas"])
api_router.include_router(niveles.router, prefix="/niveles", tags=["niveles"])
api_router.include_router(modulos.router, prefix="/modulos", tags=["modulos"])
api_router.include_router(profesores.router, prefix="/profesores", tags=["profesores"])
api_router.include_router(cursos.router, prefix="/cursos", tags=["cursos"])
api_router.include_router(horarios.router, prefix="/horarios", tags=["horarios"])
api_router.include_router(inscripciones.router, prefix="/inscripciones", tags=["inscripciones"])
api_router.include_router(pagos_profesores.router, prefix="/pagos-profesores", tags=["pagos_profesores"])
api_router.include_router(niveles_formacion.router, prefix="/niveles-formacion", tags=["niveles_formacion"])
api_router.include_router(aulas.router, prefix="/aulas", tags=["aulas"])
api_router.include_router(niveles_academicos_estudiante.router, prefix="/niveles-academicos-estudiante", tags=["niveles_academicos_estudiante"])

# Enrollment Flow Endpoints
api_router.include_router(tipos_producto.router, prefix="/tipos-producto", tags=["tipos_producto"])
api_router.include_router(paquetes.router, prefix="/paquetes", tags=["paquetes"])
api_router.include_router(inscripciones_paquete.router, prefix="/inscripciones-paquete", tags=["inscripciones_paquete"])

# Financial Module Endpoints
api_router.include_router(financial.router, prefix="/finanzas", tags=["financial"])

# Library Module Endpoints
api_router.include_router(library.router, prefix="/biblioteca", tags=["Biblioteca"])
