from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.venta import VentaCreate, VentaResponse
from app.services import ventas as venta_service
from app.services.pdf_service import generate_venta_pdf
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=VentaResponse)
def create_venta(venta: VentaCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    try:
        return venta_service.create_venta(db=db, venta=venta, usuario_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[VentaResponse])
def read_ventas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return venta_service.get_ventas(db, skip=skip, limit=limit)

@router.get("/{venta_id}", response_model=VentaResponse)
def read_venta(venta_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_venta = venta_service.get_venta(db, venta_id=venta_id)
    if db_venta is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Debug logging
    print(f"DEBUG: Venta ID: {db_venta.id}")
    print(f"DEBUG: Usuario ID: {db_venta.usuario_id}")
    print(f"DEBUG: Usuario Obj: {db_venta.usuario}")
    if db_venta.usuario:
        print(f"DEBUG: Usuario Nombre: {db_venta.usuario.nombre}")
        
    return db_venta

@router.get("/{venta_id}/pdf")
def download_venta_pdf(
    venta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    """
    Generate and download PDF receipt for a sale
    """
    venta = venta_service.get_venta(db, venta_id=venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Convert SQLAlchemy model to dict for PDF generation
    venta_dict = {
        'id': venta.id,
        'fecha': venta.fecha,
        'cliente_nombre': venta.cliente_nombre,
        'total': venta.total,
        'campus': {
            'nombre': venta.estudiante.campus.nombre if venta.estudiante and venta.estudiante.campus else 'N/A'
        },
        'usuario': {
            'nombre': f"{venta.usuario.nombre} {venta.usuario.apellido}" if venta.usuario else 'N/A'
        } if venta.usuario else None,
        'estudiante': {
            'nombres': venta.estudiante.nombres,
            'apellidos': venta.estudiante.apellidos
        } if venta.estudiante else None,
        'detalles': [
            {
                'producto': {'nombre': d.producto.nombre if d.producto else 'N/A'},
                'cantidad': d.cantidad,
                'precio_unitario': d.precio_unitario,
                'descuento': d.descuento
            } for d in venta.detalles
        ]
    }
    
    # Generate PDF
    pdf_buffer = generate_venta_pdf(venta_dict)
    
    # Return as downloadable file
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=venta_{venta_id}.pdf"
        }
    )

@router.post("/{venta_id}/cancel", response_model=VentaResponse)
def cancel_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user) # TODO: Add specific permission check
):
    try:
        return venta_service.cancel_venta(db=db, venta_id=venta_id, usuario_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
