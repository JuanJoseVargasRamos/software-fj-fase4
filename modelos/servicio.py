"""
Módulo de Servicios Especializados para Software FJ.

Define la clase abstracta Servicio y tres especializaciones concretas:
1. ReservaSala
2. AlquilerEquipo
3. AsesoriaEspecializada

Aplica polimorfismo, sobrescritura de métodos, simulación de sobrecarga
y control riguroso de excepciones de dominio.
"""

from abc import abstractmethod
from typing import Optional, Union
from modelos.base import EntidadBase
from excepciones.excepciones_sistema import (
    CalculoInconsistenteException,
    CapacidadExcedidaException,
    ParametroServicioInvalidoException,
    ServicioNoDisponibleException,
)


class Servicio(EntidadBase):
    """Clase abstracta que modela cualquier servicio ofrecido por Software FJ."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(id_entidad=codigo)
        if tarifa_base < 0:
            raise ParametroServicioInvalidoException("La tarifa base no puede ser negativa.", "tarifa_base")
        self._codigo = codigo.strip().upper()
        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def codigo(self) -> str:
        """Retorna el código único del servicio."""
        return self._codigo

    @property
    def nombre(self) -> str:
        """Retorna el nombre descriptivo del servicio."""
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        """Retorna la tarifa base monetaria del servicio."""
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        """Indica si el servicio está disponible para contratación."""
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self._disponible = bool(estado)

    def verificar_disponibilidad(self) -> None:
        """Verifica si el servicio se puede contratar; si no, lanza excepción."""
        if not self._disponible:
            raise ServicioNoDisponibleException(
                id_servicio=self._codigo,
                motivo=f"El servicio '{self._nombre}' se encuentra temporalmente inactivo o reservado."
            )

    @abstractmethod
    def describir_servicio(self) -> str:
        """Describe las características técnicas del servicio (sobrescrito por subclases)."""
        pass

    @abstractmethod
    def calcular_costo(self, cantidad_unidades: float, **kwargs) -> float:
        """Calcula el costo base o con parámetros polimórficos según la naturaleza del servicio."""
        pass

    def calcular_costo_sobrecargado(
        self,
        unidades: float,
        descuento: float = 0.0,
        impuesto_iva: float = 0.19,
        recargo_urgencia: float = 0.0,
    ) -> float:
        """Método sobrecargado flexible para cálculo de costos con variantes.

        Envuelve conversiones de tipos, validación de rangos y operaciones aritméticas.
        Aplica Exception Chaining auténtico (raise ... from error_original) cuando ocurre
        cualquier error de conversión o inconsistencia matemática.
        """
        try:
            # Conversión dinámica a punto flotante (sujeta a ValueError o TypeError si el dato es corrupto)
            cant_float = float(unidades)
            desc_float = float(descuento)
            iva_float = float(impuesto_iva)
            recargo_float = float(recargo_urgencia)

            if cant_float <= 0:
                raise ValueError(f"Las unidades de servicio deben ser mayores a cero (recibido: {cant_float}).")
            if desc_float < 0 or desc_float > 0.80:
                raise ValueError(f"El porcentaje de descuento debe oscilar entre 0% y 80% (recibido: {desc_float*100}%).")
            if iva_float < 0:
                raise ValueError(f"El porcentaje de IVA no puede ser negativo (recibido: {iva_float}).")

            # Cálculo polimórfico en la subclase correspondiente
            subtotal = self.calcular_costo(cant_float)

            # Aplicación de fórmulas financieras con validación de factores
            factor_descuento = 1.0 - desc_float
            base_imponible = (subtotal * factor_descuento) + recargo_float
            total_final = base_imponible * (1.0 + iva_float)

            if total_final < 0:
                raise ArithmeticError("El cálculo final generó un valor monetario inconsistente negativo.")

            return round(total_final, 2)

        except (ValueError, TypeError, ZeroDivisionError, ArithmeticError) as error_original:
            # Demostración explícita de encadenamiento de excepciones (raise ... from ...)
            raise CalculoInconsistenteException(
                f"Fallo en cálculo financiero sobrecargado para servicio '{self._codigo}': {str(error_original)}"
            ) from error_original

    def validar(self) -> bool:
        if not self._codigo or not self._nombre or self._tarifa_base < 0:
            return False
        return True

    def obtener_resumen(self) -> str:
        estado = "DISPONIBLE" if self._disponible else "NO DISPONIBLE"
        return f"[{self._codigo}] {self._nombre} | Tarifa Base: ${self._tarifa_base:,.2f} | Estado: {estado}"


# ---------------------------------------------------------------------------
# Servicio Especializado 1: Reserva de Salas
# ---------------------------------------------------------------------------

class ReservaSala(Servicio):
    """Servicio especializado de alquiler y reserva de salas y auditorios."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_hora: float,
        capacidad_maxima: int,
        tipo_sala: str = "Reuniones",
        incluye_proyector: bool = True,
        disponible: bool = True,
    ):
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        if capacidad_maxima <= 0:
            raise ParametroServicioInvalidoException("La capacidad máxima debe ser mayor a cero.", "capacidad_maxima")
        self.capacidad_maxima = int(capacidad_maxima)
        self.tipo_sala = tipo_sala
        self.incluye_proyector = incluye_proyector

    def validar_aforo(self, asistentes_esperados: int) -> None:
        """Verifica que el aforo no supere la capacidad permitida."""
        if asistentes_esperados <= 0:
            raise ParametroServicioInvalidoException("El número de asistentes debe ser mayor a cero.", "asistentes")
        if asistentes_esperados > self.capacidad_maxima:
            raise CapacidadExcedidaException(self.capacidad_maxima, asistentes_esperados)

    def calcular_costo(self, cantidad_unidades: float, **kwargs) -> float:
        """Sobrescribe el cálculo: Tarifa por horas + adicionales de proyector/catering."""
        horas = float(cantidad_unidades)
        if horas <= 0:
            raise ParametroServicioInvalidoException("La duración en horas debe ser positiva.", "horas")

        costo = self._tarifa_base * horas
        if kwargs.get("proyector_4k", False):
            costo += 25000.0 * horas
        asistentes = kwargs.get("asistentes", 0)
        if asistentes > 0 and kwargs.get("catering", False):
            costo += asistentes * 15000.0

        return round(costo, 2)

    def describir_servicio(self) -> str:
        proyector = "Sí" if self.incluye_proyector else "No"
        return (
            f"SALA: {self._nombre} ({self.tipo_sala}) | Capacidad: {self.capacidad_maxima} personas | "
            f"Proyector: {proyector} | Tarifa/Hora: ${self._tarifa_base:,.2f}"
        )


# ---------------------------------------------------------------------------
# Servicio Especializado 2: Alquiler de Equipos Tecnológicos
# ---------------------------------------------------------------------------

class AlquilerEquipo(Servicio):
    """Servicio especializado en el préstamo y alquiler de equipos de cómputo y redes."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_dia: float,
        categoria: str,
        deposito_garantia: float,
        disponible: bool = True,
    ):
        super().__init__(codigo, nombre, tarifa_dia, disponible)
        if deposito_garantia < 0:
            raise ParametroServicioInvalidoException("El depósito de garantía no puede ser negativo.", "deposito_garantia")
        self.categoria = categoria
        self.deposito_garantia = float(deposito_garantia)

    def calcular_costo(self, cantidad_unidades: float, **kwargs) -> float:
        """Sobrescribe el cálculo: Tarifa por días + póliza de seguro opcional."""
        dias = float(cantidad_unidades)
        if dias <= 0:
            raise ParametroServicioInvalidoException("Los días de alquiler deben ser mayores a cero.", "dias")
        if dias > 30:
            raise ParametroServicioInvalidoException("El alquiler no puede superar 30 días continuos.", "dias")

        costo = self._tarifa_base * dias
        if kwargs.get("seguro_riesgo", True):
            costo += (self._tarifa_base * 0.10) * dias

        return round(costo, 2)

    def describir_servicio(self) -> str:
        return (
            f"EQUIPO: {self._nombre} | Categoría: {self.categoria} | Depósito: ${self.deposito_garantia:,.2f} | "
            f"Tarifa/Día: ${self._tarifa_base:,.2f}"
        )


# ---------------------------------------------------------------------------
# Servicio Especializado 3: Asesoría Especializada
# ---------------------------------------------------------------------------

class AsesoriaEspecializada(Servicio):
    """Servicio de consultoría y asesoría técnica profesional."""

    FACTORES_NIVEL = {
        "JUNIOR": 1.0,
        "SENIOR": 1.5,
        "MASTER": 2.2,
    }

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_hora_base: float,
        area_tematica: str,
        nivel_consultor: str = "SENIOR",
        disponible: bool = True,
    ):
        super().__init__(codigo, nombre, tarifa_hora_base, disponible)
        nivel_normalizado = nivel_consultor.strip().upper()
        if nivel_normalizado not in self.FACTORES_NIVEL:
            raise ParametroServicioInvalidoException(
                f"Nivel de consultor inválido '{nivel_consultor}'. Opciones válidas: {list(self.FACTORES_NIVEL.keys())}",
                "nivel_consultor",
            )
        self.area_tematica = area_tematica
        self.nivel_consultor = nivel_normalizado

    def calcular_costo(self, cantidad_unidades: float, **kwargs) -> float:
        """Sobrescribe el cálculo: Horas * Tarifa Base * Multiplicador por seniority."""
        horas = float(cantidad_unidades)
        if horas <= 0:
            raise ParametroServicioInvalidoException("Las horas de asesoría deben ser mayores a cero.", "horas")
        if horas > 40:
            raise ParametroServicioInvalidoException("Una asesoría no puede programarse por más de 40 horas continuas.", "horas")

        multiplicador = self.FACTORES_NIVEL[self.nivel_consultor]
        costo = (self._tarifa_base * multiplicador) * horas

        if kwargs.get("presencial", False):
            costo += 50000.0

        return round(costo, 2)

    def describir_servicio(self) -> str:
        return (
            f"ASESORÍA: {self._nombre} | Área: {self.area_tematica} | Nivel: {self.nivel_consultor} | "
            f"Tarifa/Hora Efectiva: ${self._tarifa_base * self.FACTORES_NIVEL[self.nivel_consultor]:,.2f}"
        )
