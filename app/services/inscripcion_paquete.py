from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.models.models import InscripcionPaquete, Paquete, Estudiante, Profesor
from app.schemas.inscripcion_paquete import InscripcionPaqueteCreate, InscripcionPaqueteUpdate, InscripcionPaqueteResultado
from app.services import paquete as paquete_service


def get_inscripciones_paquete(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    estudiante_id: Optional[int] = None,
    estado_academico: Optional[str] = None,
    profesor_id: Optional[int] = None
):
    query = db.query(InscripcionPaquete)
    
    if estudiante_id:
        query = query.filter(InscripcionPaquete.estudiante_id == estudiante_id)
    if estado_academico:
        query = query.filter(InscripcionPaquete.estado_academico == estado_academico)
    if profesor_id:
        # Get inscriptions for packages with courses assigned to this professor
        # For now, filter by profesor_id in inscripcion (who evaluated)
        query = query.filter(InscripcionPaquete.profesor_id == profesor_id)
    
    return query.order_by(InscripcionPaquete.fecha_inscripcion.desc()).offset(skip).limit(limit).all()


def get_inscripcion_paquete(db: Session, inscripcion_id: int):
    return db.query(InscripcionPaquete).filter(InscripcionPaquete.id == inscripcion_id).first()


def get_inscripciones_pendientes_evaluacion(db: Session, skip: int = 0, limit: int = 100):
    """Get all inscriptions pending evaluation (estado INSCRITO)"""
    return db.query(InscripcionPaquete).filter(
        InscripcionPaquete.estado_academico == 'INSCRITO'
    ).order_by(InscripcionPaquete.fecha_inscripcion.desc()).offset(skip).limit(limit).all()


def get_ultimo_paquete_aprobado(db: Session, estudiante_id: int):
    """Get the last approved package for a student"""
    return db.query(InscripcionPaquete).filter(
        InscripcionPaquete.estudiante_id == estudiante_id,
        InscripcionPaquete.estado_academico == 'APROBADO'
    ).order_by(InscripcionPaquete.fecha_resultado.desc()).first()


def create_inscripcion_paquete(db: Session, inscripcion: InscripcionPaqueteCreate):
    db_inscripcion = InscripcionPaquete(
        estudiante_id=inscripcion.estudiante_id,
        paquete_id=inscripcion.paquete_id,
        gestion_id=inscripcion.gestion_id,
        venta_id=inscripcion.venta_id,
        estado_academico='INSCRITO'
    )
    db.add(db_inscripcion)
    db.commit()
    db.refresh(db_inscripcion)
    return db_inscripcion


def update_inscripcion_paquete(db: Session, inscripcion_id: int, inscripcion: InscripcionPaqueteUpdate):
    db_inscripcion = db.query(InscripcionPaquete).filter(InscripcionPaquete.id == inscripcion_id).first()
    if not db_inscripcion:
        return None
    
    update_data = inscripcion.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_inscripcion, key, value)
    
    db.commit()
    db.refresh(db_inscripcion)
    return db_inscripcion


def set_resultado(db: Session, inscripcion_id: int, resultado: InscripcionPaqueteResultado, profesor_id: int):
    """Set the academic result for an inscription (professor action)"""
    db_inscripcion = db.query(InscripcionPaquete).filter(InscripcionPaquete.id == inscripcion_id).first()
    if not db_inscripcion:
        return None
    
    db_inscripcion.estado_academico = resultado.estado_academico
    db_inscripcion.observaciones = resultado.observaciones
    db_inscripcion.fecha_resultado = datetime.utcnow()
    db_inscripcion.profesor_id = profesor_id
    
    db.commit()
    db.refresh(db_inscripcion)
    return db_inscripcion


def get_siguiente_paquete_para_estudiante(db: Session, estudiante_id: int):
    """
    Get suggested next package based on student's last approved inscription.
    Returns the next package in the curriculum progression.
    """
    ultimo_aprobado = get_ultimo_paquete_aprobado(db, estudiante_id)
    
    if not ultimo_aprobado:
        # No previous approvals, return first available package
        primer_paquete = db.query(Paquete).filter(Paquete.activo == True).first()
        return {
            "estudiante_id": estudiante_id,
            "ultimo_aprobado": None,
            "siguiente_paquete": paquete_service.enrich_paquete_response(db, primer_paquete) if primer_paquete else None,
            "mensaje": "Estudiante sin historial de aprobaciones. Se sugiere el primer paquete disponible."
        }
    
    # Get the package details
    paquete_anterior = db.query(Paquete).filter(Paquete.id == ultimo_aprobado.paquete_id).first()
    
    if not paquete_anterior or not paquete_anterior.modulo_id:
        return {
            "estudiante_id": estudiante_id,
            "ultimo_aprobado": enrich_inscripcion_response(db, ultimo_aprobado),
            "siguiente_paquete": None,
            "mensaje": "No se puede determinar el siguiente paquete. El paquete anterior no tiene módulo asignado."
        }
    
    siguiente = paquete_service.get_siguiente_paquete(
        db,
        paquete_anterior.programa_id,
        paquete_anterior.nivel_id,
        paquete_anterior.modulo_id
    )
    
    if siguiente:
        return {
            "estudiante_id": estudiante_id,
            "ultimo_aprobado": enrich_inscripcion_response(db, ultimo_aprobado),
            "siguiente_paquete": paquete_service.enrich_paquete_response(db, siguiente),
            "mensaje": f"Siguiente paquete sugerido: {siguiente.nombre}"
        }
    
    return {
        "estudiante_id": estudiante_id,
        "ultimo_aprobado": enrich_inscripcion_response(db, ultimo_aprobado),
        "siguiente_paquete": None,
        "mensaje": "El estudiante ha completado todos los paquetes disponibles."
    }


def delete_inscripcion_paquete(db: Session, inscripcion_id: int):
    db_inscripcion = db.query(InscripcionPaquete).filter(InscripcionPaquete.id == inscripcion_id).first()
    if not db_inscripcion:
        return None
    
    db.delete(db_inscripcion)
    db.commit()
    return db_inscripcion


def enrich_inscripcion_response(db: Session, inscripcion: InscripcionPaquete) -> dict:
    """Add related names to inscription response"""
    result = {
        "id": inscripcion.id,
        "estudiante_id": inscripcion.estudiante_id,
        "paquete_id": inscripcion.paquete_id,
        "venta_id": inscripcion.venta_id,
        "gestion_id": inscripcion.gestion_id,
        "estado_academico": inscripcion.estado_academico,
        "fecha_inscripcion": inscripcion.fecha_inscripcion,
        "fecha_resultado": inscripcion.fecha_resultado,
        "profesor_id": inscripcion.profesor_id,
        "observaciones": inscripcion.observaciones,
        "created_at": inscripcion.created_at,
        "estudiante_nombres": None,
        "estudiante_apellidos": None,
        "paquete_nombre": None,
        "programa_nombre": None,
        "nivel_nombre": None,
        "modulo_nombre": None,
        "profesor_nombres": None,
        "profesor_apellidos": None
    }
    
    if inscripcion.estudiante:
        result["estudiante_nombres"] = inscripcion.estudiante.nombres
        result["estudiante_apellidos"] = inscripcion.estudiante.apellidos
    
    if inscripcion.paquete:
        result["paquete_nombre"] = inscripcion.paquete.nombre
        if inscripcion.paquete.programa:
            result["programa_nombre"] = inscripcion.paquete.programa.nombre
        if inscripcion.paquete.nivel:
            result["nivel_nombre"] = inscripcion.paquete.nivel.nombre
        if inscripcion.paquete.modulo:
            result["modulo_nombre"] = inscripcion.paquete.modulo.nombre
    
    if inscripcion.profesor:
        result["profesor_nombres"] = inscripcion.profesor.nombres
        result["profesor_apellidos"] = inscripcion.profesor.apellidos
    
    return result
