# Sistema de Gestión de Cadena de Suministro (SCM)

Proyecto académico — Patrones de Diseño de Software
Unidades Tecnológicas de Santander (UTS)
Docente: Eliecer Montero Ojeda, Ed.D.

## Descripción

Sistema para el seguimiento de productos desde el fabricante hasta el cliente
final, con optimización de rutas y almacenamiento, predicción de demanda
mediante análisis predictivo, e integración con IoT para monitoreo en
tiempo real.

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
uvicorn src.tracking.interfaces.api:app --reload
```

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

### Autenticación (login)
- Se implementó un endpoint `POST /login` con generación de tokens **JWT**, usando `python-jose`.
- El manejo de JWT también sigue el patrón **Singleton** (`src/shared/security.py`, clase `JWTManager`), centralizando la configuración (clave secreta, algoritmo, expiración) y el control de sesiones activas por usuario.
- Se agregó control de sesión duplicada: si un usuario ya tiene un token activo y vigente, un nuevo intento de login devuelve `409 Conflict` en vez de generar un token adicional.
- Usuario de prueba temporal (`FAKE_USER` en `src/shared/auth.py`), pendiente de reemplazar por una tabla `users` real en PostgreSQL con contraseñas hasheadas.

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
```

### Pendiente
- Reemplazar `FAKE_USER` por persistencia real en PostgreSQL con hash de contraseña.
- Endpoint de `logout` para invalidar sesión manualmente.
- Iniciar dominio de `tracking` (Factory Method) y `forecasting` (Command).