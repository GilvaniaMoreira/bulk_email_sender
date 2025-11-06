"""Ponto de entrada da aplicação FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router
from app.utils.logger import logger

# Cria aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para envio massivo de e-mails usando Celery e Redis",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra rotas
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Evento executado ao iniciar a aplicação."""
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} iniciado")
    logger.info(f"Documentação disponível em: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado ao encerrar a aplicação."""
    logger.info(f"{settings.APP_NAME} encerrado")


@app.get("/")
async def root():
    """Endpoint raiz."""
    return {
        "message": f"Bem-vindo ao {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
