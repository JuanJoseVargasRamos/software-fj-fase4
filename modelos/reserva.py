"""
Módulo de Gestión de Reservas para Software FJ.

Define la clase Reserva, que integra Cliente, Servicio, Duración y Estado.
Implementa el ciclo de vida completo de la reserva (confirmación, cancelación,
procesamiento y facturación), incorporando:
- Bloques try/except
- Bloques try/except/else
- Bloques try/finally
- Encadenamiento de excepciones (raise ... from ...)
- Validación rigurosa de números finitos (protección contra NaN e Inf)
- Registro en logs de cada transición.
"""

# math se usa para validar valores finitos
import math
# Enum para definir los estados de la reserva
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

from modelos.base import EntidadBase
from modelos.cliente import Cliente
from modelos.servicio import Servicio
from excepciones.excepciones_sistema import (
    EstadoReservaInvalidoException,
    ParametroServicioInvalidoException,
    ReservaInvalidaException,
    SoftwareFJException,
)
# Logger para registrar eventos y errores
from configuracion.logger_config import logger_sistema


# Estados posibles de una reserva
class EstadoReserva(Enum):
    """Enumeración con los estados oficiales del ciclo de vida de una reserva."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"


# Reserva hereda de EntidadBase
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
        recargo_urgencia: float = 0.0,
        **detalles_servicio,
    ):
        # Llama al constructor de la clase padre
        super().__init__(id_entidad=id_reserva)

        # Valida que el cliente y el servicio sean objetos correctos
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaException("El cliente asociado debe ser una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaException("El servicio debe ser una subclase válida de Servicio.")

        # try/except: convierte los parámetros numéricos
        try:
            duracion_val = float(duracion)
            descuento_val = float(descuento)
            impuesto_val = float(impuesto)
            recargo_val = float(recargo_urgencia)
        # Si falla la conversión, se encadena la excepción con raise ... from
        except (ValueError, TypeError) as err_conversion:
            raise ParametroServicioInvalidoException(
                f"Parámetros numéricos de reserva no convertibles: {err_conversion}",
                parametro="duracion/descuento/impuesto"
            ) from err_conversion

        # Valida que todos los valores sean finitos y estén en rango
        if not math.isfinite(duracion_val) or duracion_val <= 0:
            raise ParametroServicioInvalidoException("La duración debe ser un número finito positivo.", "duracion")
        if not math.isfinite(descuento_val) or not (0.0 <= descuento_val <= 0.80):
            raise ParametroServicioInvalidoException("El descuento debe ser un valor finito entre 0% y 80%.", "descuento")
        if not math.isfinite(impuesto_val) or impuesto_val < 0:
            raise ParametroServicioInvalidoException("El impuesto debe ser un valor finito no negativo.", "impuesto")
        if not math.isfinite(recargo_val) or recargo_val < 0:
            raise ParametroServicioInvalidoException("El recargo debe ser finito no negativo.", "recargo_urgencia")

        # Verificar que el servicio esté disponible en el momento de crear la reserva
        servicio.verificar_disponibilidad()

        # Guarda los datos de la reserva
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion_val
        self._descuento = descuento_val
        self._impuesto = impuesto_val
        self._recargo_urgencia = recargo_val
        self._detalles_servicio: Dict[str, Any] = detalles_servicio
        # Toda reserva inicia en estado PENDIENTE
        self._estado = EstadoReserva.PENDIENTE
        self._costo_total = 0.0
        self._fecha_procesamiento: Optional[datetime] = None

        # Cálculo inicial del costo mediante método sobrecargado
        self.recalcular_costo()

        # Registra en el log la creación de la reserva
        logger_sistema.info(
            f"[RESERVA CREADA] Reserva {self.id_entidad} creada en estado PENDIENTE para {self._cliente.nombre} "
            f"con servicio {self._servicio.codigo}. Total estimado: ${self._costo_total:,.2f}"
        )

    # --- Propiedades ---

    # Propiedades de solo lectura
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
        # try/except/else: calcula el costo de forma segura
        try:
            total = self._servicio.calcular_costo_sobrecargado(
                unidades=self._duracion,
                descuento=self._descuento,
                impuesto_iva=self._impuesto,
                recargo_urgencia=self._recargo_urgencia,
                **self._detalles_servicio,
            )
        # Si el cálculo falla, registra el error y lo propaga
        except SoftwareFJException as exc:
            logger_sistema.error(f"Error al calcular costo para reserva {self.id_entidad}: {exc}")
            raise
        # else: solo se ejecuta si no hubo error; guarda el total
        else:
            self._costo_total = total
            logger_sistema.info(f"Costo recalculado con éxito para reserva {self.id_entidad}: ${self._costo_total:,.2f}")
            return self._costo_total

    def confirmar(self) -> bool:
        """Confirma una reserva en estado PENDIENTE.

        Demuestra el uso de validación de estado y try/except/finally.
        """
        # Variable para saber si la confirmación tuvo éxito
        confirmada = False
        # try/except/finally
        try:
            logger_sistema.info(f"Iniciando proceso de confirmación de reserva {self.id_entidad}...")
            # Solo se puede confirmar una reserva PENDIENTE
            if self._estado != EstadoReserva.PENDIENTE:
                raise EstadoReservaInvalidoException(
                    id_reserva=self.id_entidad,
                    estado_actual=self._estado.value,
                    accion_intentada="CONFIRMAR (Requiere estado PENDIENTE)",
                )

            # Cambia el estado a CONFIRMADA
            self._estado = EstadoReserva.CONFIRMADA
            confirmada = True
            logger_sistema.info(f"Reserva {self.id_entidad} confirmada satisfactoriamente.")
            return True

        # Registra la advertencia y propaga la excepción
        except EstadoReservaInvalidoException as e:
            logger_sistema.warning(f"Fallo al confirmar reserva {self.id_entidad}: {e}")
            raise

        # finally: siempre se ejecuta, haya o no error
        finally:
            logger_sistema.info(
                f"[AUDITORIA FINALLY] Concluyó intento de confirmación en {self.id_entidad}. "
                f"Estado final: {self._estado.value}. Confirmada={confirmada}"
            )

    def cancelar(self, motivo: str = "Solicitud del cliente") -> bool:
        """Cancela una reserva siempre que no se encuentre ya PROCESADA o CANCELADA.

        Demuestra try/except/else/finally combinado.
        La mutación de estado ocurre estrictamente en el bloque else.
        """
        # Variable para saber si la cancelación tuvo éxito
        exito = False
        # try/except/else/finally
        try:
            logger_sistema.info(f"Procesando cancelación de reserva {self.id_entidad} por motivo: '{motivo}'")
            # No se puede cancelar una reserva ya procesada
            if self._estado == EstadoReserva.PROCESADA:
                raise EstadoReservaInvalidoException(
                    id_reserva=self.id_entidad,
                    estado_actual=self._estado.value,
                    accion_intentada="CANCELAR (Una reserva ya completada y facturada no admite cancelación)",
                )
            # No se puede cancelar una reserva ya cancelada
            if self._estado == EstadoReserva.CANCELADA:
                raise EstadoReservaInvalidoException(
                    id_reserva=self.id_entidad,
                    estado_actual=self._estado.value,
                    accion_intentada="CANCELAR (La reserva ya se encontraba cancelada previamente)",
                )

        # Registra el error en el log y propaga la excepción
        except EstadoReservaInvalidoException as exc:
            logger_sistema.error(f"[ERROR CANCELACIÓN] {exc}")
            raise

        # else: solo si no hubo error se cambia el estado a CANCELADA
        else:
            self._estado = EstadoReserva.CANCELADA
            exito = True
            logger_sistema.info(f"Reserva {self.id_entidad} ha sido cancelada exitosamente.")

        # finally: siempre registra el resultado en el log
        finally:
            logger_sistema.info(f"[CLEANUP FINALLY] Operación de cancelación concluida en {self.id_entidad} con resultado={exito}")

        return exito

    def procesar(self) -> bool:
        """Procesa y liquida el servicio contratado.

        Requiere que la reserva esté previamente CONFIRMADA.
        """
        # try/except: procesa la reserva
        try:
            logger_sistema.info(f"Procesando y facturando reserva {self.id_entidad}...")
            # Solo se puede procesar una reserva CONFIRMADA
            if self._estado != EstadoReserva.CONFIRMADA:
                raise EstadoReservaInvalidoException(
                    id_reserva=self.id_entidad,
                    estado_actual=self._estado.value,
                    accion_intentada="PROCESAR (Se requiere confirmación previa en estado CONFIRMADA)",
                )

            # Cambia el estado a PROCESADA y guarda la fecha
            self._estado = EstadoReserva.PROCESADA
            self._fecha_procesamiento = datetime.now()
            logger_sistema.info(
                f"[RESERVA PROCESADA] Reserva {self.id_entidad} procesada con éxito. Total facturado: ${self._costo_total:,.2f}"
            )
            return True

        # Registra el error en el log y propaga la excepción
        except EstadoReservaInvalidoException as e:
            logger_sistema.error(f"[FALLO PROCESAMIENTO] Reserva {self.id_entidad}: {e}")
            raise

    # --- Métodos de la clase abstracta EntidadBase ---

    def validar(self) -> bool:
        # Verifica que cliente, servicio y duración sean válidos
        if not self._cliente.validar() or not self._servicio.validar() or self._duracion <= 0:
            raise ReservaInvalidaException("La reserva contiene parámetros inválidos.")
        return True

    def obtener_resumen(self) -> str:
        # Devuelve un texto con el resumen de la reserva
        return (
            f"RESERVA #{self.id_entidad} | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Duración: {self._duracion} | "
            f"Total: ${self._costo_total:,.2f} | Estado: {self._estado.value}"
        )

    def __str__(self) -> str:
        return self.obtener_resumen()
