import { Radio, Repeat2 } from "lucide-react";

import { formatDateTime } from "../lib/format";
import { stageLabel } from "../lib/stages";
import type { TrackingEvent } from "../lib/types";

function describe(event: TrackingEvent): string {
  const details = event.details;
  if (event.event_type === "sensor") {
    return `${details.sensor_type}: ${details.reading_value} ${details.unit}`;
  }
  return `De ${stageLabel(String(details.previous_stage))} a ${stageLabel(event.stage)}, a cargo de ${details.responsible}`;
}

interface EventListProps {
  events: TrackingEvent[];
  showProduct?: boolean;
}

/** Bitácora de eventos de seguimiento, del más reciente al más antiguo. */
export function EventList({ events, showProduct = false }: EventListProps) {
  return (
    <ul className="divide-y divide-line">
      {events.map((event, index) => {
        const Icon = event.event_type === "sensor" ? Radio : Repeat2;
        return (
          <li
            key={`${event.timestamp}-${index}`}
            className="grid grid-cols-[auto_1fr_auto] items-baseline gap-x-3 px-5 py-2.5"
          >
            <Icon
              className={`size-4 translate-y-0.5 ${
                event.event_type === "sensor" ? "text-info" : "text-go"
              }`}
              role="img"
              aria-label={event.event_type === "sensor" ? "Lectura de sensor" : "Cambio de etapa"}
            />
            <p className="min-w-0">
              {showProduct && <span className="num mr-2 font-semibold">{event.product_id}</span>}
              <span>{describe(event)}</span>
              {event.event_type === "sensor" && (
                <span className="text-ink-soft"> en {stageLabel(event.stage)}</span>
              )}
            </p>
            <time dateTime={event.timestamp} className="num text-[0.82rem] text-ink-soft">
              {formatDateTime(event.timestamp)}
            </time>
          </li>
        );
      })}
    </ul>
  );
}
