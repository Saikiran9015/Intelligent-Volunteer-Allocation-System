from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import datetime

def generate_donation_receipt(name, email, amount, donation_id):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Elite Styling - Background Accent
    p.setFillColor(colors.HexColor("#f8fafc"))
    p.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Side Decorative Bar
    p.setFillColor(colors.HexColor("#4f46e5"))
    p.rect(0, 0, 0.4 * inch, height, fill=1, stroke=0)

    # Header Section
    p.setFillColor(colors.HexColor("#0f172a"))
    p.setFont("Helvetica-Bold", 28)
    p.drawString(0.8 * inch, height - 1.2 * inch, "UnitySync Elite")
    
    p.setFont("Helvetica", 11)
    p.setFillColor(colors.HexColor("#64748b"))
    p.drawString(0.8 * inch, height - 1.5 * inch, "A Premium Platform for Social Impact Intelligence")
    
    # Horizontal Line
    p.setStrokeColor(colors.HexColor("#e2e8f0"))
    p.line(0.8 * inch, height - 1.8 * inch, width - 0.8 * inch, height - 1.8 * inch)

    # Receipt Body
    p.setFillColor(colors.HexColor("#0f172a"))
    p.setFont("Helvetica-Bold", 18)
    p.drawString(0.8 * inch, height - 2.5 * inch, "Official Impact Receipt")
    
    # Metadata Box
    p.setFillColor(colors.HexColor("#ffffff"))
    p.rect(0.8 * inch, height - 4.5 * inch, width - 1.6 * inch, 1.5 * inch, fill=1, stroke=1)
    p.setStrokeColor(colors.HexColor("#e2e8f0"))
    
    p.setFillColor(colors.HexColor("#0f172a"))
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1 * inch, height - 3.4 * inch, "RECEIPT ID")
    p.drawString(1 * inch, height - 3.7 * inch, "DATE")
    p.drawString(3 * inch, height - 3.4 * inch, "DONOR NAME")
    p.drawString(3 * inch, height - 3.7 * inch, "DONOR EMAIL")
    
    p.setFont("Helvetica", 11)
    p.setFillColor(colors.HexColor("#4f46e5"))
    p.drawString(1.8 * inch, height - 3.4 * inch, f"{donation_id}")
    p.drawString(1.8 * inch, height - 3.7 * inch, f"{datetime.datetime.now().strftime('%d %B %Y')}")
    p.drawString(4.2 * inch, height - 3.4 * inch, f"{name}")
    p.drawString(4.2 * inch, height - 3.7 * inch, f"{email}")

    # Financial Section
    p.setFillColor(colors.HexColor("#4f46e5"))
    p.rect(0.8 * inch, height - 5.8 * inch, width - 1.6 * inch, 0.8 * inch, fill=1, stroke=0)
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1.2 * inch, height - 5.4 * inch, "TOTAL CONTRIBUTION")
    p.setFont("Helvetica-Bold", 18)
    p.drawRightString(width - 1.2 * inch, height - 5.4 * inch, f"INR {amount}.00")

    # Impact Message
    p.setFillColor(colors.HexColor("#1e293b"))
    p.setFont("Helvetica-Oblique", 12)
    p.drawString(0.8 * inch, height - 6.8 * inch, "Your contribution has been successfully matched with high-priority field missions.")
    
    # Verification Footer
    p.setFont("Helvetica", 9)
    p.setFillColor(colors.HexColor("#94a3b8"))
    p.drawString(0.8 * inch, 1.2 * inch, "This document is verified by UnitySync Elite Intelligence. No physical signature required.")
    p.drawString(0.8 * inch, 1 * inch, "Verification Token: " + hmac.new(b"elite", donation_id.encode(), hashlib.sha256).hexdigest()[:16].upper())
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
from twilio.rest import Client as TwilioClient
from flask import current_app

class SMSService:
    @staticmethod
    def get_client():
        return TwilioClient(
            current_app.config['TWILIO_ACCOUNT_SID'],
            current_app.config['TWILIO_AUTH_TOKEN']
        )

    @staticmethod
    def send_emergency_alert(to_number, message):
        try:
            client = SMSService.get_client()
            message = client.messages.create(
                body=f"🔴 EMERGENCY DISPATCH: {message}",
                from_=current_app.config['TWILIO_PHONE_NUMBER'],
                to=to_number
            )
            return message.sid
        except Exception as e:
            current_app.logger.error(f"Twilio SMS Error: {e}")
            return None
