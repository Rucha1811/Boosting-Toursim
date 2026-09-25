import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { MapContainer, TileLayer, Marker, Tooltip, Popup } from "react-leaflet";
import {
  ArrowRight,
  PartyPopper,
  ShieldAlert,
  ParkingCircle,
  ChevronRight,
  Compass,
  Sparkles,
  X,
  Search,
  Loader2,
  TriangleAlert,
  Clock3,
  Users,
} from "lucide-react";
import { clsx } from "clsx";
import { usePoll, useDynamicInfo } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { pinIcon, heatPin, defaultCenter, defaultZoom } from "../lib/leaflet";
import { cat, crowdMeta } from "../lib/catalog";
import { destShort, getDestCopy } from "../lib/destCopy";
import { useDestination } from "../state/destination";
import type { Marker as MarkerT, Place } from "../lib/types";
import { fmtNum } from "../lib/catalog";
import Img from "../components/Img";
import { useAuth } from "../state/auth";
import { routeFor } from "../state/auth";

function MiniHeader() {
  const { user } = useAuth();
  const { current } = useDestination();
  const go = routeFor(user?.role ?? "tourist");
  return (
    <div className="pointer-events-none absolute inset-x-0 top-0 z-[1000]">
      <div className="pointer-events-auto flex items-center justify-between gap-3 border-b border-white/20 bg-teal-dark/80 px-4 py-2.5 text-white backdrop-blur-md sm:px-6">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-saffron text-teal-dark">
            <Sparkles className="h-4 w-4" />
          </span>
          <span className="leading-tight">
            <span className="block font-display text-base font-bold">Virsa Map</span>
            <span className="block text-[9px] uppercase tracking-[0.2em] text-sand-200">
              Live {destShort(current)} · heritage
            </span>
          </span>
        </Link>
        <div className="flex items-center gap-2 text-xs">
          {user ? (
            <Link to={go ?? "/"} className="rounded-full bg-white/15 px-3 py-1.5 font-semibold backdrop-blur hover:bg-white/25">
              {user.name.split(" ")[0]}
            </Link>
          ) : (
            <Link to="/login" className="rounded-full bg-saffron px-3 py-1.5 font-semibold text-teal-dark hover:bg-saffron-deep">
              Sign in
            </Link>
          )}
          <Link to="/" className="rounded-full bg-white/15 px-3 py-1.5 font-medium hover:bg-white/25">
            Home
          </Link>
        </div>
      </div>
    </div>
  );
}

function LiveStrip({ expand, onToggle, alerts, closures, parking, recs }: {
  expand: boolean;
  onToggle: () => void;
  alerts: number;
  closures: number;
  parking: number;
  recs: number;
}) {
  return (
    <button
      onClick={onToggle}
      className="pointer-events-auto absolute bottom-0 inset-x-0 z-[1000] flex items-center gap-2 border-t border-ink/10 bg-white/90 px-3 py-2 text-xs font-medium text-ink backdrop-blur-md sm:hidden"
    >
      {expand ? <ChevronRight className="h-3.5 w-3.5 rotate-90" /> : <ChevronRight className="h-3.5 w-3.5" />}
      Live
      {alerts > 0 && <span className="chip bg-blush-light text-blush"><TriangleAlert className="h-3 w-3" />{alerts} alerts</span>}
      {closures > 0 && <span className="chip bg-sky-100 text-sky-800">{closures} closures</span>}
      {parking > 0 && <span className="chip bg-emerald-100 text-emerald-800">{parking} parking</span>}
    </button>
  );
}

export default function ExploreMap() {
  const { current, currentId } = useDestination();
  const dc = getDestCopy(currentId);
  const { data: markers, loading } = usePoll<MarkerT[]>(() => endpoints.markers(), 45000, [currentId]);
  const { data: info } = useDynamicInfo(30000, [currentId]);
  const [catFilter, setCatFilter] = useState<string[]>([]);
  const [sel, setSel] = useState<MarkerT | null>(null);
  const [q, setQ] = useState("");
  const [panel, setPanel] = useState<"live" | "guide">("live");

  const counts = useMemo(() => {
    const m = new Map<string, number>();
    (markers ?? []).forEach((x) => {
      const k = x.type === "place" ? x.category : x.type;
      m.set(k, (m.get(k) ?? 0) + 1);
    });
    return m;
  }, [markers]);

  const filtered = useMemo(() => {
    let list = markers ?? [];
    if (catFilter.length) {
      list = list.filter((x) => (x.type === "place" ? catFilter.includes(x.category) : catFilter.includes(x.type)));
    }
    if (q.trim()) {
      list = list.filter((x) => x.name.toLowerCase().includes(q.toLowerCase()));
    }
    return list;
  }, [markers, catFilter, q]);

  const busyPlaces = useMemo(
    () =>
      (markers ?? [])
        .filter((x) => x.type === "place" && x.crowd && x.crowd !== "low")
        .sort((a, b) => (b.crowd === "critical" ? 1 : 0) + (b.crowd === "high" ? 2 : 0) - ((a.crowd === "critical" ? 1 : 0) + (a.crowd === "high" ? 2 : 0))),
    [markers],
  );

  const toggleCat = (k: string) =>
    setCatFilter((p) => (p.includes(k) ? p.filter((x) => x !== k) : [...p, k]));

  const filterChips = [
    { key: "heritage", label: "Heritage", tone: "text-saffron" },
    { key: "temple", label: "Temples", tone: "text-marigold" },
    { key: "museum", label: "Museums", tone: "text-blush" },
    { key: "artisans", label: "Artisans", tone: "text-teal" },
    { key: "market", label: "Markets", tone: "text-amber-800" },
    { key: "food", label: "Food", tone: "text-red-600" },
    { key: "culture", label: "Culture", tone: "text-rose-500" },
    { key: "experience", label: "Experiences", tone: "text-pink-600" },
    { key: "hotel", label: "Hotels", tone: "text-blue-700" },
  ];

  return (
    <div className="fixed inset-0 overflow-hidden bg-sand-100">
      <MiniHeader />

      {/* Filters + search (left overlay) */}
      <div className="pointer-events-none absolute left-3 top-16 z-[1000] w-[300px] max-w-[88vw] sm:top-[4.2rem]">
        <div className="pointer-events-auto rounded-2xl bg-white/90 p-3 shadow-lift backdrop-blur-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search places, markets, artisans…"
              className="input !py-2 pl-9"
            />
          </div>
          <div className="mt-2.5 flex flex-wrap gap-1.5">
            {filterChips.map((c) => (
              <button
                key={c.key}
                onClick={() => toggleCat(c.key)}
                className={clsx(
                  "rounded-full px-2.5 py-1 text-[11px] font-semibold transition",
                  catFilter.includes(c.key)
                    ? "bg-ink text-sand-100"
                    : "bg-sand-100 text-ink-soft hover:bg-sand-200",
                )}
              >
                {c.label}
              </button>
            ))}
          </div>
          <div className="mt-2 border-t border-ink/5 pt-2">
            <p className="text-[10px] font-semibold text-ink-muted">
              {filtered.length} spots · {busyPlaces.length} highlighted by live crowd
              {loading && <Loader2 className="ml-1 inline h-3 w-3 animate-spin" />}
            </p>
          </div>
        </div>

        {/* Busy now list */}
        {busyPlaces.length > 0 && (
          <div className="pointer-events-auto mt-2 hidden max-h-[34vh] overflow-auto rounded-2xl bg-white/90 shadow-lift backdrop-blur-md sm:block">
            <p className="sticky top-0 bg-white/95 px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-ink-muted backdrop-blur">
              Busy right now
            </p>
            {busyPlaces.slice(0, 6).map((m) => {
              const cm = crowdMeta(m.crowd ?? "low");
              return (
                <button
                  key={m.id}
                  onClick={() => setSel(m)}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-sand-100"
                >
                  <span className={clsx("h-2 w-2 shrink-0 rounded-full", cm.tone)} />
                  <span className="flex-1 truncate text-xs font-medium text-ink">{m.name}</span>
                  <span className="text-[10px] text-ink-muted">{fmtNum(m.visitors ?? 0)}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Live panel (right overlay) */}
      <div className="absolute right-3 top-16 z-[1000] hidden w-[320px] flex-col gap-3 sm:flex">
        {info?.recommendations && info.recommendations.length > 0 && (
          <div className="pointer-events-auto rounded-2xl border border-saffron/40 bg-gradient-to-br from-saffron-light to-white p-4 shadow-lift">
            <div className="flex items-center gap-2">
              <span className="chip bg-saffron text-white"><Compass className="h-3 w-3" /> Visit instead</span>
              <span className="text-[10px] font-semibold uppercase tracking-wide text-saffron-deep">
                authority approved
              </span>
            </div>
            <p className="mt-2 font-display text-sm font-semibold text-ink">
              {info.recommendations[0].source_place_name} is crowded now.
            </p>
            <div className="mt-2 space-y-1.5">
              {info.recommendations[0].alternatives.slice(0, 3).map((a) => (
                <Link
                  key={a.id}
                  to={`/places/${a.id}`}
                  className="flex items-center justify-between gap-2 rounded-xl bg-white px-3 py-2 text-xs font-medium text-teal-deep shadow-card hover:text-saffron-deep"
                >
                  {a.name}
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              ))}
            </div>
          </div>
        )}
        <div className="pointer-events-auto rounded-2xl bg-white/90 shadow-lift backdrop-blur-md">
          <div className="flex border-b border-ink/5">
            {(["live", "guide"] as const).map((p) => (
              <button
                key={p}
                onClick={() => setPanel(p)}
                className={clsx(
                  "flex-1 px-3 py-2 text-center text-xs font-semibold capitalize",
                  panel === p ? "border-b-2 border-teal text-teal-deep" : "text-ink-muted",
                )}
              >
                {p === "live" ? "Live updates" : "Heritage guide"}
              </button>
            ))}
          </div>
          <div className="max-h-[52vh] space-y-2.5 overflow-y-auto p-3">
            {panel === "live" && (
              <>
                {!info?.alerts.length && !info?.road_closures.length && !info?.temporary_parking.length && (
                  <p className="px-2 py-4 text-center text-xs text-ink-muted">All clear across {destShort(current)} right now.</p>
                )}
                {info?.alerts.map((a) => (
                  <LiveItem key={a.id} icon={<TriangleAlert className="h-4 w-4 text-blush" />} title={a.title} sub={`${a.message}${a.place_name ? ` · near ${a.place_name}` : ""}`} />
                ))}
                {info?.road_closures.map((c) => (
                  <LiveItem
                    key={c.id}
                    icon={<ShieldAlert className="h-4 w-4 text-sky-700" />}
                    title={`${c.road_name} closure`}
                    sub={`${c.description} · detour: ${c.alternate_route}`}
                  />
                ))}
                {info?.temporary_parking.map((p) => (
                  <LiveItem key={p.id} icon={<ParkingCircle className="h-4 w-4 text-emerald-700" />} title={p.name} sub={`${p.available}/${p.capacity} bays · ${p.notes}`} />
                ))}
                {info?.announcements.map((a) => (
                  <LiveItem key={a.id} icon={<Sparkles className="h-4 w-4 text-saffron" />} title={a.title} sub={a.body} />
                ))}
              </>
            )}
            {panel === "guide" && (
              <div className="space-y-3">
                <p className="text-xs leading-relaxed text-ink-soft">
                  {dc.itineraryTrail}
                </p>
                {dc.itineraryStops.map(([t, d]) => (
                  <div key={t} className="rounded-xl bg-sand-100 p-3">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-saffron-deep">{t}</p>
                    <p className="mt-1 text-xs text-ink-soft">{d}</p>
                  </div>
                ))}
                <Link to="/guide" className="flex items-center gap-1 text-xs font-semibold text-teal-deep hover:text-saffron-deep">
                  Ask the Virsa Guide <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Live strip for mobile handled by <LiveStrip> */}
      <LiveStrip
        expand={panel === "live"}
        onToggle={() => setPanel(panel === "live" ? "guide" : "live")}
        alerts={info?.alerts.length ?? 0}
        closures={info?.road_closures.length ?? 0}
        parking={info?.temporary_parking.length ?? 0}
        recs={info?.recommendations.length ?? 0}
      />

      {/* Map */}
      <MapContainer
        key={`explore-${currentId}`}
        center={current ? [current.center_lat, current.center_lng] : defaultCenter}
        zoom={current ? current.zoom : defaultZoom}
        className="h-full w-full"
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {filtered.map((m) => {
          const base = m.type === "place" ? cat(m.category) : m.type === "artisans" || m.type === "business" ? cat(m.category) : cat(m.type);
          const crowd = m.crowd;
          const size = crowd === "critical" || crowd === "high" ? "lg" : crowd === "moderate" ? "md" : "sm";
          return (
            <Marker
              key={`${m.type}-${m.id}`}
              position={[m.lat, m.lng]}
              icon={pinIcon(base.color, m.type, size, crowd)}
              eventHandlers={{ click: () => setSel(m) }}
            >
              <Tooltip direction="top" offset={[0, -26]} opacity={0.95}>
                <span className="text-xs font-semibold">{m.name}</span>
                {m.crowd && !["transport", "emergency", "parking"].includes(m.type) && (
                  <span> · {crowdMeta(m.crowd).label}</span>
                )}
              </Tooltip>
            </Marker>
          );
        })}
        {info?.road_closures.map((c) => (
          <Marker key={`clo-${c.id}`} position={[c.lat ?? current?.center_lat ?? defaultCenter[0], c.lng ?? current?.center_lng ?? defaultCenter[1]]} icon={heatPin()}>
            <Popup>
              <div className="text-xs">
                <p className="font-bold">{c.road_name}</p>
                <p>{c.alternate_route}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Selected place card */}
      {sel && (
        <div className="absolute bottom-0 left-1/2 z-[1200] w-[min(560px,94vw)] -translate-x-1/2 pb-3 sm:bottom-4">
          <div className="card overflow-hidden shadow-lift">
            <div className="flex gap-3 p-3">
              <Img src={sel.image} alt={sel.name} className="h-24 w-24 shrink-0 rounded-xl sm:h-28 sm:w-28" />
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-display text-lg font-semibold leading-tight text-ink">{sel.name}</p>
                    <p className="text-[11px] font-medium uppercase tracking-wide text-ink-faint">
                      {cat(sel.category).label}
                      {sel.subtitle ? ` · ${sel.subtitle}` : ""}
                    </p>
                  </div>
                  <button onClick={() => setSel(null)} className="rounded-full p-1.5 text-ink-muted hover:bg-ink/5">
                    <X className="h-4 w-4" />
                  </button>
                </div>
                {sel.crowd && ["place"].includes(sel.type) && (
                  <div className="mt-1.5 flex items-center gap-2">
                    <span className={clsx("chip", crowdMeta(sel.crowd).tone)}>
                      <Users className="h-3 w-3" /> {crowdMeta(sel.crowd).label}
                    </span>
                    {sel.visitors !== undefined && (
                      <span className="text-[11px] text-ink-muted">{fmtNum(sel.visitors)} people near here now</span>
                    )}
                  </div>
                )}
                <div className="mt-2 flex items-center gap-3 text-[11px] text-ink-muted">
                  {sel.status && sel.status !== "Open" && <span className="chip bg-amber-100 text-amber-800">{sel.status}</span>}
                  {sel.temporary && <span className="chip bg-emerald-100 text-emerald-800">Temporary</span>}
                </div>
              </div>
            </div>
            <div className="flex items-center justify-between gap-2 border-t border-ink/5 bg-sand-50 px-3 py-2">
              <Link
                to={sel.type === "place"
                  ? `/places/${sel.entity_id}`
                  : sel.type === "artisans" || sel.type === "business"
                    ? `/artisans/${sel.entity_id}`
                    : sel.type === "experience"
                      ? `/experiences/${sel.entity_id}`
                      : "/map"}
                className="btn btn-primary btn-sm"
              >
                {sel.type === "place" ? "Discover this heritage" : "View details"}{" "}
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
              <span className="text-[11px] text-ink-muted">Live location · tap X to close</span>
            </div>
          </div>
        </div>
      )}

      <div className="absolute bottom-2 right-2 z-[1100] hidden items-center gap-1.5 text-[10px] font-medium text-ink-muted sm:flex">
        <span className="rounded-full bg-white/85 px-2 py-1 shadow-card backdrop-blur">
          Pan & zoom to explore · pins glow with live crowd
        </span>
      </div>
    </div>
  );
}

function LiveItem({ icon, title, sub }: { icon: React.ReactNode; title: string; sub: string }) {
  return (
    <div className="flex items-start gap-2.5 rounded-xl bg-sand-50 p-2.5">
      <span className="mt-0.5 shrink-0">{icon}</span>
      <div className="min-w-0">
        <p className="text-xs font-bold text-ink">{title}</p>
        <p className="mt-0.5 line-clamp-2 text-[11px] leading-snug text-ink-muted">{sub}</p>
      </div>
    </div>
  );
}