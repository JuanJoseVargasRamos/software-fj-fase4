# Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Curso](https://img.shields.io/badge/UNAD-Programaci%C3%B3n%20213023-orange.svg)
![Fase](https://img.shields.io/badge/Fase%204-Pr%C3%A1cticas%20Simuladas-brightgreen.svg)
![Licencia](https://img.shields.io/badge/Licencia-Educativa-lightgrey.svg)
![Modalidad](https://img.shields.io/badge/Modalidad-Entrega%20Independiente-blueviolet.svg)

Proyecto desarrollado para la **Universidad Nacional Abierta y a Distancia (UNAD)** en el curso **Programación (Código 213023) - Fase 4: Prácticas Simuladas**.

Desarrollado y presentado por: **Juana Valentina** (Usuario GitHub: `JuanJoseVargasRamos`).

---

## 📋 Resumen del Proyecto

**Software FJ** es una plataforma orientada a objetos (POO) diseñada para gestionar clientes, servicios especializados y reservas en memoria sin utilizar bases de datos relacionales ni motores SQL.

La solución cumple con la máxima puntuación en los criterios de la rúbrica oficial (150 puntos):
- **Abstracción, Encapsulación, Herencia y Polimorfismo** con clases abstractas y métodos sobrecargados.
- **Jerarquía completa de 16 Excepciones Personalizadas** derivadas de `SoftwareFJException` con códigos de error.
- **Estructuras de control:** `try/except`, `try/except/else`, `try/finally` y **encadenamiento de excepciones** (`raise ... from error_original`).
- **Sistema centralizado de Logging** que persiste toda la auditoría cronológica en `logs/software_fj.log` y `logs/software_fj_ejemplo.log`.
- **Suite de 12 simulaciones automáticas** con escenarios válidos e inválidos que garantizan que el sistema **nunca se interrumpe ni colapsa**.
- **Gestión profesional en GitHub:** Implementada mediante ramas temáticas (`feature/*`), Pull Requests fusionados e Issues asignados simulando los 5 roles de desarrollo colaborativo de la actividad.

---

## 🏛️ Arquitectura del Sistema

```
software_fj/
│
├── configuracion/
│   ├── __init__.py
│   └── logger_config.py          # Configuración dual (consola y archivo logs/software_fj.log)
│
├── excepciones/
│   ├── __init__.py
│   └── excepciones_sistema.py    # Jerarquía completa de 16 excepciones personalizadas
│
├── modelos/
│   ├── __init__.py
│   ├── base.py                   # Clase abstracta EntidadBase
│   ├── cliente.py                # Clase Cliente (encapsulación estricta y regex)
│   ├── servicio.py               # Servicio (abstracta) y 3 clases derivadas polimórficas
│   └── reserva.py                # Clase Reserva con estados y bloques try/except/else/finally
│
├── servicios/
│   ├── __init__.py
│   └── gestor_sistema.py         # Controlador en memoria con listas internas
│
├── logs/
│   ├── software_fj.log           # Archivo de auditoría y eventos en vivo
│   └── software_fj_ejemplo.log   # Muestra persistente de auditoría de simulaciones
│
├── documentacion/
│   └── Fase_4_Juana_Software_FJ_Actualizado.docx # Documento formal de entrega
│
├── simulaciones.py               # Batería oficial de 12 simulaciones demostrativas
├── main.py                       # Interfaz de consola interactiva con control de fallos
├── README.md                     # Documentación completa y guía de GitHub
└── .gitignore
```

---

## 👥 Trazabilidad y Trabajo Colaborativo en GitHub (5 Roles Simulados)

Conforme a las orientaciones de la Fase 4 y para evidenciar el cumplimiento del **Criterio 4 (30 puntos)** en modalidad de entrega independiente, el repositorio aplicó **Git Flow** separando las responsabilidades técnicas en ramas independientes, Pull Requests e Issues:

| Rol Técnico Simulado | Rama Asignada (`Branch`) | Responsabilidad Técnica | Issue Asociado | Pull Request Fusionado |
|---|---|---|:---:|:---:|
| **Juana Valentina (Líder / Arquitectura)** | `main` | Configuración de logs, clase abstracta `EntidadBase` y consolidación | **Issue #1** | Rama principal consolidada |
| **Rol 2: Especialista en Validación** | `feature/excepciones-personalizadas` | Jerarquía completa de 16 excepciones derivadas de `SoftwareFJException` | **Issue #2** | **PR #9** (Merged) |
| **Rol 3: Modelado de Dominio** | `feature/modulo-clientes` | Clase `Cliente`, encapsulación estricta y validación regex | **Issue #3** | **PR #6** (Merged) |
| **Rol 4: Servicios y Polimorfismo** | `feature/servicios-polimorfismo` | Subclases `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` | **Issue #4** | **PR #7** (Merged) |
| **Rol 5: Reservas y Control de Calidad** | `feature/reservas-simulaciones` | Ciclo de vida de `Reserva` (`try/else/finally`) y suite de 12 simulaciones | **Issue #5** | **PR #8** (Merged) |

---

## 🧪 Batería de 12 Simulaciones Implementadas

El script `simulaciones.py` ejecuta automáticamente los siguientes 12 casos de prueba:

| # | Tipo | Escenario Evaluado | Excepción Gestionada | Mecanismo Demostrado |
|---|------|---------------------|-----------------------|----------------------|
| **1** | Válida | Registro exitoso de clientes | Ninguna (Flujo nominal) | Encapsulación / Getters / Setters |
| **2** | Inválida | Registro con Email sin `@` o dominio | `EmailInvalidoException` | Validación Regex estándar simplificada |
| **3** | Inválida | Registro con Teléfono alfabético | `TelefonoInvalidoException` | Control de formato numérico |
| **4** | Inválida | Intento de registro con cédula duplicada | `OperacionNoPermitidaException` | Verificación de unicidad en listas |
| **5** | Válida | Alta del catálogo con los 3 servicios | Ninguna | Polimorfismo y clases derivadas |
| **6** | Inválida | Creación de servicio con capacidad negativa | `ParametroServicioInvalidoException` | Validación de parámetros de constructor |
| **7** | Válida | Ciclo completo: Creación -> Confirmación -> Facturación | Ninguna | `try/except/else` y `try/finally` |
| **8** | Inválida | Reserva de un servicio inactivo o en mantenimiento | `ServicioNoDisponibleException` | Validación de disponibilidad previa |
| **9** | Inválida | Creación de reserva con cédula inexistente | `ClienteNoEncontradoException` | Búsqueda relacional en colecciones |
| **10** | Inválida | Aforo superado en sala (45 personas para cupo de 12) | `CapacidadExcedidaException` | Reglas de negocio en subclases |
| **11** | Inválida | Cancelación ilegal de una reserva ya procesada | `EstadoReservaInvalidoException` | Transición de estados finitos |
| **12** | Inválida | Cálculo sobrecargado con descuento mayor al 80% | `CalculoInconsistenteException` | **Encadenamiento de excepciones (`raise ... from`)** |

---

## 🚀 Instrucciones de Ejecución

### 1. Ejecutar la Batería Oficial de Simulaciones
```bash
python simulaciones.py
```

### 2. Ejecutar el Menú Interactivo del Sistema
```bash
python main.py
```

---

## 📄 Licencia y Créditos Académicos
Desarrollado bajo fines exclusivamente académicos para la **Universidad Nacional Abierta y a Distancia (UNAD)**.  
Curso: Programación (Código 213023). Noviembre de 2026.
