"""Testes da API."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Testa o endpoint raiz."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Testa o endpoint de health check."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_send_emails_invalid_request():
    """Testa envio de e-mails com requisição inválida."""
    response = client.post(
        "/api/v1/send-emails",
        json={
            "emails": [],
            "subject": "Test",
            "body": "Test body",
        },
    )
    # Deve retornar 400 ou 422 dependendo da validação
    assert response.status_code in [400, 422]


def test_send_emails_valid_request():
    """Testa envio de e-mails com requisição válida."""
    response = client.post(
        "/api/v1/send-emails",
        json={
            "emails": ["test@example.com"],
            "subject": "Test Subject",
            "body": "Test Body",
        },
    )
    # Deve aceitar a requisição (202) mesmo que não envie de fato
    assert response.status_code == 202
    assert "task_ids" in response.json()
    assert "message" in response.json()
