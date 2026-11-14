import { ArrowRight } from "lucide-react";
import { Link } from "react-router";

import { EventList } from "../components/EventList";
import { PageHeader } from "../components/Shell";
import { StripMap } from "../components/StripMap";
import { Badge, EmptyState, Panel, QueryView } from "../components/ui";
import { api } from "../lib/api";
import { formatKm, formatTime, labelFor } from "../lib/format";
import type { Alert, Product, Route, TrackingEvent } from "../lib/types";
import { useQuery } from "../lib/useQuery";

const POLL_MS = 8_000;

interface CountProps {
  value: number | null;
  label: string;
  to: string;
  tone?: "stop";
}

function Count({ value, label, to, tone }: CountProps) {
  return (
    <Link
      to={to}
      className="group flex flex-1 basis-40 items-baseline gap-2.5 px-5 py-3.5 no-underline transition-colors duration-150 hover:bg-sunken"
    >
      <span
        className={`num text-[1.9rem] leading-none font-bold ${
          tone === "stop" && value ? "text-stop" : "text-ink"
        }`}
      >
        {value ?? "–"}
      </span>
      <span className="text-[0.92rem] leading-tight text-ink-soft group-hover:text-ink">{label}</span>
    </Link>
  );
}

export function DashboardPage() {
  const products = useQuery(() => api<Product[]>("/products"), []);
  const routes = useQuery(() => api<Route[]>("/logistics/routes"), [], { pollMs: POLL_MS });
  const events = useQuery(() => api<TrackingEvent[]>("/tracking/events?limit=8"), [], {
    pollMs: POLL_MS,
  });
  const alerts = useQuery(() => api<Alert[]>("/iot/alerts"), [], { pollMs: POLL_MS });

  const inTransit = routes.data?.filter((route) => route.status === "in_transit") ?? null;
  const planned = routes.data?.filter((route) => route.status === "planned").length ?? null;

  return (
    <>
      <PageHeader title="Panel">
        Estado de la operación en este momento. Se actualiza solo cada pocos segundos.
      </PageHeader>

      <div className="mb-5 flex flex-wrap divide-x divide-line overflow-hidden rounded-panel border border-line bg-surface">
        <Count value={products.data?.length ?? null} label="productos en catálogo" to="/productos" />
        <Count value={planned} label="rutas por despachar" to="/logistica" />
        <Count value={inTransit?.length ?? null} label="rutas en tránsito" to="/logistica" />
        <Count value={alerts.data?.length ?? null} label="alertas de sensores" to="/iot" tone="stop" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <div className="space-y-5">
          <Panel title="Rutas en tránsito" patterns={["State"]} flush>
            <div className="p-5">
              <QueryView state={routes} skeletonRows={2}>
                {() =>
                  inTransit && inTransit.length > 0 ? (
                    <ul className="space-y-4">
                      {inTransit.map((route) => (
                        <li key={route.route_id}>
                          <p className="mb-1 flex flex-wrap items-center gap-x-3 gap-y-1">
                            <span className="num font-bold">Ruta #{route.route_id}</span>
                            <span className="text-ink-soft">{labelFor(route.vehicle_type)}</span>
                            <span className="num text-ink-soft">
                              {formatKm(route.total_distance_km)}
                            </span>
                          </p>
                          <StripMap
                            numbered
                            label={`Paradas de la ruta ${route.route_id}`}
                            stops={route.stops.map((stop) => ({ label: stop.location }))}
                          />
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <EmptyState
                      title="Ninguna ruta va en camino"
                      action={
                        <Link to="/logistica" className="font-semibold text-info">
                          Ir a Logística <ArrowRight className="inline size-4" aria-hidden />
                        </Link>
                      }
                    >
                      Crea una ruta y despáchala para verla aquí con sus paradas.
                    </EmptyState>
                  )
                }
              </QueryView>
            </div>
          </Panel>

          <Panel title="Últimos eventos de seguimiento" flush>
            <QueryView state={events} skeletonRows={4}>
              {(list) =>
                list.length > 0 ? (
                  <EventList events={list} showProduct />
                ) : (
                  <div className="p-5">
                    <EmptyState title="Todavía no hay eventos">
                      Los cambios de etapa y las lecturas de sensores aparecerán aquí a medida que se
                      registren en Seguimiento o en Monitoreo IoT.
                    </EmptyState>
                  </div>
                )
              }
            </QueryView>
          </Panel>
        </div>

        <Panel title="Alertas de sensores" patterns={["Observer"]} flush>
          <QueryView state={alerts} skeletonRows={3}>
            {(list) =>
              list.length > 0 ? (
                <ul className="divide-y divide-line">
                  {list.slice(0, 8).map((alert, index) => (
                    <li key={`${alert.raised_at}-${index}`} className="px-5 py-3">
                      <p className="flex flex-wrap items-center gap-2">
                        <Badge tone="stop">
                          <span className="num">
                            {alert.value} {alert.unit}
                          </span>
                        </Badge>
                        <span className="num font-semibold">{alert.device_id}</span>
                        <time
                          dateTime={alert.raised_at}
                          className="num ml-auto text-[0.82rem] text-ink-soft"
                        >
                          {formatTime(alert.raised_at)}
                        </time>
                      </p>
                      <p className="mt-1 text-[0.92rem]">{alert.message}</p>
                      <p className="num text-[0.82rem] text-ink-soft">{alert.product_id}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="p-5">
                  <EmptyState title="Sin alertas">
                    Todas las lecturas recibidas están dentro del rango seguro. Las alertas se
                    reinician cuando se reinicia la API.
                  </EmptyState>
                </div>
              )
            }
          </QueryView>
        </Panel>
      </div>
    </>
  );
}
