import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime

class EmailService:
    """
    Email notification service for IndoWater
    Supports SMTP for email delivery
    """
    
    def __init__(self):
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_user = os.environ.get('SMTP_USER', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@indowater.com')
        self.from_name = os.environ.get('FROM_NAME', 'IndoWater Support')
        
        # Check if email is configured
        self.is_configured = bool(self.smtp_user and self.smtp_password)
    
    def send_email(self, to_email: str, subject: str, html_content: str, cc: Optional[List[str]] = None) -> bool:
        """Send email using SMTP"""
        if not self.is_configured:
            print(f"⚠️ Email not configured. Would have sent: {subject} to {to_email}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                
                server.sendmail(self.from_email, recipients, msg.as_string())
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_ticket_created_notification(self, ticket_data: dict) -> bool:
        """Send notification when new ticket is created"""
        subject = f"Tiket Baru #{ticket_data['ticket_number']} - {ticket_data['subject']}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .ticket-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .label {{ font-weight: bold; color: #4b5563; }}
                .value {{ color: #1f2937; margin-left: 10px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #0EA5E9; color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🎫 Tiket Support Baru Dibuat</h2>
                </div>
                <div class="content">
                    <p>Halo {ticket_data['customer_name']},</p>
                    <p>Tiket support Anda telah berhasil dibuat dan akan segera ditangani oleh tim kami.</p>
                    
                    <div class="ticket-info">
                        <p><span class="label">Nomor Tiket:</span><span class="value">#{ticket_data['ticket_number']}</span></p>
                        <p><span class="label">Kategori:</span><span class="value">{ticket_data['category']}</span></p>
                        <p><span class="label">Prioritas:</span><span class="value">{ticket_data['priority']}</span></p>
                        <p><span class="label">Subject:</span><span class="value">{ticket_data['subject']}</span></p>
                        <p><span class="label">Deskripsi:</span><span class="value">{ticket_data['description']}</span></p>
                        <p><span class="label">Dibuat:</span><span class="value">{ticket_data['created_at']}</span></p>
                    </div>
                    
                    <p>Kami akan memberikan update melalui email dan notifikasi in-app.</p>
                    
                    <p>Terima kasih atas kesabaran Anda.</p>
                    
                    <p><strong>Tim IndoWater Support</strong></p>
                </div>
                <div class="footer">
                    <p>© 2025 IndoWater. Semua hak dilindungi.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(ticket_data['customer_email'], subject, html_content)
    
    def send_ticket_assigned_notification(self, ticket_data: dict, technician_email: str) -> bool:
        """Send notification when ticket is assigned to technician"""
        subject = f"Tiket #{ticket_data['ticket_number']} Ditugaskan kepada Anda"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .ticket-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .priority-critical {{ color: #DC2626; font-weight: bold; }}
                .priority-high {{ color: #F59E0B; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔧 Tiket Baru Ditugaskan</h2>
                </div>
                <div class="content">
                    <p>Halo {ticket_data['assigned_to_name']},</p>
                    <p>Tiket support berikut telah ditugaskan kepada Anda:</p>
                    
                    <div class="ticket-info">
                        <p><strong>Nomor Tiket:</strong> #{ticket_data['ticket_number']}</p>
                        <p><strong>Customer:</strong> {ticket_data['customer_name']}</p>
                        <p><strong>Kategori:</strong> {ticket_data['category']}</p>
                        <p><strong>Prioritas:</strong> <span class="priority-{ticket_data['priority']}">{ticket_data['priority']}</span></p>
                        <p><strong>Subject:</strong> {ticket_data['subject']}</p>
                        <p><strong>Deskripsi:</strong> {ticket_data['description']}</p>
                    </div>
                    
                    <p>Silakan segera tangani tiket ini melalui dashboard teknisi.</p>
                    
                    <p><strong>Tim IndoWater</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(technician_email, subject, html_content)
    
    def send_ticket_status_update_notification(self, ticket_data: dict, old_status: str, new_status: str) -> bool:
        """Send notification when ticket status changes"""
        
        status_messages = {
            'in_progress': 'sedang ditangani',
            'resolved': 'telah diselesaikan',
            'approve': 'menunggu persetujuan Anda',
            'closed': 'telah ditutup'
        }
        
        status_message = status_messages.get(new_status, new_status)
        subject = f"Update Tiket #{ticket_data['ticket_number']} - Status: {new_status.upper()}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .status-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin: 10px 5px; }}
                .status-resolved {{ background: #10B981; color: white; }}
                .status-approve {{ background: #F59E0B; color: white; }}
                .status-closed {{ background: #6B7280; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📢 Update Status Tiket</h2>
                </div>
                <div class="content">
                    <p>Halo {ticket_data['customer_name']},</p>
                    <p>Status tiket support Anda telah diperbarui:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <p><strong>Tiket #{ticket_data['ticket_number']}</strong></p>
                        <p>Status: <span class="status-badge status-{new_status}">{new_status.upper()}</span></p>
                    </div>
                    
                    <p>Tiket Anda <strong>{status_message}</strong>.</p>
                    
                    <p><strong>Subject:</strong> {ticket_data['subject']}</p>
                    
                    <p>Terima kasih telah menggunakan layanan IndoWater.</p>
                    
                    <p><strong>Tim IndoWater Support</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(ticket_data['customer_email'], subject, html_content)
    
    def send_critical_alert_notification(self, alert_data: dict, customer_email: str) -> bool:
        """Send email for critical alerts (urgent, leak detection, etc.)"""
        subject = f"🚨 PENTING: {alert_data['title']}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .alert-box {{ background: #FEE2E2; border-left: 4px solid #DC2626; padding: 20px; margin: 20px 0; border-radius: 6px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚨 ALERT PENTING</h2>
                </div>
                <div class="content">
                    <div class="alert-box">
                        <h3>{alert_data['title']}</h3>
                        <p>{alert_data['message']}</p>
                        <p><strong>Waktu:</strong> {alert_data['created_at']}</p>
                    </div>
                    
                    <p><strong>Tindakan yang Disarankan:</strong></p>
                    <ul>
                        <li>Login ke aplikasi untuk melihat detail lengkap</li>
                        <li>Periksa konsumsi air Anda segera</li>
                        <li>Hubungi support jika diperlukan bantuan</li>
                    </ul>
                    
                    <p><strong>Tim IndoWater</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html_content)
    
    def send_promotional_notification(self, promo_data: dict, customer_email: str) -> bool:
        """Send promotional emails (vouchers, discounts, etc.)"""
        subject = f"🎉 Promo Spesial: {promo_data['title']}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .promo-code {{ background: white; border: 2px dashed #F59E0B; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                .code {{ font-size: 24px; font-weight: bold; color: #F59E0B; letter-spacing: 2px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 {promo_data['title']}</h1>
                </div>
                <div class="content">
                    <p>{promo_data['description']}</p>
                    
                    <div class="promo-code">
                        <p style="margin: 0; font-size: 14px; color: #6B7280;">Gunakan Kode:</p>
                        <p class="code">{promo_data.get('code', 'N/A')}</p>
                        <p style="margin: 0; font-size: 12px; color: #9CA3AF;">Berlaku hingga: {promo_data.get('valid_until', 'N/A')}</p>
                    </div>
                    
                    <p><strong>Syarat & Ketentuan:</strong></p>
                    <ul>
                        <li>{promo_data.get('terms', 'Lihat aplikasi untuk detail lengkap')}</li>
                    </ul>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <strong>Jangan lewatkan kesempatan ini!</strong><br>
                        Login ke aplikasi untuk menggunakan promo.
                    </p>
                    
                    <p><strong>Tim IndoWater</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html_content)

# Create singleton instance
email_service = EmailService()
