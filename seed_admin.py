import logging
from app.db.session import SessionLocal
from app.models.models import Usuario, Role
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_admin():
    db = SessionLocal()
    try:
        # 1. Ensure Role exists
        rol = db.query(Role).filter(Role.nombre == "Administrador").first()
        if not rol:
            logger.info("Creating default role: Administrador")
            rol = Role(nombre="Administrador", descripcion="Rol con acceso total")
            db.add(rol)
            db.commit()
            db.refresh(rol)
        
        # 2. Check User
        email = "hal.flores@gmail.com"
        password_plain = "07.Hector"
        
        user = db.query(Usuario).filter(Usuario.correo == email).first()
        
        if user:
            logger.info(f"User {email} exists. Updating password...")
            user.contrasena = get_password_hash(password_plain)
            user.rol_id = rol.id
            user.activo = True
            db.commit()
            logger.info("Password updated successfully.")
        else:
            logger.info(f"Creating user {email}...")
            user = Usuario(
                nombre="Hector",
                apellido="Flores",
                correo=email,
                contrasena=get_password_hash(password_plain),
                rol_id=rol.id,
                activo=True
            )
            db.add(user)
            db.commit()
            logger.info("User created successfully.")

    except Exception as e:
        logger.error(f"Error seeding admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
