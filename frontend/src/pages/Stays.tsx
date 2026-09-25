import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BedDouble, MapPin, Home as HomeIcon } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { destShort } from "../lib/destCopy";
import { useDestination } from "../state/destination";
import type { Business } from "../lib/types";
import { fmtNum } from "../lib/catalog";
import Img from "../components/Img";
import { SectionTitle, Spinner, ErrorNote } from "../components/ui";

interface Agg {
  registered_hotels: number;
  occupancy_pct: number;
  expected_occupancy_pct: number;
  available_rooms: number;
}

export default function StaysPage() {
  const { current, currentId } = useDestination();
  const { data: hotels, loading, error } = usePoll<Business[]>(() => endpoints.hotels(), 60000, [currentId]);
  const [type, setType] = useState("All");

  const list = useMemo(() => {
    let l = hotels ?? [];
    if (type !== "All") l = l.filter((h) => h.kind === type.toLowerCase());
    return l;
  }, [hotels, type]);

  const live = usePoll<Agg | null>(async () => (await endpoints.hotelsAggregate().catch(() => null)) as Agg | null, 45000, [currentId]);

  return (
    <div className="animate-fade-up mx-auto max-w-7xl px-6 py-10">
      <header className="max-w-2xl">
        <p className="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-saffron-deep">Stay</p>
        <h1 className="font-display text-3xl font-bold text-ink sm:text-4xl">Wake up inside the heritage</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Hotels and homestays registered with the {destShort(current)} tourism ecosystem.
        </p>
      </header>

      {live.data && (
        <div className="mt-6 grid max-w-3xl grid-cols-3 gap-3">
          {[
            [<BedDouble className="h-4 w-4" />, "Registered stays", `${live.data.registered_hotels}`],
            ["Occupied", `${live.data.occupancy_pct}%`, "right now"],
            ["Rooms free", `${live.data.available_rooms}`, "tonight"],
          ].map(([i, l, v]) => (
            <div key={String(l)} className="card !p-4">
              <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-ink-faint"><span className="text-teal">{i}</span> {l}</p>
              <p className="mt-1 font-display text-2xl font-bold text-ink">{v}</p>
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 flex gap-2">
        {["All", "Hotel", "Homestay"].map((t) => (
          <button key={t} onClick={() => setType(t)} className={clsx("rounded-full px-3.5 py-1.5 text-xs font-semibold", type === t ? "bg-teal text-white" : "bg-white text-ink-soft")}>
            {t}
          </button>
        ))}
      </div>

      {loading && <Spinner />}
      {error && <ErrorNote text={error} />}

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {list.map((h) => (
          <Link key={h.id} to={`/artisans/${h.id}`} className="card group overflow-hidden transition hover:-translate-y-1 hover:shadow-lift">
            <div className="relative">
              <Img src={h.image_urls?.[0]} alt={h.name} className="h-44" />
              <span className="chip absolute left-3 top-3 bg-white/90 text-ink backdrop-blur">
                {h.kind === "homestay" ? <HomeIcon className="h-3 w-3" /> : <BedDouble className="h-3 w-3" />} {h.kind}
              </span>
            </div>
            <div className="p-5">
              <h3 className="font-display text-lg font-semibold text-ink group-hover:text-teal-deep">{h.name}</h3>
              <p className="mt-1 line-clamp-2 text-sm text-ink-muted">{h.description}</p>
              <div className="mt-3 flex items-center gap-2 text-xs text-ink-muted">
                <MapPin className="h-3.5 w-3.5 text-teal" /> {h.price_range || "On request"}
              </div>
              <span className={clsx("chip mt-3", h.status === "Open" ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800")}>
                <BedDouble className="h-3 w-3" /> {h.status}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}