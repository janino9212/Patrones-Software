import { Waypoints } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";

import { Button, EmptyState, Field, Notice, Panel } from "../../components/ui";
import { api } from "../../lib/api";
import { formatKm } from "../../lib/format";
import type { Corridor, Route } from "../../lib/types";
import { useAction } from "../../lib/useQuery";

type Placement = "none" | "main" | "sub";

const PLACEMENTS: readonly { id: Placement; label: string }[] = [
  { id: "none", label: "No incluir" },
  { id: "main", label: "Corredor" },
  { id: "sub", label: "Sub-corredor" },
];

interface CorridorsViewProps {
  routes: Route[];
}

export function CorridorsView({ routes }: CorridorsViewProps) {
  const [name, setName] = useState("");
  const [subName, setSubName] = useState("");
  const [placements, setPlacements] = useState<Record<number, Placement>>({});
  const [result, setResult] = useState<Corridor | null>(null);
  const action = useAction();

  const idsIn = (placement: Placement): number[] =>
    routes.filter((route) => placements[route.route_id] === placement).map((route) => route.route_id);
  const mainIds = idsIn("main");
  const subIds = idsIn("sub");
  const hasSub = subIds.length > 0;
  const canSubmit =
    name.trim() !== "" && mainIds.length + subIds.length > 0 && (!hasSub || subName.trim() !== "");

  const handleSubmit = (event: FormEvent): void => {
    event.preventDefault();
    void action.run(async () => {
      setResult(
        await api<Corridor>("/logistics/corridors", {
          method: "POST",
          body: {
            name: name.trim(),
            route_ids: mainIds,
            sub_corridors: hasSub ? [{ name: subName.trim(), route_ids: subIds }] : [],
          },
        }),
      );
    });
  };

  if (routes.length === 0) {
    return (
      <Panel title="Corredores" patterns={["Composite", "Iterator"]}>
        <EmptyState title="Primero necesitas rutas">
          Un corredor agrupa rutas ya creadas. Crea al menos dos en la pestaña Rutas y vuelve aquí.
        </EmptyState>
      </Panel>
    );
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
      <Panel title="Armar corredor" patterns={["Composite"]}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Nombre del corredor" htmlFor="corridor-name">
              <input
                id="corridor-name"
                className="control"
                maxLength={80}
                required
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </Field>
            <Field
              label="Nombre del sub-corredor"
              htmlFor="sub-corridor-name"
              hint="Solo si envías rutas al sub-corredor."
            >
              <input
                id="sub-corridor-name"
                className="control"
                maxLength={80}
                disabled={!hasSub}
                value={subName}
                onChange={(event) => setSubName(event.target.value)}
              />
            </Field>
          </div>

          <fieldset>
            <legend className="mb-1 text-[0.88rem] font-semibold">Dónde va cada ruta</legend>
            <ul className="divide-y divide-line rounded-control border border-line">
              {routes.map((route) => {
                const current = placements[route.route_id] ?? "none";
                return (
                  <li
                    key={route.route_id}
                    className="flex flex-wrap items-center gap-x-3 gap-y-1 px-3 py-2"
                  >
                    <span className="num font-bold">#{route.route_id}</span>
                    <span className="min-w-0 flex-1 truncate text-[0.92rem]">
                      {route.stops.map((stop) => stop.location).join(" → ")}
                    </span>
                    <span className="num text-[0.86rem] text-ink-soft">
                      {formatKm(route.total_distance_km)}
                    </span>
                    <label className="sr-only" htmlFor={`placement-${route.route_id}`}>
                      Ubicación de la ruta {route.route_id}
                    </label>
                    <select
                      id={`placement-${route.route_id}`}
                      className="control w-auto min-w-[9.5rem]"
                      value={current}
                      onChange={(event) =>
                        setPlacements({
                          ...placements,
                          [route.route_id]: event.target.value as Placement,
                        })
                      }
                    >
                      {PLACEMENTS.map((placement) => (
                        <option key={placement.id} value={placement.id}>
                          {placement.label}
                        </option>
                      ))}
                    </select>
                  </li>
                );
              })}
            </ul>
          </fieldset>

          {action.error && <Notice tone="error">{action.error}</Notice>}
          <Button
            type="submit"
            variant="primary"
            loading={action.pending}
            disabled={!canSubmit}
            icon={<Waypoints className="size-4" aria-hidden />}
          >
            Calcular corredor
          </Button>
        </form>
      </Panel>

      <Panel title="Resultado" patterns={["Iterator"]}>
        {result ? (
          <div className="space-y-3">
            <p>
              <span className="text-ink-soft">Corredor</span>{" "}
              <strong className="text-[1.1rem]">{result.name}</strong>
            </p>
            <p className="num text-[2rem] leading-none font-bold">
              {formatKm(result.total_distance_km)}
            </p>
            <p className="text-[0.86rem] text-ink-soft">
              Suma de {result.routes.length} ruta(s), incluidas las del sub-corredor, recorridas en
              profundidad:
            </p>
            <ol className="list-decimal space-y-1 pl-5">
              {result.routes.map((description, index) => (
                <li key={`${description}-${index}`}>{description}</li>
              ))}
            </ol>
          </div>
        ) : (
          <EmptyState title="Sin corredor calculado">
            Asigna rutas al corredor y, si quieres, a un sub-corredor. El total suma todas sin
            importar el nivel en el que estén.
          </EmptyState>
        )}
      </Panel>
    </div>
  );
}
