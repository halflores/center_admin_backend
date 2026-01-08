"""
Script maestro para poblar la base de datos con Permisos, Funciones y Acciones iniciales.
"""
import logging
from app.db.session import SessionLocal
from app.models.models import Funcion, Accion, Permiso, Role, RolPermiso

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_all_permissions():
    db = SessionLocal()
    try:
        # 1. Crear Acciones Básicas
        acciones_base = ['create', 'read', 'update', 'delete']
        acciones_db = {}
        
        logger.info("--- Verificando Acciones ---")
        for nombre in acciones_base:
            accion = db.query(Accion).filter(Accion.nombre == nombre).first()
            if not accion:
                accion = Accion(nombre=nombre)
                db.add(accion)
                db.flush()
                logger.info(f"Acción creada: {nombre}")
            else:
                logger.info(f"Acción existente: {nombre}")
            acciones_db[nombre] = accion

        # 2. Definir Módulos y Funciones
        # Formato: (CODIGO_FUNCION, Descripción)
        modulos = [
            # Sistema
            ('USUARIOS', 'Gestión de usuarios del sistema'),
            ('ROLES', 'Gestión de roles y permisos'),
            ('PERMISOS', 'Gestión de matriz de permisos'),
            
            # Académico
            ('CAMPUS', 'Gestión de sedes'),
            ('ESTUDIANTES', 'Gestión de estudiantes'),
            ('PROGRAMAS', 'Gestión de programas académicos'),
            ('NIVELES', 'Gestión de niveles'),
            ('MODULOS', 'Gestión de módulos de estudio'),
            ('CURSOS', 'Gestión de cursos activos'),
            ('HORARIOS', 'Gestión de horarios y aulas'),
            ('INSCRIPCIONES', 'Gestión de inscripciones'),
            
            # Profesores
            ('PROFESORES', 'Gestión de profesores'),
            ('PAGOS_PROFESOR', 'Gestión de pagos a profesores'),
            
            # Finanzas
            ('CAJA_SESIONES', 'Gestión de sesiones de caja'),
            ('GASTOS', 'Gestión de gastos'),
            ('INGRESOS', 'Gestión de ingresos'),
            ('PLANES_PAGO', 'Gestión de planes de pago'),
            ('PAGOS_NOMINA', 'Gestión de nómina'),
            ('REPORTE_CAJA', 'Reportes financieros'),
            
            # Inventario
            ('CATEGORIAS_PRODUCTO', 'Gestión de categorías de productos'),
            ('PRODUCTOS', 'Gestión de productos e inventario'),
            ('TIPOS_PRODUCTO', 'Clasificación de tipos de producto'),
            ('LISTAS_PRECIOS', 'Gestión de listas de precios'),
            ('PRECIOS_PRODUCTO', 'Asignación de precios a productos'),
            ('DESCUENTOS_ESTUDIANTE', 'Gestión de descuentos por estudiante'),
            ('PROVEEDORES', 'Gestión de proveedores'),
            ('VENTAS', 'Registro y consulta de ventas'),
            ('MOVIMIENTOS', 'Seguimiento de movimientos de inventario'),
            ('DEVOLUCIONES', 'Gestión de devoluciones'),
            ('PAQUETES', 'Gestión de paquetes de productos'),
            
            # Biblioteca
            ('LIBROS', 'Gestión de libros'),
            ('AUTORES', 'Gestión de autores'),
            ('EDITORIALES', 'Gestión de editoriales'),
            ('GENEROS', 'Gestión de géneros literarios'),
            ('PRESTAMOS', 'Gestión de préstamos de libros'),
            ('RESERVAS', 'Gestión de reservas de libros'),
            
            # Otros
            ('NIVELES_FORMACION', 'Gestión de niveles de formación profesional'),
            ('TIPOS_TRANSACCION', 'Gestión de tipos de transacción/pago'),
            ('INSCRIPCIONES_PAQUETE', 'Evaluación y seguimiento de paquetes'),
            ('EBI_APP', 'Gestión de contenido App'),
        ]

        logger.info("\n--- Verificando Funciones y Permisos ---")
        
        for func_nombre, func_desc in modulos:
            # Crear Función
            funcion = db.query(Funcion).filter(Funcion.nombre == func_nombre).first()
            if not funcion:
                funcion = Funcion(nombre=func_nombre, descripcion=func_desc)
                db.add(funcion)
                db.flush()
                logger.info(f"Función creada: {func_nombre}")
            
            # Crear Permisos (CRUD) para cada función
            for accion_nombre, accion_obj in acciones_db.items():
                permiso = db.query(Permiso).filter(
                    Permiso.funcion_id == funcion.id,
                    Permiso.accion_id == accion_obj.id
                ).first()
                
                if not permiso:
                    permiso = Permiso(funcion_id=funcion.id, accion_id=accion_obj.id)
                    db.add(permiso)
                    # logger.info(f"  + Permiso {accion_nombre} creado para {func_nombre}")

        db.commit()

        # 3. Asignar TODO al Administrador
        logger.info("\n--- Asignando Permisos a Administrador ---")
        rol_admin = db.query(Role).filter(Role.nombre == "Administrador").first()
        if not rol_admin:
            rol_admin = Role(nombre="Administrador", descripcion="Acceso total")
            db.add(rol_admin)
            db.commit()
            db.refresh(rol_admin)
        
        # Obtener todos los permisos
        todos_permisos = db.query(Permiso).all()
        count_asignados = 0
        
        for perm in todos_permisos:
            rol_perm = db.query(RolPermiso).filter(
                RolPermiso.rol_id == rol_admin.id,
                RolPermiso.permiso_id == perm.id
            ).first()
            
            if not rol_perm:
                rol_perm = RolPermiso(rol_id=rol_admin.id, permiso_id=perm.id)
                db.add(rol_perm)
                count_asignados += 1
        
        db.commit()
        logger.info(f"Se asignaron {count_asignados} nuevos permisos al Administrador.")
        logger.info("Proceso finalizado exitosamente.")

    except Exception as e:
        logger.error(f"Error en seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_all_permissions()
