"""Integração de envio de e-mails utilizando FastAPI-Mail."""

import asyncio
from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.core.config import settings
from app.domain.entities import EmailMessage
from app.utils.logger import logger


def _build_connection_config() -> ConnectionConfig:
    """Constrói a configuração para o FastMail baseada nas `settings`."""

    mail_from = settings.SMTP_FROM_EMAIL or settings.SMTP_USER or "no-reply@example.com"
    username = settings.SMTP_USER or ""
    password = settings.SMTP_PASS or ""
    use_credentials = bool(username and password)

    config = ConnectionConfig(
        MAIL_USERNAME=username,
        MAIL_PASSWORD=password,
        MAIL_FROM=mail_from,
        MAIL_PORT=settings.SMTP_PORT,
        MAIL_SERVER=settings.SMTP_HOST,
        MAIL_STARTTLS=settings.SMTP_USE_TLS,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=use_credentials,
        VALIDATE_CERTS=True,
    )
    return config

_mail_config = _build_connection_config()


def send_email(message: EmailMessage) -> bool:
    """Envia um e-mail usando FastAPI-Mail.

    Args:
        message: Entidade de domínio contendo os dados do e-mail.

    Returns:
        True em caso de sucesso, False caso contrário.
    """

    mail_from = message.from_email or settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    recipients: List[str] = [message.to]

    msg_schema = MessageSchema(
        subject=message.subject,
        recipients=recipients,
        body=message.body,
        subtype="plain",
        sender=mail_from,
    )

    fast_mail = FastMail(_mail_config)

    try:
        asyncio.run(fast_mail.send_message(msg_schema))
        logger.info(f"E-mail enviado com sucesso para: {message.to}")
        return True
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(f"Erro ao enviar e-mail para {message.to}: {exc}")
        return False

