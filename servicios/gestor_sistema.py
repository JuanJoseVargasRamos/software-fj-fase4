"""
Módulo del Gestor del Sistema para Software FJ.

Implementa la arquitectura de gestión centralizada en memoria (sin bases de datos),
utilizando listas internas para clientes, servicios y reservas.
Aplica principios de alta cohesión, desacoplamiento y registro exhaustivo de logs.
"""

from typing import List, Optional, Dict
from modelos.cliente import Cliente
from modelos.servicio import Servicio
from modelos.reserva import Reserva, EstadoReserva
from excepciones.excepciones_sistema import (
    ClienteNoEncontradoException,
    ServicioNoEncontradoException,
    ReservaInvalidaException,
    OperacionNoPermitidaException,
    SoftwareFJException,
)
from configuracion.logger_config import logger_sistema


class SistemaGestionSoftwareFJ:
    """Controlador principal de Software FJ.

    Mantiene el estado global de la aplicación en memoria mediante colecciones
    y gestiona todas las transacciones de negocio controlando excepciones.
    """

    def __init__(self, razon_social: str = "Software FJ S.A.S."):
        self.razon_social = razon_social
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        logger_sistema.info(f"Sistema inicializado con éxito para '{self.razon_social}'.")

    # -----------------------------------------------------------------------
    # Gestión de Clientes
    # -----------------------------------------------------------------------

    def registrar_cliente(self, identificacion: str, nombre: str, email: str, telefono: str) -> Cliente:
        """Registra un nuevo cliente validando que no exista duplicidad de identificación."""
        try:
            logger_sistema.info(f"Intentando registrar cliente con ID: {identificacion}")
            # Validar si ya existe
            for c in self._clientes:
                if c.identificacion == str(identificacion).strip():
                    raise OperacionNoPermitidaException(
                        f"Ya existe un cliente registrado con la identificación '{identificacion}'."
                    )

            # Instanciación sujeta a validaciones internas de Cliente
            nuevo_cliente = Cliente(identificacion, nombre, email, telefono)
            self._clientes.append(nuevo_cliente)
            logger_sistema.info(f"Cliente registrado con éxito: {nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente

        except SoftwareFJException as exc:
            logger_sistema.warning(f"Rechazo en registro de cliente ({identificacion}): {exc}")
            raise

    def buscar_cliente(self, identificacion: str) -> Cliente:
        """Busca un cliente por su documento de identidad. Lanza excepción si no existe."""
        id_limpio = str(identificacion).strip()
        for cliente in self._clientes:
            if cliente.identificacion == id_limpio:
                return cliente
        logger_sistema.error(f"Búsqueda fallida: Cliente con cédula '{identificacion}' no encontrado.")
        raise ClienteNoEncontradoException(id_limpio)

    def listar_clientes(self) -> List[Cliente]:
        """Retorna una copia de la lista de clientes registrados."""
        return list(self._clientes)

    # -----------------------------------------------------------------------
    # Gestión de Servicios
    # -----------------------------------------------------------------------

    def registrar_servicio(self, servicio: Servicio) -> None:
        """Registra un nuevo servicio en el catálogo de la empresa."""
        try:
            if not isinstance(servicio, Servicio):
                raise OperacionNoPermitidaException("El objeto a registrar debe derivar de la clase Servicio.")

            # Validar que no se repita el código
            for s in self._servicios:
                if s.codigo == servicio.codigo:
                    raise OperacionNoPermitidaException(
                        f"El código de servicio '{servicio.codigo}' ya se encuentra en uso por '{s.nombre}'."
                    )

            self._servicios.append(servicio)
            logger_sistema.info(f"Servicio incorporado al catálogo: {servicio.obtener_resumen()}")

        except SoftwareFJException as exc:
            logger_sistema.error(f"Error al registrar servicio {servicio}: {exc}")
            raise

    def buscar_servicio(self, codigo_servicio: str) -> Servicio:
        """Localiza un servicio por su código único en el catálogo."""
        codigo_limpio = str(codigo_servicio).strip().upper()
        for servicio in self._servicios:
            if servicio.codigo == codigo_limpio:
                return servicio
        logger_sistema.error(f"Búsqueda fallida: Servicio con código '{codigo_servicio}' no encontrado.")
        raise ServicioNoEncontradoException(codigo_limpio)

    def listar_servicios(self) -> List[Servicio]:
        """Retorna una copia del catálogo de servicios."""
        return list(self._servicios)

    # -----------------------------------------------------------------------
    # Gestión de Reservas
    # -----------------------------------------------------------------------

    def crear_reserva(
        self,
        id_reserva: str,
        identificacion_cliente: str,
        codigo_servicio: str,
        duracion: float,
        descuento: float = 0.0,
        impuesto: float = 0.19,
    ) -> Reserva:
        """Crea y registra una reserva vinculando cliente y servicio.

        Maneja validación de dependencias y duplicidades.
        """
        try:
            id_res_limpio = str(id_reserva).strip().upper()
            logger_sistema.info(f"Creando reserva '{id_res_limpio}' para cliente '{identificacion_cliente}'...")

            # Validar que el ID de reserva sea único
            for r in self._reservas:
                if r.id_entidad == id_res_limpio:
                    raise OperacionNoPermitidaException(f"Ya existe una reserva con el código '{id_res_limpio}'.")

            # Buscar entidades requeridas (disparan excepciones si no existen)
            cliente = self.buscar_cliente(identificacion_cliente)
            servicio = self.buscar_servicio(codigo_servicio)

            # Instanciar reserva (aplica validaciones de servicio, disponibilidad y duración)
            nueva_reserva = Reserva(
                id_reserva=id_res_limpio,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                descuento=descuento,
                impuesto=impuesto,
            )

            self._reservas.append(nueva_reserva)
            logger_sistema.info(f"Reserva registrada en el sistema: {nueva_reserva.obtener_resumen()}")
            return nueva_reserva

        except SoftwareFJException as exc:
            logger_sistema.warning(f"Rechazo en creación de reserva '{id_reserva}': {exc}")
            raise

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        """Localiza una reserva por su identificador único."""
        id_limpio = str(id_reserva).strip().upper()
        for reserva in self._reservas:
            if reserva.id_entidad == id_limpio:
                return reserva
        logger_sistema.error(f"Búsqueda fallida: Reserva '{id_reserva}' no encontrada.")
        raise ReservaInvalidaException(f"La reserva con ID '{id_reserva}' no existe en el sistema.")

    def confirmar_reserva(self, id_reserva: str) -> bool:
        """Confirma una reserva existente gestionando excepciones."""
        reserva = self.buscar_reserva(id_reserva)
        return reserva.confirmar()

    def cancelar_reserva(self, id_reserva: str, motivo: str = "Cancelado por el cliente") -> bool:
        """Cancela una reserva existente gestionando excepciones."""
        reserva = self.buscar_reserva(id_reserva)
        return reserva.cancelar(motivo)

    def procesar_reserva(self, id_reserva: str) -> bool:
        """Procesa y factura una reserva confirmada."""
        reserva = self.buscar_reserva(id_reserva)
        return reserva.procesar()

    def listar_reservas(self) -> List[Reserva]:
        """Retorna una copia de todas las reservas registradas."""
        return list(self._reservas)

    # -----------------------------------------------------------------------
    # Reportes y Estadísticas
    # -----------------------------------------------------------------------

    def generar_reporte_estado(self) -> Dict[str, any]:
        """Genera un balance del estado actual del sistema."""
        total_facturado = sum(
            r.costo_total for r in self._reservas if r.estado == EstadoReserva.PROCESADA
        )
        conteo_estados = {estado.value: 0 for estado in EstadoReserva}
        for r in self._reservas:
            conteo_estados[r.estado.value] += 1

        return {
            "empresa": self.razon_social,
            "total_clientes": len(self._clientes),
            "total_servicios": len(self._servicios),
            "total_reservas": len(self._reservas),
            "conteo_por_estado": conteo_estados,
            "ingresos_procesados": total_facturado,
        }
