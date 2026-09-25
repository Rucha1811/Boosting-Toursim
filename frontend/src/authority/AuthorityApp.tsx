import { useState } from "react";
import { NavLink, Outlet, Link, useNavigate, Routes, Route, Navigate } from "react-router-dom";
import {
  LayoutDashboard,
  Map,
  BarChart3,
  Users,
  PartyPopper,
  BellRing,
  TrafficCone,
  ParkingCircle,
  Flag,
  Store,
  BedDouble,
  TrendingUp,
  Sparkles,
  LogOut,
  ArrowLeft,
} from "lucide-react";
import { clsx } from "clsx";
import { useAuth } from "../state/auth";
import { useDestination } from "../state/destination";
import { destShort } from "../lib/destCopy";
import { MapPin, ChevronDown } from "lucide-react";
import OverviewPage from "./Overview";
import LiveMapPage from "./LiveMap";
import AnalyticsPage from "./Analytics";
import CrowdPage from "./Crowd";
import EventsPage from "./Events";
import AlertsPage from "./Alerts";
import ClosuresPage from "./Closures";
import ParkingPage from "./Parking";
import ReportsPage from "./Reports";
import BusinessesPage from "./Businesses";
import HotelsPage from "./Hotels";
import ForecastPage from "./Forecast";

const NAV = [
  { to: "/authority", label: "Command Center", icon: LayoutDashboard, end: true },
  { to: "/authority/live", label: "Live Map", icon: Map },
  { to: "/authority/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/authority/crowd", label: "Crowd & Redirects", icon: Users },
  { to: "/authority/forecast", label: "Forecast", icon: TrendingUp },
  { to: "/authority/events", label: "Festivals & Events", icon: PartyPopper },
  { to: "/authority/alerts", label: "Alerts & Notices", icon: BellRing },
  { to: "/authority/closures", label: "Road Closures", icon: TrafficCone },
  { to: "/authority/parking", label: "Parking", icon: ParkingCircle },
  { to: "/authority/reports", label: "Community Reports", icon: Flag },
  { to: "/authority/businesses", label: "Businesses", icon: Store },
  { to: "/authority/hotels", label: "Hotels", icon: BedDouble },
];

export default function AuthorityApp() {
  const { user, logout } = useAuth();
  const { current, destinations, currentId, select } = useDestination();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const roleLabel = user?.role === "authority_admin" ? "Tourism Authority · Admin" : "Tourism Authority · Officer";

  return (
    <div className="flex min-h-screen bg-sand-100">
      {/* Sidebar */}
      <aside
        className={clsx(
          "flex shrink-0 flex-col border-r border-ink/10 bg-ink text-sand-200 transition-all",
          collapsed ? "w-16" : "w-60",
        )}
      >
        <div className="flex items-center justify-between gap-2 px-4 py-4">
          <Link to="/" className="flex items-center gap-2 overflow-hidden">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-saffron text-teal-dark">
              <Sparkles className="h-4 w-4" />
            </span>
            {!collapsed && (
              <span className="leading-tight">
                <span className="block font-display text-base font-bold text-white">Authority</span>
                <span className="block text-[9px] uppercase tracking-[0.18em] text-sand-400">{destShort(current)} · Virsa</span>
              </span>
            )}
          </Link>
          <button onClick={() => setCollapsed((c) => !c)} className="text-sand-400 hover:text-white">
            {collapsed ? "»" : "«"}
          </button>
        </div>

        {!collapsed && destinations.length > 0 && (
          <div className="relative mx-2 mb-2 shrink-0">
            <MapPin className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-teal" />
            <select
              value={currentId}
              onChange={(e) => select(Number(e.target.value))}
              aria-label="Switch destination"
              className="w-full appearance-none rounded-xl border border-white/15 bg-white/5 py-2 pl-8 pr-8 text-xs font-semibold text-sand-100 outline-none transition hover:border-saffron/50"
            >
              {destinations.map((d) => (
                <option key={d.id} value={d.id} className="bg-ink text-sand-100">
                  {destShort(d)} · {d.state}
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-sand-400" />
          </div>
        )}

        <nav className="flex-1 space-y-0.5 overflow-y-auto px-2 py-2">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                  isActive ? "bg-saffron/90 text-teal-dark" : "text-sand-300 hover:bg-white/5 hover:text-white",
                )
              }
            >
              <n.icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span className="truncate">{n.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 p-3">
          {!collapsed && (
            <p className="mb-2 truncate px-1 text-[11px] font-semibold text-sand-400">{roleLabel}</p>
          )}
          <button
            onClick={() => {
              logout();
              navigate("/");
            }}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-sand-300 hover:bg-white/5 hover:text-white"
          >
            <LogOut className="h-4 w-4 shrink-0" />
            {!collapsed && <span>Sign out</span>}
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-3 border-b border-ink/10 bg-white/80 px-6 py-3 backdrop-blur">
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-1.5 text-xs font-medium text-ink-muted hover:text-teal">
              <ArrowLeft className="h-3.5 w-3.5" /> Public site
            </Link>
            <span className="hidden text-ink-faint sm:block">/</span>
            <span className="hidden items-center gap-1.5 text-xs font-medium text-ink sm:flex">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
              </span>
              Live telemetry · demo data
            </span>
          </div>
          <div className="text-xs font-semibold text-ink">{user?.name}</div>
        </header>
        <main className="flex-1 p-6">
          <Routes>
            <Route index element={<OverviewPage />} />
            <Route path="live" element={<LiveMapPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="crowd" element={<CrowdPage />} />
            <Route path="forecast" element={<ForecastPage />} />
            <Route path="events" element={<EventsPage />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="closures" element={<ClosuresPage />} />
            <Route path="parking" element={<ParkingPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="businesses" element={<BusinessesPage />} />
            <Route path="hotels" element={<HotelsPage />} />
            <Route path="*" element={<Navigate to="/authority" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}