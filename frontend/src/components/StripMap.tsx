import type { ReactNode } from "react";

export type StopState = "done" | "current" | "pending" | "halted";

export interface StripStop {
  label: string;
  detail?: ReactNode;
  state?: StopState;
}

interface StripMapProps {
  stops: StripStop[];
  /** Numera los nodos (paradas de una ruta) en vez de dejarlos lisos. */
  numbered?: boolean;
  label: string;
}

const NODE_STYLES: Record<StopState, string> = {
  done: "bg-go border-go text-white",
  current: "bg-signal border-ink text-ink",
  pending: "bg-surface border-line-strong text-ink-soft",
  halted: "bg-stop border-stop text-white",
};

/** Texto para lectores de pantalla: el color no es el único indicio. */
const STATE_TEXT: Record<StopState, string> = {
  done: "completada",
  current: "actual",
  pending: "pendiente",
  halted: "cancelada",
};

const SEGMENT_STYLES: Record<StopState, string> = {
  done: "bg-go",
  current: "bg-go",
  pending: "bg-line",
  halted: "bg-stop",
};

/**
 * Firma visual de la interfaz: un recorrido dibujado como mapa de línea,
 * con sus paradas en orden. Sirve para las etapas de un producto, las
 * paradas de una ruta y el ciclo de vida de un despacho.
 */
export function StripMap({ stops, numbered = false, label }: StripMapProps) {
  return (
    <ol aria-label={label} className="flex overflow-x-auto pt-1 pb-2">
      {stops.map((stop, index) => {
        const state = stop.state ?? "done";
        return (
          <li
            key={`${stop.label}-${index}`}
            className="relative flex min-w-[5.25rem] flex-1 flex-col items-center px-1 text-center"
            aria-current={state === "current" ? "step" : undefined}
          >
            {index > 0 && (
              <span
                aria-hidden
                className={`absolute top-[0.7rem] right-1/2 h-[4px] w-full -translate-y-1/2 ${SEGMENT_STYLES[state]}`}
              />
            )}
            <span
              className={`num relative z-10 flex size-[1.4rem] items-center justify-center rounded-full border-2 text-[0.72rem] font-bold ${NODE_STYLES[state]}`}
            >
              {numbered ? index + 1 : null}
            </span>
            <span
              className={`mt-1.5 text-[0.86rem] leading-tight ${
                state === "pending" ? "text-ink-soft" : "font-semibold text-ink"
              }`}
            >
              {stop.label}
              <span className="sr-only"> ({STATE_TEXT[state]})</span>
            </span>
            {stop.detail && (
              <span className="mt-0.5 text-[0.76rem] leading-tight text-ink-soft">{stop.detail}</span>
            )}
          </li>
        );
      })}
    </ol>
  );
}
