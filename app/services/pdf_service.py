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
