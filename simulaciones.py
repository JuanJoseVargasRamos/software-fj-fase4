"""
Módulo de Simulaciones del Sistema para Software FJ.

Ejecuta una suite modular, rigurosa y exhaustiva de 16 simulaciones oficiales
(válidas e inválidas) estructuradas como un escenario narrativo progresivo.
Aplica el principio de aserción estricta mediante el ayudante `esperar_excepcion`
para garantizar que las validaciones y excepciones de dominio se disparen de verdad
y no pasen en falso positivo (vacío).
"""

# sys se usa para devolver el código de salida del programa
import sys
from typing import Optional, Callable, Type
# Logger para registrar el resultado de cada simulación
from configuracion.logger_config import logger_sistema
# Excepciones personalizadas que se espera capturar en las simulaciones
from excepciones.excepciones_sistema import (
    CalculoInconsistenteException,
    CapacidadExcedidaException,
    ClienteNoEncontradoException,
    EmailInvalidoException,
    EstadoReservaInvalidoException,
    OperacionNoPermitidaException,
    ParametroServicioInvalidoException,
    ReservaNoEncontradaException,
    ServicioNoDisponibleException,
    TelefonoInvalidoException,
)
# Clases de servicios y gestor del sistema
from modelos.servicio import AlquilerEquipo, AsesoriaEspecializada, ReservaSala
from servicios.gestor_sistema import SistemaGestionSoftwareFJ


def separador(titulo: str):
    """Imprime un delimitador visual en consola para cada simulación."""
    print("\n" + "=" * 80)
    print(f" {titulo.upper()}")
    print("=" * 80)


def esperar_excepcion(tipo_excepcion: Type[Exception], accion: Callable[[], None], numero_sim: int) -> Exception:
    """Ejecuta una acción y exige estrictamente que lance la excepción indicada.

    Si no se lanza la excepción esperada o se produce un resultado nominal,
    falla con AssertionError para prevenir falsos positivos en las pruebas.
    """
    # try/except: ejecuta la acción esperando que lance la excepción indicada
    try:
        accion()
    # Si se lanza la excepción esperada, la simulación es exitosa y se registra en el log
    except tipo_excepcion as exc:
        print(f"[OK ESPERADO] {tipo_excepcion.__name__} capturada: {exc}")
        logger_sistema.info(f"Simulacion {numero_sim} controlada con exito: {exc}")
        return exc
    # Si se lanza otra excepción, se encadena en un AssertionError
    except Exception as exc_inesperada:
        raise AssertionError(
            f"Se esperaba {tipo_excepcion.__name__}, pero se lanzó {type(exc_inesperada).__name__}: {exc_inesperada}"
        ) from exc_inesperada

    # Si no se lanzó ninguna excepción, la prueba falla
    raise AssertionError(f"Fallo de prueba: Se esperaba {tipo_excepcion.__name__} y la operación no lanzó ninguna excepción.")


def ejecutar_simulacion(
    numero: int,
    titulo: str,
    funcion: Callable[[SistemaGestionSoftwareFJ], None],
    sistema: SistemaGestionSoftwareFJ,
) -> bool:
    """Ejecuta una simulación aislada protegiendo el flujo principal contra caídas no controladas."""
    # Muestra el título de la simulación
    separador(f"Simulacion {numero}: {titulo}")
    # try/except: un fallo en una simulación no detiene las demás
    try:
        funcion(sistema)
        return True
    # Registra el fallo en el log y continúa
    except Exception as e:
        logger_sistema.critical(f"Simulación {numero} presentó un fallo no controlado: {e!r}")
        print(f"[FALLO INESPERADO EN SIMULACIÓN {numero}]: {e!r}")
        return False


# ---------------------------------------------------------------------------
# Batería Modular de 16 Simulaciones Oficiales
# ---------------------------------------------------------------------------

def sim_01_registro_clientes_valido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 1: Registro nominal de clientes con validación regex y encapsulación."""
    # Caso válido: registra dos clientes correctos
    c1 = sistema.registrar_cliente("1010203040", "Carlos Perez Gomez", "carlos.perez@empresa.com", "3001234567")
    c2 = sistema.registrar_cliente("1098765432", "Maria Lopez Duque", "maria.lopez@startup.co", "3119876543")
    print(f"[OK] Cliente 1 creado: {c1.obtener_resumen()}")
    print(f"[OK] Cliente 2 creado: {c2.obtener_resumen()}")


def sim_02_email_invalido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 2: Rechazo estricto de correo electrónico sin formato válido."""
    # Caso inválido: correo sin arroba
    esperar_excepcion(
        EmailInvalidoException,
        lambda: sistema.registrar_cliente("1020304050", "Juan Valderrama", "juan_sin_arroba.com", "3154567890"),
        2,
    )


def sim_03_telefono_invalido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 3: Rechazo de número telefónico con caracteres alfabéticos."""
    # Caso inválido: teléfono con letras
    esperar_excepcion(
        TelefonoInvalidoException,
        lambda: sistema.registrar_cliente("1030405060", "Laura Sanchez", "laura@gmail.com", "300ABC123"),
        3,
    )


def sim_04_cedula_duplicada(sistema: SistemaGestionSoftwareFJ):
    """Simulación 4: Bloqueo de duplicidad de identificación en colecciones internas."""
    # Caso inválido: cédula repetida
    esperar_excepcion(
        OperacionNoPermitidaException,
        lambda: sistema.registrar_cliente("1010203040", "Carlos Clon Perez", "carlos.clon@correo.com", "3209998877"),
        4,
    )


def sim_05_catalogo_servicios_valido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 5: Alta e integración del catálogo de 4 servicios especializados polimórficos."""
    # Caso válido: crea un servicio de cada tipo y una sala inactiva
    s1 = ReservaSala("SALA-101", "Sala de Juntas Ejecutiva VIP", 80000.0, 12, "Ejecutiva")
    s2 = AlquilerEquipo("EQ-SRV-01", "Servidor Blade Dell PowerEdge", 250000.0, "Servidores", 1000000.0)
    s3 = AsesoriaEspecializada("ASE-IA-03", "Consultoría en Inteligencia Artificial y MLOps", 120000.0, "IA", "SENIOR")
    s4 = ReservaSala("SALA-MANT", "Auditorio Central (Mantenimiento)", 150000.0, 100, "Auditorio", disponible=False)

    # Registra los 4 servicios en el catálogo
    sistema.registrar_servicio(s1)
    sistema.registrar_servicio(s2)
    sistema.registrar_servicio(s3)
    sistema.registrar_servicio(s4)
    print("[OK] Catálogo de 4 servicios polimórficos registrado y disponible en memoria.")


def sim_06_servicio_parametro_invalido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 6: Rechazo en instanciación de servicio con capacidad máxima negativa."""
    # Caso inválido: sala con capacidad negativa
    esperar_excepcion(
        ParametroServicioInvalidoException,
        lambda: sistema.registrar_servicio(ReservaSala("SALA-ERR", "Sala Fantasma", 50000.0, capacidad_maxima=-5)),
        6,
    )


def sim_07_ciclo_completo_reserva_valido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 7: Ciclo nominal completo de reserva (Crear PENDIENTE -> Confirmar -> Procesar)."""
    # Caso válido: crea, confirma y procesa una reserva
    res1 = sistema.crear_reserva("RES-2026-001", "1010203040", "ASE-IA-03", 10.0, descuento=0.10, impuesto=0.19)
    print(f"1. Creada en estado: {res1.estado.value} | Total: ${res1.costo_total:,.2f}")
    res1.confirmar()
    print(f"2. Confirmada: {res1.estado.value}")
    res1.procesar()
    print(f"3. Procesada y facturada: {res1.estado.value}")
    print("[OK] Ciclo de vida nominal completado con éxito.")


def sim_08_servicio_no_disponible(sistema: SistemaGestionSoftwareFJ):
    """Simulación 8: Bloqueo de reserva sobre servicio inactivo o en mantenimiento."""
    # Caso inválido: reservar un servicio inactivo
    esperar_excepcion(
        ServicioNoDisponibleException,
        lambda: sistema.crear_reserva("RES-2026-002", "1098765432", "SALA-MANT", 4.0),
        8,
    )


def sim_09_cliente_inexistente(sistema: SistemaGestionSoftwareFJ):
    """Simulación 9: Rechazo relacional al asociar una reserva a una cédula no registrada."""
    # Caso inválido: cliente que no existe
    esperar_excepcion(
        ClienteNoEncontradoException,
        lambda: sistema.crear_reserva("RES-2026-003", "999999999", "EQ-SRV-01", 5.0),
        9,
    )


def sim_10_aforo_excedido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 10: Validación estricta de aforo máximo en servicio de salas."""
    # Caso inválido: más asistentes que la capacidad de la sala
    sala = sistema.buscar_servicio("SALA-101")
    if isinstance(sala, ReservaSala):
        esperar_excepcion(
            CapacidadExcedidaException,
            lambda: sala.validar_aforo(asistentes_esperados=45),
            10,
        )


def sim_11_cancelacion_ilegal_procesada(sistema: SistemaGestionSoftwareFJ):
    """Simulación 11: Rechazo de cancelación en reserva ya PROCESADA y facturada."""
    # Caso inválido: cancelar una reserva ya procesada
    res1 = sistema.buscar_reserva("RES-2026-001")
    esperar_excepcion(
        EstadoReservaInvalidoException,
        lambda: res1.cancelar(motivo="Reembolso extemporáneo"),
        11,
    )


def sim_12_cancelacion_exitosa_camino_else(sistema: SistemaGestionSoftwareFJ):
    """Simulación 12: Cancelación nominal exitosa evidenciando la mutación en bloque else."""
    # Caso válido: cancelación correcta (bloque else)
    res_canc = sistema.crear_reserva("RES-2026-CANCEL", "1010203040", "EQ-SRV-01", 3.0)
    resultado = res_canc.cancelar(motivo="Cancelación oportuna dentro del plazo legal")
    # Verifica que el estado haya cambiado a CANCELADA
    if not resultado or res_canc.estado.value != "CANCELADA":
        raise AssertionError("Fallo: La reserva no mutó su estado a CANCELADA en el bloque else.")
    print(f"[OK] Camino nominal ejecutado en bloque else: Cancelación={resultado}, Estado={res_canc.estado.value}")
    logger_sistema.info("Simulacion 12 ejecutada con exito: mutacion de estado en else comprobada.")


def sim_13_transiciones_estados_invalidas(sistema: SistemaGestionSoftwareFJ):
    """Simulación 13: Transición ilegal: intentar procesar reserva directamente en estado PENDIENTE."""
    # Caso inválido: procesar una reserva sin confirmarla
    res_pend = sistema.crear_reserva("RES-2026-PEND", "1098765432", "SALA-101", 2.0)
    esperar_excepcion(
        EstadoReservaInvalidoException,
        lambda: res_pend.procesar(),
        13,
    )


def sim_14_encadenamiento_excepciones_calculo(sistema: SistemaGestionSoftwareFJ):
    """Simulación 14: Encadenamiento explícito de excepciones (raise ... from) en cálculo con descuento > 80%."""
    # Caso inválido: descuento del 150%
    equipo = sistema.buscar_servicio("EQ-SRV-01")
    exc = esperar_excepcion(
        CalculoInconsistenteException,
        lambda: equipo.calcular_costo_sobrecargado(unidades=5.0, descuento=1.50),
        14,
    )
    # Verifica que la excepción tenga la causa original (raise ... from)
    if exc.__cause__ is None:
        raise AssertionError("Fallo: La excepción CalculoInconsistenteException no tiene causa raíz encadenada (__cause__).")
    print(f"  Causa raíz original verificada (__cause__): {repr(exc.__cause__)}")


def sim_15_reserva_no_encontrada(sistema: SistemaGestionSoftwareFJ):
    """Simulación 15: Búsqueda fallida de reserva inexistente disparando ReservaNoEncontradaException."""
    # Caso inválido: buscar una reserva que no existe
    esperar_excepcion(
        ReservaNoEncontradaException,
        lambda: sistema.buscar_reserva("RES-INEXISTENTE-999"),
        15,
    )


def sim_16_blindaje_nan_infinitos(sistema: SistemaGestionSoftwareFJ):
    """Simulación 16: Blindaje matemático estricto contra inyección de float('nan') en cálculos."""
    # Caso inválido: valor NaN en el cálculo
    equipo = sistema.buscar_servicio("EQ-SRV-01")
    exc = esperar_excepcion(
        CalculoInconsistenteException,
        lambda: equipo.calcular_costo_sobrecargado(unidades=float("nan"), descuento=0.10),
        16,
    )
    # Verifica que la causa original sea un ValueError
    if exc.__cause__ is None or not isinstance(exc.__cause__, ValueError):
        raise AssertionError("Fallo: El valor NaN no generó ValueError encadenado.")
    print(f"  Causa raíz verificada ante NaN: {repr(exc.__cause__)}")


# ---------------------------------------------------------------------------
# Orquestador Principal de Simulaciones
# ---------------------------------------------------------------------------

def ejecutar_bateria_simulaciones(sistema: Optional[SistemaGestionSoftwareFJ] = None) -> int:
    """Orquesta y ejecuta la suite completa de 16 simulaciones con métricas de control honestas.

    Retorna el número de fallos encontrados (0 si todas fueron controladas con éxito).
    """
    # Si no se recibe un sistema, se crea uno nuevo
    if sistema is None:
        sistema = SistemaGestionSoftwareFJ("Software FJ - Plataforma de Servicios")

    # Registra en el log el inicio de las simulaciones
    separador("Iniciando Bateria de 16 Simulaciones - Software FJ")
    logger_sistema.info("=== INICIO DE LA BATERIA OFICIAL DE 16 SIMULACIONES FASE 4 ===")

    # Lista de las 16 simulaciones: número, título y función
    simulaciones = [
        (1, "Registro exitoso de clientes", sim_01_registro_clientes_valido),
        (2, "Validación de correo electrónico erróneo", sim_02_email_invalido),
        (3, "Validación de teléfono no numérico", sim_03_telefono_invalido),
        (4, "Control de duplicidad de identificación", sim_04_cedula_duplicada),
        (5, "Catálogo de servicios especializados polimórficos", sim_05_catalogo_servicios_valido),
        (6, "Creación de servicio con capacidad negativa", sim_06_servicio_parametro_invalido),
        (7, "Ciclo completo de reserva (Crear -> Confirmar -> Procesar)", sim_07_ciclo_completo_reserva_valido),
        (8, "Reserva de servicio no disponible", sim_08_servicio_no_disponible),
        (9, "Creación de reserva con cliente inexistente", sim_09_cliente_inexistente),
        (10, "Validación de aforo excedido en sala", sim_10_aforo_excedido),
        (11, "Cancelación ilegal de reserva ya procesada", sim_11_cancelacion_ilegal_procesada),
        (12, "Cancelación exitosa evidenciando bloque else", sim_12_cancelacion_exitosa_camino_else),
        (13, "Transición ilegal: procesar sin confirmación previa", sim_13_transiciones_estados_invalidas),
        (14, "Encadenamiento de excepciones (raise ... from)", sim_14_encadenamiento_excepciones_calculo),
        (15, "Búsqueda de reserva inexistente (ReservaNoEncontradaException)", sim_15_reserva_no_encontrada),
        (16, "Blindaje matemático contra valores NaN/Infinitos", sim_16_blindaje_nan_infinitos),
    ]

    # Contadores de simulaciones ejecutadas y controladas
    total_ejecutadas = len(simulaciones)
    total_controladas = 0

    # Ejecuta cada simulación y cuenta las exitosas
    for num, tit, fn in simulaciones:
        exito = ejecutar_simulacion(num, tit, fn, sistema)
        if exito:
            total_controladas += 1

    # Muestra el reporte final del sistema
    separador("Reporte de Cierre del Sistema - Software FJ")
    rep = sistema.generar_reporte_estado()
    print(f"Empresa: {rep['empresa']}")
    print(f"Total Clientes Activos: {rep['total_clientes']}")
    print(f"Total Servicios en Catálogo: {rep['total_servicios']}")
    print(f"Total Reservas Gestionadas: {rep['total_reservas']}")
    print(f"Distribución de Estados: {rep['conteo_por_estado']}")
    print(f"Ingresos Totales Facturados: ${rep['ingresos_procesados']:,.2f}")
    print("-" * 80)
    print(f"MÉTRICA DE CONTROL: {total_controladas} de {total_ejecutadas} simulaciones controladas exitosamente.")

    # Calcula cuántas simulaciones fallaron
    fallos = total_ejecutadas - total_controladas
    if fallos == 0:
        print(">>> Todas las simulaciones fueron controladas exitosamente (100% de efectividad). <<<")
        print(">>> La aplicación NUNCA se detuvo ni crasheó ante ningún error. <<<")
    else:
        print(f">>> ATENCIÓN: {fallos} simulación(es) fallaron o no lanzaron la excepción requerida. <<<")

    # Registra en el log el resultado final
    logger_sistema.info(
        f"=== FIN DE LA BATERIA: {total_controladas}/{total_ejecutadas} simulaciones controladas exitosamente ==="
    )
    return fallos


# Punto de entrada: ejecuta las simulaciones si se corre este archivo
if __name__ == "__main__":
    errores = ejecutar_bateria_simulaciones()
    sys.exit(0 if errores == 0 else 1)
