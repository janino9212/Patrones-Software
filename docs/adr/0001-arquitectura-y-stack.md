# ADR-0001: Arquitectura y stack tecnológico inicial

## Estado
Aceptado

## Contexto
El proyecto exige explícitamente:
- Arquitectura basada en microservicios/hexagonal.
- Mínimo 8 patrones GoF (≥2 por categoría), visibles y evaluables.
- Cobertura de pruebas automatizadas ≥ 80 %.
- CI/CD con Git.
- Monitoreo/logging centralizado.

El equipo cuenta con un plazo académico limitado y experiencia variable en
distintos lenguajes, por lo que la solución debe priorizar simplicidad de
desarrollo sin sacrificar el cumplimiento de los requisitos técnicos.

## Opciones consideradas

1. **Java + Spring Boot**: robusto y "enterprise", pero Spring resuelve
   internamente muchos patrones (DI, proxies) lo que dificulta mostrar la
   implementación explícita de los patrones GoF exigidos. Curva de
   aprendizaje más alta para el equipo.
2. **Node.js + NestJS**: similar a Spring en cuanto a que el framework ya
   aplica varios patrones de forma implícita (decoradores, DI).
3. **Python + FastAPI**: bajo boilerplate, tipado opcional con type hints,
   configuración de pruebas y cobertura muy directa (pytest, pytest-cov),
   y permite implementar los patrones GoF de forma explícita y visible en
   el código, que es justamente lo que se evalúa.

## Decisión
Se adopta **Python 3.11 + FastAPI**, con un **monolito modular** organizado
en 4 módulos (bounded contexts): `tracking`, `logistics`, `forecasting`,
`iot`. Cada módulo implementa **arquitectura hexagonal** (domain /
application / infrastructure / interfaces) de forma independiente.

Se documenta el monolito modular como estrategia intermedia hacia
microservicios: cada módulo es desacoplado, se comunica solo a través de
puertos/interfaces definidos en `domain`, y puede extraerse a un servicio
independiente (empaquetado con Docker) sin reescribir lógica de negocio.
Esto cumple el requisito "microservicios/hexagonal" priorizando la
viabilidad del proyecto en el tiempo disponible, evitando la complejidad
operativa de microservicios reales (orquestación, service discovery, etc.)
que no aporta valor pedagógico adicional para el curso de patrones.

## Consecuencias
- Se facilita alcanzar cobertura de pruebas ≥ 80 % por la simplicidad del
  lenguaje y el ecosistema de testing.
- Los patrones GoF quedan explícitos en `domain/` y `application/` de cada
  módulo, facilitando la sustentación y el video demostrativo.
- Si se requiere escalar a microservicios reales, cada carpeta `src/<modulo>`
  puede convertirse en un repositorio/servicio independiente con mínima
  fricción, gracias al aislamiento por puertos y adaptadores.
- Se usará Docker Compose para simular el despliegue de "servicios"
  independientes cuando se necesite demostrar el enfoque distribuido.

## Referencias
- Requisitos del proyecto — Docente Eliecer Montero Ojeda, Ed.D.
- Conventional Commits: https://www.conventionalcommits.org/es/v1.0.0/
