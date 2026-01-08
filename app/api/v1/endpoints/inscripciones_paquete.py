from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.api.deps import get_current_user, check_permission
from app.models.models import Usuario, Profesor
from app.schemas.inscripcion_paquete import (
    InscripcionPaqueteCreate, InscripcionPaqueteUpdate, 
    InscripcionPaqueteResponse, InscripcionPaqueteResultado,
    SiguientePaqueteResponse
)
from app.services import inscripcion_paquete as inscripcion_service

router = APIRouter()


@router.get("/", response_model=List[InscripcionPaqueteResponse])
def get_inscripciones_paquete(
    skip: int = 0,
    limit: int = 100,
    estudiante_id: Optional[int] = None,
    estado_academico: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("inscripciones_paquete.read"))
):
    """Get all package inscriptions with optional filters"""
    inscripciones = inscripcion_service.get_inscripciones_paquete(
        db, skip=skip, limit=limit, 
        estudiante_id=estudiante_id, 
        estado_academico=estado_academico
    )
    return [inscripcion_service.enrich_inscripcion_response(db, i) for i in inscripciones]


@router.get("/pendientes", response_model=List[InscripcionPaqueteResponse])
def get_inscripciones_pendientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("inscripciones_paquete.read"))
):
    """Get inscriptions pending evaluation (for professors)"""
    inscripciones = inscripcion_service.get_inscripciones_pendientes_evaluacion(db, skip=skip, limit=limit)
    return [inscripcion_service.enrich_inscripcion_response(db, i) for i in inscripciones]


@router.get("/estudiante/{estudiante_id}/siguiente", response_model=SiguientePaqueteResponse)
def get_siguiente_paquete(
    estudiante_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("inscripciones_paquete.read"))
):
    """Get suggested next package for a student based on their progress"""
    return inscripcion_service.get_siguiente_paquete_para_estudiante(db, estudiante_id)


@router.get("/{inscripcion_id}", response_model=InscripcionPaqueteResponse)
def get_inscripcion_paquete(
    inscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("inscripciones_paquete.read"))
):
    """Get a specific package inscription by ID"""
    db_inscripcion = inscripcion_service.get_inscripcion_paquete(db, inscripcion_id)
    if not db_inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return inscripcion_service.enrich_inscripcion_response(db, db_inscripcion)


@router.post("/", response_model=InscripcionPaqueteResponse, status_code=status.HTTP_201_CREATED)
def create_inscripcion_paquete(
    inscripcion: InscripcionPaqueteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("inscripciones_paquete.create"))
):
    """Create a new package inscription"""
    db_inscripcion = inscripcion_service.create_inscripcion_paquete(db, inscripcion)
    return inscripcion_service.enrich_inscripcion_response(db, db_inscripcion)


@router.put("/{inscripcion_id}", response_model=InscripcionPaqueteResponse)
def update_inscripcion_paquete(
    inscripcion_id: int,
    inscripcion: InscripcionPaqueteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("inscripciones_paquete.update"))
):
    """Update a package inscription"""
    db_inscripcion = inscripcion_service.update_inscripcion_paquete(db, inscripcion_id, inscripcion)
    if not db_inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return inscripcion_service.enrich_inscripcion_response(db, db_inscripcion)


@router.put("/{inscripcion_id}/resultado", response_model=InscripcionPaqueteResponse)
def set_resultado(
    inscripcion_id: int,
    resultado: InscripcionPaqueteResultado,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("inscripciones_paquete.update"))
):
    """Set academic result for an inscription (professor action)"""
    # Validate estado_academico
    if resultado.estado_academico not in ['APROBADO', 'REPROBADO']:
        raise HTTPException(status_code=400, detail="Estado académico debe ser APROBADO o REPROBADO")
    
    # Get professor ID if current user is a professor
    profesor = db.query(Profesor).filter(Profesor.usuario_id == current_user.id).first()
    profesor_id = profesor.id if profesor else None
    
    db_inscripcion = inscripcion_service.set_resultado(db, inscripcion_id, resultado, profesor_id)
    if not db_inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return inscripcion_service.enrich_inscripcion_response(db, db_inscripcion)


@router.delete("/{inscripcion_id}")
def delete_inscripcion_paquete(
    inscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("inscripciones_paquete.delete"))
):
    """Delete a package inscription"""
    db_inscripcion = inscripcion_service.delete_inscripcion_paquete(db, inscripcion_id)
    if not db_inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return {"message": "Inscripción eliminada correctamente"}
