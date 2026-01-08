
"""
Script para poblar datos académicos iniciales: Campus, Programas, Niveles, Módulos.
"""
import logging
from app.db.session import SessionLocal
from app.models.models import Campus, Programa, Nivel, Modulo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_academic_data():
    db = SessionLocal()
    try:
        # 1. Campus
        logger.info("--- Sembrando Campus ---")
        campus_list = [
            {"nombre": "Sede Principal", "direccion": "Av. Heroinas", "celular": "70707070"},
            {"nombre": "Sede Norte", "direccion": "Av. America", "celular": "60606060"},
        ]
        
        for c_data in campus_list:
            exists = db.query(Campus).filter(Campus.nombre == c_data["nombre"]).first()
            if not exists:
                c = Campus(**c_data)
                db.add(c)
                logger.info(f"Campus creado: {c_data['nombre']}")
            else:
                logger.info(f"Campus existe: {c_data['nombre']}")
        db.commit()

        # 2. Programas
        logger.info("\n--- Sembrando Programas ---")
        programas = [
            ("Inglés Adultos", "Programa completo para adultos"),
            ("Inglés Children", "Programa especial para niños"),
            ("Francés", "Programa de idioma francés"),
        ]
        
        for nombre, desc in programas:
            p = db.query(Programa).filter(Programa.nombre == nombre).first()
            if not p:
                p = Programa(nombre=nombre, descripcion=desc, activo=True)
                db.add(p)
                db.flush()
                logger.info(f"Programa creado: {nombre}")
            
            # 3. Niveles y Módulos (Ejemplo para Inglés Adultos)
            if nombre == "Inglés Adultos":
                sembrar_niveles_ingles(db, p.id)

        db.commit()
        logger.info("\nDatos académicos poblados exitosamente.")

    except Exception as e:
        logger.error(f"Error seeding academic data: {e}")
        db.rollback()
    finally:
        db.close()

def sembrar_niveles_ingles(db, programa_id):
    niveles = [
        {"codigo": "A1", "nombre": "Básico", "orden": 1},
        {"codigo": "A2", "nombre": "Pre-Intermedio", "orden": 2},
        {"codigo": "B1", "nombre": "Intermedio", "orden": 3},
    ]
    
    for n_data in niveles:
        nv = db.query(Nivel).filter(Nivel.programa_id == programa_id, Nivel.codigo == n_data["codigo"]).first()
        if not nv:
            nv = Nivel(programa_id=programa_id, **n_data)
            db.add(nv)
            db.flush()
            logger.info(f"  + Nivel creado: {n_data['nombre']}")
            
            # Crear módulos para el nivel (ejemplo genérico)
            for i in range(1, 4):
                mod_nombre = f"Módulo {i} - {n_data['nombre']}"
                mod = db.query(Modulo).filter(Modulo.nivel_id == nv.id, Modulo.nombre == mod_nombre).first()
                if not mod:
                    mod = Modulo(nivel_id=nv.id, nombre=mod_nombre, codigo=f"{n_data['codigo']}.{i}", orden=i)
                    db.add(mod)
                    # logger.info(f"    - Módulo creado: {mod_nombre}")

if __name__ == "__main__":
    seed_academic_data()
