import { ArrowDown, ArrowUp, Plus, X } from "lucide-react";
import { useState } from "react";

import type { LocationItem } from "../lib/types";

interface StopsEditorProps {
  id: string;
  locations: LocationItem[];
  stops: string[];
  onChange: (stops: string[]) => void;
  max?: number;
}

const iconButton =
  "inline-flex size-8 items-center justify-center rounded-control text-ink-soft transition-colors duration-150 hover:bg-sunken hover:text-ink disabled:cursor-not-allowed disabled:opacity-35";

/** Lista ordenada de paradas: la primera es el origen de la ruta. */
export function StopsEditor({ id, locations, stops, onChange, max = 25 }: StopsEditorProps) {
  const available = locations.filter((location) => !stops.includes(location.name));
  const [candidate, setCandidate] = useState("");
  const choice = available.some((location) => location.name === candidate)
    ? candidate
    : (available[0]?.name ?? "");

  const move = (index: number, offset: number): void => {
    const target = index + offset;
    const next = [...stops];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next);
  };

  return (
    <fieldset>
      <legend className="mb-1 text-[0.88rem] font-semibold">Paradas</legend>
      {stops.length > 0 && (
        <ol className="mb-2 divide-y divide-line rounded-control border border-line">
          {stops.map((stop, index) => (
            <li key={stop} className="flex items-center gap-2 py-1 pr-1 pl-3">
              <span className="num w-5 text-[0.82rem] font-bold text-ink-soft">{index + 1}</span>
              <span className="flex-1">
                {stop}
                {index === 0 && <span className="ml-2 text-[0.8rem] text-ink-soft">origen</span>}
              </span>
              <button
                type="button"
                className={iconButton}
                disabled={index === 0}
                onClick={() => move(index, -1)}
                aria-label={`Subir ${stop}`}
              >
                <ArrowUp className="size-4" aria-hidden />
              </button>
              <button
                type="button"
                className={iconButton}
                disabled={index === stops.length - 1}
                onClick={() => move(index, 1)}
                aria-label={`Bajar ${stop}`}
              >
                <ArrowDown className="size-4" aria-hidden />
              </button>
              <button
                type="button"
                className={iconButton}
                onClick={() => onChange(stops.filter((name) => name !== stop))}
                aria-label={`Quitar ${stop}`}
              >
                <X className="size-4" aria-hidden />
              </button>
            </li>
          ))}
        </ol>
      )}
      <div className="flex gap-2">
        <label htmlFor={id} className="sr-only">
          Ubicación para agregar
        </label>
        <select
          id={id}
          className="control"
          value={choice}
          disabled={available.length === 0 || stops.length >= max}
          onChange={(event) => setCandidate(event.target.value)}
        >
          {available.length === 0 && <option value="">No quedan ubicaciones</option>}
          {available.map((location) => (
            <option key={location.name} value={location.name}>
              {location.name}
            </option>
          ))}
        </select>
        <button
          type="button"
          disabled={!choice || stops.length >= max}
          onClick={() => onChange([...stops, choice])}
          className="inline-flex min-h-[2.6rem] shrink-0 items-center gap-1.5 rounded-control border border-line-strong bg-surface px-3 font-medium transition-colors duration-150 hover:border-ink hover:bg-sunken disabled:cursor-not-allowed disabled:opacity-55"
        >
          <Plus className="size-4" aria-hidden />
          Agregar
        </button>
      </div>
      <p className="mt-1 text-[0.82rem] text-ink-soft">
        Mínimo dos. La primera parada es el origen y ninguna optimización la mueve.
      </p>
    </fieldset>
  );
}
