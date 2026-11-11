import { Scale } from "lucide-react";
import { useRef, useState } from "react";

import { StopsEditor } from "../../components/StopsEditor";
import { StripMap } from "../../components/StripMap";
import { Badge, Button, EmptyState, Notice, Panel } from "../../components/ui";
import { api } from "../../lib/api";
import { formatKm, formatNumber, labelFor } from "../../lib/format";
import type { LocationItem, StrategyResult } from "../../lib/types";
import { useAction } from "../../lib/useQuery";

interface OptimizationViewProps {
  locations: LocationItem[];
}

export function OptimizationView({ locations }: OptimizationViewProps) {
  const [stops, setStops] = useState<string[]>([]);
  const [results, setResults] = useState<StrategyResult[] | null>(null);
  const action = useAction();
  // Cambia cada vez que se editan las paradas: una respuesta pedida con
  // las paradas anteriores se descarta.
  const edition = useRef(0);

  const compare = (): void => {
    const requestedFor = edition.current;
    void action.run(async () => {
      const response = await api<StrategyResult[]>("/logistics/optimizations/compare", {
        method: "POST",
        body: { stops },
      });
      if (requestedFor === edition.current) setResults(response);
    });
  };

  const longest = results ? Math.max(...results.map((item) => item.total_distance_km)) : 0;
  const shortest = results ? Math.min(...results.map((item) => item.total_distance_km)) : 0;

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
      <Panel title="Paradas a comparar">
        <div className="space-y-4">
          <StopsEditor
            id="compare-stop"
            locations={locations}
            stops={stops}
            onChange={(next) => {
              edition.current += 1;
              setStops(next);
              setResults(null);
            }}
          />
          {action.error && <Notice tone="error">{action.error}</Notice>}
          <Button
            variant="primary"
            loading={action.pending}
            disabled={stops.length < 2}
            onClick={compare}
            icon={<Scale className="size-4" aria-hidden />}
          >
            Comparar estrategias
          </Button>
          <p className="text-[0.82rem] text-ink-soft">
            No guarda nada: aplica cada algoritmo a las mismas paradas. Las distancias son en línea
            recta entre ciudades.
          </p>
        </div>
      </Panel>

      <Panel title="Resultado por estrategia" patterns={["Strategy"]} flush>
        {!results ? (
          <div className="p-5">
            <EmptyState title="Sin comparación todavía">
              Agrega al menos tres paradas en desorden (por ejemplo Bucaramanga, Bogotá, Girón y
              Tunja) y compara: verás cómo cada estrategia las reordena y cuántos kilómetros ahorra.
            </EmptyState>
          </div>
        ) : (
          <ul className="divide-y divide-line">
            {results.map((result) => {
              const saved = longest - result.total_distance_km;
              const isBest = result.total_distance_km === shortest;
              return (
                <li key={result.strategy} className="px-5 py-4">
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                    <h3 className="text-[1.05rem] font-bold">{labelFor(result.strategy)}</h3>
                    {isBest && <Badge tone="go">Más corta</Badge>}
                    <span className="num ml-auto text-[1.15rem] font-bold">
                      {formatKm(result.total_distance_km)}
                    </span>
                  </div>
                  <p className="text-[0.86rem] text-ink-soft">
                    {result.description}
                    {saved > 0 && (
                      <span className="num font-semibold text-go">
                        {" "}
                        Ahorra {formatNumber(saved)} km.
                      </span>
                    )}
                  </p>
                  <div
                    className="my-2 h-2 rounded-full bg-sunken"
                    role="img"
                    aria-label={`${formatKm(result.total_distance_km)} de ${formatKm(longest)}`}
                  >
                    <div
                      className={`h-full origin-left rounded-full transition-transform duration-300 ease-out ${
                        isBest ? "bg-go" : "bg-line-strong"
                      }`}
                      style={{
                        transform: `scaleX(${longest ? result.total_distance_km / longest : 0})`,
                      }}
                    />
                  </div>
                  <StripMap
                    numbered
                    label={`Orden según ${labelFor(result.strategy)}`}
                    stops={result.stops.map((name) => ({ label: name }))}
                  />
                </li>
              );
            })}
          </ul>
        )}
      </Panel>
    </div>
  );
}
