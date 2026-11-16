"""
Módulo de Servicios Especializados para Software FJ.

Define la clase abstracta Servicio y tres especializaciones concretas:
1. ReservaSala
2. AlquilerEquipo
3. AsesoriaEspecializada

Aplica polimorfismo, sobrescritura de métodos, simulación de sobrecarga,
validación de números finitos (protección contra NaN e Inf) y Exception Chaining.
"""

# math.isfinite permite detectar valores NaN o infinitos
import math
from abc import abstractmethod
from modelos.base import EntidadBase
from excepciones.excepciones_sistema import (
    CalculoInconsistenteException,
    CapacidadExcedidaException,
    ParametroServicioInvalidoException,
    ServicioNoDisponibleException,
)


# Clase abstracta Servicio: hereda de EntidadBase
class Servicio(EntidadBase):
    """Clase abstracta que modela cualquier servicio ofrecido por Software FJ."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, disponible: bool = True):
        # Normalizar código antes de invocar la clase base abstracta
        codigo_limpio = str(codigo).strip().upper()
        super().__init__(id_entidad=codigo_limpio)

        # try/except: convierte la tarifa a número
        try:
            tarifa_val = float(tarifa_base)
        # Si no se puede convertir, se encadena la excepción con raise ... from
        except (ValueError, TypeError) as err:
            raise ParametroServicioInvalidoException(f"Tarifa base no convertible: {err}", "tarifa_base") from err

        # La tarifa debe ser finita y no negativa
        if not math.isfinite(tarifa_val) or tarifa_val < 0:
            raise ParametroServicioInvalidoException("La tarifa base debe ser un número finito no negativo.", "tarifa_base")

        # Atributos protegidos del servicio
        self._codigo = codigo_limpio
        self._nombre = str(nombre).strip()
        self._tarifa_base = tarifa_val
        self._disponible = bool(disponible)

    # Propiedades de solo lectura
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

    # Permite activar o desactivar el servicio
    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self._disponible = bool(estado)

    def verificar_disponibilidad(self) -> None:
        """Verifica si el servicio se puede contratar; si no, lanza excepción."""
        # Si el servicio está inactivo, lanza ServicioNoDisponibleException
        if not self._disponible:
            raise ServicioNoDisponibleException(
                id_servicio=self._codigo,
                motivo=f"El servicio '{self._nombre}' se encuentra temporalmente inactivo o reservado."
            )

    # Métodos abstractos que cada tipo de servicio debe implementar (polimorfismo)
    @abstractmethod
    def describir_servicio(self) -> str:
        """Describe las características técnicas del servicio (sobrescrito por subclases)."""
        pass

    @abstractmethod
    def calcular_costo(self, cantidad_unidades: float, **kwargs) -> float:
        """Calcula el costo base o con parámetros polimórficos según la naturaleza del servicio."""
        pass

    # Método que simula sobrecarga con parámetros opcionales
    def calcular_costo_sobrecargado(
        self,
        unidades: float,
        descuento: float = 0.0,
        impuesto_iva: float = 0.19,
        recargo_urgencia: float = 0.0,
        **kwargs,
    ) -> float:
        """Método sobrecargado flexible para cálculo de costos con variantes financieras.

        Aplica validación estricta de números finitos con math.isfinite() y encadenamiento
        de excepciones (raise ... from error_original).

        Parámetros:
            unidades (float): Cantidad de unidades/horas/días del servicio (debe ser > 0).
            descuento (float): Porcentaje de descuento comercial aplicable (0.0 a 0.80).
            impuesto_iva (float): Tasa impositiva de IVA (por defecto 0.19 correspondiente al 19%).
            recargo_urgencia (float): Monto monetario fijo en pesos sumado al subtotal con descuento.
            **kwargs: Argumentos variables para reglas de negocio específicas de subclases.

        Retorna:
            float: Costo total liquidado redondeado a dos cifras decimales.
        """
        # try/except con encadenamiento de excepciones
        try:
            # Convierte todos los parámetros a número
            cant_float = float(unidades)
            desc_float = float(descuento)
            iva_float = float(impuesto_iva)
            recargo_float = float(recargo_urgencia)

            # Validación de números finitos para evitar inyección de float('nan') o float('inf')
            if not math.isfinite(cant_float) or cant_float <= 0:
                raise ValueError(f"Las unidades deben ser un número finito mayor a cero (recibido: {cant_float}).")
            if not math.isfinite(desc_float) or not (0.0 <= desc_float <= 0.80):
                raise ValueError(f"El porcentaje de descuento debe ser finito entre 0% y 80% (recibido: {desc_float*100}%).")
            if not math.isfinite(iva_float) or iva_float < 0:
                raise ValueError(f"El porcentaje de IVA debe ser un número finito no negativo (recibido: {iva_float}).")
            if not math.isfinite(recargo_float) or recargo_float < 0:
                raise ValueError(f"El recargo de urgencia debe ser un número finito no negativo (recibido: {recargo_float}).")

            # Calcula el subtotal según el tipo de servicio (polimorfismo)
            subtotal = self.calcular_costo(cant_float, **kwargs)
            # Aplica descuento, recargo e IVA
            factor_descuento = 1.0 - desc_float
            base_imponible = (subtotal * factor_descuento) + recargo_float
            total_final = base_imponible * (1.0 + iva_float)

            # Verifica que el resultado sea un valor válido
            if not math.isfinite(total_final) or total_final < 0:
                raise ArithmeticError("El cálculo final generó un valor monetario inconsistente o no finito.")

            # Devuelve el total redondeado a 2 decimales
            return round(total_final, 2)

        # Captura errores de cálculo y los convierte en CalculoInconsistenteException
        except (ValueError, TypeError, ZeroDivisionError, ArithmeticError) as error_original:
            raise CalculoInconsistenteException(
                f"Fallo en cálculo financiero sobrecargado para servicio '{self._codigo}': {str(error_original)}"
            ) from error_original

    def validar(self) -> bool:
        """Verifica la consistencia interna del servicio."""
        # Verifica que el servicio tenga código, nombre y tarifa válidos
        if not self._codigo or not self._nombre or self._tarifa_base < 0:
            raise ParametroServicioInvalidoException("El servicio contiene campos inconsistentes.", "servicio")
        return True

    def obtener_resumen(self) -> str:
        # Devuelve un texto con el resumen del servicio
        estado = "DISPONIBLE" if self._disponible else "NO DISPONIBLE"
        return f"[{self._codigo}] {self._nombre} | Tarifa Base: ${self._tarifa_base:,.2f} | Estado: {estado}"

    def __str__(self) -> str:
        return self.describir_servicio()


# ---------------------------------------------------------------------------
# Servicio Especializado 1: Reserva de Salas
# ---------------------------------------------------------------------------

# Subclase 1: hereda de Servicio
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
        # Llama al constructor de la clase padre
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        # La capacidad debe ser mayor a cero; si no, lanza excepción personalizada
        capacidad_val = int(capacidad_maxima)
        if capacidad_val <= 0:
            raise ParametroServicioInvalidoException("La capacidad máxima debe ser mayor a cero.", "capacidad_maxima")
        # Guarda los atributos propios de la sala
        self._capacidad_maxima = capacidad_val
        self._tipo_sala = str(tipo_sala).strip()
        self._incluye_proyector = bool(incluye_proyector)

    @property
    def capacidad_maxima(self) -> int:
        return self._capacidad_maxima

    @capacidad_maxima.setter
    def capacidad_maxima(self, valor: int) -> None:
        # Valida la nueva capacidad antes de asignarla
        val = int(valor)
        if val <= 0:
            raise ParametroServicioInvalidoException("La capacidad máxima debe ser mayor a cero.", "capacidad_maxima")
        self._capacidad_maxima = val

    @property
    def tipo_sala(self) -> str:
        return self._tipo_sala

    @property
    def incluye_proyector(self) -> bool:
        return self._incluye_proyector

    def validar_aforo(self, asistentes_esperados: int) -> None:
        """Verifica que el aforo no supere la capacidad permitida."""
        # Convierte el número de asistentes
        asistentes = int(asistentes_esperados)
        # Los asistentes deben ser más de cero
        if asistentes <= 0:
            raise ParametroServicioInvalidoException("El número de asistentes debe ser mayor a cero.", "asistentes")
        # Si superan la capacidad, lanza CapacidadExcedidaException
        if asistentes > self._capacidad_maxima:
            raise CapacidadExcedidaException(self._capacidad_maxima, asistentes)

    def calcular_costo(self, cantidad_unidades: float, **kwargs) -> float:
        """Sobrescribe el cálculo: Tarifa por horas + adicionales de proyector/catering."""
        # Valida que las horas sean positivas y finitas
        horas = float(cantidad_unidades)
        if not math.isfinite(horas) or horas <= 0:
            raise ParametroServicioInvalidoException("La duración en horas debe ser positiva y finita.", "horas")

        # Costo base: tarifa por hora multiplicada por las horas
        costo = self._tarifa_base * horas
        # Cargo adicional si se pide proyector 4K
        if kwargs.get("proyector_4k", False):
            costo += 25000.0 * horas
        # Cargo adicional por catering según asistentes
        asistentes = kwargs.get("asistentes", 0)
        if asistentes > 0 and kwargs.get("catering", False):
            costo += asistentes * 15000.0

        return round(costo, 2)

    def describir_servicio(self) -> str:
        # Sobrescribe describir_servicio con los datos de la sala
        proyector = "Sí" if self._incluye_proyector else "No"
        return (
            f"SALA: {self._nombre} ({self._tipo_sala}) | Capacidad: {self._capacidad_maxima} personas | "
            f"Proyector: {proyector} | Tarifa/Hora: ${self._tarifa_base:,.2f}"
        )


# ---------------------------------------------------------------------------
# Servicio Especializado 2: Alquiler de Equipos Tecnológicos
# ---------------------------------------------------------------------------

# Subclase 2: hereda de Servicio
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
        # Llama al constructor de la clase padre
        super().__init__(codigo, nombre, tarifa_dia, disponible)
        # El depósito debe ser finito y no negativo
        deposito_val = float(deposito_garantia)
        if not math.isfinite(deposito_val) or deposito_val < 0:
            raise ParametroServicioInvalidoException("El depósito de garantía debe ser finito y no negativo.", "deposito_garantia")
        self._categoria = str(categoria).strip()
        self._deposito_garantia = deposito_val

    @property
    def categoria(self) -> str:
        return self._categoria

    @property
    def deposito_garantia(self) -> float:
        return self._deposito_garantia

    @deposito_garantia.setter
    def deposito_garantia(self, valor: float) -> None:
        # Valida el nuevo depósito antes de asignarlo
        dep = float(valor)
        if not math.isfinite(dep) or dep < 0:
            raise ParametroServicioInvalidoException("El depósito no puede ser negativo ni infinito.", "deposito_garantia")
        self._deposito_garantia = dep

    def calcular_costo(self, cantidad_unidades: float, **kwargs) -> float:
        """Sobrescribe el cálculo: Tarifa por días + póliza de seguro opcional."""
        # Valida que los días sean positivos y finitos
        dias = float(cantidad_unidades)
        if not math.isfinite(dias) or dias <= 0:
            raise ParametroServicioInvalidoException("Los días de alquiler deben ser mayores a cero y finitos.", "dias")
        # No se permite alquilar más de 30 días
        if dias > 30:
            raise ParametroServicioInvalidoException("El alquiler no puede superar 30 días continuos.", "dias")

        # Costo base: tarifa por día multiplicada por los días
        costo = self._tarifa_base * dias
        # Agrega el 10% de seguro si se solicita
        if kwargs.get("seguro_riesgo", True):
            costo += (self._tarifa_base * 0.10) * dias

        return round(costo, 2)

    def describir_servicio(self) -> str:
        # Sobrescribe describir_servicio con los datos del equipo
        return (
            f"EQUIPO: {self._nombre} | Categoría: {self._categoria} | Depósito: ${self._deposito_garantia:,.2f} | "
            f"Tarifa/Día: ${self._tarifa_base:,.2f}"
        )


# ---------------------------------------------------------------------------
# Servicio Especializado 3: Asesoría Especializada
# ---------------------------------------------------------------------------

# Subclase 3: hereda de Servicio
class AsesoriaEspecializada(Servicio):
    """Servicio de consultoría y asesoría técnica profesional."""

    # Multiplicador de tarifa según el nivel del consultor
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
        # Llama al constructor de la clase padre
        super().__init__(codigo, nombre, tarifa_hora_base, disponible)
        # Valida que el nivel del consultor exista
        nivel_normalizado = str(nivel_consultor).strip().upper()
        if nivel_normalizado not in self.FACTORES_NIVEL:
            raise ParametroServicioInvalidoException(
                f"Nivel de consultor inválido '{nivel_consultor}'. Opciones válidas: {list(self.FACTORES_NIVEL.keys())}",
                "nivel_consultor",
            )
        # Guarda los atributos propios de la asesoría
        self._area_tematica = str(area_tematica).strip()
        self._nivel_consultor = nivel_normalizado

    @property
    def area_tematica(self) -> str:
        return self._area_tematica

    @property
    def nivel_consultor(self) -> str:
        return self._nivel_consultor

    def calcular_costo(self, cantidad_unidades: float, **kwargs) -> float:
        """Sobrescribe el cálculo: Horas * Tarifa Base * Multiplicador por seniority."""
        # Valida que las horas sean positivas y finitas
        horas = float(cantidad_unidades)
        if not math.isfinite(horas) or horas <= 0:
            raise ParametroServicioInvalidoException("Las horas de asesoría deben ser mayores a cero y finitas.", "horas")
        # No se permiten más de 40 horas
        if horas > 40:
            raise ParametroServicioInvalidoException("Una asesoría no puede programarse por más de 40 horas continuas.", "horas")

        # Costo: tarifa base por multiplicador del nivel por horas
        multiplicador = self.FACTORES_NIVEL[self._nivel_consultor]
        costo = (self._tarifa_base * multiplicador) * horas

        # Cargo adicional si la asesoría es presencial
        if kwargs.get("presencial", False):
            costo += 50000.0

        return round(costo, 2)

    def describir_servicio(self) -> str:
        # Calcula la tarifa efectiva según el nivel
        tarifa_efectiva = self._tarifa_base * self.FACTORES_NIVEL[self._nivel_consultor]
        return (
            f"ASESORÍA: {self._nombre} | Área: {self._area_tematica} | Nivel: {self._nivel_consultor} | "
            f"Tarifa/Hora Efectiva: ${tarifa_efectiva:,.2f}"
        )
