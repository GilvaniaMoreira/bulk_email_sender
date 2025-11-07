"""Tarefas Celery para envio de e-mails."""

from typing import Optional
from celery import Task
from app.core.celery_app import celery_app
from app.domain.entities import EmailMessage
from app.infrastructure.email.mail_client import send_email
from app.utils.logger import logger


class EmailTask(Task):
    """Classe base para tarefas de e-mail com retry automático."""

    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutos
    retry_jitter = True
    max_retries = 3

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Callback chamado quando a tarefa falha."""
        logger.error(f"Tarefa {task_id} falhou: {exc}")


@celery_app.task(
    name="send_email_task",
    base=EmailTask,
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
)
def send_email_task(
    self,
    to: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None,
) -> dict:
    """
    Tarefa Celery para envio de um único e-mail.

    Args:
        self: Instância da tarefa (bind=True)
        to: Destinatário do e-mail
        subject: Assunto do e-mail
        body: Corpo do e-mail
        from_email: Remetente do e-mail (opcional)

    Returns:
        Dicionário com resultado do envio
    """
    try:
        # Cria entidade de domínio
        message = EmailMessage(
            to=to,
            subject=subject,
            body=body,
            from_email=from_email,
        )

        # Envia e-mail usando cliente SMTP
        success = send_email(message)

        if success:
            logger.info(f"E-mail enviado com sucesso para {to} (task_id: {self.request.id})")
            return {
                "status": "sent",
                "to": to,
                "task_id": self.request.id,
            }

        error_message = f"Falha ao enviar e-mail para {to}"
        failure_meta = {
            "status": "failed",
            "error": error_message,
            "task_id": self.request.id,
            "to": to,
        }
        logger.error(f"{error_message} (task_id: {self.request.id})")
        self.update_state(  # type: ignore[attr-defined]
            state="FAILURE",
            meta=failure_meta,
        )
        raise Exception(failure_meta)

    except Exception as e:
        error_message = f"Erro na tarefa de envio para {to}: {e}"
        failure_meta = {
            "status": "failed",
            "error": str(e),
            "task_id": getattr(self.request, "id", None),
            "to": to,
        }
        logger.error(error_message)
        try:
            self.update_state(  # type: ignore[attr-defined]
                state="FAILURE",
                meta=failure_meta,
            )
        except Exception:  # pragma: no cover - evitar que update_state oculte erro original
            pass
        raise Exception(failure_meta)
