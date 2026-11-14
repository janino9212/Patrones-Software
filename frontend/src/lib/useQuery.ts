import { useCallback, useEffect, useRef, useState } from "react";

import { errorMessage } from "./api";

export interface QueryState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
}

interface QueryOptions {
  /** Vuelve a consultar cada N milisegundos (monitoreo en vivo). */
  pollMs?: number;
  /** false para no consultar todavía (p. ej. falta elegir un producto). */
  enabled?: boolean;
}

interface Snapshot<T> {
  /** Firma de las dependencias con las que se obtuvo `data`. */
  key: string;
  data: T | null;
  error: string | null;
}

/**
 * Carga datos de la API y expone los tres estados (cargando, error, datos).
 * `deps` decide cuándo se vuelve a consultar, como en useEffect, y deben ser
 * valores serializables (cadenas, números).
 *
 * Al cambiar `deps` el resultado anterior se descarta de inmediato: nunca se
 * muestran los datos de un producto bajo el título de otro.
 */
export function useQuery<T>(
  fetcher: () => Promise<T>,
  deps: readonly unknown[],
  options: QueryOptions = {},
): QueryState<T> {
  const { pollMs, enabled = true } = options;
  const key = JSON.stringify(deps);
  const [snapshot, setSnapshot] = useState<Snapshot<T>>({ key, data: null, error: null });
  const [loading, setLoading] = useState(enabled);
  const [version, setVersion] = useState(0);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;
  // Identifica la petición más reciente: una respuesta que llega tarde (otro
  // producto, o un sondeo anterior más lento) no pisa a una más nueva.
  const latestRequest = useRef(0);

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    const run = async (showLoading: boolean): Promise<void> => {
      const requestId = ++latestRequest.current;
      const isCurrent = (): boolean => !cancelled && requestId === latestRequest.current;
      if (showLoading) setLoading(true);
      try {
        const result = await fetcherRef.current();
        if (isCurrent()) setSnapshot({ key, data: result, error: null });
      } catch (cause) {
        if (isCurrent()) {
          // Se conservan los datos de estas mismas dependencias (quedan
          // marcados como desactualizados); los de otras, no.
          setSnapshot((previous) => ({
            key,
            data: previous.key === key ? previous.data : null,
            error: errorMessage(cause),
          }));
        }
      } finally {
        if (isCurrent()) setLoading(false);
      }
    };
    void run(true);
    const timer = pollMs ? window.setInterval(() => void run(false), pollMs) : undefined;
    return () => {
      cancelled = true;
      if (timer) window.clearInterval(timer);
    };
  }, [key, version, pollMs, enabled]);

  const reload = useCallback(() => setVersion((current) => current + 1), []);
  const isFresh = enabled && snapshot.key === key;
  return {
    data: isFresh ? snapshot.data : null,
    error: isFresh ? snapshot.error : null,
    loading: enabled && (loading || !isFresh),
    reload,
  };
}

export interface ActionState {
  pending: boolean;
  error: string | null;
  run: (action: () => Promise<void>) => Promise<boolean>;
  clearError: () => void;
}

/** Ejecuta una acción (crear, despachar...) con estado de envío y de error. */
export function useAction(): ActionState {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async (action: () => Promise<void>): Promise<boolean> => {
    setPending(true);
    setError(null);
    try {
      await action();
      return true;
    } catch (cause) {
      setError(errorMessage(cause));
      return false;
    } finally {
      setPending(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);
  return { pending, error, run, clearError };
}
