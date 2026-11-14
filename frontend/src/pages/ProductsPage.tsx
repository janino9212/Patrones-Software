import { Plus } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";

import { PageHeader } from "../components/Shell";
import { StripMap } from "../components/StripMap";
import { Button, EmptyState, Field, Notice, Panel, QueryView } from "../components/ui";
import { api } from "../lib/api";
import { formatDateTime, formatNumber, labelFor } from "../lib/format";
import { stageLabel, stageStops } from "../lib/stages";
import type { Product, ProductOverview } from "../lib/types";
import { useProducts } from "../lib/useProducts";
import { useAction, useQuery } from "../lib/useQuery";

interface CreateFormProps {
  onCreated: (product: Product) => void;
}

function CreateProductForm({ onCreated }: CreateFormProps) {
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");
  const action = useAction();

  const handleSubmit = (event: FormEvent): void => {
    event.preventDefault();
    void action.run(async () => {
      const product = await api<Product>("/products", {
        method: "POST",
        body: { code: code.trim(), name: name.trim(), category: category.trim() || null },
      });
      setCode("");
      setName("");
      setCategory("");
      onCreated(product);
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Field label="Código" htmlFor="product-code" hint="Sin espacios. Ejemplo: PROD-001">
        <input
          id="product-code"
          className="control num"
          required
          maxLength={100}
          pattern="\S+"
          value={code}
          onChange={(event) => setCode(event.target.value)}
        />
      </Field>
      <Field label="Nombre" htmlFor="product-name">
        <input
          id="product-name"
          className="control"
          required
          maxLength={120}
          value={name}
          onChange={(event) => setName(event.target.value)}
        />
      </Field>
      <Field label="Categoría (opcional)" htmlFor="product-category">
        <input
          id="product-category"
          className="control"
          maxLength={60}
          value={category}
          onChange={(event) => setCategory(event.target.value)}
        />
      </Field>
      {action.error && <Notice tone="error">{action.error}</Notice>}
      <Button
        type="submit"
        variant="primary"
        loading={action.pending}
        disabled={!code.trim() || !name.trim()}
        icon={<Plus className="size-4" aria-hidden />}
      >
        Agregar producto
      </Button>
    </form>
  );
}

function OverviewPanel({ productId }: { productId: string }) {
  const overview = useQuery(
    () => api<ProductOverview>(`/products/${encodeURIComponent(productId)}/overview`),
    [productId],
  );

  return (
    <Panel title={`Resumen de ${productId}`} patterns={["Facade", "Proxy", "Decorator"]}>
      <QueryView state={overview} skeletonRows={4}>
        {(data) => (
          <div className="space-y-5">
            <div>
              <h3 className="mb-1 text-[0.88rem] font-semibold text-ink-soft">
                Etapa actual:{" "}
                <span className="text-ink">
                  {data.current_stage ? stageLabel(data.current_stage) : "sin eventos"}
                </span>
              </h3>
              <StripMap label="Etapas del producto" stops={stageStops(data.current_stage)} />
            </div>
            <dl className="grid gap-x-6 gap-y-3 sm:grid-cols-3">
              <div>
                <dt className="text-[0.82rem] text-ink-soft">Eventos registrados</dt>
                <dd className="num text-[1.3rem] font-bold">{data.events_count}</dd>
              </div>
              <div>
                <dt className="text-[0.82rem] text-ink-soft">Último evento</dt>
                <dd className="num font-semibold">
                  {data.last_event_at ? formatDateTime(data.last_event_at) : "—"}
                </dd>
              </div>
              <div>
                <dt className="text-[0.82rem] text-ink-soft">Demanda estimada</dt>
                <dd className="num text-[1.3rem] font-bold">
                  {formatNumber(data.forecast.predicted_demand)}
                  <span className="ml-1 text-[0.82rem] font-normal text-ink-soft">
                    ({formatNumber(data.forecast.confidence_interval[0])} a{" "}
                    {formatNumber(data.forecast.confidence_interval[1])})
                  </span>
                </dd>
                <dd className="text-[0.82rem] text-ink-soft">{labelFor(data.forecast.source)}</dd>
              </div>
            </dl>
          </div>
        )}
      </QueryView>
    </Panel>
  );
}

export function ProductsPage() {
  const { products, selected, select } = useProducts();

  return (
    <>
      <PageHeader title="Productos">
        Catálogo de productos. El código es el que usan Seguimiento, Pronósticos y Monitoreo IoT.
      </PageHeader>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
        <div className="space-y-5">
          <Panel title="Nuevo producto">
            <CreateProductForm
              onCreated={(product) => {
                products.reload();
                select(product.code);
              }}
            />
          </Panel>

          <Panel title="Catálogo" flush>
            <QueryView state={products}>
              {(list) =>
                list.length === 0 ? (
                  <div className="p-5">
                    <EmptyState title="El catálogo está vacío">
                      Agrega el primer producto con el formulario de arriba. Después podrás
                      registrarle eventos, demanda y lecturas de sensores.
                    </EmptyState>
                  </div>
                ) : (
                  <ul className="divide-y divide-line">
                    {list.map((product) => {
                      const isSelected = product.code === selected;
                      return (
                        <li key={product.code}>
                          <button
                            type="button"
                            onClick={() => select(product.code)}
                            aria-pressed={isSelected}
                            className={`flex w-full flex-wrap items-baseline gap-x-3 px-5 py-2.5 text-left transition-colors duration-150 ${
                              isSelected ? "bg-signal-soft" : "hover:bg-sunken"
                            }`}
                          >
                            <span className="num font-bold">{product.code}</span>
                            <span>{product.name}</span>
                            {product.category && (
                              <span className="ml-auto text-[0.82rem] text-ink-soft">
                                {product.category}
                              </span>
                            )}
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                )
              }
            </QueryView>
          </Panel>
        </div>

        {selected ? (
          <OverviewPanel productId={selected} />
        ) : (
          <Panel title="Resumen del producto" patterns={["Facade", "Proxy", "Decorator"]}>
            <EmptyState title="Elige un producto">
              Al seleccionar uno del catálogo verás aquí su etapa actual, sus eventos y su demanda
              estimada, reunidos en una sola consulta.
            </EmptyState>
          </Panel>
        )}
      </div>
    </>
  );
}
