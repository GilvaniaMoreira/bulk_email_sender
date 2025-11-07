"""Rotas da API."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from celery.result import AsyncResult
from app.api.schemas import (
    SendEmailsRequest,
    SendEmailsResponse,
    TaskStatusResponse,
)
from app.core.celery_app import celery_app
from app.domain.entities import EmailCampaign
from app.domain.services import EmailService
from app.infrastructure.tasks.email_tasks import send_email_task
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1", tags=["emails"])


@router.post(
    "/send-emails",
    response_model=SendEmailsResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enviar e-mails em massa",
    description="Cria tarefas Celery para envio de e-mails em background",
)
async def send_emails(request: SendEmailsRequest) -> SendEmailsResponse:
    """
    Endpoint para envio massivo de e-mails.

    Recebe uma lista de destinatários, assunto e corpo da mensagem,
    e cria tarefas Celery para envio em background.
    """
    try:
        # Filtra e-mails válidos
        valid_emails = EmailService.filter_valid_emails(request.emails)

        if not valid_emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum e-mail válido encontrado na lista",
            )

        # Cria campanha de e-mail
        campaign = EmailCampaign(
            emails=valid_emails,
            subject=request.subject,
            body=request.body,
            from_email=request.from_email,
        )

        # Cria tarefas Celery para cada e-mail
        task_ids = []
        for email in valid_emails:
            task = send_email_task.delay(
                to=email,
                subject=campaign.subject,
                body=campaign.body,
                from_email=campaign.from_email,
            )
            task_ids.append(task.id)
            logger.info(f"Tarefa criada para envio de e-mail para {email} (task_id: {task.id})")

        return SendEmailsResponse(
            message="Tarefas de envio criadas com sucesso",
            task_ids=task_ids,
            total_emails=len(valid_emails),
        )

    except HTTPException:
        # Propaga erros gerados intencionalmente (ex.: validação)
        raise
    except Exception as e:
        logger.error(f"Erro ao criar tarefas de envio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar requisição: {str(e)}",
        )


@router.get(
    "/task-status/{task_id}",
    response_model=TaskStatusResponse,
    summary="Consultar status de tarefa",
    description="Retorna o status atual de uma tarefa Celery",
)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Endpoint para consultar o status de uma tarefa Celery.

    Retorna informações sobre o estado atual da tarefa (pendente, concluída, falha, etc).
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        response_data = {
            "task_id": task_id,
            "status": task_result.state,
        }

        if task_result.ready():
            if task_result.successful():
                response_data["result"] = task_result.result
            else:
                response_data["error"] = str(task_result.info)

        return TaskStatusResponse(**response_data)

    except Exception as e:
        logger.error(f"Erro ao consultar status da tarefa {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar status da tarefa: {str(e)}",
        )


@router.get(
    "/health",
    summary="Health check",
    description="Endpoint para verificar se a API está funcionando",
)
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy", "service": "bulk_email_sender"}
