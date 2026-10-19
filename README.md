# Sistema de Gestión de Cadena de Suministro (SCM)

Proyecto académico — Patrones de Diseño de Software
Unidades Tecnológicas de Santander (UTS)
Docente: Eliecer Montero Ojeda, Ed.D.

## Descripción

Sistema para el seguimiento de productos desde el fabricante hasta el cliente
final, con optimización de rutas y almacenamiento, predicción de demanda
mediante análisis predictivo, e integración con IoT para monitoreo en
tiempo real.

## Objetivo general

Diseñar e implementar un sistema de gestión de cadena de suministro (SCM) basado en una arquitectura hexagonal modular, que permita el seguimiento de productos desde el fabricante hasta el cliente final, la optimización de rutas y almacenamiento, la predicción de demanda mediante análisis predictivo y la integración con dispositivos IoT para monitoreo en tiempo real, aplicando patrones de diseño GoF como estrategia de solución a los principales retos de extensibilidad, mantenibilidad y bajo acoplamiento del sistema.

## Objetivos específicos

1. Diseñar la arquitectura hexagonal del sistema, separando claramente dominio, aplicación, infraestructura e interfaces en cada uno de los módulos (`tracking`, `logistics`, `forecasting`, `iot`), de forma que el sistema quede preparado para una eventual migración a microservicios.

2. Implementar el módulo `tracking` para el registro y validación de eventos de seguimiento de productos a lo largo de la cadena de suministro, aplicando los patrones **Factory Method** (creación de eventos según tipo de sensor/etapa) y **Chain of Responsibility** (validación de eventos).

3. Implementar el módulo `logistics` para la optimización de rutas de distribución y almacenamiento, aplicando los patrones **Builder** (construcción de rutas complejas) y **Strategy** (algoritmos de optimización intercambiables).

4. Implementar el módulo `forecasting` para la predicción de demanda mediante análisis predictivo, aplicando los patrones **Decorator** (enriquecimiento de reportes) y **Command** (encapsulamiento de operaciones de generación y recálculo de pronósticos).

5. Implementar el módulo `iot` para la integración con dispositivos de distintos fabricantes y el monitoreo en tiempo real, aplicando los patrones **Adapter** (integración de dispositivos heterogéneos) y **Observer** (notificación de eventos en tiempo real).

6. Centralizar los servicios transversales de conexión a base de datos y autenticación en el módulo `shared`, aplicando el patrón **Singleton** para garantizar una única instancia del motor de base de datos y de la gestión de sesiones/JWT.

7. Garantizar la calidad del software mediante pruebas automatizadas (pytest, cobertura ≥ 80%) e integración continua (GitHub Actions), documentando las decisiones de diseño mediante ADRs y diagramas UML.

8. Contenerizar el sistema (Docker / docker-compose) para facilitar su despliegue y validar su viabilidad como base hacia una futura arquitectura de microservicios.

## Arquitectura

Monolito modular con **arquitectura hexagonal** por módulo (bounded context),
preparado para ser desplegado como microservicios independientes vía
`docker-compose`. Justificación completa en [`docs/adr/0001-arquitectura-y-stack.md`](docs/adr/0001-arquitectura-y-stack.md).

Módulos:

| Módulo | Responsabilidad |
|---|---|
| `tracking` | Seguimiento de productos fabricante → cliente final |
| `logistics` | Optimización de rutas y almacenamiento |
| `forecasting` | Predicción de demanda (análisis predictivo) |
| `iot` | Integración IoT y monitoreo en tiempo real |

Cada módulo sigue la estructura hexagonal:

```
src/<modulo>/
├── domain/          # Entidades, value objects, puertos (interfaces)
├── application/      # Casos de uso, patrones de comportamiento
├── infrastructure/    # Adaptadores: BD, mensajería, IoT, APIs externas
└── interfaces/        # Adaptadores de entrada: REST, CLI, eventos
```

## Stack tecnológico

- **Lenguaje:** Python 3.11
- **Framework API:** FastAPI
- **Pruebas:** pytest + pytest-cov (cobertura objetivo ≥ 80%)
- **CI/CD:** GitHub Actions
- **Monitoreo/Logging:** Prometheus + Grafana (por definir en infraestructura)
- **Contenedores:** Docker / docker-compose

## Patrones GoF planeados (mínimo 8, ≥2 por categoría)

Repartidos por dueño de módulo: cada integrante es responsable de 2 módulos
completos (dominio, aplicación, infraestructura, interfaces, pruebas y
documentación de esos módulos).

| Categoría | Patrón | Módulo | Uso previsto | Responsable |
|---|---|---|---|---|
| Creacional | Builder | `logistics` | Construcción de rutas de distribución complejas | Brayan Martínez |
| Creacional | Factory Method | `tracking` | Creación de eventos de tracking según tipo de sensor/etapa | Julián Niño |
| Estructural | Adapter | `iot` | Integración con dispositivos IoT de distintos fabricantes | Brayan Martínez |
| Estructural | Decorator | `forecasting` | Enriquecimiento de reportes de predicción de demanda | Julián Niño |
| Comportamiento | Strategy | `logistics` | Algoritmos de optimización de rutas intercambiables | Brayan Martínez |
| Comportamiento | Observer | `iot` | Notificación en tiempo real de eventos IoT | Brayan Martínez |
| Comportamiento | Chain of Responsibility | `tracking` | Validación de eventos de la cadena de suministro | Julián Niño |
| Comportamiento | Command | `forecasting` | Encapsular operaciones de generación/recálculo de pronósticos | Julián Niño |

(Sujeto a ajuste conforme avance el diseño; se documentará en UML y ADRs.)

### Dueños de módulo

| Módulo | Responsable principal |
|---|---|
| `logistics` | Brayan Martínez |
| `iot` | Brayan Martínez |
| `tracking` | Julián Niño |
| `forecasting` | Julián Niño |

Cada quien abre sus propias ramas `feature/<modulo>-...` desde `develop` para
trabajar en sus módulos, pero cualquiera puede hacer PR de revisión sobre el
módulo del otro.

## Cómo ejecutar (en construcción)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # completar DATABASE_URL y JWT_SECRET_KEY reales
uvicorn src.main:app --reload
```

### Configuración (variables de entorno)

La app lee la configuración desde variables de entorno (con `.env` local vía
`python-dotenv`, que **no** se sube al repo). Ver [`.env.example`](.env.example)
para el listado completo:

| Variable | Uso | Default si no está definida |
|---|---|---|
| `DATABASE_URL` | Connection string de Postgres (local o en la nube, p.ej. Neon) | Postgres local (`localhost:5432/scm_db`) |
| `JWT_SECRET_KEY` | Clave para firmar/verificar los JWT | Clave de desarrollo, **no usar en producción** |
| `JWT_ALGORITHM` | Algoritmo de firma JWT | `HS256` |
| `JWT_EXPIRE_MINUTES` | Minutos de expiración del token | `60` |

Para usar una base de datos en la nube (Neon, Supabase, etc.) en vez de una
instalación local de Postgres, solo hay que definir `DATABASE_URL` en el
`.env` con la connection string que entregue el proveedor — el resto del
código (Singleton `DatabaseConnection`) no cambia.

## Pruebas

```bash
pytest --cov=src --cov-report=term-missing
```

## Estructura de commits

Este repositorio usa [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/):
`feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, `build`.

## Equipo

| Nombre | Módulos a cargo |
|---|---|
| Brayan Martínez | `logistics`, `iot` |
| Julián Niño | `tracking`, `forecasting` |

## Licencia

Uso académico — UTS.

## Patron Singleton


---

## Registro de avances — Módulo `shared` (conexión BD + autenticación)

### Base de datos
- Se implementó el patrón **Singleton** (`src/shared/database.py`) para centralizar la creación del `engine` de SQLAlchemy y el `sessionmaker`, garantizando una única instancia thread-safe (con `threading.Lock` y doble chequeo) reutilizada en toda la aplicación.
- Se agregó el endpoint `GET /health`, que ejecuta una consulta real (`SELECT 1`) contra PostgreSQL para verificar la conexión, en lugar de solo confirmar que el servidor está en pie.

### Autenticación (login y registro)
- Se implementó un endpoint `POST /login` con generación de tokens **JWT**, usando `python-jose`.
- El manejo de JWT también sigue el patrón **Singleton** (`src/shared/security.py`, clase `JWTManager`), centralizando la configuración (clave secreta, algoritmo, expiración) y el control de sesiones activas por usuario.
- Se agregó control de sesión duplicada: si un usuario ya tiene un token activo y vigente, un nuevo intento de login devuelve `409 Conflict` en vez de generar un token adicional.
- Los usuarios ya se persisten en una tabla real `users` de PostgreSQL (`src/shared/models.py`), con contraseñas hasheadas con `bcrypt` (`src/shared/password_hashing.py`) — ya no se usa el `FAKE_USER` en memoria.
- Al arrancar la app (`src/main.py`, `lifespan`), se crea la tabla `users` si no existe y se siembra un usuario `admin`/`admin123` si la tabla está vacía, para que las pruebas manuales (Postman, curl) funcionen sin pasos extra.
- Nuevo endpoint `POST /register` para crear usuarios adicionales (devuelve `409 Conflict` si el username ya existe).

### Cómo probarlo
```bash
# Verificar conexión a BD
GET http://127.0.0.1:8000/health

# Login (Postman / curl)
POST http://127.0.0.1:8000/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

# Registrar un usuario nuevo
POST http://127.0.0.1:8000/register
Content-Type: application/json

{
  "username": "nuevo_usuario",
  "password": "clave123"
}
```

### Pendiente
- Endpoint de `logout` para invalidar sesión manualmente.
- Frontend separado (fuera de este backend) con diseño UX/UI, a construir después.
- Iniciar dominio de `forecasting` (Command).

---

## Módulo `tracking` — Patrón: Factory Method

**Responsable habitual del módulo:** Julián Niño (ver tabla de dueños de módulo).

Implementa el registro de eventos de seguimiento de productos en la cadena
de suministro, usando **Factory Method** para decidir qué tipo de evento
construir según el dato recibido (sensor IoT o cambio de etapa), tal como
lo pide el objetivo específico del módulo.

### Diseño
- `src/tracking/domain/entities.py`: `TrackingEvent` (base) y los productos
  concretos `SensorTrackingEvent` / `StageChangeTrackingEvent`.
- `src/tracking/domain/event_factory.py`: `TrackingEventCreator` (Creator
  abstracto) con `SensorEventCreator` y `StageChangeEventCreator` como
  subclases concretas — el patrón Factory Method en sí.
- `src/tracking/application/register_event.py`: caso de uso que resuelve el
  Creator adecuado y persiste el evento a través de un puerto de repositorio.
- `src/tracking/infrastructure/`: adaptador SQLAlchemy (`tracking_events`)
  que reutiliza la sesión de `get_db()` — es decir, el engine único de
  `DatabaseConnection` (Singleton) de `src/shared`. El Factory Method **no**
  crea su propia conexión ni se implementa como Singleton: son patrones
  distintos y se mantienen separados a propósito.
- `src/tracking/interfaces/api.py`: `POST /tracking/events` y
  `GET /tracking/events/{product_id}`.

### Cómo probarlo
```bash
# Evento de sensor
POST http://127.0.0.1:8000/tracking/events
Content-Type: application/json

{
  "event_type": "sensor",
  "product_id": "PROD-001",
  "stage": "transporte",
  "sensor_type": "temperatura",
  "reading_value": 4.5,
  "unit": "C"
}

# Evento de cambio de etapa
POST http://127.0.0.1:8000/tracking/events
Content-Type: application/json

{
  "event_type": "stage_change",
  "product_id": "PROD-001",
  "stage": "entrega",
  "previous_stage": "transporte",
  "responsible": "Transportista X"
}

# Historial de eventos de un producto
GET http://127.0.0.1:8000/tracking/events/PROD-001
```

### Pendiente
- Chain of Responsibility para validar los eventos antes de guardarlos
  (siguiente patrón planeado para este módulo).
- Los endpoints de tracking todavía no exigen JWT (igual que el resto de
  la API por ahora).

---

## Semana 3 — Patrón: Singleton

**Módulo:** `shared` (transversal a `tracking` y `forecasting`)
**Responsable:** Julián Niño

### Código
![Clase database](docs/images/patron_Singleton_Instancia_BD.png)
![Clase JWTManager](docs/images/patrons_Singleton_Loggin.png)


### Prueba de funcionamiento
![Consola mostrando instancia única](docs/images/patron_Singleton_Prueba_login.png)

### Dónde se implementa
![Ubicación en la arquitectura hexagonal](docs/images/arquitectura_hexagonal.png)

**Justificación:** se usa para garantizar una única instancia de conexión a BD / configuración JWT, compartida en toda la aplicación sin duplicar recursos.


---
## Semana 4
## Registro de avances — Módulo `tracking` (Abstract Factory)

### Contexto
- El **Factory Method** (implementado por el compañero de módulo) resuelve la **creación** del `TrackingEvent` según su tipo (`sensor` o `stage_change`).
- El **Abstract Factory** resuelve un problema distinto: el **procesamiento** del evento ya creado — construye una familia coherente de dos componentes (`validador` + `notificador`) según ese mismo tipo de evento, sin duplicar ni interferir con el Factory Method existente.

### Código
CLASE ABSCTRAC FACTORY
![Puertos del Abstract Factory](docs/images/semana-4/puertos.png)

FAMILIA DE PROCESOS
![Familias concretas (sensor y stage_change)](docs/images/semana-4/familias.png)

FACTORIES (SELECTOR)
![Registro selector de fábricas](docs/images/semana-4/registro.png)

REGISTRO EVENTO
![Registro selector de fábricas](docs/images/semana-4/Registro-Evento.png)

### Prueba de funcionamiento

PRUEBA DE LOGS EN CONSOLA
![Consola mostrando familia seleccionada y notificación generada](docs/images/semana-4/prueba-consola.png)

EJECUCIONES  EN POSTMAN
![Postman: evento tipo sensor registrado correctamente](docs/images/semana-4/postman-sensor.png)

![Postman: error 400 por validación de negocio (temperatura fuera de rango)](docs/images/semana-4/postman-error-validacion.png)

### Video explicativo
[Ver sustentación en video](https://youtu.be/NaDLKI6nF7g)
### Dónde se implementa
- **Puertos:** `src/tracking/domain/processing_ports.py`
- **Familias concretas:** `src/tracking/infrastructure/factories/`
- **Registro/selector:** `src/tracking/application/processing_factory_registry.py`
- **Integración:** `src/tracking/application/register_event.py`

### Cómo probarlo
```bash
POST http://127.0.0.1:8000/tracking/events
Content-Type: application/json

{
  "event_type": "sensor",
  "product_id": "PROD-001",
  "stage": "transporte",
  "sensor_type": "temperatura",
  "reading_value": 23.5,
  "unit": "°C"
}
```

```bash
POST http://127.0.0.1:8000/tracking/events
Content-Type: application/json

{
  "event_type": "stage_change",
  "product_id": "PROD-001",
  "stage": "transporte",
  "previous_stage": "fabricacion",
  "responsible": "Julian Nino"
}
```

### Justificación del patrón
Se usa Abstract Factory porque, para cada tipo de evento de tracking, el validador y el notificador deben ser mutuamente coherentes (por ejemplo, el validador de sensor nunca debe combinarse con el notificador de cambio de etapa). El registro selector permite agregar nuevos tipos de evento sin modificar el código existente, solo registrando una nueva familia concreta.

### Pendiente
- Endpoints CRUD de `products` para dejar de usar `product_id` "quemado" y consultarlo real desde la base de datos.
- Validar que el `product_id` exista antes de registrar un evento de tracking.

---

## Módulo `logistics` — Patrón: Builder (+ Director)

**Responsable:** Brayan Martínez.

Implementa la construcción de rutas de distribución complejas, tal como lo
pide el objetivo específico del módulo.

### Diseño
- `src/logistics/domain/entities.py`: `DistributionRoute` (producto,
  inmutable) y `RouteStop`.
- `src/logistics/domain/route_builder.py`: `RouteBuilder` (Builder
  abstracto) y `DistributionRouteBuilder` (concreto) — construcción
  encadenada (`set_vehicle().set_departure_date().add_stop()...build()`),
  validando las invariantes mínimas (vehículo, fecha, ≥2 paradas) solo al
  llamar `build()`.
- `src/logistics/domain/route_director.py`: `RouteDirector` — conoce
  "recetas" estándar (`standard`, `express`) y las reproduce sobre
  cualquier `RouteBuilder`, sin acoplarse a la clase concreta.
- `src/logistics/application/create_route.py`: caso de uso que elige entre
  usar el Director (rutas `standard`/`express`) o construir una ruta
  `custom` a mano con el mismo Builder, y persiste el resultado.
- `src/logistics/infrastructure/`: adaptador SQLAlchemy (`distribution_routes`)
  que reutiliza `get_db()` — el engine único de `DatabaseConnection`
  (Singleton) de `src/shared`. El Builder **no** es Singleton ni crea su
  propia conexión: son patrones distintos, deliberadamente separados.
- `src/logistics/interfaces/api.py`: `POST /logistics/routes`,
  `GET /logistics/routes/{route_id}`, `GET /logistics/routes`.

### Cómo probarlo
```bash
# Ruta estándar (Director: vehículo y notas por defecto)
POST http://127.0.0.1:8000/logistics/routes
Content-Type: application/json

{
  "route_type": "standard",
  "stops": ["Bodega Central", "Cliente A", "Cliente B"],
  "departure_date": "2026-09-10"
}

# Ruta express (Director: otro vehículo + notas automáticas)
POST http://127.0.0.1:8000/logistics/routes
Content-Type: application/json

{
  "route_type": "express",
  "stops": ["Bodega Central", "Cliente A"],
  "departure_date": "2026-09-10"
}

# Ruta personalizada (usa el Builder directamente, sin Director)
POST http://127.0.0.1:8000/logistics/routes
Content-Type: application/json

{
  "route_type": "custom",
  "stops": ["Bodega Central", "Cliente A"],
  "departure_date": "2026-09-10",
  "vehicle_type": "furgon_refrigerado",
  "total_distance_km": 15.3
}

# Consultar rutas
GET http://127.0.0.1:8000/logistics/routes
GET http://127.0.0.1:8000/logistics/routes/{route_id}
```

### Justificación del patrón
Una ruta de distribución tiene partes obligatorias (vehículo, fecha,
paradas) y opcionales (distancia total, notas), y el orden en que se
agregan no debería importarle a quien la construye. El Builder encapsula
ese ensamblaje paso a paso y solo valida las invariantes al final
(`build()`), evitando productos a medio construir. El Director además
demuestra que se puede reutilizar la misma lógica de construcción para
distintas "recetas" estándar sin repetir código en cada lugar que crea
una ruta `standard` o `express`.

### Pendiente
- Persistir el catálogo real de `vehicle_type` (hoy son strings libres).
- Validar direcciones/paradas contra un catálogo real en vez de texto libre.

### Decisión: no se incluye el patrón Prototype

**Contexto:** de los 5 patrones creacionales del catálogo GoF, el proyecto ya
implementa 4: Singleton, Factory Method, Abstract Factory y Builder.

**Decisión:** no se incluye Prototype.

**Justificación:**
- Prototype resuelve la clonación de instancias existentes cuando construirlas
  desde cero es costoso. En este proyecto, todas las entidades (eventos de
  tracking, productos, rutas) se construyen a partir de datos de entrada
  variables en cada solicitud — no existe un caso real de "partir de una
  instancia base y clonarla con pequeñas variaciones".
- Los 4 patrones creacionales ya implementados cubren de forma genuina los
  problemas de creación de objetos presentes en el sistema: instancia única
  compartida (Singleton), selección de subtipo según dato de entrada (Factory
  Method), familias de objetos coherentes (Abstract Factory), y construcción
  paso a paso de objetos complejos (Builder).
- Agregar Prototype sin un caso de uso genuino añadiría complejidad
  injustificada al código, contrario al principio de aplicar cada patrón
  donde resuelve un problema real.

**Alternativa a futuro:** si `logistics` llegara a necesitar generar rutas
recurrentes a partir de una plantilla base con pequeñas variaciones, Prototype
sería el candidato natural para esa extensión.

---

## Semana 5 — Patrones estructurales

Implementados en el commit `91fd5d5` (PR #10, Julián Niño). Los patrones están
en el código; las pruebas automáticas y esta documentación se agregaron
después, en la rama `fix/revision-patrones-estructurales`.

### Decorator — `forecasting`
- `src/forecasting/domain/forecast_report.py`: `ForecastReport` (componente) y
  `BaseForecastReport` (componente concreto).
- `src/forecasting/domain/report_decorators.py`: `ConfidenceIntervalDecorator`
  (intervalo de ±10 %) y `TrendAnnotationDecorator` (`alza` con 3 o más
  eventos, `insuficientes datos` en caso contrario). Se pueden apilar en
  cualquier orden.
- `src/forecasting/application/generate_forecast_report.py`: lee los eventos
  del producto desde el puerto de `tracking` y arma el reporte decorado.
- `GET /forecasting/reports/{product_id}`.

> **Nota:** la demanda base es una **estimación simulada** (`nº de eventos × 12.5`),
> no un modelo predictivo real. Sirve para demostrar el patrón; el modelo real
> queda pendiente.

### Adapter + Bridge — `iot`
- **Adapter:** `SensorDataPort` (Target) en `src/iot/domain/`,
  `VendorATemperatureClient` (Adaptee, simulado) y `VendorATemperatureAdapter`
  en `src/iot/infrastructure/`. Normaliza el payload del fabricante
  (`sensorId`/`tempC`) a un `SensorReading` común.
- **Bridge:** `NotificationDispatcher` (Abstraction: `Urgent...` y `Routine...`)
  delega el envío en un `NotificationChannel` (Implementor: `MqttChannel` y
  `WebhookChannel`). La urgencia y el canal varían de forma independiente.
  El Bridge **no estaba** en la tabla de patrones planeados (tampoco el Composite).
- `src/iot/application/ingest_sensor_reading.py`: encadena Adapter →
  Factory Method + Abstract Factory (tracking) → Bridge.
- `POST /iot/sensors/{vendor}/ingest` con `vendor` = `a` o `a-faulty`
  (este último simula una lectura de -60 °C, rechazada con `400`).

```bash
POST http://127.0.0.1:8000/iot/sensors/a/ingest
Content-Type: application/json

{ "product_id": "PROD-001", "stage": "transporte" }
```

### Composite — `logistics`
- `src/logistics/domain/route_component.py` (componente), `route_leaf.py`
  (`SingleRoute`, hoja) y `route_corridor.py` (`RouteCorridor`, compuesto, que
  puede contener rutas u otros corredores).
- `POST /logistics/corridors` agrupa rutas ya creadas y suma su distancia.

```bash
POST http://127.0.0.1:8000/logistics/corridors
Content-Type: application/json

{ "name": "Corredor Norte", "route_ids": [1, 2] }
```

### Cambios de la revisión
- `tracking`: `SensorEventValidator` ahora rechaza temperaturas menores a
  -50 con unidad `°C` **o** `C` (antes solo `°C`, con una condición redundante).
  La regla se aplica por unidad, no por `sensor_type`.
- `iot`: la clase de despacho urgente se llama `UrgentNotificationDispatcher`;
  `NotificationDispatcher` es abstracta.
- Los mensajes de Decorator, Adapter, Bridge y Composite usan `logging` en vez
  de `print` (los `[ABSTRACT FACTORY]` de la semana 4 siguen usando `print`).

### Pendiente
- Observer (`iot`), Strategy (`logistics`), Chain of Responsibility
  (`tracking`) y Command (`forecasting`).
- Los endpoints nuevos de `iot` y `logistics` tampoco exigen JWT (el de
  `forecasting` sí, desde la semana 10: ver Proxy más abajo).


---

## Semanas 9 y 10 — Facade, Flyweight y Proxy

Los diagramas UML de los siete patrones estructurales están en
[`docs/uml/`](docs/uml/) (fuentes `.puml` y PNG). El documento técnico
actualizado es [`docs/semana_10.docx`](docs/semana_10.docx), y las decisiones
de diseño están en
[`docs/adr/0002-patrones-estructurales.md`](docs/adr/0002-patrones-estructurales.md).

### Facade — módulo `products` (semana 9)
- `src/products/application/product_overview_facade.py`: `ProductOverviewFacade`
  combina el historial de `tracking` y el reporte de `forecasting` en una sola
  llamada. Depende de los puertos `TrackingEventRepository` y
  `ForecastReportService`, no de clases concretas.
- `src/products/interfaces/api.py`: `GET /products/{product_id}/overview`
  (requiere JWT, ver Proxy).
- No incluye rutas de `logistics`: una `DistributionRoute` no guarda
  `product_id`, así que no hay relación que consultar.

### Flyweight — módulo `logistics` (semana 10)
- `src/logistics/domain/vehicle_type.py`: `VehicleType` (inmutable) y
  `VehicleTypeFactory`, que entrega siempre la misma instancia para cada tipo
  del catálogo (`camion_estandar`, `moto_express`, `furgon_refrigerado`).
- `DistributionRoute.vehicle` devuelve el flyweight de su tipo de vehículo, y
  la respuesta de las rutas agrega el campo `refrigerated`.
- **Aplicabilidad limitada:** el ahorro de memoria es pequeño porque el
  sistema no maneja millones de rutas; se implementa porque el tipo de
  vehículo es estado inmutable repetido y avanza el catálogo pendiente.
- Los códigos fuera del catálogo (texto libre en rutas `custom`) **no** se
  guardan en el pool, para que un cliente no pueda hacer crecer la memoria
  enviando códigos distintos.

### Proxy de protección — módulo `forecasting` (semana 10)
- `src/forecasting/domain/report_service.py`: `ForecastReportService` (Subject)
  y `ForecastAccessDenied`.
- `src/forecasting/application/authorized_forecast_report_proxy.py`:
  `AuthorizedForecastReportProxy` valida el JWT con `JWTManager` y solo
  entonces delega en `GenerateForecastReportUseCase` (RealSubject).
- **Cambio de comportamiento:** `GET /forecasting/reports/{product_id}` y
  `GET /products/{product_id}/overview` ahora exigen
  `Authorization: Bearer <token>` (se obtiene en `POST /login`) y responden
  `401` si falta o es inválido.
- Se evaluó un Proxy de caché, pero se eligió el de protección porque cierra el
  pendiente de seguridad ya registrado.
- **Ojo:** `POST /login` responde `409` si el usuario ya tiene una sesión
  vigente, y todavía no existe logout. Si pierdes el token, hay que esperar a
  que expire (60 min por defecto) para iniciar sesión de nuevo.

```bash
POST http://127.0.0.1:8000/login
{ "username": "admin", "password": "admin123" }

GET http://127.0.0.1:8000/products/PROD-001/overview
Authorization: Bearer <access_token>
```

### Pendiente
- Patrones de comportamiento: Strategy (`logistics`), Observer (`iot`),
  Chain of Responsibility (`tracking`) y Command (`forecasting`).
- Proteger con JWT los endpoints de `tracking`, `logistics` e `iot`.
- Persistir el catálogo de tipos de vehículo.
