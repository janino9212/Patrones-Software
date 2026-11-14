import { RadioTower } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";

import { ProductSelect } from "../components/ProductSelect";
import { PageHeader } from "../components/Shell";
import { Badge, Button, EmptyState, Field, Notice, Panel, QueryView } from "../components/ui";
import { api } from "../lib/api";
import { formatTime, labelFor } from "../lib/format";
import { STAGES, stageLabel } from "../lib/stages";
import type { Alert, Device, IngestResult, Reading, Vendor } from "../lib/types";
import { useProducts } from "../lib/useProducts";
import { useAction, useQuery } from "../lib/useQuery";

const POLL_MS = 4_000;

interface IngestFormProps {
  vendors: Vendor[];
  productId: string;
  onIngested: () => void;
}

function IngestForm({ vendors, productId, onIngested }: IngestFormProps) {
  const [vendorCode, setVendorCode] = useState(vendors[0]?.code ?? "");
  const [stage, setStage] = useState("transporte");
  const [value, setValue] = useState("");
  const [result, setResult] = useState<IngestResult | null>(null);
  const action = useAction();
  const vendor = vendors.find((item) => item.code === vendorCode);

  const handleSubmit = (event: FormEvent): void => {
    event.preventDefault();
    setResult(null);
    void action.run(async () => {
      const response = await api<IngestResult>(
        `/iot/sensors/${encodeURIComponent(vendorCode)}/ingest`,
        {
          method: "POST",
          body: {
            product_id: productId,
            stage,
            simulated_value:
              vendor?.accepts_simulated_value && value !== "" ? Number(value) : null,
          },
        },
      );
      setResult(response);
      onIngested();
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Field
        label="Dispositivo"
        htmlFor="vendor"
        hint="Cada fabricante entrega sus datos en un formato distinto."
      >
        <select
          id="vendor"
          className="control"
          value={vendorCode}
          onChange={(event) => {
            setVendorCode(event.target.value);
            setValue("");
          }}
        >
          {vendors.map((item) => (
            <option key={item.code} value={item.code}>
              {item.label}
            </option>
          ))}
        </select>
      </Field>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Etapa" htmlFor="iot-stage">
          <select
            id="iot-stage"
            className="control"
            value={stage}
            onChange={(event) => setStage(event.target.value)}
          >
            {STAGES.map((item) => (
              <option key={item.code} value={item.code}>
                {item.label}
              </option>
            ))}
          </select>
        </Field>
        <Field
          label={`Lectura simulada (${vendor?.unit ?? ""})`}
          htmlFor="simulated"
          hint={
            vendor?.accepts_simulated_value
              ? "Vacío usa el valor fijo del dispositivo."
              : "Este sensor siempre reporta −60 °C."
          }
        >
          <input
            id="simulated"
            type="number"
            step="any"
            min="-1000"
            max="1000"
            inputMode="decimal"
            className="control num"
            disabled={!vendor?.accepts_simulated_value}
            value={value}
            onChange={(event) => setValue(event.target.value)}
          />
        </Field>
      </div>

      {action.error && <Notice tone="error">{action.error}</Notice>}
      {result && !action.error && (
        <Notice tone="success">
          {result.device_id} reportó{" "}
          <span className="num">
            {result.reading_value} {result.unit}
          </span>
          . Notificado por {labelFor(result.notified_via)}.
        </Notice>
      )}

      <Button
        type="submit"
        variant="primary"
        loading={action.pending}
        disabled={!productId || !vendorCode}
        icon={<RadioTower className="size-4" aria-hidden />}
      >
        Enviar lectura
      </Button>
      <p className="text-[0.82rem] text-ink-soft">
        No hay sensores físicos conectados: las lecturas salen de clientes simulados de cada
        fabricante. Prueba 38 °C para levantar una alerta.
      </p>
    </form>
  );
}

function LiveFeed({ readings }: { readings: Reading[] }) {
  // Solo se anima la lectura que llegó después de la primera carga.
  const seen = useRef<string | null>(null);
  const newestKey = readings[0] ? `${readings[0].received_at}${readings[0].device_id}` : null;
  const isArrival = seen.current !== null && newestKey !== seen.current;
  useEffect(() => {
    seen.current = newestKey ?? "";
  }, [newestKey]);

  if (readings.length === 0) {
    return (
      <div className="p-5">
        <EmptyState title="Esperando lecturas">
          Envía una lectura con el formulario y aparecerá aquí en segundos. El panel se reinicia
          cuando se reinicia la API; las lecturas quedan guardadas en Seguimiento.
        </EmptyState>
      </div>
    );
  }
  return (
    <ul className="divide-y divide-line">
      {readings.slice(0, 12).map((reading, index) => (
        <li
          key={`${reading.received_at}-${reading.device_id}`}
          className={`grid grid-cols-[5.5rem_1fr_auto] items-baseline gap-x-3 px-5 py-2.5 ${
            index === 0 && isArrival ? "arrival" : ""
          }`}
        >
          <span className="num font-bold">{reading.device_id}</span>
          <span className="min-w-0">
            <span className="num font-semibold">
              {reading.value} {reading.unit}
            </span>
            <span className="text-ink-soft">
              {" "}
              de {reading.sensor_type}, <span className="num">{reading.product_id}</span> en{" "}
              {stageLabel(reading.stage)}
            </span>
          </span>
          <time dateTime={reading.received_at} className="num text-[0.82rem] text-ink-soft">
            {formatTime(reading.received_at)}
          </time>
        </li>
      ))}
    </ul>
  );
}

export function IotPage() {
  const { products, selected, select } = useProducts();
  const vendors = useQuery(() => api<Vendor[]>("/iot/vendors"), []);
  const readings = useQuery(() => api<Reading[]>("/iot/readings/recent"), [], { pollMs: POLL_MS });
  const alerts = useQuery(() => api<Alert[]>("/iot/alerts"), [], { pollMs: POLL_MS });
  const devices = useQuery(() => api<Device[]>("/iot/devices"), [], { pollMs: POLL_MS });

  const refresh = (): void => {
    readings.reload();
    alerts.reload();
    devices.reload();
  };

  return (
    <>
      <PageHeader title="Monitoreo IoT">
        Lecturas de los sensores que viajan con cada producto, y las alertas cuando una se sale del
        rango seguro.
      </PageHeader>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
        <div className="space-y-5">
          <Panel title="Simular una lectura" patterns={["Adapter", "Bridge"]}>
            <div className="space-y-4">
              <QueryView state={products} skeletonRows={1}>
                {(list) => (
                  <ProductSelect id="iot-product" products={list} value={selected} onChange={select} />
                )}
              </QueryView>
              <QueryView state={vendors} skeletonRows={3}>
                {(list) => (
                  <IngestForm
                    key={selected}
                    vendors={list}
                    productId={selected}
                    onIngested={refresh}
                  />
                )}
              </QueryView>
            </div>
          </Panel>

          <Panel title="Dispositivos" patterns={["Observer"]} flush>
            <QueryView state={devices} skeletonRows={2}>
              {(list) =>
                list.length === 0 ? (
                  <div className="p-5">
                    <EmptyState title="Ningún dispositivo ha reportado">
                      Aparecerán aquí con su última lectura en cuanto envíen la primera.
                    </EmptyState>
                  </div>
                ) : (
                  <ul className="divide-y divide-line">
                    {list.map((device) => (
                      <li
                        key={device.device_id}
                        className="flex flex-wrap items-baseline gap-x-3 px-5 py-2.5"
                      >
                        <span className="num font-bold">{device.device_id}</span>
                        <span className="text-ink-soft">{device.sensor_type}</span>
                        <span className="num ml-auto font-semibold">
                          {device.last_value} {device.unit}
                        </span>
                        <span className="num basis-full text-[0.82rem] text-ink-soft">
                          {device.readings_count} lectura(s), última a las{" "}
                          {formatTime(device.last_seen_at)}
                        </span>
                      </li>
                    ))}
                  </ul>
                )
              }
            </QueryView>
          </Panel>
        </div>

        <div className="space-y-5">
          <Panel
            title="Lecturas en vivo"
            patterns={["Observer"]}
            aside={<Badge tone="go">Cada 4 s</Badge>}
            flush
          >
            <QueryView state={readings} skeletonRows={4}>
              {(list) => <LiveFeed readings={list} />}
            </QueryView>
          </Panel>

          <Panel title="Alertas por umbral" patterns={["Observer"]} flush>
            <QueryView state={alerts} skeletonRows={2}>
              {(list) =>
                list.length === 0 ? (
                  <div className="p-5">
                    <EmptyState title="Sin alertas">
                      Rangos seguros: temperatura de 2 a 30 °C y humedad de 20 a 80 %. Una lectura
                      fuera de ellos levanta una alerta aquí.
                    </EmptyState>
                  </div>
                ) : (
                  <ul className="divide-y divide-line">
                    {list.slice(0, 10).map((alert, index) => (
                      <li key={`${alert.raised_at}-${index}`} className="px-5 py-3">
                        <p className="flex flex-wrap items-center gap-2">
                          <Badge tone="stop">
                            <span className="num">
                              {alert.value} {alert.unit}
                            </span>
                          </Badge>
                          <span className="num font-bold">{alert.device_id}</span>
                          <span className="num text-ink-soft">{alert.product_id}</span>
                          <time
                            dateTime={alert.raised_at}
                            className="num ml-auto text-[0.82rem] text-ink-soft"
                          >
                            {formatTime(alert.raised_at)}
                          </time>
                        </p>
                        <p className="mt-1 text-[0.92rem]">{alert.message}</p>
                      </li>
                    ))}
                  </ul>
                )
              }
            </QueryView>
          </Panel>
        </div>
      </div>
    </>
  );
}
