"""
Módulo: Logger de Análise

Configuração centralizada de logging para o sistema de análise interativa.
Garante logs estruturados em console e arquivo com rotação diária.
"""

import logging
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


def configurar_logger(
    nome: str = "analise",
    nivel: str = "INFO",
    dir_logs: str = "logs",
    formato: Optional[str] = None
) -> logging.Logger:
    """
    Configura logger com saída para console e arquivo.

    Args:
        nome: Nome do logger (ex: "analise", "ferramentas.preco")
        nivel: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        dir_logs: Diretório para salvar arquivos de log
        formato: Formato customizado de log (usa padrão se None)

    Returns:
        logging.Logger: Logger configurado

    Example:
        >>> logger = configurar_logger("meu_modulo", nivel="DEBUG")
        >>> logger.info("Módulo iniciado")
    """
    # Criar diretório de logs se não existir
    path_logs = Path(dir_logs)
    path_logs.mkdir(parents=True, exist_ok=True)

    # Obter ou criar logger
    logger = logging.getLogger(nome)
    logger.setLevel(getattr(logging, nivel.upper()))

    # Evitar duplicação de handlers
    if logger.handlers:
        return logger

    # Formato padrão
    if formato is None:
        formato = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(formato)

    # Handler para Console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para Arquivo (rotação diária)
    arquivo_log = path_logs / f"analise_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = TimedRotatingFileHandler(
        arquivo_log,
        when="midnight",
        interval=1,
        backupCount=30,  # Manter 30 dias de logs
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.debug(f"Logger '{nome}' configurado com sucesso")
    return logger


# Logger global para uso rápido
logger_padrao = configurar_logger("analise")


def obter_logger(nome: str) -> logging.Logger:
    """
    Obtém logger já configurado ou cria um novo.

    Args:
        nome: Nome do logger (ex: "ferramentas.preco_atual")

    Returns:
        logging.Logger: Logger configurado
    """
    # Se logger já existe e tem handlers, retornar
    logger_existente = logging.getLogger(nome)
    if logger_existente.handlers:
        return logger_existente

    # Caso contrário, configurar novo
    return configurar_logger(nome)
