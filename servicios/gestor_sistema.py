"""
Módulo del Gestor del Sistema para Software FJ.

Implementa la arquitectura de gestión centralizada en memoria (sin bases de datos),
utilizando listas internas para clientes, servicios y reservas.
Aplica principios de alta cohesión, desacoplamiento y registro exhaustivo de logs.
"""

# Tipos para indicar listas y diccionarios en las anotaciones
from typing import List, Dict, Any
from modelos.cliente import Cliente
from modelos.servicio import Servicio
from modelos.reserva import Reserva, EstadoReserva
from excepciones.excepciones_sistema import (
    ClienteNoEncontradoException,
    ServicioNoEncontradoException,
    ReservaNoEncontradaException,
    OperacionNoPermitidaException,
    SoftwareFJException,
)
# Logger para registrar eventos y errores en el archivo de logs
from configuracion.logger_config import logger_sistema


class SistemaGestionSoftwareFJ:
    """Controlador principal de Software FJ.

    Mantiene el estado global de la aplicación en memoria mediante colecciones
    y gestiona todas las transacciones de negocio controlando excepciones.
    """

    # Nombre de la empresa
    def __init__(self, razon_social: str = "Software FJ S.A.S."):
        self.razon_social = razon_social
        # Listas internas en memoria (no se usa base de datos)
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        # Registra en el log que el sistema inició
        logger_sistema.info(f"Sistema inicializado con éxito para '{self.razon_social}'.")

    # -----------------------------------------------------------------------
    # Gestión de Clientes
    # -----------------------------------------------------------------------

    def registrar_cliente(self, identificacion: str, nombre: str, email: str, telefono: str) -> Cliente:
        """Registra un nuevo cliente validando que no exista duplicidad de identificación."""
        # try/except: si ocurre un error de dominio se registra en el log y se propaga
        try:
            logger_sistema.info(f"Intentando registrar cliente con ID: {identificacion}")
            # Recorre los clientes para verificar que la cédula no esté repetida
            for c in self._clientes:
                if c.identificacion == str(identificacion).strip():
                    raise OperacionNoPermitidaException(
                        f"Ya existe un cliente registrado con la identificación '{identificacion}'."
                    )

            # Crea el cliente; el constructor valida todos los datos
            nuevo_cliente = Cliente(identificacion, nombre, email, telefono)
            # Agrega el cliente a la lista en memoria
            self._clientes.append(nuevo_cliente)
            logger_sistema.info(f"Cliente registrado con éxito: {nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente

        # Captura cualquier excepción personalizada del sistema
        except SoftwareFJException as exc:
            # Registra la advertencia en el log
            logger_sistema.warning(f"Rechazo en registro de cliente ({identificacion}): {exc}")
            # Vuelve a lanzar la excepción para que la maneje quien llamó al método
            raise

    def buscar_cliente(self, identificacion: str) -> Cliente:
        """Busca un cliente por su documento de identidad. Lanza excepción si no existe."""
        # Limpia la cédula recibida
        id_limpio = str(identificacion).strip()
        # Busca el cliente en la lista
        for cliente in self._clientes:
            if cliente.identificacion == id_limpio:
                return cliente
        # Si no se encontró, registra el error y lanza la excepción
        logger_sistema.error(f"Búsqueda fallida: Cliente con cédula '{identificacion}' no encontrado.")
        raise ClienteNoEncontradoException(id_limpio)

    def listar_clientes(self) -> List[Cliente]:
        """Retorna una copia de la lista de clientes registrados."""
        # Devuelve una copia para no modificar la lista original
        return list(self._clientes)

    # -----------------------------------------------------------------------
    # Gestión de Servicios
    # -----------------------------------------------------------------------

    def registrar_servicio(self, servicio: Servicio) -> None:
        """Registra un nuevo servicio en el catálogo de la empresa."""
        # try/except para controlar errores al registrar servicios
        try:
            # Solo se permiten objetos que hereden de Servicio
            if not isinstance(servicio, Servicio):
                raise OperacionNoPermitidaException("El objeto a registrar debe derivar de la clase Servicio.")

            # Verifica que el código del servicio no esté repetido
            for s in self._servicios:
                if s.codigo == servicio.codigo:
                    raise OperacionNoPermitidaException(
                        f"El código de servicio '{servicio.codigo}' ya se encuentra en uso por '{s.nombre}'."
                    )

            # Agrega el servicio al catálogo
            self._servicios.append(servicio)
            logger_sistema.info(f"Servicio incorporado al catálogo: {servicio.obtener_resumen()}")

        # Registra el error en el log y lo propaga
        except SoftwareFJException as exc:
            logger_sistema.error(f"Error al registrar servicio {servicio}: {exc}")
            raise

    def buscar_servicio(self, codigo_servicio: str) -> Servicio:
        """Localiza un servicio por su código único en el catálogo."""
        # Normaliza el código a mayúsculas
        codigo_limpio = str(codigo_servicio).strip().upper()
        for servicio in self._servicios:
            if servicio.codigo == codigo_limpio:
                return servicio
        # Si no existe, registra el error y lanza la excepción
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
        recargo_urgencia: float = 0.0,
        **detalles_servicio,
    ) -> Reserva:
        """Crea y registra una reserva vinculando cliente y servicio."""
        # try/except: controla errores al crear la reserva
        try:
            id_res_limpio = str(id_reserva).strip().upper()
            logger_sistema.info(f"Creando reserva '{id_res_limpio}' para cliente '{identificacion_cliente}'...")

            # Verifica que el código de reserva no esté repetido
            for r in self._reservas:
                if r.id_entidad == id_res_limpio:
                    raise OperacionNoPermitidaException(f"Ya existe una reserva con el código '{id_res_limpio}'.")

            # Busca cliente y servicio; si no existen se lanzan excepciones
            cliente = self.buscar_cliente(identificacion_cliente)
            servicio = self.buscar_servicio(codigo_servicio)

            # Crea la reserva; su constructor valida los parámetros
            nueva_reserva = Reserva(
                id_reserva=id_res_limpio,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                descuento=descuento,
                impuesto=impuesto,
                recargo_urgencia=recargo_urgencia,
                **detalles_servicio,
            )

            # Guarda la reserva en la lista
            self._reservas.append(nueva_reserva)
            logger_sistema.info(f"Reserva registrada en el sistema: {nueva_reserva.obtener_resumen()}")
            return nueva_reserva

        # Registra el rechazo en el log y propaga la excepción
        except SoftwareFJException as exc:
            logger_sistema.warning(f"Rechazo en creación de reserva '{id_reserva}': {exc}")
            raise

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        """Localiza una reserva por su identificador único. Lanza ReservaNoEncontradaException si no existe."""
        # Normaliza el código de la reserva
        id_limpio = str(id_reserva).strip().upper()
        for reserva in self._reservas:
            if reserva.id_entidad == id_limpio:
                return reserva
        # Si no existe, registra el error y lanza ReservaNoEncontradaException
        logger_sistema.error(f"Búsqueda fallida: Reserva '{id_reserva}' no encontrada.")
        raise ReservaNoEncontradaException(id_limpio)

    def confirmar_reserva(self, id_reserva: str) -> bool:
        """Confirma una reserva existente gestionando excepciones."""
        # Busca la reserva y la confirma
        reserva = self.buscar_reserva(id_reserva)
        return reserva.confirmar()

    def cancelar_reserva(self, id_reserva: str, motivo: str = "Cancelado por el cliente") -> bool:
        """Cancela una reserva existente gestionando excepciones."""
        # Busca la reserva y la cancela con el motivo indicado
        reserva = self.buscar_reserva(id_reserva)
        return reserva.cancelar(motivo)

    def procesar_reserva(self, id_reserva: str) -> bool:
        """Procesa y factura una reserva confirmada."""
        # Busca la reserva y la procesa (factura)
        reserva = self.buscar_reserva(id_reserva)
        return reserva.procesar()

    def listar_reservas(self) -> List[Reserva]:
        """Retorna una copia de todas las reservas registradas."""
        return list(self._reservas)

    # -----------------------------------------------------------------------
    # Reportes y Estadísticas
    # -----------------------------------------------------------------------

    def generar_reporte_estado(self) -> Dict[str, Any]:
        """Genera un balance del estado actual del sistema."""
        # Suma el costo de las reservas que ya fueron procesadas
        total_facturado = sum(
            r.costo_total for r in self._reservas if r.estado == EstadoReserva.PROCESADA
        )
        # Cuenta cuántas reservas hay en cada estado
        conteo_estados = {estado.value: 0 for estado in EstadoReserva}
        for r in self._reservas:
            conteo_estados[r.estado.value] += 1

        # Devuelve el reporte en un diccionario
        return {
            "empresa": self.razon_social,
            "total_clientes": len(self._clientes),
            "total_servicios": len(self._servicios),
            "total_reservas": len(self._reservas),
            "conteo_por_estado": conteo_estados,
            "ingresos_procesados": total_facturado,
        }
