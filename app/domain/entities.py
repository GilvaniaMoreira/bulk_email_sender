"""Entidades de domínio."""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class EmailMessage:
    """Entidade que representa uma mensagem de e-mail."""

    to: str
    subject: str
    body: str
    from_email: Optional[str] = None
    sent_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed

    def __post_init__(self):
        """Valida a entidade após inicialização."""
        if not self.to or "@" not in self.to:
            raise ValueError("Email destinatário inválido")
        if not self.subject:
            raise ValueError("Assunto do e-mail é obrigatório")
        if not self.body:
            raise ValueError("Corpo do e-mail é obrigatório")


@dataclass
class EmailCampaign:
    """Entidade que representa uma campanha de e-mail."""

    emails: List[str]
    subject: str
    body: str
    from_email: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Valida a campanha após inicialização."""
        if not self.emails:
            raise ValueError("Lista de e-mails não pode estar vazia")
        if not self.subject:
            raise ValueError("Assunto do e-mail é obrigatório")
        if not self.body:
            raise ValueError("Corpo do e-mail é obrigatório")
