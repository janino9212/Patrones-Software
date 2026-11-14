const BASE_URL: string =
  (import.meta.env?.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

const TOKEN_KEY = "scm.token";
const USER_KEY = "scm.user";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type UnauthorizedListener = () => void;
let onUnauthorized: UnauthorizedListener | null = null;

export function setUnauthorizedListener(listener: UnauthorizedListener | null): void {
  onUnauthorized = listener;
}

// sessionStorage: la sesión dura lo que la pestaña y no queda en disco.
export const session = {
  token: (): string | null => sessionStorage.getItem(TOKEN_KEY),
  user: (): string | null => sessionStorage.getItem(USER_KEY),
  save(token: string, user: string): void {
    sessionStorage.setItem(TOKEN_KEY, token);
    sessionStorage.setItem(USER_KEY, user);
  },
  clear(): void {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
  },
};

interface ValidationIssue {
  loc?: (string | number)[];
  msg?: string;
}

/** Traduce el `detail` de FastAPI (texto o lista de validación) a una frase. */
export function describeDetail(detail: unknown, fallback: string): string {
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return (detail as ValidationIssue[])
      .map((issue) => {
        const field = (issue.loc ?? []).filter((part) => part !== "body").join(".");
        const message = issue.msg ?? "valor no válido";
        return field ? `${field}: ${message}` : message;
      })
      .join("; ");
  }
  return fallback;
}

const STATUS_FALLBACK: Record<number, string> = {
  400: "La solicitud no es válida.",
  401: "Tu sesión terminó. Inicia sesión de nuevo.",
  404: "No se encontró lo que buscabas.",
  409: "La operación no aplica al estado actual.",
  422: "Revisa los datos del formulario.",
};

interface RequestOptions {
  method?: "GET" | "POST" | "DELETE";
  body?: unknown;
  /** false para /login y /register: un 401 ahí no significa sesión vencida. */
  authenticated?: boolean;
}

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, authenticated = true } = options;
  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = session.token();
  if (authenticated && token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      "No hay conexión con la API. Verifica que el backend esté en ejecución.",
      0,
    );
  }

  if (response.ok) return (await response.json()) as T;

  const payload: unknown = await response.json().catch(() => null);
  const detail = (payload as { detail?: unknown } | null)?.detail;
  const fallback = STATUS_FALLBACK[response.status] ?? `Error ${response.status} del servidor.`;
  if (response.status === 401 && authenticated) {
    // Solo cierra la sesión si el token rechazado sigue siendo el actual:
    // la respuesta tardía de una sesión anterior no debe tumbar la nueva.
    if (session.token() === token) onUnauthorized?.();
    throw new ApiError(STATUS_FALLBACK[401], 401);
  }
  throw new ApiError(describeDetail(detail, fallback), response.status);
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Ocurrió un error inesperado.";
}
