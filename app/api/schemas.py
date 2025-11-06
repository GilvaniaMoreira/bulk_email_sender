"""Schemas Pydantic para validação de entrada/saída da API."""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class SendEmailsRequest(BaseModel):
    """Schema de requisição para envio de e-mails."""

    emails: List[EmailStr] = Field(..., description="Lista de e-mails destinatários")
    subject: str = Field(..., min_length=1, description="Assunto do e-mail")
    body: str = Field(..., min_length=1, description="Corpo do e-mail")
    from_email: Optional[EmailStr] = Field(None, description="E-mail remetente (opcional)")

    class Config:
        """Configuração do schema."""

        json_schema_extra = {
            "example": {
                "emails": ["user1@email.com", "user2@email.com"],
                "subject": "Assunto do e-mail",
                "body": "Conteúdo da mensagem",
            }
        }


class SendEmailsResponse(BaseModel):
    """Schema de resposta para envio de e-mails."""

    message: str
    task_ids: List[str] = Field(..., description="IDs das tarefas Celery criadas")
    total_emails: int = Field(..., description="Total de e-mails processados")


class TaskStatusResponse(BaseModel):
    """Schema de resposta para status de tarefa."""

    task_id: str
    status: str = Field(..., description="Status da tarefa: PENDING, SUCCESS, FAILURE, RETRY")
    result: Optional[dict] = Field(None, description="Resultado da tarefa (se concluída)")
    error: Optional[str] = Field(None, description="Mensagem de erro (se falhou)")
