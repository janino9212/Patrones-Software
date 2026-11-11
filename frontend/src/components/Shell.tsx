import {
  Boxes,
  ChartLine,
  LayoutDashboard,
  LogOut,
  MapPinned,
  Radio,
  Route as RouteIcon,
  Shapes,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useEffect } from "react";
import type { ReactNode } from "react";
import { NavLink, Outlet } from "react-router";

import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";
import { useQuery } from "../lib/useQuery";

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
}

const NAV: readonly NavItem[] = [
  { to: "/", label: "Panel", icon: LayoutDashboard },
  { to: "/productos", label: "Productos", icon: Boxes },
  { to: "/seguimiento", label: "Seguimiento", icon: MapPinned },
  { to: "/logistica", label: "Logística", icon: RouteIcon },
  { to: "/pronosticos", label: "Pronósticos", icon: ChartLine },
  { to: "/iot", label: "Monitoreo IoT", icon: Radio },
  { to: "/patrones", label: "Patrones", icon: Shapes },
];

interface Health {
  status: string;
  database: string;
}

function HealthIndicator() {
  const health = useQuery(() => api<Health>("/health"), [], { pollMs: 20_000 });
  const connected = health.data?.database === "connected";
  const text = health.loading && !health.data
    ? "Comprobando API"
    : health.error
      ? "API sin conexión"
      : connected
        ? "API y base de datos en línea"
        : "Base de datos sin conexión";
  const dot = health.error || (health.data && !connected) ? "bg-stop" : "bg-[#5fd08e]";
  return (
    <p className="flex items-center gap-2 text-[0.8rem] text-rail-ink-soft" role="status">
      <span className={`size-2 shrink-0 rounded-full ${dot}`} aria-hidden />
      {text}
    </p>
  );
}

export function Shell() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[15.5rem_1fr]">
      <a
        href="#contenido"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-control focus:bg-signal focus:px-3 focus:py-2 focus:font-semibold"
      >
        Saltar al contenido
      </a>

      <aside className="bg-rail text-rail-ink lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col">
        <div className="flex items-center gap-3 px-5 pt-5 pb-4">
          <svg viewBox="0 0 32 32" className="size-9 shrink-0" aria-hidden>
            <path d="M7 16h18" stroke="#f5c400" strokeWidth="3" strokeLinecap="round" />
            <circle cx="7" cy="16" r="4" fill="#f5c400" />
            <circle cx="16" cy="16" r="4" fill="#0e3b2c" stroke="#f5c400" strokeWidth="2.5" />
            <circle cx="25" cy="16" r="4" fill="#0e3b2c" stroke="#f5c400" strokeWidth="2.5" />
          </svg>
          <div className="leading-tight">
            <p className="text-[1.15rem] font-extrabold tracking-tight text-white">SCM</p>
            <p className="text-[0.78rem] text-rail-ink-soft">Cadena de suministro</p>
          </div>
        </div>

        <nav aria-label="Secciones" className="overflow-x-auto px-3 pb-3 [scrollbar-width:none] lg:flex-1 lg:overflow-y-auto">
          <ul className="flex gap-1 lg:flex-col">
            {NAV.map(({ to, label, icon: Icon }) => (
              <li key={to} className="shrink-0">
                <NavLink
                  to={to}
                  end={to === "/"}
                  className={({ isActive }) =>
                    `flex items-center gap-2.5 rounded-control px-3 py-2 font-semibold whitespace-nowrap no-underline transition-colors duration-150 ${
                      isActive
                        ? "bg-signal text-ink"
                        : "text-rail-ink hover:bg-rail-raised hover:text-white"
                    }`
                  }
                >
                  <Icon className="size-[1.1rem] shrink-0" aria-hidden />
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="hidden border-t border-rail-raised px-5 py-4 lg:block">
          <HealthIndicator />
        </div>
      </aside>

      <div className="flex min-w-0 flex-col">
        <header className="flex items-center justify-end gap-3 border-b border-line bg-surface px-5 py-2.5 lg:px-8">
          <p className="mr-auto text-[0.88rem] text-ink-soft lg:hidden">
            Sesión de <strong className="text-ink">{user}</strong>
          </p>
          <p className="hidden text-[0.88rem] text-ink-soft lg:block">
            Sesión de <strong className="text-ink">{user}</strong>
          </p>
          <button
            type="button"
            onClick={() => void logout()}
            className="inline-flex min-h-9 items-center gap-1.5 rounded-control border border-line-strong px-3 text-[0.88rem] font-semibold transition-colors duration-150 hover:border-ink hover:bg-sunken"
          >
            <LogOut className="size-4" aria-hidden />
            Cerrar sesión
          </button>
        </header>
        <main id="contenido" tabIndex={-1} className="flex-1 px-5 py-6 outline-none lg:px-8 lg:py-7">
          <div className="mx-auto max-w-[78rem]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

interface PageHeaderProps {
  title: string;
  children?: ReactNode;
}

export function PageHeader({ title, children }: PageHeaderProps) {
  // El título de la pestaña anuncia en qué pantalla se está.
  useEffect(() => {
    document.title = `${title} | SCM`;
  }, [title]);

  return (
    <header className="mb-5">
      <h1 className="text-[1.75rem] leading-tight font-extrabold">{title}</h1>
      {children && <p className="mt-1 max-w-[70ch] text-ink-soft">{children}</p>}
    </header>
  );
}
