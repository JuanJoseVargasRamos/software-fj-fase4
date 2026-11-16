"""
Módulo de Excepciones Personalizadas para Software FJ.

Define una jerarquía robusta de 17 excepciones orientadas a objetos
para capturar de forma precisa cualquier inconsistencia del dominio:
validaciones de datos, reglas de negocio de reservas, estado de servicios,
búsquedas relacionales y cálculos financieros.
"""


# Excepción raíz: hereda de Exception y de ella derivan todas las demás
class SoftwareFJException(Exception):
    """Excepción raíz para todas las anomalías en el sistema Software FJ."""

    # Recibe el mensaje y un código de error para identificar el tipo de fallo
    def __init__(self, mensaje: str, codigo_error: str = "ERR-GENERICO"):
        # Inicializa la clase Exception con el mensaje
        super().__init__(mensaje)
        # Guarda el mensaje y el código como atributos
        self.mensaje = mensaje
        self.codigo_error = codigo_error

    # Al imprimir la excepción se muestra [CODIGO] mensaje
    def __str__(self) -> str:
        return f"[{self.codigo_error}] {self.mensaje}"


# ---------------------------------------------------------------------------
# Excepciones de Validación de Datos de Entrada
# ---------------------------------------------------------------------------

# Excepción general para datos de entrada inválidos
class DatosInvalidosException(SoftwareFJException):
    """Lanzada cuando un dato no cumple con el formato o rango requerido."""

    def __init__(self, mensaje: str, campo: str = "Desconocido"):
        # Asigna el código de error y el campo que falló
        super().__init__(mensaje, codigo_error="ERR-DATOS-INVALIDOS")
        self.campo = campo


# Excepción para cédulas con formato o longitud incorrecta
class IdentificacionInvalidaException(DatosInvalidosException):
    """Lanzada cuando la identificación no tiene formato numérico o longitud adecuada."""

    def __init__(self, mensaje: str, valor: str = ""):
        super().__init__(f"Identificación inválida '{valor}': {mensaje}", campo="identificacion")
        # Sobrescribe el código de error con uno más específico
        self.codigo_error = "ERR-ID-INVALIDA"
        self.valor = valor


# Excepción para correos sin formato válido
class EmailInvalidoException(DatosInvalidosException):
    """Lanzada cuando el correo electrónico no cumple con la estructura estándar."""

    def __init__(self, mensaje: str, email_erroneo: str = ""):
        super().__init__(f"Email inválido '{email_erroneo}': {mensaje}", campo="email")
        # Código de error específico del correo
        self.codigo_error = "ERR-EMAIL-INVALIDO"
        self.email_erroneo = email_erroneo


# Excepción para teléfonos con letras o longitud incorrecta
class TelefonoInvalidoException(DatosInvalidosException):
    """Lanzada cuando el teléfono contiene caracteres no numéricos o longitud inadecuada."""

    def __init__(self, mensaje: str, telefono_erroneo: str = ""):
        super().__init__(f"Teléfono inválido '{telefono_erroneo}': {mensaje}", campo="telefono")
        # Código de error específico del teléfono
        self.codigo_error = "ERR-TEL-INVALIDO"
        self.telefono_erroneo = telefono_erroneo


# ---------------------------------------------------------------------------
# Excepciones de Servicios
# ---------------------------------------------------------------------------

# Excepción base para errores relacionados con servicios
class ServicioException(SoftwareFJException):
    """Base para excepciones asociadas a la gestión y configuración de servicios."""

    def __init__(self, mensaje: str, codigo_error: str = "ERR-SERVICIO"):
        super().__init__(mensaje, codigo_error)


# Se lanza cuando se intenta reservar un servicio inactivo
class ServicioNoDisponibleException(ServicioException):
    """Lanzada al intentar solicitar o reservar un servicio que se encuentra inactivo."""

    def __init__(self, id_servicio: str, motivo: str = "El servicio está inactivo o fuera de servicio"):
        super().__init__(
            f"El servicio '{id_servicio}' no se encuentra disponible: {motivo}",
            codigo_error="ERR-SERVICIO-NO-DISPONIBLE"
        )
        # Guarda el código del servicio que no estaba disponible
        self.id_servicio = id_servicio


# Se lanza cuando un parámetro del servicio es incorrecto (tarifa, capacidad, horas)
class ParametroServicioInvalidoException(ServicioException):
    """Lanzada cuando los parámetros específicos de un servicio son incongruentes."""

    def __init__(self, mensaje: str, parametro: str = ""):
        super().__init__(f"Parámetro de servicio inválido ({parametro}): {mensaje}", codigo_error="ERR-PARAM-SERVICIO")
        self.parametro = parametro


# Se lanza cuando los asistentes superan la capacidad de la sala
class CapacidadExcedidaException(ServicioException):
    """Lanzada cuando el número de asistentes excede el aforo permitido de la sala."""

    def __init__(self, capacidad_max: int, personas_solicitadas: int):
        super().__init__(
            f"Capacidad máxima excedida. Máximo permitido: {capacidad_max}, Solicitados: {personas_solicitadas}",
            codigo_error="ERR-CAPACIDAD-EXCEDIDA"
        )
        # Guarda la capacidad máxima y las personas solicitadas
        self.capacidad_max = capacidad_max
        self.capacidad_maxima = capacidad_max
        self.personas_solicitadas = personas_solicitadas


# ---------------------------------------------------------------------------
# Excepciones de Reservas
# ---------------------------------------------------------------------------

# Excepción base para errores en reservas
class ReservaException(SoftwareFJException):
    """Base para errores en el ciclo de vida de una reserva."""

    def __init__(self, mensaje: str, codigo_error: str = "ERR-RESERVA"):
        super().__init__(mensaje, codigo_error)


# Se lanza cuando la reserva tiene datos inconsistentes
class ReservaInvalidaException(ReservaException):
    """Lanzada cuando una reserva posee inconsistencias en sus componentes."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-RESERVA-INVALIDA")


# Se lanza cuando se intenta un cambio de estado no permitido
class EstadoReservaInvalidoException(ReservaException):
    """Lanzada cuando se intenta una transición de estado ilegal."""

    def __init__(self, id_reserva: str, estado_actual: str, accion_intentada: str):
        super().__init__(
            f"No es posible ejecutar '{accion_intentada}' en la reserva '{id_reserva}' con estado actual '{estado_actual}'",
            codigo_error="ERR-ESTADO-TRANSICION-ILEGAL"
        )
        # Guarda la reserva, su estado actual y la acción que se intentó
        self.id_reserva = id_reserva
        self.estado_actual = estado_actual
        self.accion_intentada = accion_intentada


# Se lanza cuando la cédula del cliente no está registrada
class ClienteNoEncontradoException(ReservaException):
    """Lanzada al intentar asociar una reserva a un cliente no registrado."""

    def __init__(self, identificacion: str):
        super().__init__(f"Cliente con identificación '{identificacion}' no existe en el sistema.", codigo_error="ERR-CLIENTE-NO-HALLADO")
        self.identificacion = identificacion


# Se lanza cuando el código de servicio no existe en el catálogo
class ServicioNoEncontradoException(ReservaException):
    """Lanzada al buscar un código de servicio inexistente en el catálogo."""

    def __init__(self, id_servicio: str):
        super().__init__(f"Servicio con código '{id_servicio}' no fue localizado.", codigo_error="ERR-SERVICIO-NO-HALLADO")
        self.id_servicio = id_servicio


# Se lanza cuando se busca una reserva que no existe
class ReservaNoEncontradaException(ReservaException):
    """Lanzada al buscar una reserva por identificador que no existe en el sistema."""

    def __init__(self, id_reserva: str):
        super().__init__(f"La reserva con ID '{id_reserva}' no existe en el sistema.", codigo_error="ERR-RESERVA-NO-HALLADA")
        self.id_reserva = id_reserva


# ---------------------------------------------------------------------------
# Excepciones de Operaciones y Cálculos
# ---------------------------------------------------------------------------

# Se lanza cuando una operación no está permitida (ej. cédula duplicada)
class OperacionNoPermitidaException(SoftwareFJException):
    """Lanzada cuando una acción infringe las políticas globales de seguridad u operación."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-OPERACION-NO-PERMITIDA")


# Se lanza cuando un cálculo de costos falla; se usa con raise ... from
class CalculoInconsistenteException(SoftwareFJException):
    """Lanzada cuando el cálculo financiero arroja valores anómalos o división errónea."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-CALCULO-INCONSISTENTE")
