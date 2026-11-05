"""
Módulo Base de Entidades para Software FJ.

Define la clase abstracta EntidadBase, raíz de las entidades
del dominio de la aplicación, implementando el principio de abstracción.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class EntidadBase(ABC):
    """Clase abstracta que define el comportamiento y estructura base

    de cualquier entidad administrable dentro del sistema de Software FJ.
    """

    def __init__(self, id_entidad: str):
        if not id_entidad or not isinstance(id_entidad, str):
            raise ValueError("El identificador de la entidad no puede ser nulo o vacío.")
        self._id_entidad = id_entidad.strip()
        self._fecha_creacion = datetime.now()

    @property
    def id_entidad(self) -> str:
        """Obtiene el identificador único de la entidad."""
        return self._id_entidad

    @property
    def fecha_creacion(self) -> datetime:
        """Obtiene la fecha y hora de creación de la entidad."""
        return self._fecha_creacion

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Retorna una cadena descriptiva con el resumen de la entidad.

        Debe ser implementado obligatoriamente por todas las clases hijas.
        """
        pass

    @abstractmethod
    def validar(self) -> bool:
        """Verifica la consistencia interna de los datos de la entidad.

        Debe ser implementado por las subclases para garantizar integridad.
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id_entidad}>"
