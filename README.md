# Bulk Email Sender

Sistema completo para **envio massivo de e-mails** usando **FastAPI**, **Celery**, **Redis** e **SMTP**, seguindo uma **arquitetura limpa e modular (Clean Architecture simplificada)**.

## Objetivo

API REST para envio de e-mails em massa, onde o processamento ocorre **em background** via Celery, evitando travar o sistema principal e permitindo processamento assíncrono e escalável.

## Como executar

### Pré-requisitos

- Docker e Docker Compose instalados
- Credenciais SMTP (Gmail, Outlook, etc.)

### 1. Configurar variáveis de ambiente

Copie o arquivo `env.example` para `.env` e configure suas credenciais SMTP:

```bash
cp env.example .env
```

Edite o `.env` com suas credenciais:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASS=sua_senha_app
SMTP_USE_TLS=true
```

Se estiver usando Mailtrap ou outro SMTP de testes, substitua as variáveis acima pelos valores fornecidos pelo serviço (host, porta, usuário e senha). Recomenda-se criar uma conta Mailtrap e utilizar as credenciais do inbox de sandbox para validar os envios sem depender de provedores de e-mail reais.

### 2. Executar com Docker Compose

```bash
docker-compose up --build
```

Isso irá subir os seguintes serviços:

- **API FastAPI**: `http://localhost:8000`
- **Redis**: `localhost:6379`
- **Celery Worker**: Processa tarefas em background
- **Flower**: Monitoramento de tarefas em `http://localhost:5555`



## Documentação da API

Após iniciar a aplicação, acesse:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints

### POST `/api/v1/send-emails`

Envia e-mails em massa. Cria tarefas Celery para processamento em background.

**Request:**
```json
{
  "emails": ["user1@email.com", "user2@email.com"],
  "subject": "Assunto do e-mail",
  "body": "Conteúdo da mensagem",
  "from_email": "remetente@email.com"  // opcional
}
```

**Response (202 Accepted):**
```json
{
  "message": "Tarefas de envio criadas com sucesso",
  "task_ids": ["abc123", "def456"],
  "total_emails": 2
}
```

### GET `/api/v1/task-status/{task_id}`

Consulta o status de uma tarefa Celery.

**Response:**
```json
{
  "task_id": "abc123",
  "status": "SUCCESS",
  "result": {
    "status": "sent",
    "to": "user1@email.com",
    "task_id": "abc123"
  },
  "error": null
}
```

**Status possíveis:**
- `PENDING`: Tarefa aguardando processamento
- `STARTED`: Tarefa em execução
- `SUCCESS`: Tarefa concluída com sucesso
- `FAILURE`: Tarefa falhou
- `RETRY`: Tarefa sendo reexecutada

### GET `/api/v1/health`

Health check da API.

**Response:**
```json
{
  "status": "healthy",
  "service": "bulk_email_sender"
}
```

## Monitoramento com Flower

Acesse `http://localhost:5555` para monitorar:

- Tarefas em execução
- Histórico de tarefas
- Estatísticas de workers
- Logs em tempo real

## Testes

Execute os testes com:

```bash
pytest tests/
```

## Configurações

### Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SMTP_HOST` | Servidor SMTP | `smtp.mail.com` |
| `SMTP_PORT` | Porta SMTP | `587` |
| `SMTP_USER` | Usuário SMTP | - |
| `SMTP_PASS` | Senha SMTP | - |
| `SMTP_USE_TLS` | Usar TLS | `true` |
| `REDIS_HOST` | Host do Redis | `redis` |
| `REDIS_PORT` | Porta do Redis | `6379` |
| `DEBUG` | Modo debug | `false` |

## Padrões e Boas Práticas

### Arquitetura Limpa

- **Separação de responsabilidades**: Domínio, Infraestrutura e API em camadas distintas
- **Dependency Injection**: Cliente SMTP injetado nas tarefas
- **Validação**: Pydantic para validação de entrada/saída

### Celery

- **Retry automático**: Tarefas com retry exponencial em caso de falha
- **Timeouts**: Limites de tempo para evitar travamentos
- **Task tracking**: Rastreamento de status de tarefas

### Código

- **Tipagem estática**: Type hints em todo o código
- **Logging**: Logs estruturados para debugging
- **Tratamento de erros**: Tratamento robusto de exceções

## Exemplo de uso

### Usando cURL

```bash
curl -X POST "http://localhost:8000/api/v1/send-emails" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["destinatario1@email.com", "destinatario2@email.com"],
    "subject": "Teste de envio",
    "body": "Este é um e-mail de teste enviado via API."
  }'
```

### Usando Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/send-emails",
    json={
        "emails": ["user@example.com"],
        "subject": "Teste",
        "body": "Corpo do e-mail"
    }
)

print(response.json())
# {'message': 'Tarefas de envio criadas com sucesso', 'task_ids': [...], 'total_emails': 1}

# Consultar status
task_id = response.json()["task_ids"][0]
status = requests.get(f"http://localhost:8000/api/v1/task-status/{task_id}")
print(status.json())
```


Desenvolvido com FastAPI, Celery e Redis
