
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import Prestamo, Estudiante

def inspect_loans():
    db = SessionLocal()
    try:
        prestamos = db.query(Prestamo).filter(Prestamo.tipo_prestamo == 'ACADEMICO').all()
        print(f"Found {len(prestamos)} academic loans")
        for p in prestamos:
            print(f"ID: {p.id}, EstudianteID: {p.estudiante_id}, UsuarioID: {p.usuario_id}, Estado: {p.estado}")
            if p.estudiante_id:
                estudiante = db.query(Estudiante).get(p.estudiante_id)
                print(f"  -> Estudiante: {estudiante.nombres} {estudiante.apellidos}" if estudiante else "  -> Estudiante NOT FOUND")
            else:
                print("  -> No Estudiante ID")
                
            # Check relationship access directly
            print(f"  -> Relationship 'estudiante': {p.estudiante}")

    finally:
        db.close()

if __name__ == "__main__":
    inspect_loans()
