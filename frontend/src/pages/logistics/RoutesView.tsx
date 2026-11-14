import { Ban, PackageCheck, Plus, Snowflake, Truck } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";

import { StopsEditor } from "../../components/StopsEditor";
import { StripMap } from "../../components/StripMap";
import type { StopState } from "../../components/StripMap";
import { Badge, Button, EmptyState, Field, Notice, Panel, QueryView } from "../../components/ui";
import { api } from "../../lib/api";
import { formatDay, formatKm, labelFor, localToday } from "../../lib/format";
import type {
  LocationItem,
  Route,
  RouteAction,
  RouteStatus,
  VehicleType,
} from "../../lib/types";
import { useAction } from "../../lib/useQuery";
import type { QueryState } from "../../lib/useQuery";

const ROUTE_TYPES = [
  { code: "standard", label: "Estándar", hint: "Camión estándar, definido por el Director." },
  { code: "express", label: "Express", hint: "Moto express con prioridad alta." },
  { code: "custom", label: "Personalizada", hint: "Tú eliges el vehículo." },
] as const;
type RouteType = (typeof ROUTE_TYPES)[number]["code"];

const OPTIMIZATIONS = ["none", "nearest_neighbor", "two_opt"] as const;

const STATUS_TONE: Record<RouteStatus, "idle" | "info" | "go" | "stop"> = {
  planned: "idle",
  in_transit: "info",
  delivered: "go",
  cancelled: "stop",
};

const STOP_STATE: Record<RouteStatus, StopState> = {
  planned: "pending",
  in_transit: "done",
  delivered: "done",
  cancelled: "halted",
};

const ACTIONS: Record<
  RouteAction,
  { label: string; icon: LucideIcon; variant: "primary" | "secondary" | "danger" }
> = {
  dispatch: { label: "Despachar", icon: Truck, variant: "primary" },
  deliver: { label: "Marcar entregada", icon: PackageCheck, variant: "primary" },
  cancel: { label: "Cancelar", icon: Ban, variant: "danger" },
};

interface CreateRouteFormProps {
  locations: LocationItem[];
  vehicles: VehicleType[];
  onCreated: () => void;
}

function CreateRouteForm({ locations, vehicles, onCreated }: CreateRouteFormProps) {
  const [routeType, setRouteType] = useState<RouteType>("standard");
  const [stops, setStops] = useState<string[]>([]);
  const [departure, setDeparture] = useState(() => localToday());
  const [vehicle, setVehicle] = useState(vehicles[0]?.code ?? "");
  const [optimization, setOptimization] = useState<string>("nearest_neighbor");
  const action = useAction();

  const handleSubmit = (event: FormEvent): void => {
    event.preventDefault();
    void action.run(async () => {
      await api("/logistics/routes", {
        method: "POST",
        body: {
          route_type: routeType,
          stops,
          departure_date: departure,
          vehicle_type: routeType === "custom" ? vehicle : null,
          optimization,
        },
      });
      setStops([]);
      onCreated();
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <fieldset>
        <legend className="mb-1 text-[0.88rem] font-semibold">Tipo de ruta</legend>
        <div className="flex flex-wrap gap-2">
          {ROUTE_TYPES.map((type) => {
            const checked = routeType === type.code;
            return (
              <label
                key={type.code}
                className={`cursor-pointer rounded-control border px-3.5 py-2 font-semibold transition-colors duration-150 has-[:focus-visible]:outline-[3px] has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-info ${
                  checked
                    ? "border-ink bg-signal-soft"
                    : "border-line-strong bg-surface hover:border-ink-soft"
                }`}
              >
                <input
                  type="radio"
                  name="route-type"
                  className="sr-only"
                  checked={checked}
                  onChange={() => setRouteType(type.code)}
                />
                {type.label}
              </label>
            );
          })}
        </div>
        <p className="mt-1 text-[0.82rem] text-ink-soft">
          {ROUTE_TYPES.find((type) => type.code === routeType)?.hint}
        </p>
      </fieldset>

      {routeType === "custom" && (
        <Field label="Vehículo" htmlFor="vehicle">
          <select
            id="vehicle"
            className="control"
            value={vehicle}
            onChange={(event) => setVehicle(event.target.value)}
          >
            {vehicles.map((item) => (
              <option key={item.code} value={item.code}>
                {labelFor(item.code)}
                {item.refrigerated ? " (refrigerado)" : ""}
              </option>
            ))}
          </select>
        </Field>
      )}

      <StopsEditor id="route-stop" locations={locations} stops={stops} onChange={setStops} />

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Fecha de salida" htmlFor="departure">
          <input
            id="departure"
            type="date"
            className="control num"
            required
            value={departure}
            onChange={(event) => setDeparture(event.target.value)}
          />
        </Field>
        <Field label="Orden de las paradas" htmlFor="optimization">
          <select
            id="optimization"
            className="control"
            value={optimization}
            onChange={(event) => setOptimization(event.target.value)}
          >
            {OPTIMIZATIONS.map((name) => (
              <option key={name} value={name}>
                {labelFor(name)}
              </option>
            ))}
          </select>
        </Field>
      </div>

      {action.error && <Notice tone="error">{action.error}</Notice>}
      <Button
        type="submit"
        variant="primary"
        loading={action.pending}
        disabled={stops.length < 2 || !departure}
        icon={<Plus className="size-4" aria-hidden />}
      >
        Crear ruta
      </Button>
    </form>
  );
}

interface RouteRowProps {
  route: Route;
  onChanged: () => void;
}

function RouteRow({ route, onChanged }: RouteRowProps) {
  const action = useAction();

  const transition = (name: RouteAction): void => {
    void action.run(async () => {
      await api(`/logistics/routes/${route.route_id}/transition`, {
        method: "POST",
        body: { action: name },
      });
      onChanged();
    });
  };

  return (
    <li className="px-5 py-4">
      <div className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1.5">
        <h3 className="num text-[1.05rem] font-bold">Ruta #{route.route_id}</h3>
        <Badge tone={STATUS_TONE[route.status]}>{labelFor(route.status_label)}</Badge>
        <span className="inline-flex items-center gap-1 text-ink-soft">
          {route.refrigerated && (
            <Snowflake className="size-4 text-info" role="img" aria-label="Refrigerado" />
          )}
          {labelFor(route.vehicle_type)}
        </span>
        <span className="num text-ink-soft">{formatKm(route.total_distance_km)}</span>
        <span className="num ml-auto text-[0.86rem] text-ink-soft">
          Sale el {formatDay(route.departure_date)}
        </span>
      </div>

      <StripMap
        numbered
        label={`Paradas de la ruta ${route.route_id}`}
        stops={route.stops.map((stop) => ({
          label: stop.location,
          state: STOP_STATE[route.status],
        }))}
      />
      {route.notes && <p className="mt-1 text-[0.86rem] text-ink-soft">{route.notes}</p>}

      {route.allowed_actions.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {route.allowed_actions.map((name) => {
            const { label, icon: Icon, variant } = ACTIONS[name];
            return (
              <Button
                key={name}
                size="sm"
                variant={variant}
                disabled={action.pending}
                onClick={() => transition(name)}
                icon={<Icon className="size-4" aria-hidden />}
              >
                {label}
              </Button>
            );
          })}
        </div>
      )}
      {action.error && (
        <div className="mt-2">
          <Notice tone="error">{action.error}</Notice>
        </div>
      )}
    </li>
  );
}

interface RoutesViewProps {
  routes: QueryState<Route[]>;
  locations: LocationItem[];
  vehicles: VehicleType[];
}

export function RoutesView({ routes, locations, vehicles }: RoutesViewProps) {
  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
      <Panel title="Nueva ruta" patterns={["Builder", "Strategy", "Flyweight"]}>
        <CreateRouteForm locations={locations} vehicles={vehicles} onCreated={routes.reload} />
      </Panel>

      <Panel title="Rutas" patterns={["State"]} flush>
        <QueryView state={routes} skeletonRows={4}>
          {(list) =>
            list.length === 0 ? (
              <div className="p-5">
                <EmptyState title="Aún no hay rutas">
                  Crea la primera con el formulario. Empezará como planificada; desde aquí podrás
                  despacharla, entregarla o cancelarla.
                </EmptyState>
              </div>
            ) : (
              <ul className="divide-y divide-line">
                {[...list].reverse().map((route) => (
                  <RouteRow key={route.route_id} route={route} onChanged={routes.reload} />
                ))}
              </ul>
            )
          }
        </QueryView>
      </Panel>
    </div>
  );
}
