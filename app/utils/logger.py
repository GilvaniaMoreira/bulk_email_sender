"""Configuração de logging."""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "bulk_email_sender", level: Optional[int] = None) -> logging.Logger:
    """
    Configura e retorna um logger.

    Args:
        name: Nome do logger
        level: Nível de log (default: INFO)

    Returns:
        Logger configurado
    """
    if level is None:
        level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evita duplicar handlers
    if logger.handlers:
        return logger

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formato das mensagens
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


# Logger padrão da aplicação
logger = setup_logger()
