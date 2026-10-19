# ADR-0002: Aplicabilidad de Facade, Flyweight y Proxy

## Estado
Aceptado

## Contexto
Los patrones estructurales Adapter, Bridge, Composite y Decorator ya estaban
implementados (semanas 7 y 8). Faltaban Facade, Flyweight y Proxy (semanas 9
y 10). La regla del proyecto es aplicar cada patrón solo donde resuelve un
problema real y, si no aplica, justificar por qué (como se hizo con Prototype).

## Decisión

### Facade — sí aplica
Consultar el estado de un producto exige combinar `tracking` (historial) y
`forecasting` (pronóstico). Se crea `ProductOverviewFacade` en un paquete
nuevo, `src/products`, porque una fachada que combina dos módulos no
pertenece a ninguno de ellos. Depende de puertos, no de clases concretas.
No se incluye `logistics`: una `DistributionRoute` no guarda `product_id`.

### Flyweight — aplica de forma limitada
Cada ruta repite su tipo de vehículo (texto libre; el catálogo real figuraba
como pendiente). Se comparte un `VehicleType` inmutable por cada tipo del
catálogo. El beneficio de memoria es modesto, porque el sistema no maneja
millones de rutas; se acepta porque el estado compartido es real y avanza el
catálogo pendiente. Los códigos fuera del catálogo no se guardan en el pool,
para evitar crecimiento ilimitado de memoria a partir de entrada del cliente.

### Proxy — sí aplica (de protección)
Se evaluaron dos variantes:
1. **Protección (JWT):** valida el token antes de ejecutar el caso de uso.
   Cierra el pendiente "los endpoints no exigen JWT".
2. **Caché:** guarda reportes ya calculados. Descartada por ahora: no cambia
   el comportamiento del sistema y el cálculo actual es una operación simple.

Se elige la primera y se aplica solo a `forecasting` y a la fachada de
`products`, para no cambiar el comportamiento de los demás endpoints.

## Consecuencias
- `GET /forecasting/reports/{product_id}` y
  `GET /products/{product_id}/overview` ahora requieren
  `Authorization: Bearer <token>` y responden 401 si falta o es inválido.
- Los endpoints de `tracking`, `logistics` e `iot` siguen sin exigir JWT.
- El proxy valida firma y vencimiento, pero no si la sesión fue invalidada
  manualmente (el logout sigue pendiente).
- `POST /login` devuelve 409 si ya hay una sesión vigente y no hay logout:
  un token perdido bloquea el acceso hasta que expire.
- `RouteResponse` agrega el campo `refrigerated` (cambio aditivo).
- El catálogo de vehículos está en el código; persistirlo queda pendiente.

## Referencias
- [ADR-0001](0001-arquitectura-y-stack.md)
- Diagramas UML en `docs/uml/`
