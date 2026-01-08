"""
Script para agregar funciones y permisos del módulo de Finanzas
"""
from app.db.session import SessionLocal
from app.models.models import Funcion, Accion, Permiso
from sqlalchemy.exc import IntegrityError

def add_finance_permissions():
    db = SessionLocal()
    try:
        # Definir las funciones de finanzas que necesitamos
        finance_functions = [
            ('CAJA_SESIONES', 'Gestión de sesiones de caja (abrir/cerrar)'),
            ('GASTOS', 'Registro y gestión de gastos'),
            ('CATEGORIAS_GASTO', 'Gestión de categorías de gastos'),
            ('INGRESOS_VARIOS', 'Registro de ingresos varios'),
            ('CAJA_MOVIMIENTOS', 'Consulta de movimientos de caja'),
            ('PLANES_PAGO', 'Gestión de planes de pago y cuentas por cobrar'),
            ('PAGOS_NOMINA', 'Gestión de pagos de nómina'),
            ('REPORTE_CAJA', 'Generación de reportes de caja'),
        ]
        
        # Obtener todas las acciones
        acciones = db.query(Accion).filter(Accion.nombre.in_(['read', 'create', 'update', 'delete'])).all()
        print(f"Acciones encontradas: {[a.nombre for a in acciones]}")
        
        # Crear funciones y permisos
        for func_name, func_desc in finance_functions:
            # Verificar si la función ya existe
            existing_func = db.query(Funcion).filter(Funcion.nombre == func_name).first()
            
            if not existing_func:
                # Crear la función
                new_func = Funcion(
                    nombre=func_name,
                    descripcion=func_desc
                )
                db.add(new_func)
                db.flush()  # Para obtener el ID
                print(f"✓ Función creada: {func_name}")
                funcion_id = new_func.id
            else:
                print(f"- Función ya existe: {func_name}")
                funcion_id = existing_func.id
            
            # Crear permisos para cada acción
            for accion in acciones:
                # Verificar si el permiso ya existe
                existing_perm = db.query(Permiso).filter(
                    Permiso.funcion_id == funcion_id,
                    Permiso.accion_id == accion.id
                ).first()
                
                if not existing_perm:
                    new_perm = Permiso(
                        funcion_id=funcion_id,
                        accion_id=accion.id
                    )
                    db.add(new_perm)
                    print(f"  ✓ Permiso creado: {func_name}.{accion.nombre}")
                else:
                    print(f"  - Permiso ya existe: {func_name}.{accion.nombre}")
        
        db.commit()
        print("\n✅ Script completado exitosamente")
        
        # Mostrar resumen
        print("\n=== RESUMEN ===")
        for func_name, _ in finance_functions:
            func = db.query(Funcion).filter(Funcion.nombre == func_name).first()
            if func:
                perms_count = db.query(Permiso).filter(Permiso.funcion_id == func.id).count()
                print(f"{func_name}: {perms_count} permisos")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_finance_permissions()
