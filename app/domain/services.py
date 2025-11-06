"""Serviços de domínio (regras de negócio puras)."""

from typing import List
from app.domain.entities import EmailMessage, EmailCampaign
from app.utils.logger import logger


class EmailService:
    """Serviço de domínio para validação e processamento de e-mails."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida se um e-mail tem formato válido.

        Args:
            email: Endereço de e-mail a validar

        Returns:
            True se válido, False caso contrário
        """
        if not email or "@" not in email:
            return False

        parts = email.split("@")
        if len(parts) != 2:
            return False

        local, domain = parts
        if not local or not domain:
            return False

        if "." not in domain:
            return False

        return True

    @staticmethod
    def filter_valid_emails(emails: List[str]) -> List[str]:
        """
        Filtra e retorna apenas e-mails válidos.

        Args:
            emails: Lista de e-mails a filtrar

        Returns:
            Lista de e-mails válidos
        """
        valid_emails = []
        invalid_emails = []

        for email in emails:
            if EmailService.validate_email(email):
                valid_emails.append(email)
            else:
                invalid_emails.append(email)
                logger.warning(f"E-mail inválido ignorado: {email}")

        if invalid_emails:
            logger.info(f"Total de e-mails inválidos ignorados: {len(invalid_emails)}")

        return valid_emails

    @staticmethod
    def create_email_messages(campaign: EmailCampaign) -> List[EmailMessage]:
        """
        Cria uma lista de EmailMessage a partir de uma campanha.

        Args:
            campaign: Campanha de e-mail

        Returns:
            Lista de mensagens de e-mail
        """
        valid_emails = EmailService.filter_valid_emails(campaign.emails)
        messages = []

        for email in valid_emails:
            try:
                message = EmailMessage(
                    to=email,
                    subject=campaign.subject,
                    body=campaign.body,
                    from_email=campaign.from_email,
                )
                messages.append(message)
            except ValueError as e:
                logger.error(f"Erro ao criar mensagem para {email}: {e}")

        return messages
