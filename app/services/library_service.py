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
            joinedload(Prestamo.profesor),
            joinedload(Prestamo.usuario)
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

        # Determinar si es extracurricular
        es_extracurricular = False
        if prestamo_in.estudiante_id:
            es_extracurricular = LibraryService.verificar_es_extracurricular(
                db, 
                prestamo_in.estudiante_id, 
                prestamo_in.libro_id
            )

        # Create loan
        db_prestamo = Prestamo(
            **prestamo_in.model_dump(),
            usuario_registro_id=usuario_registro_id,
            es_extracurricular=es_extracurricular
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
            joinedload(Reserva.profesor),
            joinedload(Reserva.usuario)
        ).offset(skip).limit(limit).all()

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
                                  observaciones: str = None, usuario_registro_id: int = None):
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
        
        # For academic loans, usuario_id is the student ID, so we use estudiante_id field
        db_prestamo = Prestamo(
            libro_id=libro_id,
            estudiante_id=usuario_id,  # Store student ID in estudiante_id field
            tipo_prestamo="ACADEMICO",
            modulo_id=modulo_id,
            fecha_prestamo=fecha_prestamo,
            fecha_devolucion_esperada=fecha_devolucion_esperada,
            observaciones=observaciones,
            estado="ACTIVO",
            usuario_registro_id=usuario_registro_id
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
        return db.query(Prestamo).options(
            joinedload(Prestamo.libro),
            joinedload(Prestamo.estudiante),
            joinedload(Prestamo.profesor),
            joinedload(Prestamo.usuario)
        ).filter(
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
    def create_reserva_v2(db: Session, libro_id: int, usuario_id: Optional[int] = None, 
                         estudiante_id: Optional[int] = None, profesor_id: Optional[int] = None):
        """Create a book reservation for user, student, or professor"""
        # Check if book is available
        if LibraryService.verificar_disponibilidad(db, libro_id):
            raise ValueError("El libro está disponible, no es necesario reservar")
        
        # Build filter for existing active reservation
        reservation_filter = [Reserva.libro_id == libro_id, Reserva.estado == "ACTIVA"]
        
        if estudiante_id:
            reservation_filter.append(Reserva.estudiante_id == estudiante_id)
        elif profesor_id:
            reservation_filter.append(Reserva.profesor_id == profesor_id)
        elif usuario_id:
            reservation_filter.append(Reserva.usuario_id == usuario_id)
        else:
            raise ValueError("Debe especificar un usuario, estudiante o profesor")

        # Check if already has an active reservation for this book
        existing = db.query(Reserva).filter(and_(*reservation_filter)).first()
        
        if existing:
            raise ValueError("Ya existe una reserva activa para este libro")
        
        db_reserva = Reserva(
            libro_id=libro_id,
            usuario_id=usuario_id,
            estudiante_id=estudiante_id,
            profesor_id=profesor_id,
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

    @staticmethod
    def entregar_reserva(db: Session, reserva_id: int, usuario_registro_id: int):
        """Convert an active reservation into a physical loan"""
        from datetime import date, timedelta
        
        reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva:
            raise ValueError("Reserva no encontrada")
        
        if reserva.estado != "ACTIVA":
            raise ValueError(f"No se puede entregar una reserva en estado {reserva.estado}")
            
        # Verify book availability
        libro = db.query(Libro).filter(Libro.id == reserva.libro_id).first()
        if not libro or libro.cantidad_disponible < 1:
            raise ValueError("Libro no disponible para entrega")

        # Determine loan type and return date (Default to personal 7 days)
        # We could improve this by asking the type, but 7 days is a safe default for reservations
        fecha_prestamo = date.today()
        fecha_devolucion_esperada = fecha_prestamo + timedelta(days=7)
        
        # Create loan
        db_prestamo = Prestamo(
            libro_id=reserva.libro_id,
            estudiante_id=reserva.estudiante_id,
            profesor_id=reserva.profesor_id,
            usuario_id=reserva.usuario_id,
            tipo_prestamo="PERSONAL", # Defaulting to personal when picking up reservation
            fecha_prestamo=fecha_prestamo,
            fecha_devolucion_esperada=fecha_devolucion_esperada,
            estado="ACTIVO",
            usuario_registro_id=usuario_registro_id
        )
        db.add(db_prestamo)
        
        # Mark reservation as completed
        reserva.estado = "COMPLETADA"
        
        # Decrease book availability
        libro.cantidad_disponible -= 1
        
        db.commit()
        db.refresh(db_prestamo)
        return db_prestamo

    
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

    @staticmethod
    def get_libros_sugeridos_estudiante(db: Session, estudiante_id: int):
        """
        Obtiene libros sugeridos para un estudiante basado en su módulo actual.
        Retorna libros obligatorios y recomendados con información de disponibilidad.
        Check InscripcionPaquete first, then fallback to Inscripcion.
        """
        from app.models.models import Estudiante, Inscripcion, Curso, Modulo, InscripcionPaquete, Paquete
        

        try:
            # Obtener el estudiante
            estudiante = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
            if not estudiante:
                raise ValueError("Estudiante no encontrado")
            
            modulo_id = None  # Initialize to None
            error_p = ""
            error_f = ""

            # 1. Try InscripcionPaquete (New System)
            try:
                print(f"DEBUG: Checking InscripcionPaquete for student {estudiante_id}")
                inscripcion_paquete = db.query(InscripcionPaquete).join(Paquete).filter(
                    InscripcionPaquete.estudiante_id == estudiante_id,
                    InscripcionPaquete.estado_academico.in_(['INSCRITO', 'Inscrito', 'inscrito'])
                ).order_by(InscripcionPaquete.fecha_inscripcion.desc()).first()

                if inscripcion_paquete:
                    print(f"DEBUG: Found InscripcionPaquete: ID={inscripcion_paquete.id}, Paquete={inscripcion_paquete.paquete_id}")
                    if inscripcion_paquete.paquete:
                        print(f"DEBUG: Paquete found: {inscripcion_paquete.paquete.nombre}, ModuloID={inscripcion_paquete.paquete.modulo_id}")
                        if inscripcion_paquete.paquete.modulo_id:
                            modulo_id = inscripcion_paquete.paquete.modulo_id
                else:
                    print("DEBUG: No InscripcionPaquete found with status INSCRITO")
            except Exception as e:
                print(f"DEBUG: Error checking InscripcionPaquete: {e}")
                error_p = str(e)
                import traceback
                traceback.print_exc()

            # 2. Fallback to Inscripcion (Old System)
            if not modulo_id:
                print("DEBUG: Fallback to old Inscripcion table")
                try:
                    inscripcion_activa = db.query(Inscripcion).join(Curso).filter(
                        Inscripcion.estudiante_id == estudiante_id,
                        Inscripcion.estado.in_(['ACTIVO', 'Activo', 'activo'])
                    ).first()
                    
                    if inscripcion_activa:
                        print(f"DEBUG: Found old Inscripcion: {inscripcion_activa.id}")
                        if inscripcion_activa.curso and inscripcion_activa.curso.modulo_id:
                            modulo_id = inscripcion_activa.curso.modulo_id
                            print(f"DEBUG: Resolved module from old system: {modulo_id}")
                    else:
                        print("DEBUG: No ACTIVE old Inscripcion found")
                except Exception as e:
                     print(f"DEBUG: Error checking old Inscripcion: {e}")
                     error_f = str(e)
                     import traceback
                     traceback.print_exc()
            
            if not modulo_id:
                # DEBUG HACK: Return error as book
                return [{
                    "id": 0,
                    "titulo": f"ERR: P={error_p} | F={error_f}",
                    "isbn": "ERROR",
                    "autor": "SYSTEM",
                    "editorial": "DEBUG",
                    "disponible": False,
                    "copias_disponibles": 0,
                    "tipo_asignacion": "obligatorio",
                    "orden": 0,
                    "modulo_id": 0
                }]
            
            print(f"DEBUG: Fetching books for module {modulo_id}")
            
            # Obtener libros asociados al módulo (activos)
            asociaciones = db.query(ModuloLibro).options(
                joinedload(ModuloLibro.libro)
            ).filter(
                ModuloLibro.modulo_id == modulo_id,
                ModuloLibro.activo == True
            ).all()
            
            # Construir respuesta con información de disponibilidad
            libros_sugeridos = []
            
            for asoc in asociaciones:
                libro = asoc.libro
                if not libro:
                    continue
                
                # Verificar disponibilidad
                disponible = libro.cantidad_disponible > 0 if hasattr(libro, 'cantidad_disponible') else True
                copias_disponibles = libro.cantidad_disponible if hasattr(libro, 'cantidad_disponible') else 0
                
                # Get authors string
                autores_str = "Desconocido"
                if libro.libro_autores:
                    nombres_autores = []
                    for la in libro.libro_autores:
                        if la.autor:
                            nombres_autores.append(f"{la.autor.nombres} {la.autor.apellidos}")
                    if nombres_autores:
                        autores_str = ", ".join(nombres_autores)

                libros_sugeridos.append({
                    "id": libro.id,
                    "titulo": libro.titulo,
                    "isbn": libro.isbn,
                    "autor": autores_str, 
                    "editorial": libro.editorial.nombre if libro.editorial else "Sin Editorial",
                    "disponible": disponible,
                    "copias_disponibles": copias_disponibles,
                    "tipo_asignacion": asoc.tipo_asignacion,
                    "orden": asoc.orden,
                    "modulo_id": modulo_id # Return the found module ID so frontend can use it if needed
                })
            
            # Ordenar: obliga
            
            # Ordenar: obligatorios primero, luego por orden, luego por disponibilidad
            libros_sugeridos.sort(key=lambda x: (
                x["tipo_asignacion"] != "obligatorio",  # obligatorio primero
                x["orden"],  # luego por orden
                not x["disponible"]  # disponibles primero
            ))
            
            return libros_sugeridos
            
        except Exception as e:
            print(f"CRITICAL ERROR in get_libros_sugeridos_estudiante: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def verificar_es_extracurricular(db: Session, estudiante_id: int, libro_id: int) -> bool:
        """
        Verifica si un préstamo es extracurricular (libro no asociado al módulo del estudiante).
        """
        from app.models.models import Inscripcion, InscripcionPaquete, Paquete, Curso
        
        if not estudiante_id:
            return False  # Si no hay estudiante, no es extracurricular
        
        modulo_id = None
        
        # 1. Try InscripcionPaquete
        try:
            inscripcion_paquete = db.query(InscripcionPaquete).join(Paquete).filter(
                InscripcionPaquete.estudiante_id == estudiante_id,
                InscripcionPaquete.estado_academico.in_(['INSCRITO', 'Inscrito', 'inscrito'])
            ).order_by(InscripcionPaquete.fecha_inscripcion.desc()).first()

            if inscripcion_paquete and inscripcion_paquete.paquete and inscripcion_paquete.paquete.modulo_id:
                modulo_id = inscripcion_paquete.paquete.modulo_id
        except Exception as e:
            print(f"DEBUG: Error checking InscripcionPaquete in verify: {e}")

        # 2. Fallback to Inscripcion
        if not modulo_id:
            try:
                inscripcion = db.query(Inscripcion).join(Curso).filter(
                    Inscripcion.estudiante_id == estudiante_id,
                    Inscripcion.estado.in_(['ACTIVO', 'Activo', 'activo'])
                ).first()
                if inscripcion and inscripcion.curso and inscripcion.curso.modulo_id:
                     modulo_id = inscripcion.curso.modulo_id
            except Exception as e:
                print(f"DEBUG: Error checking old Inscripcion in verify: {e}")
        
        if not modulo_id:
            return True  # Sin módulo activo, considerarlo extracurricular
        
        # Verificar si el libro está asociado al módulo
        asociacion = db.query(ModuloLibro).filter(
            ModuloLibro.modulo_id == modulo_id,
            ModuloLibro.libro_id == libro_id,
            ModuloLibro.activo == True
        ).first()
        
        return asociacion is None  # Es extracurricular si no hay asociación

