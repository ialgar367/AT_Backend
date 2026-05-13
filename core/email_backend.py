from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent


class SendGridBackend(BaseEmailBackend):
    """
    Backend de email para producción usando SendGrid API HTTP
    Más confiable que SMTP y sin problemas de certificados SSL
    """
    
    def send_messages(self, email_messages):
        """
        Envía emails usando la API HTTP de SendGrid
        """
        if not email_messages:
            return 0
        
        sent_count = 0
        sg = SendGridAPIClient(settings.EMAIL_HOST_PASSWORD)
        
        for message in email_messages:
            try:
                from_email = Email(message.from_email)
                to_email = To(message.to[0] if message.to else message.recipients()[0])
                subject = message.subject
                
                # Buscar contenido HTML en alternatives
                html_content = None
                if hasattr(message, 'alternatives') and message.alternatives:
                    for content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            html_content = content
                            break
                
                # Crear el objeto Mail
                if html_content:
                    mail = Mail(
                        from_email=from_email,
                        to_emails=to_email,
                        subject=subject,
                        plain_text_content=Content("text/plain", message.body),
                        html_content=HtmlContent(html_content)
                    )
                else:
                    mail = Mail(
                        from_email=from_email,
                        to_emails=to_email,
                        subject=subject,
                        plain_text_content=Content("text/plain", message.body)
                    )
                
                # Enviar
                response = sg.send(mail)
                
                if response.status_code in [200, 201, 202]:
                    sent_count += 1
                    
            except Exception as e:
                if not self.fail_silently:
                    raise
        
        return sent_count
