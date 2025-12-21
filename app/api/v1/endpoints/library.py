from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.api.deps import get_db, get_current_user
from app.models.models import Usuario
from app.services.library_service import LibraryService
from app.schemas.library import (
    GeneroLiterarioCreate, GeneroLiterarioUpdate, GeneroLiterarioOut,
    EditorialCreate, EditorialUpdate, EditorialOut,
    AutorCreate, AutorUpdate, AutorOut,
    LibroCreate, LibroUpdate, LibroOut, LibroOutDetailed,
    PrestamoCreate, PrestamoOut,
    MultaPrestamoOut,
    ReservaCreate, ReservaOut,
    ModuloLibroOut
)

router = APIRouter()

# --- Géneros Literarios ---
@router.get("/generos", response_model=List[GeneroLiterarioOut])
def read_generos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return LibraryService.get_generos(db, skip=skip, limit=limit)

@router.post("/generos", response_model=GeneroLiterarioOut)
def create_genero(genero_in: GeneroLiterarioCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return LibraryService.create_genero(db, genero_in)

@router.put("/generos/{genero_id}", response_model=GeneroLiterarioOut)
def update_genero(genero_id: int, genero_in: GeneroLiterarioUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    genero = LibraryService.update_genero(db, genero_id, genero_in)
    if not genero:
        raise HTTPException(status_code=404, detail="Género no encontrado")
    return genero

@router.delete("/generos/{genero_id}")
def delete_genero(genero_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if LibraryService.delete_genero(db, genero_id):
        return {"msg": "Género eliminado"}
    raise HTTPException(status_code=404, detail="Género no encontrado")

# --- Editoriales ---
@router.get("/editoriales", response_model=List[EditorialOut])
def read_editoriales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return LibraryService.get_editoriales(db, skip=skip, limit=limit)

@router.post("/editoriales", response_model=EditorialOut)
def create_editorial(editorial_in: EditorialCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return LibraryService.create_editorial(db, editorial_in)

@router.put("/editoriales/{editorial_id}", response_model=EditorialOut)
def update_editorial(editorial_id: int, editorial_in: EditorialUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    editorial = LibraryService.update_editorial(db, editorial_id, editorial_in)
    if not editorial:
        raise HTTPException(status_code=404, detail="Editorial no encontrada")
    return editorial

@router.delete("/editoriales/{editorial_id}")
def delete_editorial(editorial_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if LibraryService.delete_editorial(db, editorial_id):
        return {"msg": "Editorial eliminada"}
    raise HTTPException(status_code=404, detail="Editorial no encontrada")

# --- Autores ---
@router.get("/autores", response_model=List[AutorOut])
def read_autores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return LibraryService.get_autores(db, skip=skip, limit=limit)

@router.post("/autores", response_model=AutorOut)
def create_autor(autor_in: AutorCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return LibraryService.create_autor(db, autor_in)

@router.put("/autores/{autor_id}", response_model=AutorOut)
def update_autor(autor_id: int, autor_in: AutorUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    autor = LibraryService.update_autor(db, autor_id, autor_in)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor

@router.delete("/autores/{autor_id}")
def delete_autor(autor_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if LibraryService.delete_autor(db, autor_id):
        return {"msg": "Autor eliminado"}
    raise HTTPException(status_code=404, detail="Autor no encontrado")

# --- Libros ---
@router.get("/libros", response_model=List[LibroOutDetailed])
def read_libros(
    skip: int = 0, 
    limit: int = 100, 
    genero_id: Optional[int] = None,
    editorial_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return LibraryService.get_libros(db, skip=skip, limit=limit, genero_id=genero_id, editorial_id=editorial_id, search=search)

@router.get("/libros/{libro_id}", response_model=LibroOutDetailed)
def read_libro(libro_id: int, db: Session = Depends(get_db)):
    libro = LibraryService.get_libro(db, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro

@router.get("/libros/isbn/{isbn}", response_model=LibroOutDetailed)
def read_libro_by_isbn(isbn: str, db: Session = Depends(get_db)):
    libro = LibraryService.get_libro_by_isbn(db, isbn)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro

@router.post("/libros", response_model=LibroOut)
def create_libro(libro_in: LibroCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return LibraryService.create_libro(db, libro_in)

@router.put("/libros/{libro_id}", response_model=LibroOut)
def update_libro(libro_id: int, libro_in: LibroUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    libro = LibraryService.update_libro(db, libro_id, libro_in)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro

@router.delete("/libros/{libro_id}")
def delete_libro(libro_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if LibraryService.delete_libro(db, libro_id):
        return {"msg": "Libro eliminado"}
    raise HTTPException(status_code=404, detail="Libro no encontrado")

# --- Préstamos ---
@router.get("/prestamos", response_model=List[PrestamoOut])
def read_prestamos(
    skip: int = 0, 
    limit: int = 100, 
    estado: Optional[str] = None,
    usuario_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return LibraryService.get_prestamos(db, skip=skip, limit=limit, estado=estado, usuario_id=usuario_id)

@router.post("/prestamos", response_model=PrestamoOut)
def create_prestamo(prestamo_in: PrestamoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    try:
        return LibraryService.create_prestamo(db, prestamo_in, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/prestamos/{prestamo_id}/devolver", response_model=PrestamoOut)
def devolver_libro(
    prestamo_id: int, 
    fecha_devolucion: date, 
    observaciones: Optional[str] = None, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return LibraryService.devolver_libro(db, prestamo_id, fecha_devolucion, observaciones)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Reservas ---
@router.get("/reservas", response_model=List[ReservaOut])
def read_reservas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return LibraryService.get_reservas(db, skip=skip, limit=limit)

@router.post("/reservas", response_model=ReservaOut)
def create_reserva(reserva_in: ReservaCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return LibraryService.create_reserva(db, reserva_in)

@router.put("/reservas/{reserva_id}/cancelar")
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if LibraryService.cancelar_reserva(db, reserva_id):
        return {"msg": "Reserva cancelada"}
    raise HTTPException(status_code=404, detail="Reserva no encontrada")


# ==================== NUEVOS ENDPOINTS SISTEMA DE PRÉSTAMOS ====================

# --- Préstamos Personales ---
@router.post("/prestamos/personal", response_model=PrestamoOut)
def create_prestamo_personal(
    libro_id: int,
    usuario_id: int,
    fecha_prestamo: date,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a personal loan (7 days)"""
    try:
        return LibraryService.create_prestamo_personal(
            db, libro_id, usuario_id, fecha_prestamo, observaciones
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Préstamos Académicos ---
@router.post("/prestamos/academico", response_model=PrestamoOut)
def create_prestamo_academico(
    libro_id: int,
    usuario_id: int,
    modulo_id: int,
    fecha_prestamo: date,
    fecha_devolucion_esperada: date,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Create an academic loan (module-based)"""
    try:
        return LibraryService.create_prestamo_academico(
            db, libro_id, usuario_id, modulo_id, 
            fecha_prestamo, fecha_devolucion_esperada, observaciones
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Devolución de Libros ---
@router.post("/prestamos/{prestamo_id}/devolver", response_model=PrestamoOut)
def devolver_libro(
    prestamo_id: int,
    fecha_devolucion: date,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Register book return and calculate late fee"""
    try:
        return LibraryService.devolver_libro_v2(db, prestamo_id, fecha_devolucion, observaciones)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Consultas de Préstamos ---
@router.get("/prestamos/atrasados", response_model=List[PrestamoOut])
def get_prestamos_atrasados(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get all overdue loans"""
    return LibraryService.get_prestamos_atrasados(db)


@router.get("/prestamos/calendario", response_model=List[PrestamoOut])
def get_prestamos_calendario(
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get loans for calendar view"""
    return LibraryService.get_prestamos_calendario(db, fecha_inicio, fecha_fin)


@router.get("/prestamos/usuario/{usuario_id}", response_model=List[PrestamoOut])
def get_prestamos_usuario(
    usuario_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get loans by user"""
    return LibraryService.get_prestamos(db, skip=skip, limit=limit, usuario_id=usuario_id)


# --- Multas ---
@router.get("/multas", response_model=List[MultaPrestamoOut])
def get_multas(
    skip: int = 0,
    limit: int = 100,
    pagado: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get all late fees"""
    return LibraryService.get_multas(db, skip=skip, limit=limit, pagado=pagado)


@router.post("/multas/{multa_id}/pagar", response_model=MultaPrestamoOut)
def pagar_multa(
    multa_id: int,
    metodo_pago: str,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Register multa payment"""
    try:
        return LibraryService.pagar_multa(db, multa_id, metodo_pago, observaciones)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Reservas Mejoradas ---
@router.post("/reservas/v2", response_model=ReservaOut)
def create_reserva_v2(
    libro_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a book reservation with validation"""
    try:
        return LibraryService.create_reserva_v2(db, libro_id, usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reservas/usuario/{usuario_id}", response_model=List[ReservaOut])
def get_reservas_usuario(
    usuario_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get reservations by user"""
    return LibraryService.get_reservas(db, skip=skip, limit=limit, usuario_id=usuario_id)


# --- Módulo-Libros ---
@router.post("/modulos/{modulo_id}/libros", response_model=ModuloLibroOut)
def assign_libro_to_modulo(
    modulo_id: int,
    libro_id: int,
    orden: int = 1,
    obligatorio: bool = True,
    descripcion: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Assign a book to a module"""
    try:
        return LibraryService.assign_libro_to_modulo(
            db, modulo_id, libro_id, orden, obligatorio, descripcion
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/modulos/{modulo_id}/libros", response_model=List[ModuloLibroOut])
def get_libros_by_modulo(
    modulo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get all books assigned to a module"""
    return LibraryService.get_libros_by_modulo(db, modulo_id)


@router.delete("/modulos/{modulo_id}/libros/{libro_id}")
def remove_libro_from_modulo(
    modulo_id: int,
    libro_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove a book from a module"""
    try:
        LibraryService.remove_libro_from_modulo(db, modulo_id, libro_id)
        return {"msg": "Libro removido del módulo"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Disponibilidad ---
@router.get("/libros/{libro_id}/disponibilidad")
def check_disponibilidad(
    libro_id: int,
    db: Session = Depends(get_db)
):
    """Check if a book is available for loan"""
    disponible = LibraryService.verificar_disponibilidad(db, libro_id)
    return {"libro_id": libro_id, "disponible": disponible}

