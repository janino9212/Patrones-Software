import { Calculator, Plus, RefreshCw, Undo2 } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";

import { DemandChart } from "../components/DemandChart";
import { ProductSelect } from "../components/ProductSelect";
import { PageHeader } from "../components/Shell";
import { Badge, Button, EmptyState, Field, Notice, Panel, QueryView } from "../components/ui";
import { ApiError, api } from "../lib/api";
import { formatDateTime, formatNumber, labelFor, localMonth, monthToPeriod } from "../lib/format";
import type {
  CommandLogEntry,
  DemandRecord,
  ForecastModel,
  ForecastPlan,
  ForecastReport,
} from "../lib/types";
import { useProducts } from "../lib/useProducts";
import { useAction, useQuery } from "../lib/useQuery";

/** Un producto sin pronóstico responde 404: aquí eso es "todavía no hay". */
async function fetchPlan(productId: string): Promise<ForecastPlan | "none"> {
  try {
    return await api<ForecastPlan>(`/forecasting/plans/${encodeURIComponent(productId)}`);
  } catch (cause) {
    if (cause instanceof ApiError && cause.status === 404) return "none";
    throw cause;
  }
}

interface DemandFormProps {
  productId: string;
  onSaved: () => void;
}

function DemandForm({ productId, onSaved }: DemandFormProps) {
  const [month, setMonth] = useState(() => localMonth());
  const [quantity, setQuantity] = useState("");
  const action = useAction();

  const handleSubmit = (event: FormEvent): void => {
    event.preventDefault();
    void action.run(async () => {
      await api("/forecasting/demand", {
        method: "POST",
        body: { product_id: productId, period: monthToPeriod(month), quantity: Number(quantity) },
      });
      setQuantity("");
      onSaved();
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <Field label="Mes" htmlFor="demand-month">
          <input
            id="demand-month"
            type="month"
            className="control num"
            required
            value={month}
            onChange={(event) => setMonth(event.target.value)}
          />
        </Field>
        <Field label="Unidades vendidas" htmlFor="demand-quantity">
          <input
            id="demand-quantity"
            type="number"
            min="0"
            step="any"
            inputMode="decimal"
            className="control num"
            required
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
          />
        </Field>
      </div>
      {action.error && <Notice tone="error">{action.error}</Notice>}
      <Button
        type="submit"
        loading={action.pending}
        disabled={!month || quantity === ""}
        icon={<Plus className="size-4" aria-hidden />}
      >
        Guardar mes
      </Button>
      <p className="text-[0.82rem] text-ink-soft">
        Si el mes ya tiene una cifra, se corrige con la nueva.
      </p>
    </form>
  );
}

interface PlanControlsProps {
  productId: string;
  plan: ForecastPlan | null;
  models: ForecastModel[];
  onChanged: () => void;
}

function PlanControls({ productId, plan, models, onChanged }: PlanControlsProps) {
  const [model, setModel] = useState(models[0]?.name ?? "");
  const action = useAction();

  const run = (path: string, body: object): void => {
    void action.run(async () => {
      await api(path, { method: "POST", body });
      onChanged();
    });
  };
  const command = (name: "generate" | "recalculate"): void =>
    run("/forecasting/commands", { action: name, product_id: productId, model });

  return (
    <div className="space-y-4">
      {plan ? (
        <dl className="grid grid-cols-2 gap-x-6 gap-y-3">
          <div className="col-span-2">
            <dt className="text-[0.82rem] text-ink-soft">Demanda estimada para el próximo mes</dt>
            <dd className="num text-[2.2rem] leading-tight font-bold">
              {formatNumber(plan.predicted_demand)}
              <span className="ml-1.5 text-[0.95rem] font-normal text-ink-soft">unidades</span>
            </dd>
          </div>
          <div>
            <dt className="text-[0.82rem] text-ink-soft">Modelo</dt>
            <dd className="font-semibold">{labelFor(plan.model)}</dd>
          </div>
          <div>
            <dt className="text-[0.82rem] text-ink-soft">Calculado</dt>
            <dd className="num">
              {formatDateTime(plan.generated_at)}, con {plan.based_on_records} mes(es)
            </dd>
          </div>
        </dl>
      ) : (
        <EmptyState title="Este producto aún no tiene pronóstico">
          Carga uno o más meses de demanda, elige un modelo y pulsa Generar.
        </EmptyState>
      )}

      <Field
        label="Modelo de pronóstico"
        htmlFor="forecast-model"
        hint={`Necesita al menos ${models.find((item) => item.name === model)?.min_points ?? 1} mes(es) de demanda.`}
      >
        <select
          id="forecast-model"
          className="control"
          value={model}
          onChange={(event) => setModel(event.target.value)}
        >
          {models.map((item) => (
            <option key={item.name} value={item.name}>
              {item.label}
            </option>
          ))}
        </select>
      </Field>

      {action.error && <Notice tone="error">{action.error}</Notice>}

      <div className="flex flex-wrap gap-2">
        {plan ? (
          <Button
            variant="primary"
            loading={action.pending}
            onClick={() => command("recalculate")}
            icon={<RefreshCw className="size-4" aria-hidden />}
          >
            Recalcular
          </Button>
        ) : (
          <Button
            variant="primary"
            loading={action.pending}
            onClick={() => command("generate")}
            icon={<Calculator className="size-4" aria-hidden />}
          >
            Generar
          </Button>
        )}
        <Button
          disabled={!plan?.can_undo || action.pending}
          onClick={() => run("/forecasting/commands/undo", { product_id: productId })}
          icon={<Undo2 className="size-4" aria-hidden />}
        >
          Deshacer
        </Button>
      </div>
      {plan && !plan.can_undo && (
        <p className="text-[0.82rem] text-ink-soft">
          No hay operaciones por deshacer: la bitácora se reinició con la API.
        </p>
      )}
    </div>
  );
}

function CommandLog({ entries }: { entries: CommandLogEntry[] }) {
  if (entries.length === 0) {
    return (
      <div className="p-5">
        <EmptyState title="Bitácora vacía">
          Cada vez que generes, recalcules o deshagas un pronóstico quedará anotado aquí.
        </EmptyState>
      </div>
    );
  }
  return (
    <ul className="divide-y divide-line">
      {entries.slice(0, 10).map((entry, index) => (
        <li
          key={`${entry.executed_at}-${index}`}
          className="flex flex-wrap items-center gap-x-3 gap-y-1 px-5 py-2.5"
        >
          <Badge tone={entry.undone ? "caution" : "go"}>
            {entry.undone ? `Deshecho: ${labelFor(entry.command)}` : labelFor(entry.command)}
          </Badge>
          <span className="num font-semibold">{entry.product_id}</span>
          <time dateTime={entry.executed_at} className="num ml-auto text-[0.82rem] text-ink-soft">
            {formatDateTime(entry.executed_at)}
          </time>
        </li>
      ))}
    </ul>
  );
}

export function ForecastingPage() {
  const { products, selected, select } = useProducts();
  const enabled = Boolean(selected);
  const path = encodeURIComponent(selected);

  const models = useQuery(() => api<ForecastModel[]>("/forecasting/models"), []);
  const demand = useQuery(() => api<DemandRecord[]>(`/forecasting/demand/${path}`), [selected], {
    enabled,
  });
  const plan = useQuery(() => fetchPlan(selected), [selected], { enabled });
  const report = useQuery(() => api<ForecastReport>(`/forecasting/reports/${path}`), [selected], {
    enabled,
  });
  const log = useQuery(() => api<CommandLogEntry[]>("/forecasting/commands"), []);

  const refreshPlan = (): void => {
    plan.reload();
    report.reload();
    log.reload();
  };
  const currentPlan = plan.data && plan.data !== "none" ? plan.data : null;
  const forecastPoint =
    currentPlan && report.data
      ? {
          value: report.data.predicted_demand,
          low: report.data.confidence_interval[0],
          high: report.data.confidence_interval[1],
        }
      : null;

  return (
    <>
      <PageHeader title="Pronósticos">
        Carga la demanda real de cada mes y estima la del siguiente con el modelo que elijas.
      </PageHeader>

      <div className="mb-5 max-w-md">
        <QueryView state={products} skeletonRows={1}>
          {(list) => (
            <ProductSelect id="forecast-product" products={list} value={selected} onChange={select} />
          )}
        </QueryView>
      </div>

      {enabled && (
        <div className="grid gap-5 xl:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
          <div className="space-y-5">
            <Panel title="Demanda y pronóstico" patterns={["Decorator", "Proxy"]}>
              <QueryView state={demand} skeletonRows={4}>
                {(records) =>
                  records.length === 0 ? (
                    <EmptyState title="Sin historial de demanda">
                      Registra las unidades vendidas de al menos un mes en el formulario de abajo.
                      Con dos o más meses también podrás usar la tendencia lineal.
                    </EmptyState>
                  ) : (
                    <>
                      <DemandChart records={records} forecast={forecastPoint} />
                      {forecastPoint && (
                        <p className="mt-2 text-[0.86rem] text-ink-soft">
                          La barra amarilla es el pronóstico; la línea vertical, su intervalo de
                          confianza de ±10 % (de{" "}
                          <span className="num">{formatNumber(forecastPoint.low)}</span> a{" "}
                          <span className="num">{formatNumber(forecastPoint.high)}</span>).
                        </p>
                      )}
                    </>
                  )
                }
              </QueryView>
              <div className="mt-5 border-t border-line pt-4">
                <h3 className="mb-2 font-bold">Registrar demanda de un mes</h3>
                <DemandForm key={selected} productId={selected} onSaved={demand.reload} />
              </div>
            </Panel>
          </div>

          <div className="space-y-5">
            <Panel title="Pronóstico vigente" patterns={["Template Method", "Command", "Memento"]}>
              <QueryView state={models} skeletonRows={3}>
                {(modelList) => (
                  <QueryView state={plan} skeletonRows={3}>
                    {() => (
                      <PlanControls
                        key={selected}
                        productId={selected}
                        plan={currentPlan}
                        models={modelList}
                        onChanged={refreshPlan}
                      />
                    )}
                  </QueryView>
                )}
              </QueryView>
            </Panel>

            <Panel title="Bitácora de operaciones" patterns={["Command"]} flush>
              <QueryView state={log} skeletonRows={3}>
                {(entries) => <CommandLog entries={entries} />}
              </QueryView>
            </Panel>
          </div>
        </div>
      )}
    </>
  );
}
