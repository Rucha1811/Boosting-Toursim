import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  PartyPopper,
  ArrowRight,
  Calendar,
  MapPin,
  Users,
  Clock,
  TrafficCone,
  ParkingCircle,
  Sparkles,
  Plus,
  Minus,
} from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useDestination } from "../state/destination";
import { fmtNum } from "../lib/catalog";
import type { Festival, Event } from "../lib/types";
import Img from "../components/Img";
import { SectionTitle, Spinner, ErrorNote } from "../components/ui";

function dateRange(f: Festival): string {
  const fmt = (s: string) => new Date(s).toLocaleDateString("en-IN", { month: "short", day: "numeric" });
  return `${fmt(f.start_date)} – ${fmt(f.end_date)}`;
}

export function FestivalsPage() {
  const { currentId } = useDestination();
  const { data: festivals, loading, error } = usePoll<Festival[]>(() => endpoints.festivals(), 60000, [currentId]);

  return (
    <div className="animate-fade-up mx-auto max-w-7xl px-6 py-10">
      <header className="max-w-2xl">
        <p className="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-saffron-deep">Festival Mode</p>
        <h1 className="font-display text-3xl font-bold text-ink sm:text-4xl">Celebrate with the city</h1>
        <p className="mt-2 text-sm text-ink-muted">
          During big festivals the ecosystem shifts into <span className="font-semibold text-saffron-deep">Festival Mode</span> —
          live capacity guidance, alternative routes and artist-led suggestions flow straight to the map.
        </p>
      </header>

      {loading && <Spinner />}
      {error && <ErrorNote text={error} />}

      <div className="mt-8 space-y-6">
        {(festivals ?? []).map((f) => {
          const live = f.status === "live";
          const upcoming = f.status === "upcoming";
          return (
            <Link key={f.id} to={`/festivals/${f.id}`} className="card group grid overflow-hidden transition hover:shadow-lift md:grid-cols-[1fr_2fr]">
              <div className="relative">
                <Img src={f.hero_image_url} alt={f.name} className="h-56 md:h-full" />
                <span className={clsx("chip absolute left-3 top-3", live ? "bg-saffron text-white" : upcoming ? "bg-teal text-white" : "bg-white/90 text-ink")}>
                  <PartyPopper className={live ? "h-3 w-3 animate-pulse" : "h-3 w-3"} />
                  {live ? "Live now" : upcoming ? "Upcoming" : "Past"}
                </span>
              </div>
              <div className="flex flex-col justify-center p-7">
                <h2 className="font-display text-2xl font-bold text-ink group-hover:text-teal-deep sm:text-3xl">{f.name}</h2>
                <p className="mt-1 text-sm text-ink-muted">{f.subtitle}</p>
                <p className="mt-3 text-sm leading-relaxed text-ink-soft">{f.description}</p>
                <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-ink-muted">
                  <span className="flex items-center gap-1.5"><Calendar className="h-4 w-4 text-saffron-deep" /> {dateRange(f)}</span>
                  <span className="flex items-center gap-1.5"><Users className="h-4 w-4 text-teal" /> ~{fmtNum(f.expected_visitors)} expected</span>
                </div>
                <span className="mt-5 inline-flex w-fit items-center gap-2 rounded-full bg-teal px-4 py-2 text-sm font-semibold text-white transition group-hover:gap-3">
                  {live ? "Enter festival mode" : "See the plan"} <ArrowRight className="h-4 w-4" />
                </span>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export function FestivalDetailPage() {
  const { id } = useParams();
  const fid = Number(id);
  const { data, loading, error } = usePoll<{ festival: Festival; events: Event[] }>(() => endpoints.festival(fid), 45000, [fid]);
  const [showSchedule, setShowSchedule] = useState(false);

  const schedule = useMemo(() => Object.entries(data?.festival.schedule_json ?? {}), [data?.festival.schedule_json]);

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [fid]);

  if (loading && !data) return <div className="mx-auto max-w-7xl px-6 py-10"><Spinner /></div>;
  if (error && !data) return <div className="mx-auto max-w-7xl px-6 py-10"><ErrorNote text={error} /></div>;
  if (!data) return null;

  const { festival: f, events } = data;
  const live = f.status === "live";
  const totalEvents = events.length;

  return (
    <div className="animate-fade-up">
      {/* HERO */}
      <section className="relative">
        <Img src={f.hero_image_url} alt={f.name} className="h-[52vh] min-h-[400px]" />
        <div className="absolute inset-0 bg-gradient-to-t from-ink/90 via-ink/30 to-transparent" />
        <div className="absolute inset-x-0 bottom-0">
          <div className="mx-auto max-w-7xl px-6 pb-8">
            <div className="flex flex-wrap items-center gap-2">
              <span className={clsx("chip", live ? "bg-saffron text-white" : "bg-teal-mid text-white")}>
                <PartyPopper className={live ? "h-3.5 w-3.5 animate-pulse" : "h-3.5 w-3.5"} />
                {live ? "FESTIVAL MODE · LIVE" : f.status.toUpperCase()}
              </span>
              <span className="chip bg-white/20 text-white backdrop-blur"><Calendar className="h-3.5 w-3.5" /> {dateRange(f)}</span>
            </div>
            <h1 className="mt-3 font-display text-4xl font-bold text-white sm:text-6xl">{f.name}</h1>
            <p className="mt-2 max-w-2xl text-sm text-sand-200 sm:text-base">{f.subtitle}</p>
            <div className="mt-4 flex flex-wrap gap-6 text-xs text-sand-200">
              <span className="flex items-center gap-1.5"><Users className="h-4 w-4" /> ~{fmtNum(f.expected_visitors)} visitors expected</span>
              <span className="flex items-center gap-1.5"><Sparkles className="h-4 w-4" /> {totalEvents} curated events</span>
              {f.capacity != null && <span className="flex items-center gap-1.5">Manageable capacity: {fmtNum(f.capacity)}</span>}
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-6 py-10">
        {live && (
          <div className="mb-8 rounded-2xl border border-marigold/40 bg-marigold-light p-5">
            <p className="flex items-center gap-2 text-sm font-bold text-amber-800">
              <Sparkles className="h-4 w-4" /> Festival Mode is active
            </p>
            <p className="mt-1 text-sm text-ink-soft">
              Live recommendations divert crowds from peak venues, temporary parking is open, and the tourism authority is
              monitoring every venue on the live map. Your map refreshes automatically.
            </p>
            <Link to="/map" className="btn btn-dark btn-sm mt-3">
              <PartyPopper className="h-4 w-4" /> Open the live festival map
            </Link>
          </div>
        )}

        {/* EVENTS */}
        <SectionTitle
          kicker="The programme"
          title="Events across the city"
          sub="Each event includes expected crowd and authority-planned traffic and parking guidance."
        />
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {events.map((e) => (
            <div key={e.id} className="card flex flex-col p-5">
              <div className="flex items-center justify-between gap-2">
                <span className="chip bg-blush-light text-blush">{e.category}</span>
                {e.status !== "Open" && <span className="chip bg-amber-100 text-amber-800">{e.status}</span>}
              </div>
              <h3 className="mt-3 font-display text-lg font-semibold text-ink">{e.name}</h3>
              <p className="mt-1 line-clamp-2 text-sm text-ink-muted">{e.description}</p>
              <div className="mt-3 space-y-1.5 text-xs text-ink-muted">
                <p className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5 text-teal" /> {e.location_name}</p>
                <p className="flex items-center gap-1.5"><Calendar className="h-3.5 w-3.5 text-teal" /> {e.start_date} · {e.start_time}–{e.end_time}</p>
                <p className="flex items-center gap-1.5"><Users className="h-3.5 w-3.5 text-teal" /> {fmtNum(e.expected_visitors)} expected · cap {fmtNum(e.capacity)}</p>
              </div>
              {(e.traffic_impact || e.parking_requirements) && (
                <div className="mt-3 rounded-xl bg-sand-100 p-3 text-[11px] leading-relaxed text-ink-soft">
                  {e.traffic_impact && <p className="flex items-start gap-1.5"><TrafficCone className="mt-0.5 h-3.5 w-3.5 shrink-0 text-saffron-deep" /> {e.traffic_impact}</p>}
                  {e.parking_requirements && <p className="mt-1 flex items-start gap-1.5"><ParkingCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-teal" /> {e.parking_requirements}</p>}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* SCHEDULE */}
        {schedule.length > 0 && (
          <div className="mt-12">
            <button onClick={() => setShowSchedule((s) => !s)} className="flex items-center gap-2 text-sm font-bold text-ink">
              <Calendar className="h-4 w-4 text-saffron-deep" /> Day-by-day rhythm
              {showSchedule ? <Minus className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            </button>
            {showSchedule && (
              <div className="mt-4 space-y-3">
                {schedule.map(([day, text]) => (
                  <div key={day} className="card flex gap-4 p-4">
                    <span className="w-24 shrink-0 font-display text-sm font-bold text-saffron-deep">{day}</span>
                    <p className="text-sm leading-relaxed text-ink-soft">{text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* CTA */}
        <div className="mt-12 grid gap-4 sm:grid-cols-2">
          <Link to="/map" className="card flex items-center justify-between p-6 transition hover:shadow-lift">
            <div>
              <p className="font-display text-lg font-semibold text-ink">Where is it all happening?</p>
              <p className="text-sm text-ink-muted">See every venue on the live city map.</p>
            </div>
            <ArrowRight className="h-6 w-6 text-teal" />
          </Link>
          <Link to="/guide" className="card flex items-center justify-between p-6 transition hover:shadow-lift">
            <div>
              <p className="font-display text-lg font-semibold text-ink">Not sure what to catch?</p>
              <p className="text-sm text-ink-muted">Ask the Virsa Guide to plan your festival evening.</p>
            </div>
            <Sparkles className="h-6 w-6 text-saffron-deep" />
          </Link>
        </div>
      </div>
    </div>
  );
}