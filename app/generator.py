import os

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


def create_pdf(path, name, title, issued_by, issue_date):
    """Draws one certificate and saves it at path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    w, h = landscape(A4)
    c = canvas.Canvas(path, pagesize=(w, h))

    # double border
    c.setLineWidth(4)
    c.rect(30, 30, w - 60, h - 60)
    c.setLineWidth(1)
    c.rect(40, 40, w - 80, h - 80)

    # text
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(w / 2, h - 120, "Certificate of Completion")

    c.setFont("Helvetica", 16)
    c.drawCentredString(w / 2, h - 180, "This is to certify that")

    c.setFont("Helvetica-BoldOblique", 34)
    c.drawCentredString(w / 2, h / 2, name)

    c.setFont("Helvetica", 16)
    c.drawCentredString(w / 2, h / 2 - 50, "has successfully completed")

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w / 2, h / 2 - 90, title)

    c.setFont("Helvetica", 14)
    c.drawString(80, 80, f"Date: {issue_date}")
    c.drawRightString(w - 80, 80, f"Issued by: {issued_by}")

    c.save()