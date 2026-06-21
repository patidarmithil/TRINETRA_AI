import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
class ChallanAgent:
    def create(self, plate, violations, evidence_image_path=None):
        os.makedirs("outputs/challans", exist_ok=True)
        filename = f"outputs/challans/{plate}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        story = []
        # Custom styles
        title_style = ParagraphStyle(
            name='TitleStyle',
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1e293b'),
            alignment=1, # Center
            spaceAfter=20
        )
        header_style = ParagraphStyle(
            name='HeaderStyle',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=10,
            spaceAfter=10
        )
        normal_style = ParagraphStyle(
            name='NormalStyle',
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155')
        )
        bold_style = ParagraphStyle(
            name='BoldStyle',
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1e293b')
        )
        # Title Header
        story.append(Paragraph("TRINETRA AI - TRAFFIC VIOLATION REPORT", title_style))
        story.append(Spacer(1, 10))
        # Metadata table
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        violation_text = ", ".join(violations) if violations else "No Violations Detected"
        data = [
            [Paragraph("<b>Receipt Number:</b>", normal_style), Paragraph(f"TRN-{datetime.now().strftime('%Y%m%d%H%M%S')}", normal_style)],
            [Paragraph("<b>Vehicle License Plate:</b>", normal_style), Paragraph(plate, bold_style)],
            [Paragraph("<b>Date & Time:</b>", normal_style), Paragraph(timestamp, normal_style)],
            [Paragraph("<b>Reported Violations:</b>", normal_style), Paragraph(violation_text, bold_style)]
        ]
        t = Table(data, colWidths=[150, 350])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        # Add Evidence Image if provided
        if evidence_image_path and os.path.exists(evidence_image_path):
            story.append(Paragraph("EVIDENCE IMAGE (AI OBJECT DETECTS & ANNOTATIONS)", header_style))
            try:
                from PIL import Image as PILImage
                with PILImage.open(evidence_image_path) as img:
                    img_width, img_height = img.size
                aspect = img_height / img_width
                display_width = 450
                display_height = int(display_width * aspect)
                # Keep height within printable boundaries
                if display_height > 300:
                    display_height = 300
                    display_width = int(display_height / aspect)
                story.append(Image(evidence_image_path, width=display_width, height=display_height))
            except Exception as e:
                print(f"Error adding evidence image to PDF: {e}")
            story.append(Spacer(1, 15))
        story.append(Paragraph("<b>Notice:</b> This document serves as an official AI-generated traffic violation ticket. If you wish to appeal this decision, please present the above receipt number to the traffic administrative office.", normal_style))
        doc.build(story)
        return filename