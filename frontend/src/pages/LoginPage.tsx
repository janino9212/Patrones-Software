import { LogIn, UserPlus } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";
import { Navigate, useLocation } from "react-router";

import { useAuth } from "../auth/AuthContext";
import { StripMap } from "../components/StripMap";
import { Button, Field, Notice } from "../components/ui";
import { useAction } from "../lib/useQuery";

type Mode = "login" | "register";

const JOURNEY = [
  { label: "Fabricante", state: "done" as const },
  { label: "Bodega", state: "done" as const },
  { label: "En ruta", state: "current" as const },
  { label: "Cliente", state: "pending" as const },
];

export function LoginPage() {
  const { user, login, register, expiredNotice } = useAuth();
  const location = useLocation();
  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const action = useAction();

  if (user) {
    const from = (location.state as { from?: string } | null)?.from ?? "/";
    return <Navigate to={from} replace />;
  }

  const isLogin = mode === "login";

  const handleSubmit = (event: FormEvent): void => {
    event.preventDefault();
    void action.run(() =>
      isLogin ? login(username.trim(), password) : register(username.trim(), password),
    );
  };

  const switchMode = (): void => {
    action.clearError();
    setMode(isLogin ? "register" : "login");
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-[minmax(0,5fr)_minmax(0,4fr)]">
      <section className="flex flex-col justify-between bg-rail px-7 py-9 text-rail-ink lg:px-14 lg:py-14">
        <div>
          <p className="text-[1.15rem] font-extrabold tracking-tight text-white">SCM</p>
          <h1 className="mt-10 max-w-[16ch] text-[2.6rem] leading-[1.08] font-extrabold text-white lg:text-[3.3rem]">
            Del fabricante al cliente, tramo a tramo.
          </h1>
          <p className="mt-5 max-w-[46ch] text-[1.05rem] text-rail-ink-soft">
            Seguimiento de productos, rutas de distribución, pronóstico de demanda y monitoreo de
            sensores en un solo sistema.
          </p>
        </div>
        <div className="mt-10 rounded-panel bg-surface px-3 pt-4 pb-2 text-ink">
          <StripMap stops={JOURNEY} label="Recorrido de un producto" />
        </div>
      </section>

      <section className="flex items-center justify-center bg-ground px-6 py-10">
        <form onSubmit={handleSubmit} className="w-full max-w-[24rem] space-y-5" noValidate>
          <header>
            <h2 className="text-[1.6rem] font-extrabold">
              {isLogin ? "Inicia sesión" : "Crea tu cuenta"}
            </h2>
            <p className="mt-1 text-ink-soft">
              {isLogin
                ? "Usa tu usuario de la plataforma."
                : "Quedarás con la sesión iniciada al terminar."}
            </p>
          </header>

          {expiredNotice && !action.error && <Notice tone="info">{expiredNotice}</Notice>}
          {action.error && <Notice tone="error">{action.error}</Notice>}

          <Field label="Usuario" htmlFor="username">
            <input
              id="username"
              className="control"
              autoComplete="username"
              autoFocus
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />
          </Field>
          <Field
            label="Contraseña"
            htmlFor="password"
            hint={isLogin ? undefined : "Mínimo 6 caracteres."}
          >
            <input
              id="password"
              type="password"
              className="control"
              autoComplete={isLogin ? "current-password" : "new-password"}
              required
              minLength={isLogin ? undefined : 6}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </Field>

          <Button
            type="submit"
            variant="primary"
            className="w-full"
            loading={action.pending}
            disabled={!username.trim() || !password}
            icon={
              isLogin ? (
                <LogIn className="size-4" aria-hidden />
              ) : (
                <UserPlus className="size-4" aria-hidden />
              )
            }
          >
            {isLogin ? "Entrar" : "Crear cuenta y entrar"}
          </Button>

          <p className="text-[0.92rem] text-ink-soft">
            {isLogin ? "¿No tienes usuario?" : "¿Ya tienes usuario?"}{" "}
            <button
              type="button"
              onClick={switchMode}
              className="font-semibold text-info underline underline-offset-4 hover:text-ink"
            >
              {isLogin ? "Crea una cuenta" : "Inicia sesión"}
            </button>
          </p>
        </form>
      </section>
    </div>
  );
}
