from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user, get_current_active_user
from app.models.models import Usuario
from app.schemas.financial import (
    CategoriaGastoCreate, CategoriaGastoOut, CategoriaGastoUpdate,
    GastoCreate, GastoUpdate, GastoOut,
    CajaSesionCreate, CajaSesionClose, CajaSesionOut, CajaMovimientoOut,
    PlanPagoCreate, PlanPagoOut, PagoCuotaCreate,
    PagoNominaCreate, PagoNominaOut, PagoNominaUpdate
)
from app.services.financial_service import FinancialService

router = APIRouter()

# --- Categorias Gasto ---
@router.post("/gastos/categorias", response_model=CategoriaGastoOut)
def create_categoria_gasto(
    categoria: CategoriaGastoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.create_categoria_gasto(db, categoria)

@router.get("/gastos/categorias", response_model=List[CategoriaGastoOut])
def read_categorias_gasto(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.get_categorias_gasto(db, skip=skip, limit=limit)

@router.put("/gastos/categorias/{categoria_id}", response_model=CategoriaGastoOut)
def update_categoria_gasto(
    categoria_id: int,
    categoria: CategoriaGastoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.update_categoria_gasto(db, categoria_id, categoria)

@router.delete("/gastos/categorias/{categoria_id}", response_model=CategoriaGastoOut)
def delete_categoria_gasto(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return FinancialService.delete_categoria_gasto(db, categoria_id)

# --- Gastos ---
@router.post("/gastos", response_model=GastoOut)
def register_gasto(gasto: GastoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return FinancialService.create_gasto(db, gasto, current_user.id)

@router.put("/gastos/{gasto_id}", response_model=GastoOut)
def update_gasto(gasto_id: int, gasto: GastoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    updated_gasto = FinancialService.update_gasto(db, gasto_id, gasto, current_user.id)
    if not updated_gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return updated_gasto

@router.delete("/gastos/{gasto_id}")
def delete_gasto(gasto_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    success = FinancialService.delete_gasto(db, gasto_id)
    if not success:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return {"message": "Gasto eliminado correctamente"}

@router.get("/gastos", response_model=List[GastoOut])
def get_gastos(
    skip: int = 0, 
    limit: int = 100, 
    fecha_inicio: datetime = None, 
    fecha_fin: datetime = None,
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_active_user)
):
    return FinancialService.get_gastos(db, skip=skip, limit=limit, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

# --- Caja ---
@router.get("/caja/sesion", response_model=Optional[CajaSesionOut])
def get_active_session(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.get_active_session(db, current_user.id)

@router.post("/caja/abrir", response_model=CajaSesionOut)
def open_session(
    sesion: CajaSesionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Depending on roles, maybe only admin or specific role can open?
    # For now, allow active user.
    return FinancialService.open_session(db, sesion, current_user.id)

@router.post("/caja/cerrar", response_model=CajaSesionOut)
def close_session(
    data: CajaSesionClose,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.close_session(db, data, current_user.id)


@router.get("/caja/movimientos", response_model=List[CajaMovimientoOut])
def read_movimientos(
    sesion_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.get_movimientos(db, sesion_id, usuario_id, fecha_inicio, fecha_fin, skip, limit)

@router.get("/caja/reporte-pdf")
def download_reporte_caja_pdf(
    sesion_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Generate and download PDF report for cash movements
    """
    from fastapi.responses import StreamingResponse
    from app.services.pdf_service import generate_reporte_caja_pdf
    from app.models.models import CajaSesion, CajaArqueo
    
    # Get movements with all data
    movements = FinancialService.get_movimientos(db, sesion_id, usuario_id, fecha_inicio, fecha_fin, skip=0, limit=1000)
    
    # Convert to dict for PDF generation
    movements_data = []
    for mov in movements:
        movements_data.append({
            'id': mov.id,
            'fecha': mov.fecha,
            'tipo': mov.tipo,
            'categoria': mov.categoria,
            'monto': float(mov.monto),
            'descripcion': mov.descripcion,
            'metodo_pago': mov.metodo_pago,
            'numero_voucher': mov.numero_voucher,
            'usuario': {
                'nombre': f"{mov.usuario.nombre} {mov.usuario.apellido}" if mov.usuario else 'N/A'
            } if mov.usuario else None
        })
    
    # Get arqueo data if filtering by session or date range
    arqueo_data = None
    if sesion_id:
        # Get arqueo for specific session
        sesion = db.query(CajaSesion).filter(CajaSesion.id == sesion_id).first()
        if sesion and sesion.arqueo:
            arqueo_data = {
                'billetes_200': sesion.arqueo.billetes_200,
                'billetes_100': sesion.arqueo.billetes_100,
                'billetes_50': sesion.arqueo.billetes_50,
                'billetes_20': sesion.arqueo.billetes_20,
                'billetes_10': sesion.arqueo.billetes_10,
                'monedas_5': sesion.arqueo.monedas_5,
                'monedas_2': sesion.arqueo.monedas_2,
                'monedas_1': sesion.arqueo.monedas_1,
                'monedas_050': sesion.arqueo.monedas_050,
                'monedas_020': sesion.arqueo.monedas_020,
                'monedas_010': sesion.arqueo.monedas_010,
                'monto_total': float(sesion.arqueo.monto_total)
            }
    elif fecha_inicio and fecha_fin:
        # Get most recent closed session in date range
        sesion = db.query(CajaSesion).filter(
            CajaSesion.fecha_cierre >= fecha_inicio,
            CajaSesion.fecha_cierre <= fecha_fin,
            CajaSesion.estado == 'CERRADA'
        ).order_by(CajaSesion.fecha_cierre.desc()).first()
        
        if sesion and sesion.arqueo:
            arqueo_data = {
                'billetes_200': sesion.arqueo.billetes_200,
                'billetes_100': sesion.arqueo.billetes_100,
                'billetes_50': sesion.arqueo.billetes_50,
                'billetes_20': sesion.arqueo.billetes_20,
                'billetes_10': sesion.arqueo.billetes_10,
                'monedas_5': sesion.arqueo.monedas_5,
                'monedas_2': sesion.arqueo.monedas_2,
                'monedas_1': sesion.arqueo.monedas_1,
                'monedas_050': sesion.arqueo.monedas_050,
                'monedas_020': sesion.arqueo.monedas_020,
                'monedas_010': sesion.arqueo.monedas_010,
                'monto_total': float(sesion.arqueo.monto_total)
            }
    
    # Generate PDF - pass current_user for signature and arqueo data
    pdf_buffer = generate_reporte_caja_pdf(
        movements_data, 
        fecha_inicio, 
        fecha_fin, 
        current_user=current_user,
        arqueo_data=arqueo_data
    )
    
    # Generate filename
    filename = "reporte_caja"
    if fecha_inicio and fecha_fin:
        filename += f"_{fecha_inicio.date()}_{fecha_fin.date()}"
    filename += ".pdf"
    
    # Return as downloadable file
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )



# --- Cuentas por Cobrar ---
@router.get("/cuentas-cobrar", response_model=List[PlanPagoOut])
def read_plans_pending(
    estudiante_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.get_pending_plans(db, estudiante_id)

@router.post("/cuentas-cobrar/{plan_id}/pagar", response_model=PlanPagoOut)
def pay_installment(
    plan_id: int,
    payment: PagoCuotaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.register_cuota_payment(db, plan_id, payment, current_user.id)

# --- Nomina ---
@router.post("/nomina", response_model=PagoNominaOut)
def pay_payroll(
    nomina: PagoNominaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.register_nomina_payment(db, nomina, current_user.id)

@router.get("/nomina", response_model=List[PagoNominaOut])
def read_payroll(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.get_nomina_payments(db, skip, limit)

@router.put("/nomina/{pago_id}", response_model=PagoNominaOut)
def update_payroll_payment(
    pago_id: int,
    nomina: PagoNominaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.update_nomina_payment(db, pago_id, nomina)

@router.delete("/nomina/{pago_id}", response_model=PagoNominaOut)
def delete_payroll_payment(
    pago_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return FinancialService.delete_nomina_payment(db, pago_id)
