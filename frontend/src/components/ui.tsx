import { CircleAlert, CircleCheck, LoaderCircle } from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

import { PatternTag } from "./PatternTag";

type ButtonVariant = "primary" | "secondary" | "danger" | "quiet";

const BUTTON_STYLES: Record<ButtonVariant, string> = {
  primary:
    "bg-signal text-ink border-signal-strong hover:bg-signal-strong active:translate-y-px font-semibold",
  secondary:
    "bg-surface text-ink border-line-strong hover:border-ink hover:bg-sunken active:translate-y-px font-medium",
  danger:
    "bg-surface text-stop border-stop/50 hover:bg-stop-soft hover:border-stop active:translate-y-px font-medium",
  quiet: "bg-transparent text-ink-soft border-transparent hover:bg-sunken hover:text-ink font-medium",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  loading?: boolean;
  icon?: ReactNode;
  size?: "md" | "sm";
}

export function Button({
  variant = "secondary",
  loading = false,
  icon,
  size = "md",
  children,
  disabled,
  type = "button",
  className = "",
  ...rest
}: ButtonProps) {
  const sizing = size === "sm" ? "min-h-9 px-3 text-[0.88rem]" : "min-h-[2.6rem] px-4";
  return (
    <button
      type={type}
      disabled={disabled || loading}
      aria-busy={loading}
      className={`inline-flex items-center justify-center gap-2 rounded-control border transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-55 ${sizing} ${BUTTON_STYLES[variant]} ${className}`}
      {...rest}
    >
      {loading ? <LoaderCircle className="size-4 animate-spin" aria-hidden /> : icon}
      {children}
    </button>
  );
}

interface FieldProps {
  label: string;
  htmlFor: string;
  hint?: string;
  children: ReactNode;
  className?: string;
}

export function Field({ label, htmlFor, hint, children, className = "" }: FieldProps) {
  return (
    <div className={className}>
      <label htmlFor={htmlFor} className="mb-1 block text-[0.88rem] font-semibold text-ink">
        {label}
      </label>
      {children}
      {hint && <p className="mt-1 text-[0.82rem] text-ink-soft">{hint}</p>}
    </div>
  );
}

interface PanelProps {
  title: string;
  patterns?: string[];
  aside?: ReactNode;
  children: ReactNode;
  className?: string;
  flush?: boolean;
}

/** Sección de trabajo: título, patrones que la respaldan y contenido. */
export function Panel({ title, patterns = [], aside, children, className = "", flush }: PanelProps) {
  return (
    <section className={`rounded-panel border border-line bg-surface ${className}`}>
      <header className="flex flex-wrap items-center gap-x-3 gap-y-2 border-b border-line px-5 py-3">
        <h2 className="mr-auto text-[1.05rem] font-bold">{title}</h2>
        {patterns.length > 0 && (
          <ul className="flex flex-wrap gap-1.5" aria-label="Patrones que respaldan esta sección">
            {patterns.map((pattern) => (
              <li key={pattern}>
                <PatternTag name={pattern} />
              </li>
            ))}
          </ul>
        )}
        {aside}
      </header>
      <div className={flush ? "" : "p-5"}>{children}</div>
    </section>
  );
}

interface NoticeProps {
  tone: "error" | "success" | "info";
  children: ReactNode;
}

const NOTICE_STYLES: Record<NoticeProps["tone"], string> = {
  error: "bg-stop-soft text-stop border-stop/30",
  success: "bg-go-soft text-go border-go/30",
  info: "bg-info-soft text-info border-info/30",
};

export function Notice({ tone, children }: NoticeProps) {
  const Icon = tone === "success" ? CircleCheck : CircleAlert;
  return (
    <p
      role={tone === "error" ? "alert" : "status"}
      className={`flex items-start gap-2 rounded-control border px-3 py-2 text-[0.92rem] font-medium ${NOTICE_STYLES[tone]}`}
    >
      <Icon className="mt-0.5 size-4 shrink-0" aria-hidden />
      <span>{children}</span>
    </p>
  );
}

type BadgeTone = "idle" | "go" | "info" | "stop" | "caution";

const BADGE_STYLES: Record<BadgeTone, string> = {
  idle: "bg-idle-soft text-idle",
  go: "bg-go-soft text-go",
  info: "bg-info-soft text-info",
  stop: "bg-stop-soft text-stop",
  caution: "bg-caution-soft text-caution",
};

export function Badge({ tone, children }: { tone: BadgeTone; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[0.8rem] font-semibold whitespace-nowrap ${BADGE_STYLES[tone]}`}
    >
      <span className="size-1.5 rounded-full bg-current" aria-hidden />
      {children}
    </span>
  );
}

interface EmptyStateProps {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}

/** Estado vacío: dice qué falta y cuál es el siguiente paso. */
export function EmptyState({ title, children, action }: EmptyStateProps) {
  return (
    <div className="rounded-control border border-dashed border-line-strong bg-ground/60 px-5 py-6">
      <p className="font-semibold">{title}</p>
      <p className="mt-1 max-w-[60ch] text-[0.92rem] text-ink-soft">{children}</p>
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}

export function SkeletonRows({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-2.5" role="status" aria-busy="true">
      <span className="sr-only">Cargando</span>
      {Array.from({ length: rows }, (_, index) => (
        <div key={index} className="skeleton h-9" style={{ width: `${100 - index * 9}%` }} />
      ))}
    </div>
  );
}

interface QueryViewProps<T> {
  state: { data: T | null; error: string | null; loading: boolean; reload: () => void };
  children: (data: T) => ReactNode;
  skeletonRows?: number;
}

/** Resuelve cargando / error / datos de una consulta en un solo lugar. */
export function QueryView<T>({ state, children, skeletonRows }: QueryViewProps<T>) {
  if (state.data !== null) {
    if (!state.error) return <>{children(state.data)}</>;
    // La última actualización falló: se muestran los datos que había,
    // avisando de que pueden estar desactualizados.
    return (
      <>
        <div className="flex flex-wrap items-center gap-3 border-b border-line px-5 py-2.5">
          <div className="min-w-0 flex-1">
            <Notice tone="error">No se pudo actualizar: {state.error}</Notice>
          </div>
          <Button size="sm" onClick={state.reload}>
            Reintentar
          </Button>
        </div>
        {children(state.data)}
      </>
    );
  }
  if (state.error) {
    return (
      <div className="space-y-3">
        <Notice tone="error">{state.error}</Notice>
        <Button size="sm" onClick={state.reload}>
          Reintentar
        </Button>
      </div>
    );
  }
  return <SkeletonRows rows={skeletonRows} />;
}

interface TabsProps<T extends string> {
  tabs: readonly { id: T; label: string }[];
  current: T;
  onChange: (id: T) => void;
  label: string;
}

export function Tabs<T extends string>({ tabs, current, onChange, label }: TabsProps<T>) {
  return (
    <div role="group" aria-label={label} className="flex gap-1 overflow-x-auto overflow-y-hidden border-b border-line [scrollbar-width:none]">
      {tabs.map((tab) => {
        const selected = tab.id === current;
        return (
          <button
            key={tab.id}
            type="button"
            aria-pressed={selected}
            onClick={() => onChange(tab.id)}
            className={`border-b-[3px] px-4 py-2.5 font-semibold whitespace-nowrap transition-colors duration-150 ${
              selected
                ? "border-signal-strong text-ink"
                : "border-transparent text-ink-soft hover:text-ink"
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
