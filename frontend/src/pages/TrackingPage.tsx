import { Send } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";

import { EventList } from "../components/EventList";
import { ProductSelect } from "../components/ProductSelect";
import { PageHeader } from "../components/Shell";
import { StripMap } from "../components/StripMap";
import { Button, EmptyState, Field, Notice, Panel, QueryView, Tabs } from "../components/ui";
import { api } from "../lib/api";
import { STAGES, stageStops } from "../lib/stages";
import type { EventType, TrackingEvent } from "../lib/types";
import { useProducts } from "../lib/useProducts";
import { useAction, useQuery } from "../lib/useQuery";

const EVENT_TABS = [
  { id: "stage_change", label: "Cambio de etapa" },
  { id: "sensor", label: "Lectura de sensor" },
] as const;

const SENSOR_TYPES = [
  { code: "temperatura", label: "Temperatura", unit: "°C" },
  { code: "humedad", label: "Humedad", unit: "%" },
] as const;

interface StageSelectProps {
  id: string;
  label: string;
  value: string;
  onChange: (stage: string) => void;
}

function StageSelect({ id, label, value, onChange }: StageSelectProps) {
  return (
    <Field label={label} htmlFor={id}>
      <select
        id={id}
        className="control"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {STAGES.map((stage) => (
          <option key={stage.code} value={stage.code}>
            {stage.label}
          </option>
        ))}
      </select>
    </Field>
  );
}

interface RegisterFormProps {
  productId: string;
  onRegistered: () => void;
}

function RegisterEventForm({ productId, onRegistered }: RegisterFormProps) {
  const [eventType, setEventType] = useState<EventType>("stage_change");
  const [stage, setStage] = useState("almacenamiento");
  const [previousStage, setPreviousStage] = useState("fabricacion");
  const [responsible, setResponsible] = useState("");
  const [sensorType, setSensorType] = useState<string>(SENSOR_TYPES[0].code);
  const [reading, setReading] = useState("");
  const [saved, setSaved] = useState(false);
  const action = useAction();

  const unit = SENSOR_TYPES.find((sensor) => sensor.code === sensorType)?.unit ?? "";

  const handleSubmit = (event: FormEvent): void => {
    event.preventDefault();
    setSaved(false);
    const body =
      eventType === "stage_change"
        ? { event_type: eventType, product_id: productId, stage, previous_stage: previousStage, responsible }
        : {
            event_type: eventType,
            product_id: productId,
            stage,
            sensor_type: sensorType,
            reading_value: reading === "" ? null : Number(reading),
            unit,
          };
    void action
      .run(async () => {
        await api("/tracking/events", { method: "POST", body });
      })
      .then((ok) => {
        if (!ok) return;
        setSaved(true);
        setReading("");
        onRegistered();
      });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      <Tabs
        label="Tipo de evento"
        tabs={EVENT_TABS}
        current={eventType}
        onChange={(next) => {
          setEventType(next);
          setSaved(false);
          action.clearError();
        }}
      />

      {eventType === "stage_change" ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <StageSelect
              id="previous-stage"
              label="Etapa anterior"
              value={previousStage}
              onChange={setPreviousStage}
            />
            <StageSelect id="stage" label="Etapa nueva" value={stage} onChange={setStage} />
          </div>
          <Field label="Responsable" htmlFor="responsible" hint="Quién entrega o recibe el producto.">
            <input
              id="responsible"
              className="control"
              maxLength={100}
              value={responsible}
              onChange={(event) => setResponsible(event.target.value)}
            />
          </Field>
        </>
      ) : (
        <>
          <StageSelect id="stage" label="Etapa en la que se midió" value={stage} onChange={setStage} />
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Tipo de sensor" htmlFor="sensor-type">
              <select
                id="sensor-type"
                className="control"
                value={sensorType}
                onChange={(event) => setSensorType(event.target.value)}
              >
                {SENSOR_TYPES.map((sensor) => (
                  <option key={sensor.code} value={sensor.code}>
                    {sensor.label}
                  </option>
                ))}
              </select>
            </Field>
            <Field label={`Lectura (${unit})`} htmlFor="reading">
              <input
                id="reading"
                type="number"
                step="any"
                inputMode="decimal"
                className="control num"
                value={reading}
                onChange={(event) => setReading(event.target.value)}
              />
            </Field>
          </div>
        </>
      )}

      {action.error && <Notice tone="error">{action.error}</Notice>}
      {saved && !action.error && <Notice tone="success">Evento registrado.</Notice>}

      <Button
        type="submit"
        variant="primary"
        loading={action.pending}
        disabled={!productId}
        icon={<Send className="size-4" aria-hidden />}
      >
        Registrar evento
      </Button>
      <p className="text-[0.82rem] text-ink-soft">
        El formulario no bloquea campos vacíos a propósito: envíalo incompleto para ver qué eslabón
        de la cadena de validación lo rechaza.
      </p>
    </form>
  );
}

export function TrackingPage() {
  const { products, selected, select } = useProducts();
  const events = useQuery(
    () => api<TrackingEvent[]>(`/tracking/events/${encodeURIComponent(selected)}`),
    [selected],
    { enabled: Boolean(selected) },
  );

  const newestFirst = events.data ? [...events.data].reverse() : [];
  const lastStageChange = newestFirst.find((event) => event.event_type === "stage_change");
  const currentStage = (lastStageChange ?? newestFirst[0])?.stage ?? null;

  return (
    <>
      <PageHeader title="Seguimiento">
        Registra por dónde va cada producto y qué midieron sus sensores, del fabricante al cliente.
      </PageHeader>

      <div className="mb-5 max-w-md">
        <QueryView state={products} skeletonRows={1}>
          {(list) => (
            <ProductSelect id="tracking-product" products={list} value={selected} onChange={select} />
          )}
        </QueryView>
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
        <Panel
          title="Registrar evento"
          patterns={["Chain of Responsibility", "Factory Method", "Abstract Factory"]}
        >
          <RegisterEventForm key={selected} productId={selected} onRegistered={events.reload} />
        </Panel>

        <Panel title={selected ? `Recorrido de ${selected}` : "Recorrido"} flush>
          {!selected ? (
            <div className="p-5">
              <EmptyState title="Sin producto seleccionado">
                Elige un producto para ver su recorrido y su historial de eventos.
              </EmptyState>
            </div>
          ) : (
            <QueryView state={events} skeletonRows={4}>
              {() => (
                <>
                  <div className="border-b border-line px-5 pt-4 pb-2">
                    <StripMap label="Etapas del producto" stops={stageStops(currentStage)} />
                  </div>
                  {newestFirst.length > 0 ? (
                    <EventList events={newestFirst} />
                  ) : (
                    <div className="p-5">
                      <EmptyState title="Este producto aún no tiene eventos">
                        Registra su primer cambio de etapa (por ejemplo, de Fabricación a
                        Almacenamiento) y aparecerá aquí.
                      </EmptyState>
                    </div>
                  )}
                </>
              )}
            </QueryView>
          )}
        </Panel>
      </div>
    </>
  );
}
