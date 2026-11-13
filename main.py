"""
Punto de Entrada Principal (Main) - Software FJ.

Proporciona una interfaz interactiva de consola que permite ejecutar
tanto la batería completa de simulaciones como operaciones individuales
en tiempo real con manejo integral de excepciones y logging continuo.
Totalmente blindado contra EOFError, entradas NaN/Inf y fallos inesperados.
"""

import sys
import math
from pathlib import Path

# Configurar el path del proyecto para importaciones directas
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from configuracion.logger_config import logger_sistema
from excepciones.excepciones_sistema import SoftwareFJException
from modelos.servicio import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from servicios.gestor_sistema import SistemaGestionSoftwareFJ
from simulaciones import ejecutar_bateria_simulaciones


def menu_principal():
    print("""
===================================================================
       SOFTWARE FJ - SISTEMA INTEGRAL DE GESTIÓN (FASE 4)
             UNAD - CURSO DE PROGRAMACIÓN (213023)
===================================================================
1. Ejecutar Batería de 14 Simulaciones Oficiales (Requisito Rúbrica)
2. Registrar un Cliente
3. Consultar y Listar Clientes
4. Registrar un Servicio Especializado
5. Consultar Catálogo de Servicios
6. Crear una Reserva
7. Confirmar una Reserva
8. Procesar / Facturar una Reserva
9. Cancelar una Reserva
10. Ver Reporte de Estado y Métricas
11. Ver últimas líneas del archivo de Logs
0. Salir de la Aplicación
-------------------------------------------------------------------""")


def precargar_datos_demo(sistema: SistemaGestionSoftwareFJ):
    """Carga datos iniciales para facilitar la interacción manual del usuario."""
    try:
        sistema.registrar_cliente("1001001001", "Ana Gomez Restrepo", "ana.gomez@gmail.com", "3104567890")
        sistema.registrar_servicio(
            ReservaSala("SALA-VIP", "Sala VIP Ejecutiva", 95000.0, 15, tipo_sala="Ejecutiva")
        )
        sistema.registrar_servicio(
            AlquilerEquipo("EQ-MAC-01", "MacBook Pro M3 Max", 120000.0, "Portátiles de Alto Rendimiento", 500000.0)
        )
        sistema.registrar_servicio(
            AsesoriaEspecializada("ASE-CYBER", "Consultoría en Ciberseguridad", 150000.0, "Seguridad Ofensiva", "SENIOR")
        )
        logger_sistema.info("Precarga inicial de datos demo realizada con éxito.")
    except Exception as e:
        logger_sistema.warning(f"Aviso durante precarga inicial: {e}")


def main():
    sistema = SistemaGestionSoftwareFJ("Software FJ S.A.S.")
    precargar_datos_demo(sistema)

    while True:
        try:
            menu_principal()
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                print("\n>>> Ejecutando batería oficial de 14 simulaciones aisladas...")
                # Pasar None garantiza un sistema fresco e independiente cada vez que se ejecute la opción
                ejecutar_bateria_simulaciones(None)
                input("\nPresione [ENTER] para regresar al menú principal...")

            elif opcion == "2":
                print("\n--- REGISTRAR NUEVO CLIENTE ---")
                try:
                    id_cliente = input("Cédula o Identificación: ").strip()
                    nombre = input("Nombre completo: ").strip()
                    email = input("Correo electrónico: ").strip()
                    tel = input("Número de teléfono: ").strip()
                    cliente = sistema.registrar_cliente(id_cliente, nombre, email, tel)
                    print(f"[OK] Cliente registrado satisfactoriamente: {cliente}")
                except SoftwareFJException as err:
                    print(f"[AVISO DEL SISTEMA]: {err}")

            elif opcion == "3":
                print("\n--- LISTADO DE CLIENTES REGISTRADOS ---")
                clientes = sistema.listar_clientes()
                if not clientes:
                    print("No hay clientes registrados en el sistema.")
                else:
                    for c in clientes:
                        print(f" • {c.obtener_resumen()}")

            elif opcion == "4":
                print("\n--- REGISTRAR SERVICIO ESPECIALIZADO ---")
                print("1. Reserva de Sala | 2. Alquiler de Equipo | 3. Asesoría Especializada")
                tipo = input("Elija el tipo de servicio (1-3): ").strip()
                codigo = input("Código del servicio (ej. SALA-201): ").strip()
                nombre = input("Nombre descriptivo: ").strip()

                try:
                    if tipo == "1":
                        tarifa = float(input("Tarifa por hora ($): ").strip())
                        capacidad = int(input("Capacidad máxima de personas: ").strip())
                        servicio = ReservaSala(codigo, nombre, tarifa, capacidad)
                    elif tipo == "2":
                        tarifa = float(input("Tarifa por día ($): ").strip())
                        cat = input("Categoría del equipo: ").strip()
                        dep = float(input("Depósito de garantía ($): ").strip())
                        servicio = AlquilerEquipo(codigo, nombre, tarifa, cat, dep)
                    elif tipo == "3":
                        tarifa = float(input("Tarifa base por hora ($): ").strip())
                        area = input("Área temática (ej. Cloud / Datos / IA): ").strip()
                        nivel = input("Nivel (JUNIOR / SENIOR / MASTER): ").strip().upper()
                        servicio = AsesoriaEspecializada(codigo, nombre, tarifa, area, nivel)
                    else:
                        print("[AVISO]: Tipo de servicio no válido. Operación cancelada.")
                        continue

                    sistema.registrar_servicio(servicio)
                    print(f"[OK] Servicio agregado exitosamente: {servicio.describir_servicio()}")
                except ValueError as ve:
                    print(f"[AVISO]: Dato numérico inválido ingresado: {ve}")
                except SoftwareFJException as err:
                    print(f"[AVISO DEL SISTEMA]: {err}")

            elif opcion == "5":
                print("\n--- CATÁLOGO DE SERVICIOS DISPONIBLES ---")
                servicios = sistema.listar_servicios()
                if not servicios:
                    print("No hay servicios en el catálogo.")
                else:
                    for s in servicios:
                        print(f" • {s.describir_servicio()}")

            elif opcion == "6":
                print("\n--- CREAR UNA NUEVA RESERVA ---")
                try:
                    id_res = input("ID o Código para la reserva (ej. RES-100): ").strip()
                    id_cli = input("Cédula del cliente: ").strip()
                    cod_serv = input("Código del servicio: ").strip()
                    dur_str = input("Duración (horas para sala/asesoría, días para equipo): ").strip()
                    desc_str = input("Descuento (ej. 0.10 para 10%, 0 si no aplica): ").strip() or "0"

                    duracion = float(dur_str)
                    descuento = float(desc_str)

                    if not math.isfinite(duracion) or not math.isfinite(descuento):
                        raise ValueError("Los valores no pueden ser NaN o Infinito.")

                    reserva = sistema.crear_reserva(
                        id_reserva=id_res,
                        identificacion_cliente=id_cli,
                        codigo_servicio=cod_serv,
                        duracion=duracion,
                        descuento=descuento,
                    )
                    print(f"[OK] Reserva creada: {reserva}")
                except ValueError as ve:
                    print(f"[AVISO]: La duración o descuento deben ser números finitos válidos: {ve}")
                except SoftwareFJException as err:
                    print(f"[AVISO DEL SISTEMA]: {err}")

            elif opcion == "7":
                print("\n--- CONFIRMAR RESERVA ---")
                id_res = input("ID de la reserva a confirmar: ").strip()
                try:
                    sistema.confirmar_reserva(id_res)
                    print(f"[OK] Reserva {id_res} confirmada exitosamente.")
                except SoftwareFJException as err:
                    print(f"[AVISO DEL SISTEMA]: {err}")

            elif opcion == "8":
                print("\n--- PROCESAR / FACTURAR RESERVA ---")
                id_res = input("ID de la reserva a procesar: ").strip()
                try:
                    sistema.procesar_reserva(id_res)
                    print(f"[OK] Reserva {id_res} procesada y facturada exitosamente.")
                except SoftwareFJException as err:
                    print(f"[AVISO DEL SISTEMA]: {err}")

            elif opcion == "9":
                print("\n--- CANCELAR RESERVA ---")
                id_res = input("ID de la reserva a cancelar: ").strip()
                motivo = input("Motivo de la cancelación: ").strip()
                try:
                    sistema.cancelar_reserva(id_res, motivo)
                    print(f"[OK] Reserva {id_res} cancelada exitosamente.")
                except SoftwareFJException as err:
                    print(f"[AVISO DEL SISTEMA]: {err}")

            elif opcion == "10":
                print("\n--- REPORTE DE ESTADO DEL SISTEMA ---")
                rep = sistema.generar_reporte_estado()
                print(f"Empresa: {rep['empresa']}")
                print(f"Clientes Registrados: {rep['total_clientes']}")
                print(f"Servicios en Catálogo: {rep['total_servicios']}")
                print(f"Reservas Gestionadas: {rep['total_reservas']}")
                print(f"Conteo por Estado: {rep['conteo_por_estado']}")
                print(f"Ingresos Facturados: ${rep['ingresos_procesados']:,.2f}")
                print("\nReservas registradas:")
                for r in sistema.listar_reservas():
                    print(f"  - {r.obtener_resumen()}")

            elif opcion == "11":
                print("\n--- REGISTRO DE AUDITORÍA (LOGS RECIENTES) ---")
                ruta_log = BASE_DIR / "logs" / "software_fj.log"
                if ruta_log.exists():
                    with open(ruta_log, "r", encoding="utf-8") as f:
                        lineas = f.readlines()
                        print(f"Mostrando últimas 15 líneas de {len(lineas)} registradas:")
                        for linea in lineas[-15:]:
                            print(linea.rstrip())
                else:
                    print("No se ha generado archivo de logs aún.")

            elif opcion == "0":
                print("\nSaliendo del sistema Software FJ. ¡Hasta pronto!")
                logger_sistema.info("Sesión finalizada por el usuario desde el menú principal.")
                break
            else:
                print("[AVISO]: Opción inválida. Ingrese un número del 0 al 11.")

        except EOFError:
            # Control de cierre de entrada estándar (evita bucles infinitos en redirecciones o Ctrl+Z/Ctrl+D)
            logger_sistema.info("Entrada estándar cerrada (EOFError detectado); finalizando ejecución limpiamente.")
            print("\n[INFO]: Entrada estándar finalizada. Cerrando Software FJ.")
            break
        except KeyboardInterrupt:
            print("\nOperación interrumpida por el usuario. Regresando al menú.")
        except Exception as e:
            print(f"[ERROR CONTROLADO]: Eventualidad imprevista: {e}")
            logger_sistema.exception(f"Excepción imprevista capturada en el bucle principal: {e}")


if __name__ == "__main__":
    main()
