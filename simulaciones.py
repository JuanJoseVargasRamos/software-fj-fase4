"""
Módulo de Simulaciones del Sistema para Software FJ.

Ejecuta una suite modular y exhaustiva de 14 simulaciones controladas (válidas e inválidas),
demostrando la solidez del manejo de excepciones, la estabilidad del flujo
de ejecución (la aplicación NUNCA colapsa gracias a una arquitectura de aislamiento),
la ejecución de caminos nominales y anómalos, y el registro unificado en logs.
"""

from typing import Optional, Callable
from configuracion.logger_config import logger_sistema
from excepciones.excepciones_sistema import (
    CalculoInconsistenteException,
    CapacidadExcedidaException,
    ClienteNoEncontradoException,
    DatosInvalidosException,
    EmailInvalidoException,
    EstadoReservaInvalidoException,
    OperacionNoPermitidaException,
    ParametroServicioInvalidoException,
    ReservaException,
    ReservaInvalidaException,
    ServicioException,
    ServicioNoDisponibleException,
    SoftwareFJException,
    TelefonoInvalidoException,
)
from modelos.cliente import Cliente
from modelos.reserva import Reserva, EstadoReserva
from modelos.servicio import AlquilerEquipo, AsesoriaEspecializada, ReservaSala
from servicios.gestor_sistema import SistemaGestionSoftwareFJ


def separador(titulo: str):
    print("\n" + "=" * 80)
    print(f" {titulo.upper()}")
    print("=" * 80)


def ejecutar_simulacion(
    numero: int,
    titulo: str,
    funcion: Callable[[SistemaGestionSoftwareFJ], None],
    sistema: SistemaGestionSoftwareFJ,
) -> bool:
    """Ejecuta una simulación de forma aislada protegiendo el hilo principal.

    Garantiza que ningún fallo imprevisto detenga el flujo general de la aplicación.
    """
    separador(f"Simulacion {numero}: {titulo}")
    try:
        funcion(sistema)
        return True
    except Exception as e:
        logger_sistema.critical(f"Simulación {numero} presentó un fallo imprevisto no capturado: {e!r}")
        print(f"[FALLO INESPERADO EN SIMULACIÓN {numero}]: {e!r}")
        return False


# ---------------------------------------------------------------------------
# Definición de Funciones de Simulación Modulares e Independientes
# ---------------------------------------------------------------------------

def sim_01_registro_clientes_valido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 1 [VÁLIDA]: Registro exitoso de clientes con datos nominales."""
    c1 = sistema.registrar_cliente("1010203040", "Carlos Perez Gomez", "carlos.perez@empresa.com", "3001234567")
    c2 = sistema.registrar_cliente("1098765432", "Maria Lopez Duque", "maria.lopez@startup.co", "3119876543")
    print(f"[OK] Cliente 1 creado: {c1.obtener_resumen()}")
    print(f"[OK] Cliente 2 creado: {c2.obtener_resumen()}")


def sim_02_email_invalido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 2 [INVÁLIDA]: Validación de correo electrónico sin formato adecuado."""
    try:
        print("Intentando registrar cliente con correo mal estructurado ('juan_sin_arroba.com')...")
        sistema.registrar_cliente("1020304050", "Juan Valderrama", "juan_sin_arroba.com", "3154567890")
        print("[FALLO DE PRUEBA]: Se esperaba EmailInvalidoException.")
    except EmailInvalidoException as e:
        print(f"[OK ESPERADO] Excepción capturada correctamente: {e}")
        print(f"  Detalle: Campo '{e.campo}', Valor erróneo: '{e.email_erroneo}'")
        logger_sistema.info(f"Simulación 2 completada exitosamente (excepción controlada): {e}")


def sim_03_telefono_invalido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 3 [INVÁLIDA]: Validación de teléfono con caracteres alfabéticos."""
    try:
        print("Intentando registrar cliente con teléfono no numérico ('300ABC123')...")
        sistema.registrar_cliente("1030405060", "Laura Sanchez", "laura@gmail.com", "300ABC123")
        print("[FALLO DE PRUEBA]: Se esperaba TelefonoInvalidoException.")
    except TelefonoInvalidoException as e:
        print(f"[OK ESPERADO] Excepción capturada correctamente: {e}")
        print(f"  Detalle: Campo '{e.campo}', Valor: '{e.telefono_erroneo}'")
        logger_sistema.info(f"Simulación 3 completada exitosamente (excepción controlada): {e}")


def sim_04_cedula_duplicada(sistema: SistemaGestionSoftwareFJ):
    """Simulación 4 [INVÁLIDA]: Control de unicidad de identificación."""
    try:
        print("Intentando registrar cliente con cédula ya existente ('1010203040')...")
        sistema.registrar_cliente("1010203040", "Carlos Clon Perez", "carlos.clon@correo.com", "3209998877")
        print("[FALLO DE PRUEBA]: Se permitió duplicidad de cédula.")
    except OperacionNoPermitidaException as e:
        print(f"[OK ESPERADO] Excepción capturada correctamente: {e}")
        logger_sistema.info(f"Simulación 4 completada exitosamente (duplicado bloqueado): {e}")


def sim_05_catalogo_servicios_valido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 5 [VÁLIDA]: Creación del catálogo con las 3 especialidades polimórficas."""
    s1 = ReservaSala("SALA-101", "Sala de Juntas Ejecutiva VIP", 80000.0, 12, "Ejecutiva")
    s2 = AlquilerEquipo("EQ-SRV-01", "Servidor Blade Dell PowerEdge", 250000.0, "Servidores", 1000000.0)
    s3 = AsesoriaEspecializada("ASE-IA-03", "Consultoría en Inteligencia Artificial y MLOps", 120000.0, "IA", "SENIOR")
    s4 = ReservaSala("SALA-MANT", "Auditorio Central (Mantenimiento)", 150000.0, 100, "Auditorio", disponible=False)

    for serv in (s1, s2, s3, s4):
        try:
            sistema.registrar_servicio(serv)
        except OperacionNoPermitidaException:
            pass  # Si ya existía por ejecución previa
    print("[OK] Catálogo de 4 servicios polimórficos registrado y disponible.")


def sim_06_servicio_parametro_invalido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 6 [INVÁLIDA]: Creación de servicio con capacidad negativa."""
    try:
        print("Intentando crear una sala con capacidad máxima negativa (-5)...")
        sala_invalida = ReservaSala("SALA-ERR", "Sala Fantasma", 50000.0, capacidad_maxima=-5)
        sistema.registrar_servicio(sala_invalida)
        print("[FALLO DE PRUEBA]: Se permitió crear sala con parámetro inválido.")
    except ParametroServicioInvalidoException as e:
        print(f"[OK ESPERADO] Excepción capturada correctamente: {e}")
        print(f"  Parámetro reportado: {e.parametro}")
        logger_sistema.info(f"Simulación 6 completada exitosamente: {e}")


def sim_07_ciclo_completo_reserva_valido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 7 [VÁLIDA]: Ciclo de vida completo (Creación -> Confirmación -> Procesamiento)."""
    res1 = sistema.crear_reserva(
        id_reserva="RES-2026-001",
        identificacion_cliente="1010203040",
        codigo_servicio="ASE-IA-03",
        duracion=10.0,
        descuento=0.10,
        impuesto=0.19,
    )
    print(f"1. Reserva creada en estado: {res1.estado.value} | Total estimado: ${res1.costo_total:,.2f}")
    res1.confirmar()
    print(f"2. Reserva confirmada: {res1.estado.value}")
    res1.procesar()
    print(f"3. Reserva procesada con éxito: {res1.estado.value}")
    print("[OK] Ciclo de vida completado satisfactoriamente.")


def sim_08_servicio_no_disponible(sistema: SistemaGestionSoftwareFJ):
    """Simulación 8 [INVÁLIDA]: Intento de reserva de un servicio inactivo o en mantenimiento."""
    try:
        print("Intentando reservar 'SALA-MANT' (en mantenimiento)...")
        sistema.crear_reserva(
            id_reserva="RES-2026-002",
            identificacion_cliente="1098765432",
            codigo_servicio="SALA-MANT",
            duracion=4.0,
        )
        print("[FALLO DE PRUEBA]: Se permitió reservar servicio inactivo.")
    except ServicioNoDisponibleException as e:
        print(f"[OK ESPERADO] Excepción capturada correctamente: {e}")
        print(f"  Servicio bloqueado: {e.id_servicio}")
        logger_sistema.info(f"Simulación 8 completada exitosamente: {e}")


def sim_09_cliente_inexistente(sistema: SistemaGestionSoftwareFJ):
    """Simulación 9 [INVÁLIDA]: Reserva vinculada a cédula no registrada."""
    try:
        print("Intentando reservar con documento '999999999' no registrado...")
        sistema.crear_reserva(
            id_reserva="RES-2026-003",
            identificacion_cliente="999999999",
            codigo_servicio="EQ-SRV-01",
            duracion=5.0,
        )
        print("[FALLO DE PRUEBA]: Se permitió asociar cliente inexistente.")
    except ClienteNoEncontradoException as e:
        print(f"[OK ESPERADO] Excepción capturada correctamente: {e}")
        print(f"  Cédula buscada: {e.identificacion}")
        logger_sistema.info(f"Simulación 9 completada exitosamente: {e}")


def sim_10_aforo_excedido(sistema: SistemaGestionSoftwareFJ):
    """Simulación 10 [INVÁLIDA]: Validación de aforo máximo en sala."""
    try:
        print("Validando aforo para 'SALA-101' (máximo 12 personas) solicitando 45 personas...")
        sala = sistema.buscar_servicio("SALA-101")
        if isinstance(sala, ReservaSala):
            sala.validar_aforo(asistentes_esperados=45)
        print("[FALLO DE PRUEBA]: Se permitió aforo excedido.")
    except CapacidadExcedidaException as e:
        print(f"[OK ESPERADO] Excepción capturada correctamente: {e}")
        print(f"  Máximo permitido: {e.capacidad_maxima}, Solicitados: {e.personas_solicitadas}")
        logger_sistema.info(f"Simulación 10 completada exitosamente: {e}")


def sim_11_cancelacion_ilegal_procesada(sistema: SistemaGestionSoftwareFJ):
    """Simulación 11 [INVÁLIDA]: Cancelación rechazada en reserva ya PROCESADA y facturada."""
    try:
        print("Intentando cancelar 'RES-2026-001' que ya fue PROCESADA...")
        res1 = sistema.buscar_reserva("RES-2026-001")
        res1.cancelar(motivo="Reembolso extemporáneo")
        print("[FALLO DE PRUEBA]: Se canceló una reserva ya procesada.")
    except EstadoReservaInvalidoException as e:
        print(f"[OK ESPERADO] Excepción capturada correctamente: {e}")
        print(f"  Estado actual: {e.estado_actual} | Acción rechazada: {e.accion_intentada}")
        logger_sistema.info(f"Simulación 11 completada exitosamente: {e}")


def sim_12_cancelacion_exitosa_camino_else(sistema: SistemaGestionSoftwareFJ):
    """Simulación 12 [VÁLIDA]: Cancelación exitosa evidenciando el bloque 'else' de try/except/else."""
    print("Creando reserva auxiliar 'RES-2026-CANCEL' para demostrar cancelación válida...")
    res_canc = sistema.crear_reserva(
        id_reserva="RES-2026-CANCEL",
        identificacion_cliente="1010203040",
        codigo_servicio="EQ-SRV-01",
        duracion=3.0,
    )
    print(f"Estado inicial de reserva: {res_canc.estado.value}")
    resultado = res_canc.cancelar(motivo="Cliente cancela oportunamente dentro del plazo")
    print(f"[OK] Camino nominal ejecutado en bloque else: Cancelación={resultado}, Estado={res_canc.estado.value}")
    logger_sistema.info(f"Simulación 12 ejecutada con éxito: mutación de estado en else demostrada.")


def sim_13_transiciones_estados_invalidas(sistema: SistemaGestionSoftwareFJ):
    """Simulación 13 [INVÁLIDA]: Intento de procesar reserva sin haberla confirmado previamente."""
    try:
        print("Creando reserva 'RES-2026-PEND' e intentando procesar directamente en estado PENDIENTE...")
        res_pend = sistema.crear_reserva(
            id_reserva="RES-2026-PEND",
            identificacion_cliente="1098765432",
            codigo_servicio="SALA-101",
            duracion=2.0,
        )
        res_pend.procesar()  # Debe fallar porque no está CONFIRMADA
        print("[FALLO DE PRUEBA]: Se procesó reserva sin confirmación previa.")
    except EstadoReservaInvalidoException as e:
        print(f"[OK ESPERADO] Excepción capturada correctamente: {e}")
        logger_sistema.info(f"Simulación 13 completada exitosamente: {e}")


def sim_14_encadenamiento_excepciones_calculo(sistema: SistemaGestionSoftwareFJ):
    """Simulación 14 [INVÁLIDA / ENCADENAMIENTO]: Cálculo con descuento anómalo y raise ... from."""
    try:
        print("Invocando cálculo financiero con descuento fuera de rango (150%)...")
        equipo = sistema.buscar_servicio("EQ-SRV-01")
        equipo.calcular_costo_sobrecargado(unidades=5.0, descuento=1.50)
        print("[FALLO DE PRUEBA]: Se aceptó un cálculo inconsistente.")
    except CalculoInconsistenteException as e:
        print(f"[OK ESPERADO] Excepción de dominio capturada: {e}")
        print(f"  Causa raíz encadenada (__cause__): {repr(e.__cause__)}")
        logger_sistema.info(f"Simulación 14 completada exitosamente con encadenamiento: {e} -> Causa: {e.__cause__}")


# ---------------------------------------------------------------------------
# Orquestador Principal de Simulaciones
# ---------------------------------------------------------------------------

def ejecutar_bateria_simulaciones(sistema: Optional[SistemaGestionSoftwareFJ] = None):
    """Orquesta y ejecuta la suite completa de 14 simulaciones con trazabilidad y métricas reales."""
    if sistema is None:
        sistema = SistemaGestionSoftwareFJ("Software FJ - Plataforma de Servicios")

    separador("Iniciando Bateria de 14 Simulaciones - Software FJ")
    logger_sistema.info("=== INICIO DE LA BATERIA OFICIAL DE 14 SIMULACIONES FASE 4 ===")

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
    ]

    total_ejecutadas = 0
    total_controladas = 0

    for num, tit, fn in simulaciones:
        exito = ejecutar_simulacion(num, tit, fn, sistema)
        total_ejecutadas += 1
        if exito:
            total_controladas += 1

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
    print(">>> La aplicación NUNCA se detuvo ni crasheó ante ningún error. <<<")
    logger_sistema.info(
        f"=== FIN DE LA BATERIA: {total_controladas}/{total_ejecutadas} simulaciones controladas exitosamente ==="
    )


if __name__ == "__main__":
    ejecutar_bateria_simulaciones()
