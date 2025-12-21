from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from app.models.models import (
    GeneroLiterario, Editorial, Autor, Libro, LibroAutor,
    Prestamo, Reserva, MultaPrestamo, ModuloLibro
)
from app.schemas.library import (
    GeneroLiterarioCreate, GeneroLiterarioUpdate,
    EditorialCreate, EditorialUpdate,
    AutorCreate, AutorUpdate,
    LibroCreate, LibroUpdate,
    PrestamoCreate, ReservaCreate
)

class LibraryService:

    # --- Géneros Literarios ---
    @staticmethod
    def get_generos(db: Session, skip: int = 0, limit: int = 100):
        return db.query(GeneroLiterario).filter(GeneroLiterario.activo == True).offset(skip).limit(limit).all()

    @staticmethod
    def create_genero(db: Session, genero_in: GeneroLiterarioCreate):
        db_genero = GeneroLiterario(**genero_in.model_dump())
        db.add(db_genero)
        db.commit()
        db.refresh(db_genero)
        return db_genero

    @staticmethod
    def update_genero(db: Session, genero_id: int, genero_in: GeneroLiterarioUpdate):
        db_genero = db.query(GeneroLiterario).filter(GeneroLiterario.id == genero_id).first()
        if not db_genero:
            return None
        
        update_data = genero_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_genero, field, value)
            
        db.commit()
        db.refresh(db_genero)
        return db_genero
    
    @staticmethod
    def delete_genero(db: Session, genero_id: int):
        db_genero = db.query(GeneroLiterario).filter(GeneroLiterario.id == genero_id).first()
        if db_genero:
            db_genero.activo = False
            db.commit()
            return True
        return False

    # --- Editoriales ---
    @staticmethod
    def get_editoriales(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Editorial).filter(Editorial.activo == True).offset(skip).limit(limit).all()
        
    @staticmethod
    def create_editorial(db: Session, editorial_in: EditorialCreate):
        db_editorial = Editorial(**editorial_in.model_dump())
        db.add(db_editorial)
        db.commit()
        db.refresh(db_editorial)
        return db_editorial
        
    @staticmethod
    def update_editorial(db: Session, editorial_id: int, editorial_in: EditorialUpdate):
        db_editorial = db.query(Editorial).filter(Editorial.id == editorial_id).first()
        if not db_editorial:
            return None
            
        update_data = editorial_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_editorial, field, value)
            
        db.commit()
        db.refresh(db_editorial)
        return db_editorial
        
    @staticmethod
    def delete_editorial(db: Session, editorial_id: int):
        db_editorial = db.query(Editorial).filter(Editorial.id == editorial_id).first()
        if db_editorial:
            db_editorial.activo = False
            db.commit()
            return True
        return False

    # --- Autores ---
    @staticmethod
    def get_autores(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Autor).filter(Autor.activo == True).offset(skip).limit(limit).all()
        
    @staticmethod
    def create_autor(db: Session, autor_in: AutorCreate):
        db_autor = Autor(**autor_in.model_dump())
        db.add(db_autor)
        db.commit()
        db.refresh(db_autor)
        return db_autor
        
    @staticmethod
    def update_autor(db: Session, autor_id: int, autor_in: AutorUpdate):
        db_autor = db.query(Autor).filter(Autor.id == autor_id).first()
        if not db_autor:
            return None
            
        update_data = autor_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_autor, field, value)
            
        db.commit()
        db.refresh(db_autor)
        return db_autor
        
    @staticmethod
    def delete_autor(db: Session, autor_id: int):
        db_autor = db.query(Autor).filter(Autor.id == autor_id).first()
        if db_autor:
            db_autor.activo = False
            db.commit()
            return True
        return False

    # --- Libros ---
    @staticmethod
    def get_libros(db: Session, skip: int = 0, limit: int = 100, 
                  genero_id: Optional[int] = None, 
                  editorial_id: Optional[int] = None,
                  search: Optional[str] = None):
        
        query = db.query(Libro).options(
            joinedload(Libro.genero),
            joinedload(Libro.editorial),
            joinedload(Libro.libro_autores).joinedload(LibroAutor.autor)
        )
        
        if genero_id:
            query = query.filter(Libro.genero_id == genero_id)
        if editorial_id:
            query = query.filter(Libro.editorial_id == editorial_id)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Libro.titulo.ilike(search_term)) | 
                (Libro.isbn.ilike(search_term))
            )
            
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_libro(db: Session, libro_id: int):
        return db.query(Libro).filter(Libro.id == libro_id).options(
            joinedload(Libro.genero),
            joinedload(Libro.editorial),
            joinedload(Libro.libro_autores).joinedload(LibroAutor.autor)
        ).first()

    @staticmethod
    def get_libro_by_isbn(db: Session, isbn: str):
        return db.query(Libro).filter(Libro.isbn == isbn).first()

    @staticmethod
    def create_libro(db: Session, libro_in: LibroCreate):
        # Extract authors ids
        autores_ids = libro_in.autores_ids
        libro_data = libro_in.model_dump(exclude={'autores_ids'})
        
        db_libro = Libro(**libro_data)
        db.add(db_libro)
        db.commit()
        db.refresh(db_libro)
        
        # Add authors
        for i, autor_id in enumerate(autores_ids):
            libro_autor = LibroAutor(
                libro_id=db_libro.id,
                autor_id=autor_id,
                orden=i+1
            )
            db.add(libro_autor)
        
        db.commit()
        db.refresh(db_libro)
        return db_libro

    @staticmethod
    def update_libro(db: Session, libro_id: int, libro_in: LibroUpdate):
        db_libro = db.query(Libro).filter(Libro.id == libro_id).first()
        if not db_libro:
            return None
            
        # Handle authors update if provided
        if libro_in.autores_ids is not None:
            # Remove existing authors
            db.query(LibroAutor).filter(LibroAutor.libro_id == libro_id).delete()
            # Add new authors
            for i, autor_id in enumerate(libro_in.autores_ids):
                libro_autor = LibroAutor(
                    libro_id=libro_id,
                    autor_id=autor_id,
                    orden=i+1
                )
                db.add(libro_autor)
        
        update_data = libro_in.model_dump(exclude={'autores_ids'}, exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_libro, field, value)
            
        db.commit()
        db.refresh(db_libro)
        return db_libro

    @staticmethod
    def delete_libro(db: Session, libro_id: int):
        db_libro = db.query(Libro).filter(Libro.id == libro_id).first()
    # --- Préstamos ---
    @staticmethod
    def get_prestamos(db: Session, skip: int = 0, limit: int = 100, 
                     estado: Optional[str] = None, 
                     usuario_id: Optional[int] = None): # estudiante o profesor id
        query = db.query(Prestamo).options(
            joinedload(Prestamo.libro),
            joinedload(Prestamo.estudiante),
            joinedload(Prestamo.profesor)
        )
        if estado:
            query = query.filter(Prestamo.estado == estado)
        # TODO: Filter by user efficiently
        return query.order_by(Prestamo.fecha_prestamo.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_prestamo(db: Session, prestamo_in: PrestamoCreate, usuario_registro_id: int):
        # Verify availability
        libro = db.query(Libro).filter(Libro.id == prestamo_in.libro_id).first()
        if not libro or libro.cantidad_disponible < 1:
            raise ValueError("Libro no disponible")

        # Create loan
        db_prestamo = Prestamo(
            **prestamo_in.model_dump(),
            usuario_registro_id=usuario_registro_id
        )
        db.add(db_prestamo)
        
        # Decrease availability
        libro.cantidad_disponible -= 1
        
        db.commit()
        db.refresh(db_prestamo)
        return db_prestamo

    @staticmethod
    def devolver_libro(db: Session, prestamo_id: int, fecha_devolucion: date, observaciones: str = None):
        prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
        if not prestamo or prestamo.estado != 'ACTIVO':
            raise ValueError("Préstamo no encontrado o ya devuelto")
            
        prestamo.fecha_devolucion_real = fecha_devolucion
        prestamo.estado = 'DEVUELTO'
        if observaciones:
            prestamo.observaciones = observaciones
            
        # Calculate fine if overdue
        if fecha_devolucion > prestamo.fecha_devolucion_esperada:
            dias_retraso = (fecha_devolucion - prestamo.fecha_devolucion_esperada).days
            prestamo.multa = dias_retraso * 2.00 # $2 per day
            
        # Increase availability
        libro = db.query(Libro).filter(Libro.id == prestamo.libro_id).first()
        if libro:
            libro.cantidad_disponible += 1
            
        db.commit()
        db.refresh(prestamo)
        return prestamo

    # --- Reservas ---
    @staticmethod
    def get_reservas(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Reserva).options(
            joinedload(Reserva.libro),
            joinedload(Reserva.estudiante),
            joinedload(Reserva.profesor)
        ).filter(Reserva.estado == 'PENDIENTE').offset(skip).limit(limit).all()

    @staticmethod
    def create_reserva(db: Session, reserva_in: ReservaCreate):
        db_reserva = Reserva(**reserva_in.model_dump())
        db.add(db_reserva)
        db.commit()
        db.refresh(db_reserva)
        return db_reserva
    
    @staticmethod
    def cancelar_reserva(db: Session, reserva_id: int):
        reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if reserva:
            reserva.estado = 'CANCELADA'
            db.commit()
            return True
        return False

    # ==================== NUEVAS FUNCIONES SISTEMA DE PRÉSTAMOS ====================
    
    @staticmethod
    def verificar_disponibilidad(db: Session, libro_id: int) -> bool:
        """Check if a book is available for loan"""
        libro = db.query(Libro).filter(Libro.id == libro_id).first()
        if not libro:
            return False
        
        prestamos_activos = db.query(Prestamo).filter(
            and_(
                Prestamo.libro_id == libro_id,
                Prestamo.estado == "ACTIVO"
            )
        ).count()
        
        return libro.cantidad_disponible > prestamos_activos
    
    @staticmethod
    def create_prestamo_personal(db: Session, libro_id: int, usuario_id: int, 
                                fecha_prestamo: date, observaciones: str = None):
        """Create a personal loan (7 days)"""
        if not LibraryService.verificar_disponibilidad(db, libro_id):
            raise ValueError("El libro no está disponible para préstamo")
        
        # Calculate return date (7 days)
        fecha_devolucion_esperada = fecha_prestamo + timedelta(days=7)
        
        db_prestamo = Prestamo(
            libro_id=libro_id,
            usuario_id=usuario_id,
            tipo_prestamo="PERSONAL",
            fecha_prestamo=fecha_prestamo,
            fecha_devolucion_esperada=fecha_devolucion_esperada,
            observaciones=observaciones,
            estado="ACTIVO"
        )
        
        db.add(db_prestamo)
        
        # Update book availability
        libro = db.query(Libro).filter(Libro.id == libro_id).first()
        if libro:
            libro.cantidad_disponible -= 1
        
        db.commit()
        db.refresh(db_prestamo)
        return db_prestamo
    
    @staticmethod
    def create_prestamo_academico(db: Session, libro_id: int, usuario_id: int, modulo_id: int,
                                  fecha_prestamo: date, fecha_devolucion_esperada: date, 
                                  observaciones: str = None):
        """Create an academic loan (module-based)"""
        if not LibraryService.verificar_disponibilidad(db, libro_id):
            raise ValueError("El libro no está disponible para préstamo")
        
        # Verify book is assigned to module
        modulo_libro = db.query(ModuloLibro).filter(
            and_(
                ModuloLibro.modulo_id == modulo_id,
                ModuloLibro.libro_id == libro_id
            )
        ).first()
        
        if not modulo_libro:
            raise ValueError("Este libro no está asignado al módulo especificado")
        
        db_prestamo = Prestamo(
            libro_id=libro_id,
            usuario_id=usuario_id,
            tipo_prestamo="ACADEMICO",
            modulo_id=modulo_id,
            fecha_prestamo=fecha_prestamo,
            fecha_devolucion_esperada=fecha_devolucion_esperada,
            observaciones=observaciones,
            estado="ACTIVO"
        )
        
        db.add(db_prestamo)
        
        # Update book availability
        libro = db.query(Libro).filter(Libro.id == libro_id).first()
        if libro:
            libro.cantidad_disponible -= 1
        
        db.commit()
        db.refresh(db_prestamo)
        return db_prestamo
    
    @staticmethod
    def calcular_multa_prestamo(prestamo: Prestamo, fecha_devolucion: date = None) -> dict:
        """Calculate late fee for a loan"""
        if not fecha_devolucion:
            fecha_devolucion = date.today()
        
        if fecha_devolucion > prestamo.fecha_devolucion_esperada:
            dias_retraso = (fecha_devolucion - prestamo.fecha_devolucion_esperada).days
            monto_multa = Decimal(str(dias_retraso * 1.00))  # 1 Bs per day
            return {
                'dias_retraso': dias_retraso,
                'monto_multa': monto_multa
            }
        
        return {'dias_retraso': 0, 'monto_multa': Decimal('0.00')}
    
    @staticmethod
    def devolver_libro_v2(db: Session, prestamo_id: int, fecha_devolucion: date, 
                         observaciones: str = None):
        """Register book return and calculate late fee if applicable"""
        prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
        if not prestamo:
            raise ValueError("Préstamo no encontrado")
        
        if prestamo.estado == "DEVUELTO":
            raise ValueError("Este libro ya fue devuelto")
        
        # Update loan
        prestamo.fecha_devolucion = fecha_devolucion
        prestamo.estado = "DEVUELTO"
        if observaciones:
            prestamo.observaciones = observaciones
        
        # Calculate late fee
        multa_info = LibraryService.calcular_multa_prestamo(prestamo, fecha_devolucion)
        prestamo.dias_retraso = multa_info['dias_retraso']
        prestamo.monto_multa = multa_info['monto_multa']
        
        # Create multa record if there's a late fee
        if multa_info['monto_multa'] > 0:
            db_multa = MultaPrestamo(
                prestamo_id=prestamo_id,
                dias_retraso=multa_info['dias_retraso'],
                monto_por_dia=Decimal('1.00'),
                monto_total=multa_info['monto_multa']
            )
            db.add(db_multa)
        
        # Update book availability
        libro = db.query(Libro).filter(Libro.id == prestamo.libro_id).first()
        if libro:
            libro.cantidad_disponible += 1
        
        db.commit()
        db.refresh(prestamo)
        
        # Notify reservations if book is now available
        LibraryService.notificar_reservas_disponibles(db, prestamo.libro_id)
        
        return prestamo
    
    @staticmethod
    def get_prestamos_atrasados(db: Session):
        """Get all overdue loans"""
        today = date.today()
        return db.query(Prestamo).filter(
            and_(
                Prestamo.estado == "ACTIVO",
                Prestamo.fecha_devolucion_esperada < today
            )
        ).all()
    
    @staticmethod
    def get_prestamos_calendario(db: Session, fecha_inicio: date, fecha_fin: date):
        """Get loans for calendar view"""
        return db.query(Prestamo).filter(
            or_(
                and_(
                    Prestamo.fecha_prestamo >= fecha_inicio,
                    Prestamo.fecha_prestamo <= fecha_fin
                ),
                and_(
                    Prestamo.fecha_devolucion_esperada >= fecha_inicio,
                    Prestamo.fecha_devolucion_esperada <= fecha_fin
                )
            )
        ).all()
    
    # ==================== MULTAS ====================
    
    @staticmethod
    def get_multas(db: Session, skip: int = 0, limit: int = 100, pagado: bool = None):
        query = db.query(MultaPrestamo)
        
        if pagado is not None:
            query = query.filter(MultaPrestamo.pagado == pagado)
        
        return query.order_by(MultaPrestamo.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def pagar_multa(db: Session, multa_id: int, metodo_pago: str, observaciones: str = None):
        """Register multa payment"""
        from datetime import datetime
        
        multa = db.query(MultaPrestamo).filter(MultaPrestamo.id == multa_id).first()
        if not multa:
            raise ValueError("Multa no encontrada")
        
        if multa.pagado:
            raise ValueError("Esta multa ya fue pagada")
        
        multa.pagado = True
        multa.fecha_pago = datetime.now()
        multa.metodo_pago = metodo_pago
        if observaciones:
            multa.observaciones = observaciones
        
        # Update prestamo
        prestamo = db.query(Prestamo).filter(Prestamo.id == multa.prestamo_id).first()
        if prestamo:
            prestamo.multa_pagada = True
        
        db.commit()
        db.refresh(multa)
        return multa
    
    # ==================== RESERVAS MEJORADAS ====================
    
    @staticmethod
    def create_reserva_v2(db: Session, libro_id: int, usuario_id: int):
        """Create a book reservation"""
        # Check if book is available
        if LibraryService.verificar_disponibilidad(db, libro_id):
            raise ValueError("El libro está disponible, no es necesario reservar")
        
        # Check if user already has an active reservation for this book
        existing = db.query(Reserva).filter(
            and_(
                Reserva.libro_id == libro_id,
                Reserva.usuario_id == usuario_id,
                Reserva.estado == "ACTIVA"
            )
        ).first()
        
        if existing:
            raise ValueError("Ya tienes una reserva activa para este libro")
        
        db_reserva = Reserva(
            libro_id=libro_id,
            usuario_id=usuario_id,
            estado="ACTIVA"
        )
        
        db.add(db_reserva)
        db.commit()
        db.refresh(db_reserva)
        return db_reserva
    
    @staticmethod
    def notificar_reservas_disponibles(db: Session, libro_id: int):
        """Notify users with active reservations when book becomes available"""
        from datetime import datetime
        
        if not LibraryService.verificar_disponibilidad(db, libro_id):
            return
        
        # Get active reservations ordered by date
        reservas = db.query(Reserva).filter(
            and_(
                Reserva.libro_id == libro_id,
                Reserva.estado == "ACTIVA",
                Reserva.notificado == False
            )
        ).order_by(Reserva.fecha_reserva).all()
        
        for reserva in reservas:
            reserva.notificado = True
            reserva.fecha_notificacion = datetime.now()
            reserva.fecha_expiracion = datetime.now() + timedelta(days=2)  # 2 days to claim
            # TODO: Send actual notification (email/SMS)
        
        db.commit()
    
    # ==================== MÓDULO-LIBROS ====================
    
    @staticmethod
    def assign_libro_to_modulo(db: Session, modulo_id: int, libro_id: int, 
                              orden: int = 1, obligatorio: bool = True, descripcion: str = None):
        """Assign a book to a module"""
        # Check if already exists
        existing = db.query(ModuloLibro).filter(
            and_(
                ModuloLibro.modulo_id == modulo_id,
                ModuloLibro.libro_id == libro_id
            )
        ).first()
        
        if existing:
            raise ValueError("Este libro ya está asignado a este módulo")
        
        db_modulo_libro = ModuloLibro(
            modulo_id=modulo_id,
            libro_id=libro_id,
            orden=orden,
            obligatorio=obligatorio,
            descripcion=descripcion
        )
        
        db.add(db_modulo_libro)
        db.commit()
        db.refresh(db_modulo_libro)
        return db_modulo_libro
    
    @staticmethod
    def get_libros_by_modulo(db: Session, modulo_id: int):
        """Get all books assigned to a module"""
        return db.query(ModuloLibro).filter(
            ModuloLibro.modulo_id == modulo_id
        ).order_by(ModuloLibro.orden).all()
    
    @staticmethod
    def remove_libro_from_modulo(db: Session, modulo_id: int, libro_id: int):
        """Remove a book from a module"""
        modulo_libro = db.query(ModuloLibro).filter(
            and_(
                ModuloLibro.modulo_id == modulo_id,
                ModuloLibro.libro_id == libro_id
            )
        ).first()
        
        if not modulo_libro:
            raise ValueError("Asignación no encontrada")
        
        db.delete(modulo_libro)
        db.commit()
        return True

