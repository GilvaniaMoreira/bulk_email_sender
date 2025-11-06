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

**Nota para Gmail:** Você precisará usar uma [Senha de App](https://support.google.com/accounts/answer/185833) ao invés da senha normal da conta.

### 2. Executar com Docker Compose

```bash
docker-compose up --build
```

Isso irá subir os seguintes serviços:

- **API FastAPI**: `http://localhost:8000`
- **Redis**: `localhost:6379`
- **Celery Worker**: Processa tarefas em background
- **Flower**: Monitoramento de tarefas em `http://localhost:5555`

### 3. Executar localmente (sem Docker)

#### Instalar dependências

```bash
pip install -r requirements.txt
```

#### Iniciar Redis

```bash
# Com Docker
docker run -d -p 6379:6379 redis:7-alpine

# Ou instale e inicie localmente
```

#### Configurar variáveis de ambiente

Crie um arquivo `.env` ou exporte as variáveis:

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=seu_email@gmail.com
export SMTP_PASS=sua_senha_app
export SMTP_USE_TLS=true
```

#### Iniciar serviços

**Terminal 1 - API:**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 - Celery Worker:**
```bash
celery -A app.core.celery_app worker --loglevel=info
```

**Terminal 3 - Flower (opcional):**
```bash
celery -A app.core.celery_app flower --port=5555
```

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
| `SMTP_HOST` | Servidor SMTP | `smtp.gmail.com` |
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

## Melhorias Futuras

- [ ] Integração com SendGrid, Mailgun, AWS SES
- [ ] Agendamento de campanhas com Celery Beat
- [ ] Banco de dados para histórico de envios (PostgreSQL)
- [ ] Templates de e-mail (Jinja2)
- [ ] Suporte a anexos
- [ ] Rate limiting
- [ ] Autenticação e autorização (JWT)
- [ ] Dashboard web para gerenciamento
- [ ] Métricas e analytics (Prometheus)
- [ ] Suporte a HTML e e-mails ricos

## Licença

Este projeto é open source e está disponível sob a licença MIT.

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

---

Desenvolvido com FastAPI, Celery e Redis
