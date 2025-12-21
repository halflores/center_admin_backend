from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import CategoriaGasto

def seed_categories():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    categories = [
        {"nombre": "Servicios Básicos", "descripcion": "Agua, Luz, Internet, Gas"},
        {"nombre": "Alquiler", "descripcion": "Pago de alquiler de inmuebles"},
        {"nombre": "Suministros de Oficina", "descripcion": "Papel, tinta, bolígrafos, etc."},
        {"nombre": "Limpieza y Mantenimiento", "descripcion": "Productos de limpieza y reparaciones"},
        {"nombre": "Publicidad y Marketing", "descripcion": "Redes sociales, folletos, campañas"},
        {"nombre": "Sueldos y Salarios", "descripcion": "Pagos a personal administrativo y docente"},
        {"nombre": "Impuestos y Tasas", "descripcion": "Pagos legales y municipales"},
        {"nombre": "Cafetería y Alimentos", "descripcion": "Insumos para cafetería o refrigerios"},
        {"nombre": "Equipos y Mobiliario", "descripcion": "Compra de computadoras, sillas, mesas"},
        {"nombre": "Transporte y Viáticos", "descripcion": "Movilidad y gastos de viaje"},
        {"nombre": "Otros", "descripcion": "Gastos varios no categorizados"}
    ]

    print("Seeding Expense Categories...")
    count = 0
    for cat_data in categories:
        exists = db.query(CategoriaGasto).filter(CategoriaGasto.nombre == cat_data["nombre"]).first()
        if not exists:
            cat = CategoriaGasto(**cat_data)
            db.add(cat)
            count += 1
            print(f"Adding: {cat_data['nombre']}")
        else:
            print(f"Skipping (exists): {cat_data['nombre']}")
    
    db.commit()
    print(f"Successfully added {count} categories.")
    db.close()

if __name__ == "__main__":
    seed_categories()
