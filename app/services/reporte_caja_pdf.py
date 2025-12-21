"""
PDF Generation Service for Cash Closure Report
Generates comprehensive cash flow reports with movement details
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from datetime import datetime
from decimal import Decimal

def generate_reporte_caja_pdf(movements_data: list, fecha_inicio=None, fecha_fin=None, usuario_id=None, db=None) -> BytesIO:
    """
    Generate a PDF report for cash movements
    
    Args:
        movements_data: List of movement dictionaries
        fecha_inicio: Start date for the report
        fecha_fin: End date for the report
        usuario_id: Filter by user ID
        db: Database session (for additional queries if needed)
        
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
    
    # Finalize PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer
