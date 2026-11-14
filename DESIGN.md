# Diseño de la interfaz

Decisiones visuales del frontend (`frontend/`). El contexto del producto está
en [`PRODUCT.md`](PRODUCT.md).

## Escena de uso

Se muestra en una sustentación académica, proyectada en un aula iluminada o en
pantalla compartida. Por eso el tema es claro, el texto base es de 17 px y el
contraste es alto: debe leerse desde el fondo del salón.

## Mundo visual: señalización vial y guías de transporte

El sistema mueve productos por carretera entre ciudades colombianas. La
interfaz toma su vocabulario de lo que ese mundo ya usa para orientar: las
señales de carretera y los mapas de línea de una ruta.

Ese mundo aporta cuatro cosas y solo esas. La navegación, los formularios y los
controles son los estándar de una aplicación web.

| Aporte | Decisión |
|---|---|
| Tipografía | **Overpass**, derivada de la tipografía de las autopistas (Highway Gothic). **Overpass Mono** solo para datos: códigos, cantidades, distancias y horas. Ambas se sirven desde el propio proyecto. |
| Paleta | Riel de navegación verde carretera, amarillo de señal para la acción principal y la selección, azul de señal informativa para las etiquetas de patrón. |
| Densidad | Paneles compactos con listas, no tarjetas sueltas. Una pantalla debe poder demostrarse sin desplazarse mucho. |
| Firma | El **mapa de línea** (`StripMap`): un recorrido dibujado como línea con sus paradas. |

## Firma: el mapa de línea

Un mismo componente dibuja los tres recorridos del sistema:

- las **etapas de un producto** (fabricación → entrega), con la actual en amarillo;
- las **paradas de una ruta**, numeradas en orden de visita;
- la comparación de **estrategias de optimización**, donde se ve cómo cada una reordena las mismas paradas.

El color del tramo indica el estado: gris pendiente, verde recorrido, rojo cancelado.

## Color

Todos los colores son tokens en `frontend/src/index.css`.

| Token | Uso |
|---|---|
| `ground`, `surface`, `sunken` | Fondo de página (verde grisáceo muy claro), paneles, zonas hundidas |
| `ink`, `ink-soft` | Texto principal y secundario |
| `rail` | Riel de navegación y panel de bienvenida |
| `signal` | Botón principal, sección activa, elemento seleccionado |
| `go`, `stop`, `caution`, `info`, `idle` | Estados: en orden, error o alerta, advertencia, informativo, inactivo |

El color nunca es el único portador de significado: cada estado lleva además su
texto (por ejemplo, la insignia "En tránsito").

## Los patrones en la interfaz

Cada panel lleva en su encabezado etiquetas azules pequeñas con los patrones
GoF que lo respaldan. Son enlaces a la página **Patrones**, que lista los 23
del catálogo con su estado, el archivo donde viven y la pantalla donde se ven.
Las etiquetas acompañan la tarea, no la interrumpen.

## Componentes

- Una sola elevación: borde de 1 px, sin sombras.
- Radios: 12 px en paneles, 8 px en controles.
- Botón principal amarillo con texto oscuro; secundario con borde; destructivo con borde rojo.
- Toda consulta tiene tres estados visibles: esqueleto al cargar, mensaje con "Reintentar" al fallar, y un estado vacío que dice cuál es el siguiente paso.
- Sin ventanas modales: todo ocurre en la página.

## Movimiento

Transiciones de 150 ms en controles. Un único momento animado: la lectura de
sensor recién llegada se revela de izquierda a derecha sobre un destello
amarillo. Se desactiva con `prefers-reduced-motion`.

## Adaptación

Hasta 1024 px el riel pasa a ser una barra superior con desplazamiento
horizontal y los paneles se apilan en una columna. Los mapas de línea largos se
desplazan dentro de su panel sin ensanchar la página.
