import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { api, session, setUnauthorizedListener } from "../lib/api";
import type { TokenResponse } from "../lib/types";

interface AuthValue {
  user: string | null;
  /** Mensaje para la pantalla de ingreso cuando la sesión terminó sola. */
  expiredNotice: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<string | null>(() => (session.token() ? session.user() : null));
  const [expiredNotice, setExpiredNotice] = useState<string | null>(null);

  useEffect(() => {
    setUnauthorizedListener(() => {
      session.clear();
      setUser(null);
      setExpiredNotice("Tu sesión terminó. Inicia sesión de nuevo para continuar.");
    });
    return () => setUnauthorizedListener(null);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const response = await api<TokenResponse>("/login", {
      method: "POST",
      body: { username, password },
      authenticated: false,
    });
    session.save(response.access_token, response.username ?? username);
    setExpiredNotice(null);
    setUser(response.username ?? username);
  }, []);

  const register = useCallback(
    async (username: string, password: string) => {
      await api("/register", {
        method: "POST",
        body: { username, password },
        authenticated: false,
      });
      await login(username, password);
    },
    [login],
  );

  const logout = useCallback(async () => {
    try {
      await api("/logout", { method: "POST" });
    } catch {
      // Si la API no responde, igual se cierra la sesión en este navegador.
    }
    session.clear();
    setExpiredNotice(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, expiredNotice, login, register, logout }),
    [user, expiredNotice, login, register, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return value;
}
