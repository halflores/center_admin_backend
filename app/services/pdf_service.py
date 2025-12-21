"""
PDF Generation Service for Ingreso Receipts
Generates half-page (letter size) receipts for inventory purchases
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from datetime import datetime
from decimal import Decimal

def generate_ingreso_pdf(ingreso_data: dict) -> BytesIO:
    """
    Generate a PDF receipt for an ingreso (inventory purchase)
    
    Args:
        ingreso_data: Dictionary containing ingreso information
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    
    # Half page letter size: 8.5" x 5.5"
    page_width = 8.5 * inch
    page_height = 5.5 * inch
    
    # Create PDF
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    # Margins
    left_margin = 0.5 * inch
    right_margin = page_width - 0.5 * inch
    top_margin = page_height - 0.5 * inch
    
    # Current Y position
    y = top_margin
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, y, "COMPROBANTE DE INGRESO")
    y -= 0.3 * inch
    
    # Horizontal line
    c.setLineWidth(1)
    c.line(left_margin, y, right_margin, y)
    y -= 0.3 * inch
    
    # Ingreso Info
    c.setFont("Helvetica", 10)
    
    # Left column
    c.drawString(left_margin, y, f"Nro: {ingreso_data.get('id', 'N/A')}")
    
    # Right column
    fecha = ingreso_data.get('fecha', datetime.now())
    if isinstance(fecha, str):
        fecha_str = fecha.split('T')[0]
    else:
        fecha_str = fecha.strftime('%d/%m/%Y')
    c.drawRightString(right_margin, y, f"Fecha: {fecha_str}")
    y -= 0.2 * inch
    
    # Provider info
    proveedor = ingreso_data.get('proveedor', {})
    if proveedor:
        c.drawString(left_margin, y, f"Proveedor: {proveedor.get('nombre', 'N/A')}")
        y -= 0.15 * inch
        if proveedor.get('direccion'):
            c.setFont("Helvetica", 9)
            c.drawString(left_margin + 0.2 * inch, y, f"Dir: {proveedor.get('direccion')}")
            y -= 0.15 * inch
        if proveedor.get('celular'):
            c.drawString(left_margin + 0.2 * inch, y, f"Tel: {proveedor.get('celular')}")
            y -= 0.15 * inch
        c.setFont("Helvetica", 10)
    
    # Invoice number
    nro_factura = ingreso_data.get('nro_factura')
    if nro_factura:
        c.drawString(left_margin, y, f"Factura: {nro_factura}")
        y -= 0.2 * inch
    
    y -= 0.1 * inch
    
    # Products table
    detalles = ingreso_data.get('detalles', [])
    
    if detalles:
        # Table header
        table_data = [['Producto', 'Cant', 'Costo Unit.', 'Subtotal']]
        
        # Table rows
        for detalle in detalles:
            producto_nombre = detalle.get('producto', {}).get('nombre', 'N/A') if isinstance(detalle.get('producto'), dict) else 'N/A'
            cantidad = detalle.get('cantidad', 0)
            costo = float(detalle.get('costo_unitario', 0))
            subtotal = float(detalle.get('subtotal', 0))
            
            table_data.append([
                producto_nombre[:30],  # Truncate long names
                str(cantidad),
                f"${costo:.2f}",
                f"${subtotal:.2f}"
            ])
        
        # Create table
        col_widths = [3.5 * inch, 0.6 * inch, 1 * inch, 1 * inch]
        table = Table(table_data, colWidths=col_widths)
        
        # Table style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ]))
        
        # Calculate table height and draw
        table_width, table_height = table.wrap(0, 0)
        table.drawOn(c, left_margin, y - table_height)
        y -= table_height + 0.2 * inch
    
    # Total
    c.setLineWidth(1)
    c.line(left_margin, y, right_margin, y)
    y -= 0.2 * inch
    
    c.setFont("Helvetica-Bold", 12)
    total = float(ingreso_data.get('total', 0))
    c.drawRightString(right_margin, y, f"TOTAL: ${total:.2f}")
    y -= 0.3 * inch
    
    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(left_margin, y, f"Usuario: {ingreso_data.get('usuario', {}).get('nombre', 'N/A') if isinstance(ingreso_data.get('usuario'), dict) else 'N/A'}")
    y -= 0.15 * inch
    
    # Signature line
    y -= 0.3 * inch
    c.line(left_margin, y, left_margin + 2 * inch, y)
    y -= 0.15 * inch
    c.setFont("Helvetica", 8)
    c.drawString(left_margin, y, "Firma Responsable")
    
    # Finalize PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

def generate_venta_pdf(venta_data: dict) -> BytesIO:
    """
    Generate a PDF receipt for a sale
    
    Args:
        venta_data: Dictionary containing sale information
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    
    # Half page letter size: 8.5" x 5.5"
    page_width = 8.5 * inch
    page_height = 5.5 * inch
    
    # Create PDF
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    # Margins
    left_margin = 0.5 * inch
    right_margin = page_width - 0.5 * inch
    top_margin = page_height - 0.5 * inch
    
    # Current Y position
    y = top_margin
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, y, "COMPROBANTE DE VENTA")
    y -= 0.3 * inch
    
    # Horizontal line
    c.setLineWidth(1)
    c.line(left_margin, y, right_margin, y)
    y -= 0.3 * inch
    
    # Venta Info
    c.setFont("Helvetica", 10)
    
    # Left column
    c.drawString(left_margin, y, f"Nro: {venta_data.get('id', 'N/A')}")
    
    # Right column
    fecha = venta_data.get('fecha', datetime.now())
    if isinstance(fecha, str):
        fecha_str = fecha.split('T')[0]
    else:
        fecha_str = fecha.strftime('%d/%m/%Y')
    c.drawRightString(right_margin, y, f"Fecha: {fecha_str}")
    y -= 0.2 * inch
    
    # Campus info
    campus_nombre = venta_data.get('campus', {}).get('nombre', 'N/A')
    c.drawString(left_margin, y, f"Campus: {campus_nombre}")
    y -= 0.2 * inch
    
    # Student info if available
    estudiante = venta_data.get('estudiante')
    if estudiante:
        estudiante_nombre = f"{estudiante.get('nombres', '')} {estudiante.get('apellidos', '')}".strip()
        c.drawString(left_margin, y, f"Estudiante: {estudiante_nombre}")
        y -= 0.2 * inch

    y -= 0.1 * inch
    
    # Products table
    detalles = venta_data.get('detalles', [])
    
    if detalles:
        # Table header
        table_data = [['Producto', 'Cant', 'Precio Unit.', 'Desc.', 'Subtotal']]
        
        # Table rows
        for detalle in detalles:
            producto_nombre = detalle.get('producto', {}).get('nombre', 'N/A') if isinstance(detalle.get('producto'), dict) else 'N/A'
            cantidad = detalle.get('cantidad', 0)
            precio = float(detalle.get('precio_unitario', 0))
            descuento = float(detalle.get('descuento', 0))
            subtotal = (precio - descuento) * cantidad
            
            table_data.append([
                producto_nombre[:25],  # Truncate long names
                str(cantidad),
                f"${precio:.2f}",
                f"${descuento:.2f}",
                f"${subtotal:.2f}"
            ])
        
        # Create table
        col_widths = [3.0 * inch, 0.5 * inch, 0.9 * inch, 0.8 * inch, 0.9 * inch]
        table = Table(table_data, colWidths=col_widths)
        
        # Table style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ]))
        
        # Calculate table height and draw
        table_width, table_height = table.wrap(0, 0)
        table.drawOn(c, left_margin, y - table_height)
        y -= table_height + 0.2 * inch
    
    # Total
    c.setLineWidth(1)
    c.line(left_margin, y, right_margin, y)
    y -= 0.2 * inch
    
    c.setFont("Helvetica-Bold", 12)
    total = float(venta_data.get('total', 0))
    c.drawRightString(right_margin, y, f"TOTAL: ${total:.2f}")
    y -= 0.3 * inch
    
    # Footer
    c.setFont("Helvetica", 9)
    usuario_nombre = venta_data.get('usuario', {}).get('nombre', 'N/A') if isinstance(venta_data.get('usuario'), dict) else 'N/A'
    c.drawString(left_margin, y, f"Atendido por: {usuario_nombre}")
    y -= 0.15 * inch
    
    # Signature line
    y -= 0.3 * inch
    c.line(left_margin, y, left_margin + 2 * inch, y)
    y -= 0.15 * inch
    c.setFont("Helvetica", 8)
    c.drawString(left_margin, y, "Firma Cliente")
    
    # Finalize PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

def generate_reporte_caja_pdf(movements_data: list, fecha_inicio=None, fecha_fin=None, current_user=None, arqueo_data=None) -> BytesIO:
    """
    Generate a PDF report for cash movements
    
    Args:
        movements_data: List of movement dictionaries
        fecha_inicio: Start date for the report
        fecha_fin: End date for the report
        current_user: Current logged-in user (for signature)
        arqueo_data: Cash count data (bills and coins)
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    
    # Full page letter size
    page_width, page_height = letter
    
    # Create PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Margins
    left_margin = 0.75 * inch
    right_margin = page_width - 0.75 * inch
    top_margin = page_height - 0.75 * inch
    bottom_margin = 0.75 * inch
    
    # Current Y position
    y = top_margin
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(page_width / 2, y, "REPORTE DE FLUJO DE CAJA")
    y -= 0.4 * inch
    
    # Date range
    c.setFont("Helvetica", 11)
    if fecha_inicio and fecha_fin:
        fecha_inicio_str = fecha_inicio.strftime('%d/%m/%Y') if not isinstance(fecha_inicio, str) else fecha_inicio.split('T')[0]
        fecha_fin_str = fecha_fin.strftime('%d/%m/%Y') if not isinstance(fecha_fin, str) else fecha_fin.split('T')[0]
        c.drawCentredString(page_width / 2, y, f"Período: {fecha_inicio_str} - {fecha_fin_str}")
    else:
        c.drawCentredString(page_width / 2, y, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 0.3 * inch
    
    # Horizontal line
    c.setLineWidth(1)
    c.line(left_margin, y, right_margin, y)
    y -= 0.4 * inch
    
    # Calculate totals
    total_ingresos = sum(m['monto'] for m in movements_data if m['tipo'] == 'INGRESO')
    total_egresos = sum(m['monto'] for m in movements_data if m['tipo'] == 'EGRESO')
    balance = total_ingresos - total_egresos
    
    # Summary boxes
    c.setFont("Helvetica-Bold", 10)
    box_width = 2.2 * inch
    box_x1 = left_margin
    box_x2 = left_margin + box_width + 0.2 * inch
    box_x3 = left_margin + (box_width + 0.2 * inch) * 2
    
    # Ingresos box
    c.setFillColorRGB(0.9, 1, 0.9)
    c.rect(box_x1, y - 0.5 * inch, box_width, 0.5 * inch, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(box_x1 + 0.1 * inch, y - 0.2 * inch, "INGRESOS:")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(box_x1 + box_width - 0.1 * inch, y - 0.4 * inch, f"${total_ingresos:.2f}")
    
    # Egresos box
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(1, 0.9, 0.9)
    c.rect(box_x2, y - 0.5 * inch, box_width, 0.5 * inch, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(box_x2 + 0.1 * inch, y - 0.2 * inch, "EGRESOS:")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(box_x2 + box_width - 0.1 * inch, y - 0.4 * inch, f"${total_egresos:.2f}")
    
    # Balance box
    c.setFont("Helvetica-Bold", 10)
    balance_color = (0.9, 0.9, 1) if balance >= 0 else (1, 0.9, 0.9)
    c.setFillColorRGB(*balance_color)
    c.rect(box_x3, y - 0.5 * inch, box_width, 0.5 * inch, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(box_x3 + 0.1 * inch, y - 0.2 * inch, "BALANCE:")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(box_x3 + box_width - 0.1 * inch, y - 0.4 * inch, f"${balance:.2f}")
    
    y -= 0.7 * inch
    
    # Movements table
    if movements_data:
        # Table header
        table_data = [['Fecha', 'Tipo', 'Categoría', 'Descripción', 'Usuario', 'Método', 'Voucher', 'Monto']]
        
        # Table rows
        for mov in movements_data:
            fecha = mov.get('fecha', datetime.now())
            if isinstance(fecha, str):
                fecha_str = fecha.split('T')[0] + ' ' + fecha.split('T')[1][:5]
            else:
                fecha_str = fecha.strftime('%d/%m %H:%M')
            
            tipo = mov.get('tipo', 'N/A')
            categoria = mov.get('categoria', 'N/A')[:15]
            descripcion = mov.get('descripcion', '')[:30]
            usuario = mov.get('usuario', {}).get('nombre', 'N/A') if mov.get('usuario') else 'N/A'
            metodo = mov.get('metodo_pago', '-')[:10] if mov.get('metodo_pago') else '-'
            voucher = mov.get('numero_voucher', '-')[:12] if mov.get('numero_voucher') else '-'
            monto = mov.get('monto', 0)
            
            # Format monto with sign
            monto_str = f"${monto:.2f}" if tipo == 'INGRESO' else f"-${monto:.2f}"
            
            table_data.append([
                fecha_str,
                tipo[:3],  # ING or EGR
                categoria,
                descripcion,
                usuario[:15],
                metodo,
                voucher,
                monto_str
            ])
        
        # Create table with adjusted column widths
        col_widths = [0.9*inch, 0.5*inch, 0.9*inch, 1.8*inch, 0.9*inch, 0.7*inch, 0.8*inch, 0.7*inch]
        
        # Check if we need pagination
        rows_per_page = 25
        total_pages = (len(table_data) - 1 + rows_per_page - 1) // rows_per_page  # -1 for header, ceiling division
        
        for page_num in range(total_pages):
            if page_num > 0:
                c.showPage()
                y = top_margin
            
            # Get rows for this page
            start_row = page_num * rows_per_page + 1  # +1 to skip header on subsequent pages
            end_row = min(start_row + rows_per_page, len(table_data))
            
            # Always include header
            page_table_data = [table_data[0]] + table_data[start_row:end_row]
            
            table = Table(page_table_data, colWidths=col_widths)
            
            # Table style
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),  # Right align monto column
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
            ]))
            
            # Add alternating row colors
            for i in range(1, len(page_table_data)):
                if i % 2 == 0:
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa'))
                    ]))
            
            # Calculate table height and draw
            table_width, table_height = table.wrap(0, 0)
            table.drawOn(c, left_margin, y - table_height)
            
            # Page number
            c.setFont("Helvetica", 8)
            c.drawRightString(right_margin, bottom_margin - 0.2 * inch, f"Página {page_num + 1} de {total_pages}")
            
            # Add arqueo and signature on last page only
            if page_num == total_pages - 1:
                # Calculate available space for arqueo
                current_y = y - table_height - 0.3 * inch
                
                # Add Arqueo de Caja section if data is available
                if arqueo_data:
                    c.setFont("Helvetica-Bold", 12)
                    current_y -= 0.3 * inch
                    c.drawString(left_margin, current_y, "ARQUEO DE CAJA (Billetaje)")
                    current_y -= 0.05 * inch
                    c.setLineWidth(0.5)
                    c.line(left_margin, current_y, left_margin + 3 * inch, current_y)
                    current_y -= 0.25 * inch
                    
                    # Create arqueo table
                    arqueo_table_data = [['Denominación', 'Cantidad', 'Subtotal']]
                    
                    # Billetes
                    if arqueo_data.get('billetes_200', 0) > 0:
                        arqueo_table_data.append(['Bs. 200', str(arqueo_data['billetes_200']), f"${arqueo_data['billetes_200'] * 200:.2f}"])
                    if arqueo_data.get('billetes_100', 0) > 0:
                        arqueo_table_data.append(['Bs. 100', str(arqueo_data['billetes_100']), f"${arqueo_data['billetes_100'] * 100:.2f}"])
                    if arqueo_data.get('billetes_50', 0) > 0:
                        arqueo_table_data.append(['Bs. 50', str(arqueo_data['billetes_50']), f"${arqueo_data['billetes_50'] * 50:.2f}"])
                    if arqueo_data.get('billetes_20', 0) > 0:
                        arqueo_table_data.append(['Bs. 20', str(arqueo_data['billetes_20']), f"${arqueo_data['billetes_20'] * 20:.2f}"])
                    if arqueo_data.get('billetes_10', 0) > 0:
                        arqueo_table_data.append(['Bs. 10', str(arqueo_data['billetes_10']), f"${arqueo_data['billetes_10'] * 10:.2f}"])
                    
                    # Monedas
                    if arqueo_data.get('monedas_5', 0) > 0:
                        arqueo_table_data.append(['Bs. 5', str(arqueo_data['monedas_5']), f"${arqueo_data['monedas_5'] * 5:.2f}"])
                    if arqueo_data.get('monedas_2', 0) > 0:
                        arqueo_table_data.append(['Bs. 2', str(arqueo_data['monedas_2']), f"${arqueo_data['monedas_2'] * 2:.2f}"])
                    if arqueo_data.get('monedas_1', 0) > 0:
                        arqueo_table_data.append(['Bs. 1', str(arqueo_data['monedas_1']), f"${arqueo_data['monedas_1'] * 1:.2f}"])
                    if arqueo_data.get('monedas_050', 0) > 0:
                        arqueo_table_data.append(['Bs. 0.50', str(arqueo_data['monedas_050']), f"${arqueo_data['monedas_050'] * 0.50:.2f}"])
                    if arqueo_data.get('monedas_020', 0) > 0:
                        arqueo_table_data.append(['Bs. 0.20', str(arqueo_data['monedas_020']), f"${arqueo_data['monedas_020'] * 0.20:.2f}"])
                    if arqueo_data.get('monedas_010', 0) > 0:
                        arqueo_table_data.append(['Bs. 0.10', str(arqueo_data['monedas_010']), f"${arqueo_data['monedas_010'] * 0.10:.2f}"])
                    
                    # Total row
                    arqueo_table_data.append(['TOTAL', '', f"${arqueo_data.get('monto_total', 0):.2f}"])
                    
                    # Create and style arqueo table
                    arqueo_col_widths = [1.5*inch, 0.8*inch, 1*inch]
                    arqueo_table = Table(arqueo_table_data, colWidths=arqueo_col_widths)
                    
                    arqueo_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -2), 8),
                        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, -1), (-1, -1), 9),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.black),
                        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
                    ]))
                    
                    # Draw arqueo table
                    arqueo_table_width, arqueo_table_height = arqueo_table.wrap(0, 0)
                    arqueo_table.drawOn(c, left_margin, current_y - arqueo_table_height)
                    current_y -= arqueo_table_height + 0.4 * inch
                
                # Add signature field
                # Get cashier name from current_user
                cashier_name = "Cajero"
                if current_user:
                    cashier_name = f"{current_user.nombre} {current_user.apellido}"
                
                # Position signature at bottom of page
                signature_y = bottom_margin + 0.8 * inch
                
                # Signature line
                c.setLineWidth(0.5)
                c.line(left_margin, signature_y, left_margin + 3 * inch, signature_y)
                
                # Signature label
                c.setFont("Helvetica", 9)
                signature_y -= 0.15 * inch
                c.drawString(left_margin, signature_y, f"Firma del Cajero: {cashier_name}")
    
    # Finalize PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

    """
    Generate a PDF report for cash movements
    
    Args:
        movements_data: List of movement dictionaries
        fecha_inicio: Start date for the report
        fecha_fin: End date for the report
        current_user: Current logged-in user (for signature)
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    
    # Full page letter size
    page_width, page_height = letter
    
    # Create PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Margins
    left_margin = 0.75 * inch
    right_margin = page_width - 0.75 * inch
    top_margin = page_height - 0.75 * inch
    bottom_margin = 0.75 * inch
    
    # Current Y position
    y = top_margin
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(page_width / 2, y, "REPORTE DE FLUJO DE CAJA")
    y -= 0.4 * inch
    
    # Date range
    c.setFont("Helvetica", 11)
    if fecha_inicio and fecha_fin:
        fecha_inicio_str = fecha_inicio.strftime('%d/%m/%Y') if not isinstance(fecha_inicio, str) else fecha_inicio.split('T')[0]
        fecha_fin_str = fecha_fin.strftime('%d/%m/%Y') if not isinstance(fecha_fin, str) else fecha_fin.split('T')[0]
        c.drawCentredString(page_width / 2, y, f"Período: {fecha_inicio_str} - {fecha_fin_str}")
    else:
        c.drawCentredString(page_width / 2, y, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 0.3 * inch
    
    # Horizontal line
    c.setLineWidth(1)
    c.line(left_margin, y, right_margin, y)
    y -= 0.4 * inch
    
    # Calculate totals
    total_ingresos = sum(m['monto'] for m in movements_data if m['tipo'] == 'INGRESO')
    total_egresos = sum(m['monto'] for m in movements_data if m['tipo'] == 'EGRESO')
    balance = total_ingresos - total_egresos
    
    # Summary boxes
    c.setFont("Helvetica-Bold", 10)
    box_width = 2.2 * inch
    box_x1 = left_margin
    box_x2 = left_margin + box_width + 0.2 * inch
    box_x3 = left_margin + (box_width + 0.2 * inch) * 2
    
    # Ingresos box
    c.setFillColorRGB(0.9, 1, 0.9)
    c.rect(box_x1, y - 0.5 * inch, box_width, 0.5 * inch, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(box_x1 + 0.1 * inch, y - 0.2 * inch, "INGRESOS:")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(box_x1 + box_width - 0.1 * inch, y - 0.4 * inch, f"${total_ingresos:.2f}")
    
    # Egresos box
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(1, 0.9, 0.9)
    c.rect(box_x2, y - 0.5 * inch, box_width, 0.5 * inch, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(box_x2 + 0.1 * inch, y - 0.2 * inch, "EGRESOS:")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(box_x2 + box_width - 0.1 * inch, y - 0.4 * inch, f"${total_egresos:.2f}")
    
    # Balance box
    c.setFont("Helvetica-Bold", 10)
    balance_color = (0.9, 0.9, 1) if balance >= 0 else (1, 0.9, 0.9)
    c.setFillColorRGB(*balance_color)
    c.rect(box_x3, y - 0.5 * inch, box_width, 0.5 * inch, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(box_x3 + 0.1 * inch, y - 0.2 * inch, "BALANCE:")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(box_x3 + box_width - 0.1 * inch, y - 0.4 * inch, f"${balance:.2f}")
    
    y -= 0.7 * inch
    
    # Movements table
    if movements_data:
        # Table header
        table_data = [['Fecha', 'Tipo', 'Categoría', 'Descripción', 'Usuario', 'Método', 'Voucher', 'Monto']]
        
        # Table rows
        for mov in movements_data:
            fecha = mov.get('fecha', datetime.now())
            if isinstance(fecha, str):
                fecha_str = fecha.split('T')[0] + ' ' + fecha.split('T')[1][:5]
            else:
                fecha_str = fecha.strftime('%d/%m %H:%M')
            
            tipo = mov.get('tipo', 'N/A')
            categoria = mov.get('categoria', 'N/A')[:15]
            descripcion = mov.get('descripcion', '')[:30]
            usuario = mov.get('usuario', {}).get('nombre', 'N/A') if mov.get('usuario') else 'N/A'
            metodo = mov.get('metodo_pago', '-')[:10] if mov.get('metodo_pago') else '-'
            voucher = mov.get('numero_voucher', '-')[:12] if mov.get('numero_voucher') else '-'
            monto = mov.get('monto', 0)
            
            # Format monto with sign
            monto_str = f"${monto:.2f}" if tipo == 'INGRESO' else f"-${monto:.2f}"
            
            table_data.append([
                fecha_str,
                tipo[:3],  # ING or EGR
                categoria,
                descripcion,
                usuario[:15],
                metodo,
                voucher,
                monto_str
            ])
        
        # Create table with adjusted column widths
        col_widths = [0.9*inch, 0.5*inch, 0.9*inch, 1.8*inch, 0.9*inch, 0.7*inch, 0.8*inch, 0.7*inch]
        
        # Check if we need pagination
        rows_per_page = 25
        total_pages = (len(table_data) - 1 + rows_per_page - 1) // rows_per_page  # -1 for header, ceiling division
        
        for page_num in range(total_pages):
            if page_num > 0:
                c.showPage()
                y = top_margin
            
            # Get rows for this page
            start_row = page_num * rows_per_page + 1  # +1 to skip header on subsequent pages
            end_row = min(start_row + rows_per_page, len(table_data))
            
            # Always include header
            page_table_data = [table_data[0]] + table_data[start_row:end_row]
            
            table = Table(page_table_data, colWidths=col_widths)
            
            # Table style
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),  # Right align monto column
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
            ]))
            
            # Add alternating row colors
            for i in range(1, len(page_table_data)):
                if i % 2 == 0:
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa'))
                    ]))
            
            # Calculate table height and draw
            table_width, table_height = table.wrap(0, 0)
            table.drawOn(c, left_margin, y - table_height)
            
            # Page number
            c.setFont("Helvetica", 8)
            c.drawRightString(right_margin, bottom_margin - 0.2 * inch, f"Página {page_num + 1} de {total_pages}")
            
            # Add signature field on last page only
            if page_num == total_pages - 1:
                # Get cashier name from current_user
                cashier_name = "Cajero"
                if current_user:
                    cashier_name = f"{current_user.nombre} {current_user.apellido}"
                
                # Position signature at bottom of page
                signature_y = bottom_margin + 0.8 * inch
                
                # Signature line
                c.setLineWidth(0.5)
                c.line(left_margin, signature_y, left_margin + 3 * inch, signature_y)
                
                # Signature label
                c.setFont("Helvetica", 9)
                signature_y -= 0.15 * inch
                c.drawString(left_margin, signature_y, f"Firma del Cajero: {cashier_name}")
    
    # Finalize PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer
