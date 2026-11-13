"""
Módulo de Gestión de Clientes para Software FJ.

Define la clase Cliente, garantizando una rigurosa encapsulación de atributos
privados y validaciones exhaustivas mediante excepciones personalizadas.
"""

import re
from modelos.base import EntidadBase
from excepciones.excepciones_sistema import (
    DatosInvalidosException,
    EmailInvalidoException,
    IdentificacionInvalidaException,
    TelefonoInvalidoException,
)


class Cliente(EntidadBase):
    """Representa a un cliente dentro de Software FJ.

    Aplica el principio de encapsulación protegiendo todos los datos personales
    con variables privadas y métodos de acceso controlados por validadores.
    """

    PATRON_EMAIL = re.compile(r"^[\w\.-]+@([\w-]+\.)+[a-zA-Z]{2,}$")
    PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s'-]+$")

    def __init__(self, identificacion: str, nombre: str, email: str, telefono: str):
        """Inicializa una instancia de Cliente tras validar previamente la identificación."""
        id_limpia = self._validar_identificacion(identificacion)
        super().__init__(id_entidad=id_limpia)

        self.__identificacion = id_limpia
        self.__nombre = ""
        self.__email = ""
        self.__telefono = ""

        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.validar()

    @staticmethod
    def _validar_identificacion(valor: str) -> str:
        """Valida que la cédula sea numérica y tenga entre 6 y 12 dígitos."""
        if not valor or not isinstance(valor, str):
            raise IdentificacionInvalidaException("La identificación no puede ser nula ni vacía.", str(valor))
        limpio = valor.strip()
        if not limpio.isdigit() or len(limpio) < 6 or len(limpio) > 12:
            raise IdentificacionInvalidaException(
                "La identificación debe ser numérica y contener entre 6 y 12 dígitos.", limpio
            )
        return limpio

    # --- Getters y Setters encapsulados ---

    @property
    def identificacion(self) -> str:
        """Obtiene la identificación (cédula o NIT) del cliente."""
        return self.__identificacion

    @identificacion.setter
    def identificacion(self, valor: str) -> None:
        self.__identificacion = self._validar_identificacion(valor)
        self._id_entidad = self.__identificacion

    @property
    def nombre(self) -> str:
        """Obtiene el nombre completo del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not isinstance(valor, str):
            raise DatosInvalidosException("El nombre del cliente no puede ser nulo o vacío.", campo="nombre")
        limpio = valor.strip()
        if len(limpio) < 3:
            raise DatosInvalidosException("El nombre debe tener al menos 3 caracteres.", campo="nombre")
        if not self.PATRON_NOMBRE.match(limpio):
            raise DatosInvalidosException("El nombre solo debe contener caracteres alfabéticos, espacios, guiones o apóstrofes.", campo="nombre")
        self.__nombre = limpio

    @property
    def email(self) -> str:
        """Obtiene el correo electrónico del cliente."""
        return self.__email

    @email.setter
    def email(self, valor: str) -> None:
        if not valor or not isinstance(valor, str):
            raise EmailInvalidoException("El correo electrónico no puede estar vacío.", str(valor))
        limpio = valor.strip().lower()
        if not self.PATRON_EMAIL.match(limpio):
            raise EmailInvalidoException(
                "El formato de correo electrónico debe ser válido (ejemplo: usuario@dominio.com).",
                limpio,
            )
        self.__email = limpio

    @property
    def telefono(self) -> str:
        """Obtiene el número telefónico del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not valor or not isinstance(valor, str):
            raise TelefonoInvalidoException("El número de teléfono no puede estar vacío.", str(valor))
        limpio = valor.strip()
        if not limpio.isdigit() or len(limpio) < 7 or len(limpio) > 10:
            raise TelefonoInvalidoException(
                "El teléfono debe contener únicamente dígitos numéricos (entre 7 y 10 dígitos).", limpio
            )
        self.__telefono = limpio

    # --- Métodos de la clase abstracta EntidadBase ---

    def validar(self) -> bool:
        """Valida que todos los atributos privados posean datos consistentes."""
        if not self.__identificacion or not self.__nombre or not self.__email or not self.__telefono:
            raise DatosInvalidosException("La entidad Cliente tiene campos requeridos incompletos.", campo="cliente")
        return True

    def obtener_resumen(self) -> str:
        """Retorna una descripción legible y resumida del cliente."""
        return f"Cliente: {self.__nombre} | ID: {self.__identificacion} | Tel: {self.__telefono} | Email: {self.__email}"

    def __str__(self) -> str:
        return self.obtener_resumen()
