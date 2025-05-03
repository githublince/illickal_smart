import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import Bill

def generate_bill_pdf(billno):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, f"Bill Number: {billno}")
    y = 760
    bills = Bill.objects.filter(billno__billno=billno)
    total = 0
    for bill in bills:
        line = f"{bill.product.name} - {bill.count} x {bill.product.rr_price} = {bill.total_price}"
        p.drawString(100, y, line)
        y -= 20
        total += bill.total_price
    p.drawString(100, y - 20, f"Total: {total}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

