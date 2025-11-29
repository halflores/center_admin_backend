from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api import deps
from app.schemas.ingreso import IngresoCreate, IngresoResponse
from app.services import ingreso_service
from app.services.pdf_service import generate_ingreso_pdf
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=IngresoResponse)
def create_ingreso(
    ingreso_in: IngresoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.check_permission("ingresos.create"))
):
    return ingreso_service.create_ingreso(db=db, ingreso_in=ingreso_in, current_user=current_user)

@router.get("/", response_model=List[IngresoResponse])
def read_ingresos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.check_permission("ingresos.read"))
):
    return ingreso_service.get_ingresos(db, skip=skip, limit=limit)

@router.get("/{ingreso_id}", response_model=IngresoResponse)
def read_ingreso(
    ingreso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    ingreso = ingreso_service.get_ingreso(db, ingreso_id=ingreso_id)
    if not ingreso:
        raise HTTPException(status_code=404, detail="Ingreso not found")
    return ingreso

@router.get("/{ingreso_id}/pdf")
def download_ingreso_pdf(
    ingreso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    """
    Generate and download PDF receipt for an ingreso
    """
    ingreso = ingreso_service.get_ingreso(db, ingreso_id=ingreso_id)
    if not ingreso:
        raise HTTPException(status_code=404, detail="Ingreso not found")
    
    # Convert SQLAlchemy model to dict for PDF generation
    ingreso_dict = {
        'id': ingreso.id,
        'fecha': ingreso.fecha,
        'nro_factura': ingreso.nro_factura,
        'total': ingreso.total,
        'proveedor': {
            'nombre': ingreso.proveedor.nombre if ingreso.proveedor else 'N/A',
            'direccion': ingreso.proveedor.direccion if ingreso.proveedor else None,
            'celular': ingreso.proveedor.celular if ingreso.proveedor else None,
        } if ingreso.proveedor else None,
        'usuario': {
            'nombre': f"{ingreso.usuario.nombre} {ingreso.usuario.apellido}" if ingreso.usuario else 'N/A'
        } if ingreso.usuario else None,
        'detalles': [
            {
                'producto': {'nombre': d.producto.nombre if d.producto else 'N/A'},
                'cantidad': d.cantidad,
                'costo_unitario': d.costo_unitario,
                'subtotal': d.subtotal
            } for d in ingreso.detalles
        ]
    }
    
    # Generate PDF
    pdf_buffer = generate_ingreso_pdf(ingreso_dict)
    
    # Return as downloadable file
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=ingreso_{ingreso_id}.pdf"
        }
    )

