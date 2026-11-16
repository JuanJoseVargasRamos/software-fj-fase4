"""
Módulo Base de Entidades para Software FJ.

Define la clase abstracta EntidadBase, raíz de las entidades
del dominio de la aplicación, implementando el principio de abstracción.
"""

# Importa ABC y abstractmethod para crear clases abstractas
from abc import ABC, abstractmethod
# Importa datetime para registrar la fecha de creación de cada entidad
from datetime import datetime


# Clase abstracta: no se puede instanciar directamente, solo heredar
class EntidadBase(ABC):
    """Clase abstracta que define el comportamiento y estructura base

    de cualquier entidad administrable dentro del sistema de Software FJ.
    """

    def __init__(self, id_entidad: str):
        # Valida que el identificador exista y sea texto; si no, lanza un error
        if not id_entidad or not isinstance(id_entidad, str):
            raise ValueError("El identificador de la entidad no puede ser nulo o vacío.")
        # Guarda el identificador sin espacios al inicio ni al final
        self._id_entidad = id_entidad.strip()
        # Registra la fecha y hora exacta en que se creó la entidad
        self._fecha_creacion = datetime.now()

    # Propiedad de solo lectura para consultar el identificador
    @property
    def id_entidad(self) -> str:
        """Obtiene el identificador único de la entidad."""
        return self._id_entidad

    # Propiedad de solo lectura para consultar la fecha de creación
    @property
    def fecha_creacion(self) -> datetime:
        """Obtiene la fecha y hora de creación de la entidad."""
        return self._fecha_creacion

    # Método abstracto: cada clase hija debe implementarlo
    @abstractmethod
    def obtener_resumen(self) -> str:
        """Retorna una cadena descriptiva con el resumen de la entidad.

        Debe ser implementado obligatoriamente por todas las clases hijas.
        """
        pass

    # Método abstracto de validación que cada clase hija debe implementar
    @abstractmethod
    def validar(self) -> bool:
        """Verifica la consistencia interna de los datos de la entidad.

        Debe ser implementado por las subclases para garantizar integridad.
        """
        pass

    # Representación técnica del objeto para depuración
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id_entidad}>"
