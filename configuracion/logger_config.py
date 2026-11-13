"""
Módulo de Configuración de Logging para Software FJ.

Establece la configuración centralizada de logs del sistema con soporte
de rotación automática de archivos (RotatingFileHandler) y salida dual a consola.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configurar_logger(nombre: str = "SoftwareFJ") -> logging.Logger:
    """Configura y retorna un logger unificado para toda la aplicación.

    Parámetros:
        nombre (str): Nombre del logger. Por defecto 'SoftwareFJ'.

    Retorna:
        logging.Logger: Instancia configurada del logger con rotación de archivos.
    """
    logger = logging.getLogger(nombre)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    ruta_base = Path(__file__).resolve().parent.parent
    ruta_logs = ruta_base / "logs"
    ruta_logs.mkdir(parents=True, exist_ok=True)
    archivo_log = ruta_logs / "software_fj.log"

    formato_archivo = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | [%(module)s:%(funcName)s:%(lineno)d] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    formato_consola = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Manejador con rotación: 1 MB por archivo y hasta 3 archivos de respaldo
    manejador_archivo = RotatingFileHandler(
        archivo_log, maxBytes=1_048_576, backupCount=3, encoding="utf-8"
    )
    manejador_archivo.setLevel(logging.DEBUG)
    manejador_archivo.setFormatter(formato_archivo)

    manejador_consola = logging.StreamHandler()
    manejador_consola.setLevel(logging.INFO)
    manejador_consola.setFormatter(formato_consola)

    logger.addHandler(manejador_archivo)
    logger.addHandler(manejador_consola)

    return logger


logger_sistema = configurar_logger()
