export type PatternCategory = "Creacional" | "Estructural" | "Comportamiento";
export type PatternStatus = "implementado" | "limitado" | "descartado";

export interface PatternEntry {
  name: string;
  category: PatternCategory;
  status: PatternStatus;
  module: string;
  /** Qué resuelve en este sistema, o por qué no aplica. */
  reason: string;
  /** Archivo principal, relativo a la raíz del repositorio. */
  source?: string;
  /** Pantalla donde se ve actuar. */
  screen?: { label: string; path: string };
}

export function patternSlug(name: string): string {
  return name.toLowerCase().replace(/\s+/g, "-");
}

export const PATTERNS: readonly PatternEntry[] = [
  {
    name: "Singleton",
    category: "Creacional",
    status: "implementado",
    module: "shared",
    reason:
      "Una sola instancia del motor de base de datos y del gestor de JWT para toda la aplicación.",
    source: "src/shared/database.py y src/shared/security.py",
    screen: { label: "Inicio de sesión", path: "/login" },
  },
  {
    name: "Factory Method",
    category: "Creacional",
    status: "implementado",
    module: "tracking",
    reason: "Cada Creator decide qué subtipo de evento construir: lectura de sensor o cambio de etapa.",
    source: "src/tracking/domain/event_factory.py",
    screen: { label: "Seguimiento", path: "/seguimiento" },
  },
  {
    name: "Abstract Factory",
    category: "Creacional",
    status: "implementado",
    module: "tracking",
    reason:
      "Entrega la pareja validador + notificador que corresponde a cada tipo de evento, sin mezclarlas.",
    source: "src/tracking/domain/processing_ports.py",
    screen: { label: "Seguimiento", path: "/seguimiento" },
  },
  {
    name: "Builder",
    category: "Creacional",
    status: "implementado",
    module: "logistics",
    reason:
      "Arma la ruta paso a paso y valida al final; el Director reproduce las recetas estándar y express.",
    source: "src/logistics/domain/route_builder.py",
    screen: { label: "Logística: Rutas", path: "/logistica" },
  },
  {
    name: "Prototype",
    category: "Creacional",
    status: "descartado",
    module: "—",
    reason:
      "Ninguna entidad se crea clonando otra: eventos, rutas y pronósticos nacen de datos distintos en cada solicitud, y construirlos no es costoso.",
  },
  {
    name: "Adapter",
    category: "Estructural",
    status: "implementado",
    module: "iot",
    reason:
      "Traduce el formato propio de cada fabricante de sensores a una lectura común.",
    source: "src/iot/infrastructure/sensor_adapters.py",
    screen: { label: "Monitoreo IoT", path: "/iot" },
  },
  {
    name: "Bridge",
    category: "Estructural",
    status: "implementado",
    module: "iot",
    reason:
      "Separa la urgencia de una notificación del canal por el que sale (MQTT o webhook).",
    source: "src/iot/domain/notification_dispatcher.py",
    screen: { label: "Monitoreo IoT", path: "/iot" },
  },
  {
    name: "Composite",
    category: "Estructural",
    status: "implementado",
    module: "logistics",
    reason:
      "Un corredor agrupa rutas y otros corredores, y todos responden igual a «¿cuánto mides?».",
    source: "src/logistics/domain/route_corridor.py",
    screen: { label: "Logística: Corredores", path: "/logistica?vista=corredores" },
  },
  {
    name: "Decorator",
    category: "Estructural",
    status: "implementado",
    module: "forecasting",
    reason:
      "Añade al reporte base el intervalo de confianza, la tendencia y el origen del dato, apilables.",
    source: "src/forecasting/domain/report_decorators.py",
    screen: { label: "Pronósticos", path: "/pronosticos" },
  },
  {
    name: "Facade",
    category: "Estructural",
    status: "implementado",
    module: "products",
    reason:
      "Una sola llamada reúne el historial de tracking y el pronóstico de un producto.",
    source: "src/products/application/product_overview_facade.py",
    screen: { label: "Productos", path: "/productos" },
  },
  {
    name: "Flyweight",
    category: "Estructural",
    status: "limitado",
    module: "logistics",
    reason:
      "Todas las rutas comparten el mismo objeto por tipo de vehículo. El ahorro es modesto: no hay millones de rutas.",
    source: "src/logistics/domain/vehicle_type.py",
    screen: { label: "Logística: Rutas", path: "/logistica" },
  },
  {
    name: "Proxy",
    category: "Estructural",
    status: "implementado",
    module: "forecasting",
    reason:
      "Valida la sesión antes de dejar pasar la petición al generador de reportes.",
    source: "src/forecasting/application/authorized_forecast_report_proxy.py",
    screen: { label: "Pronósticos", path: "/pronosticos" },
  },
  {
    name: "Chain of Responsibility",
    category: "Comportamiento",
    status: "implementado",
    module: "tracking",
    reason:
      "Cada eslabón revisa una regla del evento y lo pasa al siguiente; el primero que falla corta la cadena.",
    source: "src/tracking/domain/validation_chain.py",
    screen: { label: "Seguimiento", path: "/seguimiento" },
  },
  {
    name: "Command",
    category: "Comportamiento",
    status: "implementado",
    module: "forecasting",
    reason:
      "Generar y recalcular un pronóstico son objetos que se registran en una bitácora y se pueden deshacer.",
    source: "src/forecasting/application/forecast_commands.py",
    screen: { label: "Pronósticos", path: "/pronosticos" },
  },
  {
    name: "Iterator",
    category: "Comportamiento",
    status: "limitado",
    module: "logistics",
    reason:
      "Recorre todas las rutas de un corredor sin exponer su anidación. Python ya trae el protocolo; aquí se escribe la clase iteradora explícita.",
    source: "src/logistics/domain/route_corridor.py",
    screen: { label: "Logística: Corredores", path: "/logistica?vista=corredores" },
  },
  {
    name: "Memento",
    category: "Comportamiento",
    status: "implementado",
    module: "forecasting",
    reason:
      "Antes de recalcular se guarda una instantánea del pronóstico; deshacer la restaura.",
    source: "src/forecasting/domain/forecast_plan.py",
    screen: { label: "Pronósticos", path: "/pronosticos" },
  },
  {
    name: "Observer",
    category: "Comportamiento",
    status: "implementado",
    module: "iot",
    reason:
      "Cada lectura aceptada se publica a tres observadores: panel en vivo, alertas por umbral y estado de dispositivos.",
    source: "src/iot/domain/sensor_observer.py",
    screen: { label: "Monitoreo IoT", path: "/iot" },
  },
  {
    name: "State",
    category: "Comportamiento",
    status: "implementado",
    module: "logistics",
    reason:
      "El estado de la ruta decide qué acciones admite: una planificada se despacha, una entregada ya no cambia.",
    source: "src/logistics/domain/route_state.py",
    screen: { label: "Logística: Rutas", path: "/logistica" },
  },
  {
    name: "Strategy",
    category: "Comportamiento",
    status: "implementado",
    module: "logistics",
    reason:
      "El algoritmo que ordena las paradas se elige al crear la ruta: orden ingresado, vecino más cercano o 2-opt.",
    source: "src/logistics/domain/route_optimization.py",
    screen: { label: "Logística: Optimización", path: "/logistica?vista=optimizacion" },
  },
  {
    name: "Template Method",
    category: "Comportamiento",
    status: "implementado",
    module: "forecasting",
    reason:
      "Todo modelo de pronóstico sigue los mismos pasos; cada uno solo aporta su fórmula de estimación.",
    source: "src/forecasting/domain/forecast_models.py",
    screen: { label: "Pronósticos", path: "/pronosticos" },
  },
  {
    name: "Interpreter",
    category: "Comportamiento",
    status: "descartado",
    module: "—",
    reason:
      "El sistema no define ningún lenguaje ni gramática que evaluar: las reglas de validación y los umbrales son fijos, no expresiones escritas por el usuario.",
  },
  {
    name: "Mediator",
    category: "Comportamiento",
    status: "descartado",
    module: "—",
    reason:
      "No hay objetos pares que se hablen entre sí de muchos a muchos. La coordinación ya vive en los casos de uso y en la Facade, y los avisos, en el Observer.",
  },
  {
    name: "Visitor",
    category: "Comportamiento",
    status: "descartado",
    module: "—",
    reason:
      "La única jerarquía candidata (eventos) tiene dos subtipos y la Abstract Factory ya separa su comportamiento. El doble despacho añadiría más código del que ahorra.",
  },
] as const;

export const PATTERN_CATEGORIES: readonly PatternCategory[] = [
  "Creacional",
  "Estructural",
  "Comportamiento",
];
