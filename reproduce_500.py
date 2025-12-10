import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.models import Usuario, RolPermiso, Permiso, Funcion, Accion, TipoProducto

def test_everything():
    db = SessionLocal()
    try:
        print("1. Testing DB connection...")
        # Try a simple query
        user = db.query(Usuario).filter(Usuario.correo == 'hal.flores@gmail.com').first()
        if not user:
            print("   User 'hal.flores@gmail.com' not found. Falling back to first user.")
            user = db.query(Usuario).first()
        
        if not user:
             print("   No users found. Cannot test permissions logic properly without a user.")
        else:
            print(f"   User found: {user.nombre} {user.apellido} (ID: {user.id}, Role ID: {user.rol_id})")
            
            # 2. Test Permission Logic Simulation
            print("\n2. Testing Permission Logic...")
            required_permission = "tipos_producto.read"
            print(f"   Checking for permission: {required_permission}")
            
            has_perm = False
            if user.rol:
                print(f"   User Role: {user.rol.nombre}")
                if not user.rol.permisos:
                    print("   User role has NO permissions assigned.")
                
                for rol_permiso in user.rol.permisos:
                    try:
                        permiso = rol_permiso.permiso
                        if not permiso:
                             print(f"   [WARN] Orphan RolPermiso object found")
                             continue
                             
                        # Check for None explicitly to mirror potential crash sites
                        f_nom = permiso.funcion.nombre 
                        a_nom = permiso.accion.nombre
                        
                        permission_str = f"{f_nom}.{a_nom}"
                        # print(f"   - Validated: {permission_str}")
                        
                        if permission_str == "movimientos.read":
                            print(f"   [FOUND] movements.read permission found!")
                    except Exception as e:
                        print(f"   [CRASH] Error validation permission record: {e}")
            
            if not has_perm:
                print(f"   FAILURE: User does NOT have permission {required_permission}")

        # 3. Test TipoProducto Query and Validation
        from app.schemas.tipo_producto import TipoProductoResponse
        print("\n3. Testing TipoProducto Query and Schema Validation...")
        try:
            tipos = db.query(TipoProducto).all()
            print(f"   Query successful. Found {len(tipos)} tipos de producto.")
            for t in tipos:
                print(f"   - {t.nombre} (ID: {t.id}, Created At: {t.created_at})")
                try:
                    # Simulate Pydantic validation
                    validated = TipoProductoResponse.model_validate(t)
                    print(f"     > Validation OK: {validated}")
                except Exception as ve:
                    print(f"     > Validation FAILED: {ve}")
        except Exception as e:
            print(f"   CRASH during TipoProducto query: {e}")
            import traceback
            traceback.print_exc()

        # 4. Test Movimientos Service
        print("\n4. Testing Movimientos Service...")
        from app.services import movimientos as movimiento_service
        try:
            movs = movimiento_service.get_movimientos(db, skip=0, limit=10)
            print(f"   SUCCESS: Retrieved {len(movs)} movements.")
            for m in movs:
                print(f"   - Mov ID {m['id']}: Product {m['producto_id']} Type {m['tipo_movimiento']}")
        except Exception as e:
            print(f"   CRASH inside get_movimientos: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"General Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_everything()
