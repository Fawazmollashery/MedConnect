from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime


def generate_prescription_pdf(user, message, response):
    """
    Generates a PDF file containing patient details, query, and the chatbot's response.

    Args:
        user (User): The user object containing patient details.
        message (str): The message sent by the user.
        response (str): The chatbot's response.

    Returns:
        bytes: The PDF content as bytes.
    """
    # Create a buffer to receive PDF data
    buffer = BytesIO()
    
    # Initialize the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define a container for the elements
    elements = []
    
    # Get default styles
    styles = getSampleStyleSheet()
    
    # Add custom styles if not already defined
    if 'Title' not in styles:
        styles.add(ParagraphStyle(
            name='Title',
            fontSize=24,
            spaceAfter=20,
            alignment=1  # Center alignment
        ))
    if 'Disclaimer' not in styles:
        styles.add(ParagraphStyle(
            name='Disclaimer',
            fontSize=8,
            textColor=colors.grey
        ))
    
    # Add title
    elements.append(Paragraph("Medical Consultation Report", styles['Title']))
    
    # Add date and time
    current_date_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    elements.append(Paragraph(f"Date: {current_date_time}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Add patient details
    patient_data = [
        ['Patient Information'],
        ['Name:', user.username],
        ['Patient ID:', f'PT{user.id:06d}'],
    ]
    table = Table(patient_data, colWidths=[2 * inch, 4 * inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('SPAN', (0, 0), (1, 0)),
        ('GRID', (0, 1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Add query and response
    elements.append(Paragraph("Consultation Details", styles['Heading2']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Patient's Query:", styles['Heading3']))
    elements.append(Paragraph(message, styles['Normal']))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Medical Advice:", styles['Heading3']))
    elements.append(Paragraph(response, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Add disclaimer
    elements.append(Paragraph(
        "DISCLAIMER: This is an AI-generated consultation report and should not be "
        "considered a replacement for professional medical advice. Always consult a "
        "qualified healthcare provider for diagnosis and treatment.",
        styles['Disclaimer']
    ))
    
    # Build the PDF
    doc.build(elements)
    
    # Get PDF content from the buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content
