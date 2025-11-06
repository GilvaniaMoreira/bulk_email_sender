"""Cliente SMTP para envio de e-mails."""

from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.domain.entities import EmailMessage
from app.utils.logger import logger


class SMTPClient:
    """Cliente para envio de e-mails via SMTP."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: Optional[bool] = None,
    ):
        """
        Inicializa o cliente SMTP.

        Args:
            host: Host do servidor SMTP
            port: Porta do servidor SMTP
            user: Usuário SMTP
            password: Senha SMTP
            use_tls: Se deve usar TLS
        """
        self.host = host or settings.SMTP_HOST
        self.port = port or settings.SMTP_PORT
        self.user = user or settings.SMTP_USER
        self.password = password or settings.SMTP_PASS
        self.use_tls = use_tls if use_tls is not None else settings.SMTP_USE_TLS

    def send_email(self, message: EmailMessage) -> bool:
        """
        Envia um e-mail via SMTP.

        Args:
            message: Mensagem de e-mail a enviar

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Cria mensagem MIME
            msg = MIMEMultipart()
            msg["From"] = message.from_email or settings.SMTP_FROM_EMAIL or self.user
            msg["To"] = message.to
            msg["Subject"] = message.subject

            # Adiciona corpo da mensagem
            msg.attach(MIMEText(message.body, "plain", "utf-8"))

            # Conecta ao servidor SMTP
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()

                if self.user and self.password:
                    server.login(self.user, self.password)

                # Envia e-mail
                text = msg.as_string()
                server.sendmail(
                    msg["From"],
                    message.to,
                    text,
                )

            logger.info(f"E-mail enviado com sucesso para: {message.to}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Erro de autenticação SMTP ao enviar para {message.to}: {e}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Destinatário recusado ao enviar para {message.to}: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"Servidor SMTP desconectado ao enviar para {message.to}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar e-mail para {message.to}: {e}")
            return False


# Instância global do cliente SMTP
smtp_client = SMTPClient()
