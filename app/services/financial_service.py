from sqlalchemy.orm import Session, joinedload
from app.models.models import (
    CategoriaGasto, Gasto, CajaSesion, CajaMovimiento, 
    PlanPago, DetallePlanPago, PagoNomina, Usuario
)
from app.schemas.financial import (
    CategoriaGastoCreate, CategoriaGastoUpdate,
    GastoCreate, GastoUpdate, CajaSesionCreate, CajaSesionClose,
    PlanPagoCreate, PagoCuotaCreate, PagoNominaCreate, PagoNominaUpdate
)
from datetime import datetime
from fastapi import HTTPException
from app.services.movimientos import MovimientoService

class FinancialService:

    # --- Categorias Gasto ---
    @staticmethod
    def create_categoria_gasto(db: Session, categoria: CategoriaGastoCreate):
        db_cat = CategoriaGasto(**categoria.model_dump())
        db.add(db_cat)
        db.commit()
        db.refresh(db_cat)
        return db_cat

    @staticmethod
    def get_categorias_gasto(db: Session, skip: int = 0, limit: int = 100):
        # Return all (active or not? Usually we want active for dropdowns, but maybe all for management list)
        # For management list we might want all. Let's filter by default active=True for now, 
        # but maybe we should add a parameter.
        return db.query(CategoriaGasto).filter(CategoriaGasto.activo == True).offset(skip).limit(limit).all()

    @staticmethod
    def update_categoria_gasto(db: Session, categoria_id: int, categoria_in: CategoriaGastoUpdate):
        db_cat = db.query(CategoriaGasto).filter(CategoriaGasto.id == categoria_id).first()
        if not db_cat:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
        update_data = categoria_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cat, field, value)
            
        db.add(db_cat)
        db.commit()
        db.refresh(db_cat)
        return db_cat

    @staticmethod
    def delete_categoria_gasto(db: Session, categoria_id: int):
        db_cat = db.query(CategoriaGasto).filter(CategoriaGasto.id == categoria_id).first()
        if not db_cat:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
        # Soft delete
        db_cat.activo = False
        db.add(db_cat)
        db.commit()
        return db_cat

    # --- Gastos ---
    @staticmethod
    def create_gasto(db: Session, gasto: GastoCreate, usuario_id: int):
        # Verify Session is Open? Optional, but good practice for ensuring money comes from somewhere.
        # For now, just record it.
        
        db_gasto = Gasto(**gasto.model_dump(), usuario_id=usuario_id)
        db.add(db_gasto)
        db.commit()
        db.refresh(db_gasto)
        
        # Record Movement in Cash Flow
        FinancialService.register_movement(
            db, 
            tipo="EGRESO", 
            categoria="GASTO", 
            monto=gasto.monto, 
            descripcion=f"Gasto: {gasto.descripcion}", 
            usuario_id=usuario_id,
            referencia_tabla="gastos",
            referencia_id=db_gasto.id,
            metodo_pago=gasto.metodo_pago,
            numero_voucher=gasto.comprobante_referencia
        )
        
        return db_gasto

    @staticmethod
    def get_gastos(db: Session, skip: int = 0, limit: int = 100, fecha_inicio: datetime = None, fecha_fin: datetime = None):
        query = db.query(Gasto)
        if fecha_inicio:
            query = query.filter(Gasto.fecha_gasto >= fecha_inicio)
        if fecha_fin:
            # Set time to end of day: 23:59:59
            fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(Gasto.fecha_gasto <= fecha_fin)
        return query.order_by(Gasto.fecha_gasto.desc()).offset(skip).limit(limit).all()
        
    @staticmethod
    def update_gasto(db: Session, gasto_id: int, gasto_update: GastoUpdate, usuario_id: int):
        gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
        if not gasto:
            return None
            
        # Update fields
        update_data = gasto_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(gasto, key, value)
            
        # Update associated cash movement if exists
        mov = db.query(CajaMovimiento).filter(
            CajaMovimiento.referencia_tabla == 'gastos', 
            CajaMovimiento.referencia_id == gasto.id
        ).first()
        
        if mov:
            if gasto_update.monto is not None:
                mov.monto = gasto_update.monto
            if gasto_update.descripcion is not None:
                # Keep original format if possible or just update description
                mov.descripcion = f"Gasto: {gasto_update.descripcion}" 
                
        db.commit()
        db.refresh(gasto)
        return gasto

    @staticmethod
    def delete_gasto(db: Session, gasto_id: int):
        gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
        if not gasto:
            return False
            
        # Delete associated cash movement
        db.query(CajaMovimiento).filter(
            CajaMovimiento.referencia_tabla == 'gastos',
            CajaMovimiento.referencia_id == gasto.id
        ).delete()
        
        db.delete(gasto)
        db.commit()
        return True

    # --- Caja (Cash Flow) ---
    @staticmethod
    def get_active_session(db: Session, usuario_id: int):
        return db.query(CajaSesion).filter(
            CajaSesion.usuario_id == usuario_id, 
            CajaSesion.estado == 'ABIERTA'
        ).first()

    @staticmethod
    def open_session(db: Session, session_in: CajaSesionCreate, usuario_id: int):
        active = FinancialService.get_active_session(db, usuario_id)
        if active:
            raise HTTPException(status_code=400, detail="Ya existe una sesión abierta para este usuario.")
        
        db_session = CajaSesion(**session_in.model_dump(), usuario_id=usuario_id, estado='ABIERTA')
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        # Initial Balance Movement if > 0
        if db_session.monto_inicial > 0:
            FinancialService.register_movement(
                db, 
                tipo="INGRESO", 
                categoria="APERTURA", 
                monto=db_session.monto_inicial, 
                descripcion="Monto inicial de apertura", 
                usuario_id=usuario_id,
                sesion_id=db_session.id
            )
            
        return db_session

    @staticmethod
    def close_session(db: Session, close_data: CajaSesionClose, usuario_id: int):
        from app.models.models import CajaArqueo # Inner import to avoid circular dependency if any

        session = FinancialService.get_active_session(db, usuario_id)
        if not session:
            raise HTTPException(status_code=400, detail="No hay sesión abierta para cerrar.")
            
        # Calculate expected amount based on movements
        ingress = db.query(CajaMovimiento).filter(
            CajaMovimiento.sesion_id == session.id, 
            CajaMovimiento.tipo == 'INGRESO'
        ).all()
        
        egress = db.query(CajaMovimiento).filter(
            CajaMovimiento.sesion_id == session.id, 
            CajaMovimiento.tipo == 'EGRESO'
        ).all()
        
        total_ingreso = sum(m.monto for m in ingress)
        total_egreso = sum(m.monto for m in egress)
        
        expected = session.monto_inicial + total_ingreso - total_egreso
        
        real_amount = close_data.monto_final_real

        # Process Arqueo if provided
        if close_data.arqueo:
             # Create Arqueo Record
             arqueo_db = CajaArqueo(
                 caja_sesion_id=session.id,
                 **close_data.arqueo.model_dump()
             )
             db.add(arqueo_db)
             # If arqueo is provided, we might want to prioritize its total or just use it as backup.
             # Typically usage: User inputs bills, client calculates total, sends everything.
             # We can verify:
             # calculated_arqueo = ...
             # For now, trust the sent total or the manually entered one.
             # If close_data.monto_final_real matches arqueo.monto_total, good.
             
             if close_data.arqueo.monto_total != real_amount:
                 # Warning or overwrite? Let's overwrite real_amount with arqueo total if they differ? 
                 # Or just assume real_amount is the source of truth for the session record.
                 pass

        session.fecha_cierre = datetime.utcnow()
        session.monto_final_esperado = expected
        session.monto_final_real = real_amount
        session.diferencia = real_amount - expected
        session.observaciones = close_data.observaciones
        session.estado = 'CERRADA'
        
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def register_movement(db: Session, tipo: str, categoria: str, monto: float, descripcion: str, usuario_id: int, sesion_id: int = None, referencia_tabla: str = None, referencia_id: int = None, metodo_pago: str = None, numero_voucher: str = None):
        if sesion_id is None:
            # Try to associate with active session of user
            active = FinancialService.get_active_session(db, usuario_id)
            if active:
                sesion_id = active.id
        
        mov = CajaMovimiento(
            sesion_id=sesion_id,
            tipo=tipo,
            categoria=categoria,
            monto=monto,
            descripcion=descripcion,
            usuario_id=usuario_id,
            referencia_tabla=referencia_tabla,
            referencia_id=referencia_id,
            metodo_pago=metodo_pago,
            numero_voucher=numero_voucher
        )
        db.add(mov)
        db.commit()
        return mov

    @staticmethod
    def get_movimientos(db: Session, sesion_id: int = None, usuario_id: int = None, fecha_inicio: datetime=None, fecha_fin: datetime=None, skip: int = 0, limit: int = 100):
        query = db.query(CajaMovimiento).options(joinedload(CajaMovimiento.usuario))
        if sesion_id:
            query = query.filter(CajaMovimiento.sesion_id == sesion_id)
        if usuario_id:
             query = query.filter(CajaMovimiento.usuario_id == usuario_id)
        if fecha_inicio:
             query = query.filter(CajaMovimiento.fecha >= fecha_inicio)
        if fecha_fin:
             query = query.filter(CajaMovimiento.fecha <= fecha_fin)
             
        return query.order_by(CajaMovimiento.fecha.desc()).offset(skip).limit(limit).all()

    # --- Cuentas por Cobrar (Receivables) ---
    @staticmethod
    def create_plan_pago(db: Session, plan: PlanPagoCreate):
        # Calculate pending
        pago = PlanPago(
            **plan.model_dump(),
            saldo_pendiente=plan.monto_total,
            estado='PENDIENTE'
        )
        db.add(pago)
        db.commit()
        db.refresh(pago)
        return pago

    @staticmethod
    def register_cuota_payment(db: Session, plan_id: int, payment: PagoCuotaCreate, usuario_id: int):
        plan = db.query(PlanPago).options(joinedload(PlanPago.estudiante)).filter(PlanPago.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan de pago no encontrado")
            
        if plan.estado == 'PAGADO':
             raise HTTPException(status_code=400, detail="El plan ya está pagado totalmente")

        # Create Payment Detail
        detalle = DetallePlanPago(
            plan_pago_id=plan.id,
            monto=payment.monto,
            metodo_pago=payment.metodo_pago,
            referencia_pago=payment.referencia_pago,
            usuario_id=usuario_id
        )
        db.add(detalle)
        
        # Update Plan
        # Use simple addition, SQLAlchemy handles Decimal conversion if standard types are used
        plan.monto_pagado = plan.monto_pagado + payment.monto
        plan.saldo_pendiente = plan.monto_total - plan.monto_pagado
        
        if plan.saldo_pendiente <= 0:
            plan.estado = 'PAGADO'
            plan.saldo_pendiente = 0 # Prevent negative
        else:
            plan.estado = 'PARCIAL'
            
        db.commit()
        
        # Register Cash Movement
        FinancialService.register_movement(
            db,
            tipo="INGRESO",
            categoria="COBRO_CUOTA",
            monto=payment.monto,
            descripcion=f"Pago cuota: {plan.estudiante.nombres} {plan.estudiante.apellidos}" if plan.estudiante else f"Pago cuota estudiante: {plan.estudiante_id}",
            usuario_id=usuario_id,
            referencia_tabla="detalle_plan_pago",
            referencia_id=detalle.id,
            metodo_pago=payment.metodo_pago,
            numero_voucher=payment.referencia_pago
        )
        
        db.refresh(plan)
        # Ensure relationships are loaded for Pydantic
        return db.query(PlanPago).options(joinedload(PlanPago.estudiante)).filter(PlanPago.id == plan.id).first()

    @staticmethod
    def get_pending_plans(db: Session, estudiante_id: int = None):
        query = db.query(PlanPago).options(joinedload(PlanPago.estudiante)).filter(PlanPago.estado != 'PAGADO')
        if estudiante_id:
            query = query.filter(PlanPago.estudiante_id == estudiante_id)
        return query.all()

    # --- Nomina ---
    @staticmethod
    def register_nomina_payment(db: Session, nomina: PagoNominaCreate, admin_id: int):
        payment = PagoNomina(
            **nomina.model_dump(),
            usuario_admin_id=admin_id,
            estado='PAGADO' # Assume immediate payment or modify flow
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Get Employee Details for Description
        employee = db.query(Usuario).filter(Usuario.id == nomina.usuario_empleado_id).first()
        employee_name = f"{employee.nombre} {employee.apellido}" if employee else str(nomina.usuario_empleado_id)

        # Register Cash Movement
        FinancialService.register_movement(
            db,
            tipo="EGRESO",
            categoria="NOMINA",
            monto=nomina.monto,
            descripcion=f"Pago nomina a {employee_name} - {payment.tipo_pago}",
            usuario_id=admin_id,
            referencia_tabla="pagos_nomina",
            referencia_id=payment.id,
            metodo_pago=nomina.metodo_pago,
            numero_voucher=nomina.nro_transaccion
        )
        
        return payment

    @staticmethod
    def get_nomina_payments(db: Session, skip: int = 0, limit: int = 100):
        return db.query(PagoNomina).order_by(PagoNomina.fecha_pago.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_nomina_payment(db: Session, pago_id: int, pago_in: PagoNominaUpdate):
        payment = db.query(PagoNomina).filter(PagoNomina.id == pago_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
            
        # Update fields
        update_data = pago_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)
            
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Update corresponding Cash Movement if amount changed
        mov = db.query(CajaMovimiento).filter(
            CajaMovimiento.referencia_tabla == 'pagos_nomina',
            CajaMovimiento.referencia_id == payment.id
        ).first()
        
        if mov:
            if 'monto' in update_data:
                mov.monto = payment.monto
            if 'descripcion' in update_data:
                # Get Employee Details for Description
                employee = db.query(Usuario).filter(Usuario.id == payment.usuario_empleado_id).first()
                employee_name = f"{employee.nombre} {employee.apellido}" if employee else str(payment.usuario_empleado_id)
                mov.descripcion = f"Pago nomina a {employee_name} - {payment.tipo_pago}" # Re-generate description or use update_data
            
            db.add(mov)
            db.commit()
            
        return payment

    @staticmethod
    def delete_nomina_payment(db: Session, pago_id: int):
        payment = db.query(PagoNomina).filter(PagoNomina.id == pago_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
            
        # Find associated movement
        mov = db.query(CajaMovimiento).filter(
            CajaMovimiento.referencia_tabla == 'pagos_nomina',
            CajaMovimiento.referencia_id == payment.id
        ).first()
        
        if mov:
            db.delete(mov)
            
        db.delete(payment)
        db.commit()
        return payment
