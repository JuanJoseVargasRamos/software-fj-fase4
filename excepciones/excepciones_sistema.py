"""
Módulo de Excepciones Personalizadas para Software FJ.

Define una jerarquía robusta de excepciones orientadas a objetos
para capturar de forma precisa cualquier inconsistencia del dominio:
validaciones de datos, reglas de negocio de reservas, estado de servicios
y cálculos financieros.
"""


class SoftwareFJException(Exception):
    """Excepción raíz para todas las anomalías en el sistema Software FJ.
    
    Permite capturar cualquier error propio del dominio sin atrapar
    excepciones genéricas del sistema de Python a menos que sea explícito.
    """

    def __init__(self, mensaje: str, codigo_error: str = "ERR-GENERICO"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error

    def __str__(self) -> str:
        return f"[{self.codigo_error}] {self.mensaje}"


# ---------------------------------------------------------------------------
# Excepciones de Validación de Datos de Entrada
# ---------------------------------------------------------------------------

class DatosInvalidosException(SoftwareFJException):
    """Lanzada cuando un dato suministrado por el usuario no cumple con el formato o rango requerido."""

    def __init__(self, mensaje: str, campo: str = "Desconocido"):
        super().__init__(mensaje, codigo_error="ERR-DATOS-INVALIDOS")
        self.campo = campo


class IdentificacionInvalidaException(DatosInvalidosException):
    """Lanzada cuando la cédula o ID no tiene el formato numérico o longitud adecuada."""

    def __init__(self, mensaje: str, valor: str = ""):
        super().__init__(f"Identificación inválida '{valor}': {mensaje}", campo="identificacion")
        self.codigo_error = "ERR-ID-INVALIDA"
        self.valor = valor


class EmailInvalidoException(DatosInvalidosException):
    """Lanzada cuando el correo electrónico no cumple con la estructura estándar (RFC 5322)."""

    def __init__(self, mensaje: str, email_erroneo: str = ""):
        super().__init__(f"Email inválido '{email_erroneo}': {mensaje}", campo="email")
        self.codigo_error = "ERR-EMAIL-INVALIDO"
        self.email_erroneo = email_erroneo


class TelefonoInvalidoException(DatosInvalidosException):
    """Lanzada cuando el teléfono contiene caracteres no numéricos o longitud inadecuada."""

    def __init__(self, mensaje: str, telefono_erroneo: str = ""):
        super().__init__(f"Teléfono inválido '{telefono_erroneo}': {mensaje}", campo="telefono")
        self.codigo_error = "ERR-TEL-INVALIDO"
        self.telefono_erroneo = telefono_erroneo


# ---------------------------------------------------------------------------
# Excepciones de Servicios
# ---------------------------------------------------------------------------

class ServicioException(SoftwareFJException):
    """Base para excepciones asociadas a la gestión y configuración de servicios."""

    def __init__(self, mensaje: str, codigo_error: str = "ERR-SERVICIO"):
        super().__init__(mensaje, codigo_error)


class ServicioNoDisponibleException(ServicioException):
    """Lanzada al intentar solicitar o reservar un servicio que se encuentra inactivo, ocupado o en mantenimiento."""

    def __init__(self, id_servicio: str, motivo: str = "El servicio está inactivo o fuera de servicio"):
        super().__init__(
            f"El servicio '{id_servicio}' no se encuentra disponible: {motivo}",
            codigo_error="ERR-SERVICIO-NO-DISPONIBLE"
        )
        self.id_servicio = id_servicio


class ParametroServicioInvalidoException(ServicioException):
    """Lanzada cuando los parámetros específicos de un servicio (duración, días, capacidad) son incongruentes."""

    def __init__(self, mensaje: str, parametro: str = ""):
        super().__init__(f"Parámetro de servicio inválido ({parametro}): {mensaje}", codigo_error="ERR-PARAM-SERVICIO")
        self.parametro = parametro


class CapacidadExcedidaException(ServicioException):
    """Lanzada cuando el número de asistentes excede el aforo permitido de la sala."""

    def __init__(self, capacidad_max: int, personas_solicitadas: int):
        super().__init__(
            f"Capacidad máxima excedida. Máximo permitido: {capacidad_max}, Solicitados: {personas_solicitadas}",
            codigo_error="ERR-CAPACIDAD-EXCEDIDA"
        )
        self.capacidad_max = capacidad_max
        self.capacidad_maxima = capacidad_max
        self.personas_solicitadas = personas_solicitadas


# ---------------------------------------------------------------------------
# Excepciones de Reservas
# ---------------------------------------------------------------------------

class ReservaException(SoftwareFJException):
    """Base para errores en el ciclo de vida de una reserva (creación, confirmación, cancelación)."""

    def __init__(self, mensaje: str, codigo_error: str = "ERR-RESERVA"):
        super().__init__(mensaje, codigo_error)


class ReservaInvalidaException(ReservaException):
    """Lanzada cuando una reserva no puede constituirse por inconsistencias en sus componentes."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-RESERVA-INVALIDA")


class EstadoReservaInvalidoException(ReservaException):
    """Lanzada cuando se intenta una transición de estado ilegal (ej. cancelar una reserva ya procesada)."""

    def __init__(self, id_reserva: str, estado_actual: str, accion_intentada: str):
        super().__init__(
            f"No es posible ejecutar '{accion_intentada}' en la reserva '{id_reserva}' con estado actual '{estado_actual}'",
            codigo_error="ERR-ESTADO-TRANSICION-ILEGAL"
        )
        self.id_reserva = id_reserva
        self.estado_actual = estado_actual
        self.accion_intentada = accion_intentada


class ClienteNoEncontradoException(ReservaException):
    """Lanzada al intentar asociar una reserva a un cliente no registrado."""

    def __init__(self, identificacion: str):
        super().__init__(f"Cliente con identificación '{identificacion}' no existe en el sistema.", codigo_error="ERR-CLIENTE-NO-HALLADO")
        self.identificacion = identificacion


class ServicioNoEncontradoException(ReservaException):
    """Lanzada al buscar un código de servicio inexistente en el catálogo."""

    def __init__(self, id_servicio: str):
        super().__init__(f"Servicio con código '{id_servicio}' no fue localizado.", codigo_error="ERR-SERVICIO-NO-HALLADO")
        self.id_servicio = id_servicio


# ---------------------------------------------------------------------------
# Excepciones de Operaciones y Cálculos
# ---------------------------------------------------------------------------

class OperacionNoPermitidaException(SoftwareFJException):
    """Lanzada cuando una acción infringe las políticas globales de seguridad u operación de Software FJ."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-OPERACION-NO-PERMITIDA")


class CalculoInconsistenteException(SoftwareFJException):
    """Lanzada cuando el cálculo financiero arroja valores anómalos (ej. costos negativos o división entre cero)."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-CALCULO-INCONSISTENTE")
