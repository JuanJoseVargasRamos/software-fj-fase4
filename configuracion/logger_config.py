"""
Módulo de Configuración de Logging para Software FJ.

Este módulo establece la configuración centralizada de los logs del sistema,
permitiendo registrar eventos informativos, advertencias y excepciones críticas
tanto en la consola como en un archivo persistente en disco (logs/software_fj.log).
"""

import logging
import os
from pathlib import Path


def configurar_logger(nombre: str = "SoftwareFJ") -> logging.Logger:
    """Configura y retorna un logger unificado para toda la aplicación.

    Parámetros:
        nombre (str): Nombre del logger. Por defecto 'SoftwareFJ'.

    Retorna:
        logging.Logger: Instancia configurada del logger.
    """
    logger = logging.getLogger(nombre)

    # Evitar registrar múltiples manejadores si ya está configurado
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Determinar la ruta absoluta para la carpeta de logs
    ruta_base = Path(__file__).resolve().parent.parent
    ruta_logs = ruta_base / "logs"
    ruta_logs.mkdir(parents=True, exist_ok=True)
    archivo_log = ruta_logs / "software_fj.log"

    # Formato profesional detallado para auditoría y rúbrica
    formato_archivo = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | [%(module)s:%(funcName)s:%(lineno)d] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    formato_consola = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # 1. Manejador para archivo con codificación UTF-8
    manejador_archivo = logging.FileHandler(archivo_log, encoding="utf-8", mode="a")
    manejador_archivo.setLevel(logging.DEBUG)
    manejador_archivo.setFormatter(formato_archivo)

    # 2. Manejador para consola
    manejador_consola = logging.StreamHandler()
    manejador_consola.setLevel(logging.INFO)
    manejador_consola.setFormatter(formato_consola)

    # Agregar manejadores al logger principal
    logger.addHandler(manejador_archivo)
    logger.addHandler(manejador_consola)

    return logger


# Instancia por defecto lista para importar
logger_sistema = configurar_logger()
