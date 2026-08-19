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

| Categoría | Patrón | Módulo / uso previsto |
|---|---|---|
| Creacional | Factory Method | Creación de eventos de tracking según tipo de sensor/etapa |
| Creacional | Builder | Construcción de rutas de distribución complejas |
| Estructural | Adapter | Integración con dispositivos IoT de distintos fabricantes |
| Estructural | Decorator | Enriquecimiento de reportes de predicción de demanda |
| Comportamiento | Strategy | Algoritmos de optimización de rutas intercambiables |
| Comportamiento | Observer | Notificación en tiempo real de eventos IoT/tracking |
| Comportamiento | Command | Operaciones sobre inventario/almacenamiento |
| Comportamiento | Chain of Responsibility | Validación de eventos de la cadena de suministro |

(Sujeto a ajuste conforme avance el diseño; se documentará en UML y ADRs.)

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

- (agregar integrantes)

## Licencia

Uso académico — UTS.
