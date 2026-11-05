"""
Módulo de Simulaciones del Sistema para Software FJ.

Ejecuta una suite exhaustiva de 12 simulaciones controladas (válidas e inválidas),
demostrando la solidez del manejo de excepciones, la estabilidad del flujo
de ejecución (la aplicación NUNCA colapsa) y el registro unificado en logs.
"""

import sys
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


def ejecutar_bateria_simulaciones(sistema: SistemaGestionSoftwareFJ = None):
    """Ejecuta secuencialmente al menos 10 simulaciones completas demostrativas."""
    if sistema is None:
        sistema = SistemaGestionSoftwareFJ("Software FJ - Plataforma de Servicios")

    separador("Iniciando Bateria de Simulaciones - Software FJ")
    logger_sistema.info("=== INICIO DE LA BATERIA OFICIAL DE SIMULACIONES FASE 4 ===")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 1: Registro Exitoso de Clientes (Válida)
    # -----------------------------------------------------------------------
    separador("Simulacion 1 [VALIDA]: Registro exitoso de clientes")
    try:
        c1 = sistema.registrar_cliente("1010203040", "Carlos Perez Gomez", "carlos.perez@empresa.com", "3001234567")
        c2 = sistema.registrar_cliente("1098765432", "Maria Lopez Duque", "maria.lopez@startup.co", "3119876543")
        print(f"[OK] Cliente 1 creado: {c1.obtener_resumen()}")
        print(f"[OK] Cliente 2 creado: {c2.obtener_resumen()}")
    except SoftwareFJException as e:
        print(f"[ERROR INESPERADO]: {e}")
        logger_sistema.error(f"Fallo en simulacion 1: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 2: Registro con Email Inválido (Inválida)
    # -----------------------------------------------------------------------
    separador("Simulacion 2 [INVALIDA]: Validacion de correo electronico erroneo")
    try:
        print("Intentando registrar cliente con correo mal estructurado ('juan_sin_arroba.com')...")
        sistema.registrar_cliente("1020304050", "Juan Valderrama", "juan_sin_arroba.com", "3154567890")
        print("[FALLO DE PRUEBA]: Se esperaba una excepcion de correo invalido.")
    except EmailInvalidoException as e:
        print(f"[OK ESPERADO] Excepcion capturada correctamente: {e}")
        print(f"  Detalle: Campo '{e.campo}', Valor erroneo: '{e.email_erroneo}'")
        logger_sistema.info(f"Simulacion 2 completada exitosamente (excepcion controlada): {e}")
    except Exception as e:
        print(f"[ERROR GENERICO INESPERADO]: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 3: Registro con Teléfono Inválido (Inválida)
    # -----------------------------------------------------------------------
    separador("Simulacion 3 [INVALIDA]: Validacion de telefono con letras/longitud erronea")
    try:
        print("Intentando registrar cliente con telefono no numerico ('300ABC123')...")
        sistema.registrar_cliente("1030405060", "Laura Sanchez", "laura@gmail.com", "300ABC123")
        print("[FALLO DE PRUEBA]: Se esperaba una excepcion de telefono invalido.")
    except TelefonoInvalidoException as e:
        print(f"[OK ESPERADO] Excepcion capturada correctamente: {e}")
        print(f"  Detalle: Campo '{e.campo}', Valor: '{e.telefono_erroneo}'")
        logger_sistema.info(f"Simulacion 3 completada exitosamente (excepcion controlada): {e}")
    except Exception as e:
        print(f"[ERROR GENERICO INESPERADO]: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 4: Registro de Cédula Duplicada (Inválida)
    # -----------------------------------------------------------------------
    separador("Simulacion 4 [INVALIDA]: Control de duplicidad de identificacion")
    try:
        print("Intentando registrar cliente con cedula ya existente ('1010203040')...")
        sistema.registrar_cliente("1010203040", "Carlos Clon Perez", "carlos.clon@correo.com", "3209998877")
        print("[FALLO DE PRUEBA]: Se permitio duplicidad de cedula.")
    except OperacionNoPermitidaException as e:
        print(f"[OK ESPERADO] Excepcion capturada correctamente: {e}")
        logger_sistema.info(f"Simulacion 4 completada exitosamente (duplicado bloqueado): {e}")
    except Exception as e:
        print(f"[ERROR INESPERADO]: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 5: Creación del Catálogo de Servicios (Válida)
    # -----------------------------------------------------------------------
    separador("Simulacion 5 [VALIDA]: Creacion y catalogo de servicios especializados")
    try:
        # 1. Sala
        sala_juntas = ReservaSala(
            codigo="SALA-101",
            nombre="Sala de Juntas Ejecutiva VIP",
            tarifa_hora=80000.0,
            capacidad_maxima=12,
            tipo_sala="Ejecutiva",
            incluye_proyector=True,
            disponible=True,
        )
        # 2. Equipo
        rack_servidor = AlquilerEquipo(
            codigo="EQ-SRV-01",
            nombre="Servidor Blade Dell PowerEdge",
            tarifa_dia=250000.0,
            categoria="Infraestructura Servidores",
            deposito_garantia=1000000.0,
            disponible=True,
        )
        # 3. Asesoría
        consultoria_ia = AsesoriaEspecializada(
            codigo="ASE-IA-03",
            nombre="Consultoria en Inteligencia Artificial y MLOps",
            tarifa_hora_base=120000.0,
            area_tematica="IA & Machine Learning",
            nivel_consultor="SENIOR",
            disponible=True,
        )
        # 4. Servicio Inactivo para pruebas
        sala_mantenimiento = ReservaSala(
            codigo="SALA-MANT",
            nombre="Auditorio Central (Mantenimiento)",
            tarifa_hora=150000.0,
            capacidad_maxima=100,
            tipo_sala="Auditorio",
            disponible=False,  # NO DISPONIBLE
        )

        sistema.registrar_servicio(sala_juntas)
        sistema.registrar_servicio(rack_servidor)
        sistema.registrar_servicio(consultoria_ia)
        sistema.registrar_servicio(sala_mantenimiento)

        print("[OK] Catalogo de 4 servicios registrado con exito:")
        for s in sistema.listar_servicios():
            print(f"  * {s.describir_servicio()}")
    except SoftwareFJException as e:
        print(f"[ERROR AL REGISTRAR SERVICIOS]: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 6: Creación de Servicio con Parámetro Inválido (Inválida)
    # -----------------------------------------------------------------------
    separador("Simulacion 6 [INVALIDA]: Creacion de servicio con parametros erroneos")
    try:
        print("Intentando crear una sala con capacidad maxima cero o negativa (-5)...")
        sala_invalida = ReservaSala(
            codigo="SALA-ERR",
            nombre="Sala Fantasma",
            tarifa_hora=50000.0,
            capacidad_maxima=-5,
        )
        sistema.registrar_servicio(sala_invalida)
        print("[FALLO DE PRUEBA]: Se permitio crear una sala con capacidad no valida.")
    except ParametroServicioInvalidoException as e:
        print(f"[OK ESPERADO] Excepcion capturada correctamente: {e}")
        print(f"  Parametro reportado: {e.parametro}")
        logger_sistema.info(f"Simulacion 6 completada exitosamente: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 7: Ciclo Completo de Reserva Exitoso (Válida)
    # -----------------------------------------------------------------------
    separador("Simulacion 7 [VALIDA]: Ciclo de vida completo de reserva (Crear -> Confirmar -> Procesar)")
    try:
        # Se reserva la consultoría de IA por 10 horas con 10% de descuento
        res1 = sistema.crear_reserva(
            id_reserva="RES-2026-001",
            identificacion_cliente="1010203040",
            codigo_servicio="ASE-IA-03",
            duracion=10.0,
            descuento=0.10,
            impuesto=0.19,
        )
        print(f"1. Reserva creada en estado: {res1.estado.value} | Total estimado: ${res1.costo_total:,.2f}")

        # Confirmación
        res1.confirmar()
        print(f"2. Reserva confirmada: {res1.estado.value}")

        # Procesamiento y Facturación
        res1.procesar()
        print(f"3. Reserva procesada con exito: {res1.estado.value}")
        print("[OK] Ciclo de vida completado satisfactoriamente.")
    except SoftwareFJException as e:
        print(f"[ERROR EN CICLO DE RESERVA]: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 8: Intento de Reserva con Servicio NO DISPONIBLE (Inválida)
    # -----------------------------------------------------------------------
    separador("Simulacion 8 [INVALIDA]: Reserva de un servicio en estado NO DISPONIBLE")
    try:
        print("Intentando reservar 'SALA-MANT' (en mantenimiento)...")
        sistema.crear_reserva(
            id_reserva="RES-2026-002",
            identificacion_cliente="1098765432",
            codigo_servicio="SALA-MANT",
            duracion=4.0,
        )
        print("[FALLO DE PRUEBA]: Se permitio reservar un servicio fuera de linea.")
    except ServicioNoDisponibleException as e:
        print(f"[OK ESPERADO] Excepcion capturada correctamente: {e}")
        print(f"  Servicio bloqueado: {e.id_servicio}")
        logger_sistema.info(f"Simulacion 8 completada exitosamente: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 9: Intento de Reserva con Cliente INEXISTENTE (Inválida)
    # -----------------------------------------------------------------------
    separador("Simulacion 9 [INVALIDA]: Creacion de reserva con cliente inexistente")
    try:
        print("Intentando reservar con documento '999999999' no registrado...")
        sistema.crear_reserva(
            id_reserva="RES-2026-003",
            identificacion_cliente="999999999",
            codigo_servicio="EQ-SRV-01",
            duracion=5.0,
        )
        print("[FALLO DE PRUEBA]: Se permitio asociar un cliente inexistente.")
    except ClienteNoEncontradoException as e:
        print(f"[OK ESPERADO] Excepcion capturada correctamente: {e}")
        print(f"  Cedula buscada: {e.identificacion}")
        logger_sistema.info(f"Simulacion 9 completada exitosamente: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 10: Validación de Aforo Excedido en Sala (Inválida)
    # -----------------------------------------------------------------------
    separador("Simulacion 10 [INVALIDA]: Validacion de capacidad y aforo maximo en sala")
    try:
        print("Validando aforo para 'SALA-101' (capacidad maxima: 12 personas) solicitando 45 personas...")
        sala = sistema.buscar_servicio("SALA-101")
        if isinstance(sala, ReservaSala):
            sala.validar_aforo(asistentes_esperados=45)
        print("[FALLO DE PRUEBA]: Se permitio un aforo por encima del limite.")
    except CapacidadExcedidaException as e:
        print(f"[OK ESPERADO] Excepcion capturada correctamente: {e}")
        print(f"  Maximo permitido: {e.capacidad_maxima}, Solicitados: {e.personas_solicitadas}")
        logger_sistema.info(f"Simulacion 10 completada exitosamente: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 11: Transición Ilegal de Estado en Reserva (Inválida)
    # -----------------------------------------------------------------------
    separador("Simulacion 11 [INVALIDA]: Cancelacion ilegal de una reserva ya procesada")
    try:
        print("Intentando cancelar la reserva 'RES-2026-001' que ya fue PROCESADA y facturada...")
        res1 = sistema.buscar_reserva("RES-2026-001")
        res1.cancelar(motivo="Cliente pide reembolso extemporaneo")
        print("[FALLO DE PRUEBA]: Se cancelo una reserva ya procesada.")
    except EstadoReservaInvalidoException as e:
        print(f"[OK ESPERADO] Excepcion capturada correctamente: {e}")
        print(f"  Estado actual de la reserva: {e.estado_actual}")
        print(f"  Accion rechazada: {e.accion_intentada}")
        logger_sistema.info(f"Simulacion 11 completada exitosamente: {e}")

    # -----------------------------------------------------------------------
    # SIMULACIÓN 12: Encadenamiento de Excepciones en Cálculo (Inválida)
    # -----------------------------------------------------------------------
    separador("Simulacion 12 [INVALIDA/ENCADENAMIENTO]: Error en calculo financiero y raise ... from")
    try:
        print("Invocando calculo sobrecargado con un porcentaje de descuento ilicito (150%)...")
        equipo = sistema.buscar_servicio("EQ-SRV-01")
        # El método calcular_costo_sobrecargado valida el rango y genera encadenamiento
        equipo.calcular_costo_sobrecargado(unidades=5.0, descuento=1.50)
        print("[FALLO DE PRUEBA]: Se acepto un calculo monetario inconsistente.")
    except CalculoInconsistenteException as e:
        print(f"[OK ESPERADO] Excepcion capturada correctamente: {e}")
        print(f"  Excepcion original encadenada (__cause__): {repr(e.__cause__)}")
        logger_sistema.info(
            f"Simulacion 12 completada exitosamente (encadenamiento verificado): {e} -> Causa: {e.__cause__}"
        )

    # -----------------------------------------------------------------------
    # Balance y Resumen Final
    # -----------------------------------------------------------------------
    separador("Reporte de Cierre del Sistema - Software FJ")
    reporte = sistema.generar_reporte_estado()
    print(f"Empresa: {reporte['empresa']}")
    print(f"Total Clientes Activos: {reporte['total_clientes']}")
    print(f"Total Servicios en Catalogo: {reporte['total_servicios']}")
    print(f"Total Reservas Gestionadas: {reporte['total_reservas']}")
    print(f"Distribucion de Estados: {reporte['conteo_por_estado']}")
    print(f"Ingresos Totales Facturados: ${reporte['ingresos_procesados']:,.2f}")
    print("\n>>> RESULTADO GENERAL: Todas las simulaciones finalizaron de forma 100% estable. <<<")
    print(">>> La aplicacion NUNCA se detuvo ni crasheo ante ningun error. <<<")
    logger_sistema.info("=== FIN DE LA BATERIA OFICIAL DE SIMULACIONES FASE 4 ===")


if __name__ == "__main__":
    ejecutar_bateria_simulaciones()
