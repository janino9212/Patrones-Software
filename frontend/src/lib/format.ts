const dateTime = new Intl.DateTimeFormat("es-CO", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});
const timeOnly = new Intl.DateTimeFormat("es-CO", {
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
});
const dayOnly = new Intl.DateTimeFormat("es-CO", {
  day: "2-digit",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});
const monthOnly = new Intl.DateTimeFormat("es-CO", {
  month: "short",
  year: "2-digit",
  timeZone: "UTC",
});
const number = new Intl.NumberFormat("es-CO", { maximumFractionDigits: 1 });

export const formatDateTime = (iso: string): string => dateTime.format(new Date(iso));
export const formatTime = (iso: string): string => timeOnly.format(new Date(iso));
/** Para fechas sin hora (YYYY-MM-DD): se leen en UTC para no correr el día. */
export const formatDay = (isoDate: string): string => dayOnly.format(new Date(isoDate));
export const formatMonth = (isoDate: string): string => monthOnly.format(new Date(isoDate));
export const formatNumber = (value: number): string => number.format(value);

export function formatKm(value: number | null): string {
  return value === null ? "Sin distancia" : `${formatNumber(value)} km`;
}

/** "furgon_refrigerado" -> "Furgón refrigerado" para los códigos conocidos. */
const LABELS: Record<string, string> = {
  camion_estandar: "Camión estándar",
  moto_express: "Moto express",
  furgon_refrigerado: "Furgón refrigerado",
  moving_average: "Promedio móvil",
  exponential_smoothing: "Suavizado exponencial",
  linear_trend: "Tendencia lineal",
  eventos_tracking: "Estimación por eventos",
  none: "Orden ingresado",
  nearest_neighbor: "Vecino más cercano",
  two_opt: "2-opt",
  generate: "Generar",
  recalculate: "Recalcular",
  sensor: "Sensor",
  stage_change: "Cambio de etapa",
  mqtt: "MQTT",
  webhook: "Webhook",
};

export function labelFor(code: string): string {
  if (LABELS[code]) return LABELS[code];
  const text = code.replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

const pad = (value: number): string => String(value).padStart(2, "0");

/** Hoy como YYYY-MM-DD en la hora local (toISOString usa UTC y, de noche
 *  en Colombia, ya devuelve el día siguiente). */
export function localToday(now: Date = new Date()): string {
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

/** Mes actual como YYYY-MM en la hora local. */
export function localMonth(now: Date = new Date()): string {
  return localToday(now).slice(0, 7);
}

/** Primer día del mes de un valor de <input type="month"> (YYYY-MM). */
export function monthToPeriod(month: string): string {
  return `${month}-01`;
}
