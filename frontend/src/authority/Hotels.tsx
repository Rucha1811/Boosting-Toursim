import { BedDouble, TrendingUp, CalendarClock } from "lucide-react";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import type { Business } from "../lib/types";
import { PageHead, Load, Stat } from "./shared";
import { Spinner } from "../components/ui";

interface Agg {
  registered_hotels: number;
  occupancy_pct: number;
  expected_occupancy_pct: number;
  available_rooms: number;
  is_demo: boolean;
}

export default function HotelsPage() {
  const { data: agg, loading: la, error: ea } = usePoll<Agg>(() => endpoints.hotelsAggregateAdmin() as unknown as Promise<Agg>, 30000);
  const { data: hotels, loading, error } = usePoll<Business[]>(() => endpoints.hotels(), 60000);

  return (
    <div>
      <PageHead
        kicker="Accommodation"
        title="Hotel occupancy"
        sub="Aggregate occupancy across registered stays, with festival uplift forecast."
      />
      <Load data={agg} loading={la} error={ea}>
        {(a) => (
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            <Stat tone="saffron" icon={<BedDouble className="h-5 w-5" />} label="Occupancy tonight" value={`${a.occupancy_pct}%`} sub={`expected ${a.expected_occupancy_pct}%`} />
            <Stat tone="teal" icon={<CalendarClock className="h-5 w-5" />} label="Rooms free tonight" value={a.available_rooms} />
            <Stat tone="ink" icon={<TrendingUp className="h-5 w-5" />} label="Registered stays" value={a.registered_hotels} sub={a.is_demo ? "demo aggregate" : "live"} />
          </div>
        )}
      </Load>

      {loading && <Spinner />}
      {error && !hotels && <p className="text-sm text-blush">Failed to load hotels: {error}</p>}
      {(hotels ?? []).length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {hotels?.map((h) => (
            <div key={h.id} className="card p-5">
              <p className="text-[11px] uppercase tracking-wide text-ink-faint">{h.kind}</p>
              <h3 className="mt-1 font-display text-base font-semibold text-ink">{h.name}</h3>
              <p className="mt-1 line-clamp-2 text-xs text-ink-muted">{h.description}</p>
              <p className="mt-3 text-xs text-ink-muted">Pricing: {h.price_range || "—"}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}