"""
Módulo de Configuración de Logging para Software FJ.

Establece la configuración centralizada de logs del sistema con soporte
de rotación automática de archivos (RotatingFileHandler) y salida dual a consola.
"""

# Módulo estándar de Python para registrar eventos (logs)
import logging
# Manejador que rota el archivo de log cuando alcanza un tamaño máximo
from logging.handlers import RotatingFileHandler
# Path permite construir rutas de archivos de forma segura
from pathlib import Path


def configurar_logger(nombre: str = "SoftwareFJ") -> logging.Logger:
    """Configura y retorna un logger unificado para toda la aplicación.

    Parámetros:
        nombre (str): Nombre del logger. Por defecto 'SoftwareFJ'.

    Retorna:
        logging.Logger: Instancia configurada del logger con rotación de archivos.
    """
    # Obtiene (o crea) el logger con el nombre indicado
    logger = logging.getLogger(nombre)

    # Si el logger ya tiene manejadores, se reutiliza para no duplicar mensajes
    if logger.handlers:
        return logger

    # Nivel DEBUG: se registran todos los mensajes
    logger.setLevel(logging.DEBUG)

    # Ruta de la carpeta raíz del proyecto
    ruta_base = Path(__file__).resolve().parent.parent
    # Ruta de la carpeta logs
    ruta_logs = ruta_base / "logs"
    # Crea la carpeta logs si no existe
    ruta_logs.mkdir(parents=True, exist_ok=True)
    # Archivo donde se guardan los eventos y errores
    archivo_log = ruta_logs / "software_fj.log"

    # Formato del archivo: fecha, nivel, módulo, función, línea y mensaje
    formato_archivo = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | [%(module)s:%(funcName)s:%(lineno)d] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Formato más corto para la consola
    formato_consola = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Manejador con rotación: 1 MB por archivo y hasta 3 archivos de respaldo
    manejador_archivo = RotatingFileHandler(
        archivo_log, maxBytes=1_048_576, backupCount=3, encoding="utf-8"
    )
    # El archivo guarda todos los niveles y usa el formato detallado
    manejador_archivo.setLevel(logging.DEBUG)
    manejador_archivo.setFormatter(formato_archivo)

    # Manejador que muestra los mensajes en consola
    manejador_consola = logging.StreamHandler()
    # En consola solo se muestran mensajes INFO o superiores
    manejador_consola.setLevel(logging.INFO)
    manejador_consola.setFormatter(formato_consola)

    # Se agregan los dos manejadores: archivo y consola
    logger.addHandler(manejador_archivo)
    logger.addHandler(manejador_consola)

    # Devuelve el logger listo para usar
    return logger


# Logger global que importan todos los módulos del sistema
logger_sistema = configurar_logger()
