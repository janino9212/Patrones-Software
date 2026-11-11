# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

React + Vite + TypeScript + Tailwind CSS en `frontend/`, consumiendo la API FastAPI de `src/`. Elegido por el usuario.

## Users

Los dos autores del proyecto (Brayan Martínez y Julián Niño), que la muestran al docente durante la sustentación académica, proyectada o en pantalla compartida. El docente observa: necesita ver cada módulo funcionando y reconocer qué patrón de diseño actúa en cada acción.

## Product Purpose

Sistema de gestión de cadena de suministro (SCM): seguimiento de productos del fabricante al cliente final, optimización de rutas, predicción de demanda y monitoreo IoT. Existe como proyecto de la asignatura Patrones de Diseño de Software (UTS). Tiene éxito si el evaluador ve el sistema operar de extremo a extremo y puede relacionar cada comportamiento con el patrón GoF que lo implementa.

## Positioning

Cada función visible está respaldada por un patrón GoF real en el backend, y la interfaz lo señala donde ocurre.

## Operating Context

Demostración guiada: iniciar sesión, crear un producto, registrar eventos, crear y despachar rutas, cargar demanda y generar un pronóstico, simular lecturas de sensores y ver alertas. Se usa en un portátil, a menudo proyectado en un aula.

## Capabilities and Constraints

- Módulos: `tracking`, `logistics`, `forecasting`, `iot`, `products`, `shared` (autenticación).
- No hay hardware IoT: las lecturas provienen de clientes de fabricante simulados.
- Las distancias son en línea recta (haversine) sobre un catálogo fijo de 12 ciudades colombianas.
- El monitor IoT y la bitácora de comandos viven en memoria del proceso y se reinician con la API.
- Idioma de la interfaz: español.

## Evidence on Hand

Solo los datos que el propio usuario crea durante la demostración. No hay clientes, métricas ni testimonios; no se deben inventar.

## Product Principles

1. Lo que se muestra es lo que el backend realmente hace; nada decorativo simula datos.
2. El patrón se señala donde actúa, sin interrumpir la tarea.
3. Legible a distancia: se proyecta en un aula.
4. Cada pantalla debe poder demostrarse en menos de un minuto.
