"""
Módulo de Gestión de Reservas para Software FJ.

Define la clase Reserva, que integra Cliente, Servicio, Duración y Estado.
Implementa el ciclo de vida completo de la reserva (confirmación, cancelación,
procesamiento y facturación), incorporando de forma rigurosa:
- Bloques try/except
- Bloques try/except/else
- Bloques try/finally
- Encadenamiento de excepciones (raise ... from ...)
- Registro en logs de cada transición.
"""

from enum import Enum
from datetime import datetime
from typing import Optional

from modelos.base import EntidadBase
from modelos.cliente import Cliente
from modelos.servicio import Servicio
from excepciones.excepciones_sistema import (
    EstadoReservaInvalidoException,
    ParametroServicioInvalidoException,
    ReservaInvalidaException,
    SoftwareFJException,
)
from configuracion.logger_config import logger_sistema


class EstadoReserva(Enum):
    """Enumeración con los estados oficiales del ciclo de vida de una reserva."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"


class Reserva(EntidadBase):
    """Integra a un Cliente con un Servicio de Software FJ.

    Administra la duración, cálculo de costo acordado y transiciones de estado.
    """

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        descuento: float = 0.0,
        impuesto: float = 0.19,
    ):
        super().__init__(id_entidad=id_reserva)

        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaException("El cliente asociado debe ser una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaException("El servicio debe ser una subclase válida de Servicio.")

        try:
            duracion_val = float(duracion)
            descuento_val = float(descuento)
            impuesto_val = float(impuesto)
        except (ValueError, TypeError) as err_conversion:
            raise ParametroServicioInvalidoException(
                f"Parámetros numéricos de reserva corruptos o no convertibles: {err_conversion}",
                parametro="duracion/descuento/impuesto"
            ) from err_conversion

        if duracion_val <= 0:
            raise ParametroServicioInvalidoException("La duración de la reserva debe ser mayor a cero.", "duracion")

        # Verificar que el servicio esté disponible en el momento de crear la reserva
        servicio.verificar_disponibilidad()

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion_val
        self._descuento = descuento_val
        self._impuesto = impuesto_val
        self._estado = EstadoReserva.PENDIENTE
        self._costo_total = 0.0
        self._fecha_procesamiento: Optional[datetime] = None

        # Cálculo inicial del costo mediante método sobrecargado
        self.recalcular_costo()

        logger_sistema.info(
            f"[RESERVA CREADA] Reserva {self.id_entidad} creada en estado PENDIENTE para {self._cliente.nombre} "
            f"con servicio {self._servicio.codigo}. Total estimado: ${self._costo_total:,.2f}"
        )

    # --- Propiedades ---

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    # --- Métodos del ciclo de vida con bloques demostrativos de excepciones ---

    def recalcular_costo(self) -> float:
        """Calcula el costo total aplicando el método sobrecargado de Servicio.

        Demuestra el uso de try/except/else para cálculo seguro.
        """
        try:
            total = self._servicio.calcular_costo_sobrecargado(
                unidades=self._duracion,
                descuento=self._descuento,
                impuesto_iva=self._impuesto,
            )
        except SoftwareFJException as exc:
            logger_sistema.error(f"Error al calcular costo para reserva {self.id_entidad}: {exc}")
            raise
        else:
            # Se ejecuta únicamente si el bloque try tuvo éxito
            self._costo_total = total
            logger_sistema.info(f"Costo recalculado con éxito para reserva {self.id_entidad}: ${self._costo_total:,.2f}")
            return self._costo_total

    def confirmar(self) -> bool:
        """Confirma una reserva en estado PENDIENTE.

        Demuestra el uso de validación de estado y try/except/finally.
        """
        confirmada = False
        try:
            logger_sistema.info(f"Iniciando proceso de confirmación de reserva {self.id_entidad}...")
            if self._estado != EstadoReserva.PENDIENTE:
                raise EstadoReservaInvalidoException(
                    id_reserva=self.id_entidad,
                    estado_actual=self._estado.value,
                    accion_intentada="CONFIRMAR (Requiere estado PENDIENTE)",
                )

            self._estado = EstadoReserva.CONFIRMADA
            confirmada = True
            logger_sistema.info(f"Reserva {self.id_entidad} confirmada satisfactoriamente.")
            return True

        except EstadoReservaInvalidoException as e:
            logger_sistema.warning(f"Fallo al confirmar reserva {self.id_entidad}: {e}")
            raise

        finally:
            # Auditoría asegurada en el archivo de logs a nivel INFO
            logger_sistema.info(
                f"[AUDITORIA FINALLY] Concluyó intento de confirmación en {self.id_entidad}. "
                f"Estado final: {self._estado.value}. Confirmada={confirmada}"
            )

    def cancelar(self, motivo: str = "Solicitud del cliente") -> bool:
        """Cancela una reserva siempre que no se encuentre ya PROCESADA o CANCELADA.

        Demuestra try/except/else/finally combinado.
        La mutación de estado ocurre estrictamente en el bloque else.
        """
        exito = False
        try:
            logger_sistema.info(f"Procesando cancelación de reserva {self.id_entidad} por motivo: '{motivo}'")
            if self._estado == EstadoReserva.PROCESADA:
                raise EstadoReservaInvalidoException(
                    id_reserva=self.id_entidad,
                    estado_actual=self._estado.value,
                    accion_intentada="CANCELAR (Una reserva ya completada y facturada no admite cancelación)",
                )
            if self._estado == EstadoReserva.CANCELADA:
                raise EstadoReservaInvalidoException(
                    id_reserva=self.id_entidad,
                    estado_actual=self._estado.value,
                    accion_intentada="CANCELAR (La reserva ya se encontraba cancelada previamente)",
                )

        except EstadoReservaInvalidoException as exc:
            logger_sistema.error(f"[ERROR CANCELACIÓN] {exc}")
            raise

        else:
            # La mutación de estado se ejecuta exclusivamente si la validación previa no lanzó excepción
            self._estado = EstadoReserva.CANCELADA
            exito = True
            logger_sistema.info(f"Reserva {self.id_entidad} ha sido cancelada exitosamente.")

        finally:
            # Auditoría asegurada en finally a nivel INFO
            logger_sistema.info(f"[CLEANUP FINALLY] Operación de cancelación concluida en {self.id_entidad} con resultado={exito}")

        return exito

    def procesar(self) -> bool:
        """Procesa y liquida el servicio contratado.

        Requiere que la reserva esté previamente CONFIRMADA.
        """
        try:
            logger_sistema.info(f"Procesando y facturando reserva {self.id_entidad}...")
            if self._estado != EstadoReserva.CONFIRMADA:
                raise EstadoReservaInvalidoException(
                    id_reserva=self.id_entidad,
                    estado_actual=self._estado.value,
                    accion_intentada="PROCESAR (Se requiere confirmación previa en estado CONFIRMADA)",
                )

            self._estado = EstadoReserva.PROCESADA
            self._fecha_procesamiento = datetime.now()
            logger_sistema.info(
                f"[RESERVA PROCESADA] Reserva {self.id_entidad} procesada con éxito. Total facturado: ${self._costo_total:,.2f}"
            )
            return True

        except EstadoReservaInvalidoException as e:
            logger_sistema.error(f"[FALLO PROCESAMIENTO] Reserva {self.id_entidad}: {e}")
            raise

    # --- Métodos de la clase abstracta EntidadBase ---

    def validar(self) -> bool:
        return self._cliente.validar() and self._servicio.validar() and self._duracion > 0

    def obtener_resumen(self) -> str:
        return (
            f"RESERVA #{self.id_entidad} | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Duración: {self._duracion} | "
            f"Total: ${self._costo_total:,.2f} | Estado: {self._estado.value}"
        )

    def __str__(self) -> str:
        return self.obtener_resumen()
