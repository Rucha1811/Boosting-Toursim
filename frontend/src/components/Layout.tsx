import { useState, useEffect, ReactNode } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Map,
  MapPin,
  HandHeart,
  Ticket,
  PartyPopper,
  BedDouble,
  Sparkles,
  ShieldAlert,
  CircleUser,
  LogOut,
  LayoutDashboard,
  Store,
  TriangleAlert,
  ChevronRight,
  Sun,
} from "lucide-react";
import { clsx } from "clsx";
import { useAuth } from "../state/auth";
import { useDestination } from "../state/destination";
import { useLanguage } from "../state/language";
import { LangToggle, LangToggleIcon, ListenButton, ReadPageButton } from "./a11y";
import { useDynamicInfo, usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { statusTone } from "../lib/catalog";
import { destShort } from "../lib/destCopy";
import type { Festival } from "../lib/types";

const NAV: { to: string; label: string; k: string; icon: ReactNode }[] = [
  { to: "/map", label: "Explore Map", k: "nav.map", icon: <Map className="h-4 w-4" /> },
  { to: "/artisans", label: "Meet the Makers", k: "nav.artisans", icon: <HandHeart className="h-4 w-4" /> },
  { to: "/experiences", label: "Experiences", k: "nav.experiences", icon: <Ticket className="h-4 w-4" /> },
  { to: "/festivals", label: "Festivals", k: "nav.festivals", icon: <PartyPopper className="h-4 w-4" /> },
  { to: "/stays", label: "Stays", k: "nav.stays", icon: <BedDouble className="h-4 w-4" /> },
  { to: "/guide", label: "Virsa Guide", k: "nav.guide", icon: <Sparkles className="h-4 w-4" /> },
];

function AlertsTicker() {
  const { currentId } = useDestination();
  const { data: info } = useDynamicInfo(30000, [currentId]);
  const items = [
    ...(info?.alerts
      .filter((a) => a.is_active)
      .map((a) => ({ text: `${a.title}: ${a.message}`, icon: <TriangleAlert className="h-3.5 w-3.5" />, tone: "text-saffron-deep" })) ?? []),
    ...(info?.road_closures
      .filter((c) => c.status !== "Normal")
      .map((c) => ({ text: `Road closure — ${c.road_name} via ${c.alternate_route}`, icon: <ShieldAlert className="h-3.5 w-3.5" />, tone: "text-blush" })) ?? []),
    ...(info?.announcements.filter((a) => a.important).map((a) => ({ text: a.title, icon: <Sun className="h-3.5 w-3.5" />, tone: "text-teal" })) ?? []),
  ];
  if (!items.length) return null;
  const doubled = [...items, ...items];
  return (
    <div className="relative z-30 overflow-hidden border-b border-ink/10 bg-gradient-to-r from-teal-deep via-teal to-teal-deep text-sand-100">
      <div className="flex whitespace-nowrap py-1.5 [animation:marquee_40s_linear_infinite] w-max">
        {doubled.map((it, i) => (
          <span key={i} className="mx-6 inline-flex items-center gap-2 text-xs font-medium opacity-90">
            {it.icon}
            {it.text}
          </span>
        ))}
      </div>
    </div>
  );
}

function FestivalStrip() {
  const { currentId } = useDestination();
  const { data } = usePoll<Festival[]>(() => endpoints.festivals(), 60000, [currentId]);
  const f = data?.find((x) => x.status === "live" || x.status === "upcoming");
  if (!f) return null;
  const live = f.status === "live";
  return (
    <Link
      to={`/festivals/${f.id}`}
      className="group relative z-30 flex items-center justify-center gap-3 overflow-hidden border-b border-marigold/30 bg-gradient-to-r from-marigold via-saffron-deep to-blush px-4 py-2 text-center text-xs font-semibold text-white sm:text-sm"
    >
      <span className="absolute inset-0 bg-toran opacity-60" />
      <span className="relative flex items-center gap-3">
        <PartyPopper className={live ? "h-4 w-4 animate-pulse" : "h-4 w-4"} />
        <span className="font-display">{live ? "Festival Mode is LIVE" : "Festival Mode"}</span>
        <span className="opacity-90">· {f.name}</span>
        <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
      </span>
    </Link>
  );
}

function DestinationSwitcher() {
  const { destinations, currentId, select } = useDestination();
  if (!destinations.length) return null;
  return (
    <div className="relative shrink-0">
      <MapPin className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-teal" />
      <select
        value={currentId}
        onChange={(e) => select(Number(e.target.value))}
        aria-label="Switch destination"
        className="appearance-none rounded-full border border-ink/15 bg-white py-1.5 pl-8 pr-7 text-xs font-semibold text-ink shadow-card outline-none transition hover:border-teal/40 focus:border-teal/60"
      >
        {destinations.map((d) => (
          <option key={d.id} value={d.id}>
            {destShort(d)} · {d.state}
          </option>
        ))}
      </select>
      <ChevronRight className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 rotate-90 text-ink-faint" />
    </div>
  );
}

const CITY_DEVA: Record<number, string> = {
  1: "वडोदरा",
  2: "अहमदाबाद",
  3: "कच्छ",
  4: "जयपुर",
  5: "वाराणसी",
};

export default function Layout({ children }: { children?: ReactNode }) {
  const { user, logout } = useAuth();
  const { current, currentId } = useDestination();
  const { t, lang } = useLanguage();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const city =
      lang === "hi" ? CITY_DEVA[currentId] ?? destShort(current) : (current?.name ?? destShort(current));
    document.title = lang === "hi" ? `विरसा · ${city} · सांस्कृतिक पर्यटन` : `Virsa · ${city}`;
    document.documentElement.lang = lang;
  }, [current, currentId, lang]);

  const roleLinks =
    user && (user.role === "authority_admin" || user.role === "authority_officer")
      ? [{ to: "/authority", label: t("nav.authority"), icon: <LayoutDashboard className="h-4 w-4" /> }]
      : user && (user.role === "business" || user.role === "artisan")
        ? [{ to: "/business", label: t("nav.business"), icon: <Store className="h-4 w-4" /> }]
        : [];

  return (
    <div className="min-h-screen bg-sand-100">
      <FestivalStrip />
      <AlertsTicker />
      <header className="sticky top-0 z-50 border-b border-ink/10 bg-sand-50/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <Link to="/" className="flex items-center gap-2.5">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal text-white shadow-card">
              <Sparkles className="h-5 w-5" />
            </span>
            <span className="leading-tight">
              <span className="block font-display text-xl font-bold tracking-tight text-ink">Virsa</span>
              <span className="block text-[10px] font-semibold uppercase tracking-[0.22em] text-teal">
                {current ? `${destShort(current)} · ${t("brand.tagline")}` : t("brand.tagline")}
              </span>
            </span>
          </Link>

          <nav className="hidden items-center gap-1 lg:flex">
            {NAV.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  clsx(
                    "flex items-center gap-1.5 rounded-full px-3.5 py-2 text-sm font-medium transition",
                    isActive ? "bg-teal/10 text-teal-deep" : "text-ink-soft hover:bg-ink/5",
                  )
                }
              >
                {n.icon}
                {t(n.k)}
              </NavLink>
            ))}
            {roleLinks.map((r) => (
              <NavLink
                key={r.to}
                to={r.to}
                className={({ isActive }) =>
                  clsx(
                    "flex items-center gap-1.5 rounded-full px-3.5 py-2 text-sm font-semibold transition",
                    isActive ? "bg-saffron/20 text-saffron-deep" : "text-saffron-deep hover:bg-saffron/10",
                  )
                }
              >
                {r.icon}
                {r.label}
              </NavLink>
            ))}
          </nav>

          <div className="hidden items-center gap-2 sm:flex">
            <DestinationSwitcher />
            <LangToggle />
            <ReadPageButton className="shrink-0" />
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setMenuOpen((o) => !o)}
                  className="flex items-center gap-2 rounded-full border border-ink/15 bg-white py-1.5 pl-1.5 pr-3 text-sm font-medium text-ink shadow-card hover:border-teal/40"
                >
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-teal text-xs font-bold text-white">
                    {user.name.slice(0, 1).toUpperCase()}
                  </span>
                  {user.name.split(" ")[0]}
                </button>
                {menuOpen && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
                    <div className="absolute right-0 z-20 mt-2 w-56 rounded-2xl bg-white p-2 shadow-lift">
                      <div className="px-3 py-2">
                        <p className="text-sm font-semibold text-ink">{user.name}</p>
                        <p className="text-xs text-ink-muted">{user.email}</p>
                      </div>
                      <div className="my-1 border-t border-ink/5" />
                      <button
                        onClick={() => {
                          setMenuOpen(false);
                          navigate("/my-reports");
                        }}
                        className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm text-ink-soft hover:bg-sand-100"
                      >
                        <CircleUser className="h-4 w-4" /> {t("account.my")}
                      </button>
                      <button
                        onClick={() => {
                          logout();
                          setMenuOpen(false);
                          navigate("/");
                        }}
                        className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm text-blush hover:bg-blush-light"
                      >
                        <LogOut className="h-4 w-4" /> {t("account.signout")}
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <Link to="/login" className="btn btn-dark btn-md">
                {t("actions.signin")}
              </Link>
            )}
          </div>
        </div>

        <nav className="flex items-center gap-2 overflow-x-auto px-4 pb-2 lg:hidden">
          <div className="shrink-0">
            <DestinationSwitcher />
          </div>
          <LangToggleIcon />
          {[...NAV, ...roleLinks].map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                clsx(
                  "flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium",
                  isActive ? "bg-teal/10 text-teal-deep" : "text-ink-soft",
                )
              }
            >
              {n.icon}
              {("k" in n && n.k) ? t(n.k as string) : n.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="min-h-[60vh]">{children ?? <Outlet />}</main>

      <footer className="mt-16 border-t border-ink/10 bg-ink text-sand-200">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="grid gap-10 md:grid-cols-4">
            <div className="md:col-span-2">
              <div className="flex items-center gap-2.5">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-mid text-white">
                  <Sparkles className="h-4 w-4" />
                </span>
                <span className="font-display text-lg font-bold text-sand-50">Virsa</span>
              </div>
              <p className="mt-3 max-w-md text-sm leading-relaxed text-sand-300">
                {t("footer.about")}
              </p>
              <div className="mt-4 flex flex-wrap gap-2 text-[11px]">
                {[["Live crowd insights", statusTone("Open")], ["AI-guided discovery", "bg-teal-mid text-white"], ["Festival Mode", "bg-saffron text-white"]].map(([t, tone]) => (
                  <span key={t} className={clsx("chip", tone)}>{t}</span>
                ))}
              </div>
            </div>
            <div>
              <p className="mb-3 text-xs font-bold uppercase tracking-widest text-sand-400">{t("footer.explore")}</p>
              <ul className="space-y-2 text-sm">
                {NAV.map((n) => (
                  <li key={n.to}>
                    <Link className="text-sand-300 hover:text-saffron" to={n.to}>{t(n.k)}</Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="mb-3 text-xs font-bold uppercase tracking-widest text-sand-400">{t("footer.community")}</p>
              <ul className="space-y-2 text-sm">
                <li><Link className="text-sand-300 hover:text-saffron" to="/report">{t("footer.report")}</Link></li>
                <li><Link className="text-sand-300 hover:text-saffron" to="/my-reports">{t("footer.track")}</Link></li>
                <li><Link className="text-sand-300 hover:text-saffron" to="/login">{t("actions.signin")}</Link></li>
                <li><Link className="text-sand-300 hover:text-saffron" to="/guide">{t("footer.askGuide")}</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-10 flex flex-col gap-3 border-t border-sand-200/10 pt-6 text-xs text-sand-400 sm:flex-row sm:items-center sm:justify-between">
            <p>© 2026 Virsa · SIH Demo · {destShort(current)}, {current?.state ?? "Gujarat"}.</p>
            <div className="flex items-center gap-3">
              <span className="hidden sm:inline">Community-Centric Intelligent Tourism Ecosystem</span>
              <ListenButton
                text={() => {
                  const el = document.querySelector("main");
                  return el ? (el as HTMLElement).innerText : "";
                }}
                variant="outline"
                iconOnly
                className="!border-sand-200/20 !bg-transparent !text-sand-300"
              />
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}