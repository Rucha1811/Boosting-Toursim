import { Link } from "react-router-dom";
import {
  Users,
  TrendingUp,
  BedDouble,
  Flag,
  BellRing,
  PartyPopper,
  ArrowRight,
  TriangleAlert,
  ThermometerSun,
} from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { destShort } from "../lib/destCopy";
import { useDestination } from "../state/destination";
import type { Overview } from "../lib/types";
import { fmtNum, crowdMeta } from "../lib/catalog";
import { PageHead, Stat, Load, levelTone } from "./shared";

export default function OverviewPage() {
  const { current, currentId } = useDestination();
  const { data, loading, error } = usePoll<Overview>(() => endpoints.overview(), 20000, [currentId]);

  return (
    <div>
      <PageHead
        kicker="Command Center"
        title={`${destShort(current)} tourism, live`}
        sub="Status refreshes every few seconds from the simulator. Everything you see is demo telemetry."
        right={
          <span className="chip bg-emerald-100 text-emerald-800">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
            </span>
            Live
          </span>
        }
      />

      <Load data={data} loading={loading} error={error}>
        {(o) => (
          <div className="space-y-6">
            {/* Stat grid */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Stat tone="teal" icon={<Users className="h-5 w-5" />} label="Visitors in the city now" value={fmtNum(o.current_visitors)} sub={`Inflow today ~${fmtNum(o.estimated_inflow_today)} · expected ${fmtNum(o.expected_inflow_today)}`} />
              <Stat tone="saffron" icon={<BedDouble className="h-5 w-5" />} label="Hotel occupancy" value={`${o.hotel_occupancy_pct}%`} sub={`${o.registered_hotels} registered stays`} />
              <Stat tone="blush" icon={<Flag className="h-5 w-5" />} label="Open community reports" value={o.open_reports} sub={`${o.resolved_reports} resolved this week`} />
              <Stat tone="ink" icon={<BellRing className="h-5 w-5" />} label="Active alerts" value={o.active_alerts} />
            </div>

            {/* Festival + Forecast banner */}
            <div className="grid gap-4 lg:grid-cols-2">
              {o.festival && (
                <div className="card relative overflow-hidden border-saffron/30 p-5">
                  <div className="absolute -right-6 -top-6 h-28 w-28 rounded-full bg-saffron/10" />
                  <div className="flex items-center gap-2">
                    <PartyPopper className="h-5 w-5 text-saffron-deep" />
                    <p className="text-xs font-bold uppercase tracking-wider text-saffron-deep">Festival Mode · {o.festival.status}</p>
                  </div>
                  <h3 className="mt-2 font-display text-xl font-bold text-ink">{o.festival.name}</h3>
                  <p className="mt-1 text-sm text-ink-muted">
                    {o.festival.start_date} → {o.festival.end_date} · ~{fmtNum(o.festival.expected_visitors)} expected
                  </p>
                  <p className="mt-3 text-sm text-ink-soft">{o.festival.subtitle}</p>
                </div>
              )}
              {o.forecast && (
                <div className="card p-5">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-teal" />
                    <p className="text-xs font-bold uppercase tracking-wider text-teal-deep">Tomorrow forecast</p>
                  </div>
                  <div className="mt-3 flex items-end gap-3">
                    <p className="font-display text-4xl font-bold text-ink">{fmtNum(o.forecast.expected_visitors)}</p>
                    <p className="pb-1 text-xs text-ink-muted">expected · {o.forecast.event_name}</p>
                  </div>
                  <p className="mt-1 text-xs text-ink-muted">
                    Peak {o.forecast.expected_peak_start}–{o.forecast.expected_peak_end} · method: {o.forecast.method}
                  </p>
                  {o.forecast.high_footfall_zones?.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {o.forecast.high_footfall_zones.map((z) => (
                        <span key={z.zone} className="chip bg-saffron-light text-saffron-deep">{z.zone}: {fmtNum(z.expected)}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Notable places */}
            <div className="card p-5">
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-2 font-display text-lg font-semibold text-ink">
                  <ThermometerSun className="h-5 w-5 text-saffron-deep" /> Notable crowd spots
                </h2>
                <Link to="/authority/crowd" className="flex items-center gap-1 text-xs font-semibold text-teal-deep hover:text-saffron-deep">
                  Manage crowds <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="text-[11px] uppercase tracking-wider text-ink-faint">
                    <tr>
                      <th className="pb-2 pr-4">Place</th>
                      <th className="pb-2 pr-4">Now</th>
                      <th className="pb-2 pr-4">Capacity</th>
                      <th className="pb-2 pr-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-ink/5">
                    {o.notable_places.map((p) => (
                      <tr key={p.place_id} className="hover:bg-sand-50">
                        <td className="py-2.5 pr-4 font-medium text-ink">{p.name}</td>
                        <td className="py-2.5 pr-4 text-ink-soft">{fmtNum(p.visitors)}</td>
                        <td className="py-2.5 pr-4 text-ink-muted">{fmtNum(p.capacity)}</td>
                        <td className="py-2.5">
                          <span className={clsx("chip", levelTone(p.level))}>{p.level}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              {/* Active events */}
              <div className="card p-5">
                <h2 className="font-display text-lg font-semibold text-ink">Events today</h2>
                {o.active_events.length === 0 ? (
                  <p className="mt-2 text-sm text-ink-muted">No events on the books for today.</p>
                ) : (
                  <div className="mt-3 space-y-2">
                    {o.active_events.map((e) => (
                      <div key={e.id} className="flex items-center justify-between rounded-xl bg-sand-50 px-3 py-2.5">
                        <div>
                          <p className="text-sm font-semibold text-ink">{e.name}</p>
                          <p className="text-[11px] text-ink-muted">{e.location_name} · {e.start_time}</p>
                        </div>
                        <span className="chip bg-blush-light text-blush">{fmtNum(e.expected_visitors)} expected</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Recent alerts */}
              <div className="card p-5">
                <div className="flex items-center justify-between">
                  <h2 className="font-display text-lg font-semibold text-ink">Active alerts</h2>
                  <Link to="/authority/alerts" className="text-xs font-semibold text-teal-deep hover:text-saffron-deep">Manage</Link>
                </div>
                {o.recent_alerts.length === 0 ? (
                  <p className="mt-2 text-sm text-ink-muted">No active alerts — visitors see a clear city.</p>
                ) : (
                  <div className="mt-3 space-y-2">
                    {o.recent_alerts.map((a) => (
                      <div key={a.id} className="flex items-start gap-3 rounded-xl bg-sand-50 px-3 py-2.5">
                        <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0 text-blush" />
                        <div>
                          <p className="text-sm font-semibold text-ink">{a.title}</p>
                          <p className="text-[11px] text-ink-muted">{a.message}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </Load>
    </div>
  );
}