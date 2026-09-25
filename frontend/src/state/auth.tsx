import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api, getToken, setToken } from "../lib/api";
import type { Role, User, TokenResponse } from "../lib/types";

interface AuthState {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (body: Record<string, unknown>) => Promise<User>;
  logout: () => void;
}

const AuthCtx = createContext<AuthState>({
  user: null,
  loading: true,
  login: async () => {
    throw new Error("no auth");
  },
  register: async () => {
    throw new Error("no auth");
  },
  logout: () => {},
});

const routeFor = (role: Role): string | null => {
  if (role === "authority_admin" || role === "authority_officer") return "/authority";
  if (role === "business" || role === "artisan") return "/business";
  return null;
};
  export const DEMO_ACCOUNTS = [
  { email: "tourist@demo.com", role: "tourist" as Role, label: "Tourist", info: "Explore the platform" },
  { email: "resident@demo.com", role: "resident" as Role, label: "Resident", info: "Report an issue" },
  { email: "artisan@demo.com", role: "artisan" as Role, label: "Artisan & Business", info: "Manage your business" },
  { email: "admin@demo.com", role: "authority_admin" as Role, label: "Authority (Admin)", info: "Command centre" },
  { email: "officer@demo.com", role: "authority_officer" as Role, label: "Authority (Officer)", info: "Operations" },
];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const raw = localStorage.getItem("virsa_user");
    if (getToken() && raw) {
      try {
        setUser(JSON.parse(raw) as User);
      } catch {
        setToken(null);
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.post<TokenResponse>("/auth/login", { email, password }, false);
    setToken(res.access_token);
    localStorage.setItem("virsa_user", JSON.stringify(res.user));
    setUser(res.user);
    return res.user;
  };

  const register = async (body: Record<string, unknown>) => {
    const res = await api.post<TokenResponse>("/auth/register", body, false);
    setToken(res.access_token);
    localStorage.setItem("virsa_user", JSON.stringify(res.user));
    setUser(res.user);
    return res.user;
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem("virsa_user");
    setUser(null);
  };

  return (
    <AuthCtx.Provider value={{ user, loading, login, register, logout }}>{children}</AuthCtx.Provider>
  );
}

export function useAuth() {
  return useContext(AuthCtx);
}

export { routeFor };