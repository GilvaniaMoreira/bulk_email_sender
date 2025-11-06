"""Testes do domínio."""

import pytest
from app.domain.entities import EmailMessage, EmailCampaign
from app.domain.services import EmailService


def test_email_message_creation():
    """Testa criação de EmailMessage válida."""
    message = EmailMessage(
        to="test@example.com",
        subject="Test",
        body="Test body",
    )
    assert message.to == "test@example.com"
    assert message.status == "pending"


def test_email_message_invalid_email():
    """Testa criação de EmailMessage com e-mail inválido."""
    with pytest.raises(ValueError):
        EmailMessage(
            to="invalid-email",
            subject="Test",
            body="Test body",
        )


def test_email_campaign_creation():
    """Testa criação de EmailCampaign válida."""
    campaign = EmailCampaign(
        emails=["test1@example.com", "test2@example.com"],
        subject="Test",
        body="Test body",
    )
    assert len(campaign.emails) == 2


def test_email_service_validate_email():
    """Testa validação de e-mail."""
    assert EmailService.validate_email("test@example.com") is True
    assert EmailService.validate_email("invalid") is False
    assert EmailService.validate_email("invalid@") is False
    assert EmailService.validate_email("@example.com") is False


def test_email_service_filter_valid_emails():
    """Testa filtro de e-mails válidos."""
    emails = ["valid@example.com", "invalid", "another@test.com"]
    valid = EmailService.filter_valid_emails(emails)
    assert len(valid) == 2
    assert "valid@example.com" in valid
    assert "another@test.com" in valid
    assert "invalid" not in valid
