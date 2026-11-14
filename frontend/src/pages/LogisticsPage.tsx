import { useSearchParams } from "react-router";

import { PageHeader } from "../components/Shell";
import { QueryView, Tabs } from "../components/ui";
import { api } from "../lib/api";
import type { LocationItem, Route, VehicleType } from "../lib/types";
import { useQuery } from "../lib/useQuery";
import { CorridorsView } from "./logistics/CorridorsView";
import { OptimizationView } from "./logistics/OptimizationView";
import { RoutesView } from "./logistics/RoutesView";

const VIEWS = [
  { id: "rutas", label: "Rutas" },
  { id: "optimizacion", label: "Optimización" },
  { id: "corredores", label: "Corredores" },
] as const;
type ViewId = (typeof VIEWS)[number]["id"];

interface Catalogs {
  locations: LocationItem[];
  vehicles: VehicleType[];
}

export function LogisticsPage() {
  const [params, setParams] = useSearchParams();
  const requested = params.get("vista");
  const view: ViewId = VIEWS.some((item) => item.id === requested) ? (requested as ViewId) : "rutas";

  const routes = useQuery(() => api<Route[]>("/logistics/routes"), []);
  const catalogs = useQuery<Catalogs>(async () => {
    const [locations, vehicles] = await Promise.all([
      api<LocationItem[]>("/logistics/locations"),
      api<VehicleType[]>("/logistics/vehicle-types"),
    ]);
    return { locations, vehicles };
  }, []);

  return (
    <>
      <PageHeader title="Logística">
        Rutas de distribución entre ciudades: créalas, compara cómo ordenar sus paradas, síguelas
        hasta la entrega y agrúpalas en corredores.
      </PageHeader>

      <div className="mb-5">
        <Tabs
          label="Vistas de logística"
          tabs={VIEWS}
          current={view}
          onChange={(next) => setParams(next === "rutas" ? {} : { vista: next }, { replace: true })}
        />
      </div>

      <QueryView state={catalogs} skeletonRows={5}>
        {({ locations, vehicles }) => (
          <>
            {view === "rutas" && (
              <RoutesView routes={routes} locations={locations} vehicles={vehicles} />
            )}
            {view === "optimizacion" && <OptimizationView locations={locations} />}
            {view === "corredores" && (
              <QueryView state={routes}>{(list) => <CorridorsView routes={list} />}</QueryView>
            )}
          </>
        )}
      </QueryView>
    </>
  );
}
