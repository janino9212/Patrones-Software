# ADR-0003: Patrones de comportamiento, sesión y frontend

## Estado
Aceptado

## Contexto
Con los patrones creacionales (4 de 5) y estructurales (7 de 7) ya
implementados, faltaba la categoría completa de comportamiento (11 patrones),
de los cuales cuatro estaban planeados desde el inicio (Strategy, Observer,
Chain of Responsibility y Command). También seguían pendientes el logout, la
protección con JWT de `tracking`, `logistics` e `iot`, el catálogo de
productos, el frontend y la contenerización.

Se mantiene la regla del proyecto: cada patrón se aplica solo donde resuelve un
problema real y, si no aplica, se justifica (como se hizo con Prototype).

## Decisión

### Patrones aplicados

| Patrón | Módulo | Problema que resuelve |
|---|---|---|
| Chain of Responsibility | `tracking` | Validar los datos crudos de un evento con reglas independientes y ordenables, antes de crearlo. |
| Strategy | `logistics` | Elegir en tiempo de ejecución el algoritmo que ordena las paradas de una ruta. |
| State | `logistics` | Que las acciones válidas sobre una ruta dependan de su estado, sin condicionales repartidos. |
| Iterator | `logistics` | Recorrer las rutas de un corredor sin conocer su anidación (aplicabilidad limitada). |
| Template Method | `forecasting` | Fijar los pasos de todo pronóstico y dejar que cada modelo aporte solo su fórmula. |
| Command | `forecasting` | Registrar y deshacer las operaciones de generar y recalcular un pronóstico. |
| Memento | `forecasting` | Restaurar el pronóstico anterior al deshacer un recálculo, sin exponer su estado. |
| Observer | `iot` | Reaccionar a cada lectura (panel, alertas, dispositivos) sin acoplar la ingesta a esas reacciones. |

Notas de diseño:

- **Chain of Responsibility.** La cadena actúa sobre los datos crudos, antes del
  Factory Method; el validador de la Abstract Factory sigue aplicando las
  reglas de negocio sobre el evento ya creado. `MissingFieldError` hereda de
  `KeyError` para conservar la respuesta `422` que ya daba la API.
- **Strategy.** Las estrategias ordenan ubicaciones de un catálogo fijo de 12
  ciudades; la distancia es en línea recta (haversine), no sobre la red vial.
  La primera parada es el origen y ninguna estrategia la mueve. Con una
  estrategia distinta de `none`, todas las paradas deben estar en el catálogo.
- **State.** El estado se guarda como texto (`status`) y el objeto State se
  resuelve al consultarlo, porque la entidad es inmutable. La transición
  inválida responde `409`.
- **Iterator.** Python ya ofrece el protocolo de iteración; se escribe la clase
  `RouteLeafIterator` explícita (con su propia pila) porque el patrón es parte
  de lo que se demuestra y porque el recorrido en profundidad del Composite no
  es trivial. Se documenta como aplicabilidad limitada.
- **Command.** El receiver (`ForecastPlanner`) se pasa en `execute`/`undo` y no
  en el constructor: está ligado a la sesión de base de datos de una petición y
  el comando la sobrevive dentro del historial del invoker.
- **Memento.** El caretaker es `RecalculateForecastCommand`. Deshacer un
  `generate` no necesita memento: basta con descartar el pronóstico.
- **Observer.** Un observador que falla no interrumpe a los demás ni a la
  ingesta, que ya quedó registrada. Las lecturas rechazadas por la validación
  no se publican.

### Patrones descartados

- **Interpreter.** No existe un lenguaje ni una gramática que evaluar. Las
  reglas de validación y los umbrales de alerta son fijos en el código; nadie
  escribe expresiones que el sistema deba interpretar. Aplicaría si los
  umbrales se definieran con una sintaxis propia (por ejemplo
  `temperatura > 30 y etapa = transporte`).
- **Mediator.** No hay un conjunto de objetos pares que se comuniquen entre sí
  de muchos a muchos. La coordinación entre módulos ya está centralizada en los
  casos de uso y en la Facade, y la difusión de avisos, en el Observer. Un
  Mediator duplicaría esa responsabilidad.
- **Visitor.** La única jerarquía candidata es la de eventos de tracking, con
  dos subtipos, y la Abstract Factory ya separa el comportamiento por tipo. El
  doble despacho añadiría una interfaz y dos métodos por operación para ahorrar
  un `isinstance`. Aplicaría si la jerarquía creciera y necesitara muchas
  operaciones nuevas (exportar, auditar, facturar) sin tocar las entidades.
- **Prototype.** Sin cambios respecto a la decisión registrada en el README.

Resultado: 19 de los 23 patrones GoF aplicados (4 creacionales, 7
estructurales, 8 de comportamiento).

### Sesión y seguridad

- `POST /login` ya no responde `409` cuando el usuario tiene una sesión
  vigente: el login nuevo **reemplaza** la sesión anterior. Cada token lleva un
  `jti` único.
- Se agrega `POST /logout` y `GET /me`.
- `JWTManager.decode_active_token` exige que el token sea la sesión activa del
  usuario. Lo usan la dependencia `current_user` y el Proxy de `forecasting`,
  de modo que un token cerrado con logout o reemplazado se rechaza aunque su
  firma siga siendo válida.
- Los routers de `tracking`, `logistics` e `iot`, el catálogo de `products` y
  los endpoints nuevos de `forecasting` exigen sesión. Solo quedan abiertos
  `/`, `/health`, `/login` y `/register`.
- CORS restringido a los orígenes de `CORS_ORIGINS`.
- `POST /register` sigue abierto para que la demostración pueda crear
  cuentas; con `ALLOW_REGISTRATION=false` responde `403`. Mientras esté
  abierto, "exigir sesión" solo significa "exigir una cuenta", no un permiso.
- Los errores de validación (`422`) ya no devuelven el valor recibido, y
  `/health` ya no expone el mensaje de error de la base de datos.
- El cambio de estado de una ruta es un `UPDATE` condicionado al estado leído,
  y el invoker de comandos ejecuta y registra cada operación bajo un mismo
  candado, para que dos peticiones simultáneas no dejen datos incoherentes.

### Frontend

Aplicación React + Vite + TypeScript + Tailwind en `frontend/`, separada del
backend y comunicada solo por la API. Las decisiones visuales están en
[`DESIGN.md`](../../DESIGN.md).

### Esquema de base de datos

El proyecto no usa Alembic. `Base.metadata.create_all` crea las tablas nuevas
(`products`, `demand_records`, `forecast_plans`) pero no altera las
existentes, así que `src/shared/schema_migrations.py` agrega al arrancar la
columna `distribution_routes.status` si falta.

## Consecuencias

- **Cambio de comportamiento:** `tracking`, `logistics` e `iot` ahora responden
  `401` sin `Authorization: Bearer <token>`.
- **Cambio de comportamiento:** un segundo login invalida el token anterior en
  lugar de fallar con `409`.
- Las sesiones, la bitácora de comandos y el monitor de sensores viven en
  memoria del proceso: se pierden al reiniciar la API y no se comparten entre
  varios workers. Los datos de negocio sí persisten en la base de datos.
- Tras reiniciar la API, deshacer no está disponible para los pronósticos
  anteriores (el botón aparece deshabilitado).
- El frontend guarda el token en `sessionStorage`. Es legible por JavaScript,
  así que un XSS podría robarlo; se acepta porque la API es Bearer y la
  alternativa (cookie `httpOnly`) exige además protección CSRF.
- El pronóstico por modelo necesita historial de demanda cargado a mano; sin
  él, el reporte conserva la estimación simulada original por eventos.
- No se valida que el `product_id` de un evento exista en el catálogo, para no
  romper los clientes que ya registraban eventos de productos arbitrarios.
- No hay límite de peticiones (rate limiting).
- La bitácora de comandos es global: cualquier usuario con sesión puede
  deshacer la última operación de un producto, sin importar quién la hizo.
- El usuario `admin`/`admin123` se siembra siempre al arrancar. Es cómodo
  para la demostración e inaceptable fuera de ella.
- En el reporte, `trend` sigue saliendo del número de eventos de tracking
  (decorador de la semana 5), aunque la demanda venga de un modelo.

## Referencias
- [ADR-0001](0001-arquitectura-y-stack.md), [ADR-0002](0002-patrones-estructurales.md)
- Diagramas UML en `docs/uml/`
