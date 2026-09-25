import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  Clock3,
  MapPin,
  Landmark,
  BookOpen,
  Volume2,
  Pause,
  Users,
  Ticket,
  Utensils,
  PartyPopper,
  Compass,
  BadgeCheck,
  IndianRupee,
  Calendar,
  Sparkles,
} from "lucide-react";
import { clsx } from "clsx";
import { usePoll, useDynamicInfo } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useDestination } from "../state/destination";
import { cat, crowdMeta } from "../lib/catalog";
import type { Place, NearbyBundle, AudioStory } from "../lib/types";
import Img from "../components/Img";
import { Spinner, ErrorNote, SectionTitle, Button, Tile } from "../components/ui";

function StoryPlayer({ story }: { story: AudioStory }) {
  const [speaking, setSpeaking] = useState(false);
  const supported = "speechSynthesis" in window;

  const tell = () => {
    if (!story) return;
    const u = new SpeechSynthesisUtterance(story.narrative);
    u.lang = story.language === "hi" ? "hi-IN" : story.language === "gu" ? "gu-IN" : "en-IN";
    u.rate = 0.98;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
    setSpeaking(true);
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
  };

  return (
    <div className="rounded-2xl border border-teal/20 bg-gradient-to-br from-teal-soft to-white p-5">
      <div className="flex items-center gap-2 text-teal-deep">
        <Volume2 className="h-5 w-5" />
        <p className="text-sm font-bold uppercase tracking-wide">The story of {story.title}</p>
      </div>
      <p className="mt-3 text-sm leading-relaxed whitespace-pre-line first-letter:float-left first-letter:mr-2 first-letter:font-display first-letter:text-4xl first-letter:font-bold first-letter:text-saffron-deep">
        {story.narrative}
      </p>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        {supported ? (
          <button
            onClick={() => {
              if (speaking) {
                window.speechSynthesis.cancel();
                setSpeaking(false);
              } else {
                tell();
              }
            }}
            className="btn btn-saffron btn-md"
          >
            {speaking ? <Pause className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            {speaking ? "Pause narration" : `Listen · ${story.duration_sec}s`}
          </button>
        ) : (
          <span className="text-xs text-ink-muted">Browser narration unavailable here.</span>
        )}
        <span className="chip bg-teal/10 text-teal-deep">{story.language.toUpperCase()}</span>
        <span className="text-xs text-ink-muted">{story.language === "hi" ? "हिन्दी" : story.language === "gu" ? "ગુજરાતી" : "English"}</span>
      </div>
    </div>
  );
}

export default function PlaceDetailPage() {
  const { id } = useParams();
  const pid = Number(id);
  const navigate = useNavigate();
  const { currentId } = useDestination();
  const { data: place, loading, error } = usePoll<Place>(() => endpoints.place(pid), 45000, [pid]);
  const { data: nearby } = usePoll<NearbyBundle>(() => endpoints.nearby(pid), 60000, [pid]);
  const { data: info } = useDynamicInfo(30000, [currentId]);
  const [readMore, setReadMore] = useState(false);

  const rec = info?.recommendations.find((r) => r.source_place_id === pid)!;
  const myAlert = info?.alerts.find((a) => a.place_id === pid);

  const story = useMemo(() => {
    if (!place?.audio_stories?.length) return null;
    return (
      place.audio_stories.find((s) => s.language === "en") ||
      place.audio_stories.find((s) => s.language === "hi") ||
      place.audio_stories[0]
    );
  }, [place]);

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [pid]);

  if (loading && !place) return <div className="mx-auto max-w-7xl px-6 py-10"><Spinner /></div>;
  if (error && !place) return <div className="mx-auto max-w-7xl px-6 py-10"><ErrorNote text={error} /></div>;
  if (!place) return null;

  const cm = crowdMeta(place.crowd_level ?? "low");
  const facts: { icon: React.ReactNode; label: string; value: string }[] = [
    { icon: <Landmark className="h-4 w-4" />, label: "Period", value: place.historical_period || "—" },
    { icon: <IndianRupee className="h-4 w-4" />, label: "Entry fee", value: place.entry_fee || "Free" },
    { icon: <Clock3 className="h-4 w-4" />, label: "Best time", value: place.best_time || "—" },
    { icon: <MapPin className="h-4 w-4" />, label: "Address", value: place.address || "—" },
  ];

  return (
    <div className="animate-fade-up">
      {/* Hero */}
      <section className="relative">
        <Img src={place.image_urls?.[0]} alt={place.name} className="h-[46vh] min-h-[360px]" />
        <div className="absolute inset-0 bg-gradient-to-t from-ink/85 via-ink/25 to-transparent" />
        <div className="absolute inset-x-0 bottom-0">
          <div className="mx-auto max-w-7xl px-6 pb-6">
            <button onClick={() => navigate(-1)} className="btn btn-sm mb-3 !bg-white/15 !text-white backdrop-blur hover:!bg-white/30">
              <ArrowLeft className="h-4 w-4" /> Back
            </button>
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="chip bg-white/20 text-white backdrop-blur">{cat(place.category).label}</span>
                  {place.subcategory && <span className="chip bg-white/10 text-sand-200 backdrop-blur">{place.subcategory}</span>}
                  {place.is_featured && (
                    <span className="chip bg-saffron text-teal-dark"><Sparkles className="h-3 w-3" /> Featured</span>
                  )}
                  {place.is_hidden && <span className="chip bg-ink/60 text-sand-200">Hidden gem</span>}
                </div>
                <h1 className="mt-2 font-display text-3xl font-bold text-white sm:text-5xl">{place.name}</h1>
                <p className="mt-2 max-w-2xl text-sm text-sand-200 sm:text-base">{place.summary}</p>
              </div>
              <div className="flex flex-col gap-2">
                {place.current_visitors !== undefined && (
                  <span className={clsx("chip w-fit px-4 py-2 text-sm", cm.tone)}>
                    <Users className="h-4 w-4" /> {cm.label} · {place.current_visitors} visitors now
                  </span>
                )}
                {myAlert && (
                  <span className="chip w-fit bg-blush text-white"><Sparkles className="h-3 w-3" /> {myAlert.title}</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
          {/* MAIN COLUMN */}
          <div className="space-y-8">
            {rec && (
              <div className="rounded-2xl border border-saffron/40 bg-gradient-to-br from-saffron-light to-white p-5">
                <div className="flex items-center gap-2">
                  <Compass className="h-5 w-5 text-saffron-deep" />
                  <p className="text-sm font-bold text-saffron-deep">The tourism authority suggests</p>
                </div>
                <p className="mt-1 text-sm text-ink-soft">
                  {place.name} is near capacity right now. Visit one of these gems nearby instead, and come back later.
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {rec.alternatives.slice(0, 4).map((a) => (
                    <Link key={a.id} to={`/places/${a.id}`} className="btn btn-outline btn-sm">
                      {a.name} <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {story && <StoryPlayer story={story} />}

            <section>
              <SectionTitle kicker="In their words" title="History & significance" />
              <div className="space-y-4 text-[15px] leading-relaxed text-ink-soft">
                <p>{place.cultural_significance}</p>
                {!readMore ? (
                  <>
                    <p className="line-clamp-3">{place.history}</p>
                    <button onClick={() => setReadMore(true)} className="text-sm font-semibold text-teal-deep hover:text-saffron-deep">
                      Read more…
                    </button>
                  </>
                ) : (
                  <>
                    <p>{place.history}</p>
                    {place.architecture && (
                      <div>
                        <p className="font-display text-base font-semibold text-ink">Architecture</p>
                        <p className="mt-1">{place.architecture}</p>
                      </div>
                    )}
                    {place.traditions && (
                      <div>
                        <p className="font-display text-base font-semibold text-ink">Living traditions</p>
                        <p className="mt-1">{place.traditions}</p>
                      </div>
                    )}
                  </>
                )}
              </div>
            </section>

            {/* Gallery */}
            {(place.image_urls ?? []).length > 1 && (
              <section>
                <SectionTitle kicker="Gallery" title={`More of ${place.name}`} />
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                  {(place.image_urls ?? []).slice(1).map((u, i) => (
                    <Img key={i} src={u} alt={`${place.name} view ${i + 2}`} className="h-36 rounded-2xl" />
                  ))}
                </div>
              </section>
            )}

            <section>
              <SectionTitle kicker="Know before you go" title="Visiting notes" />
              <div className="card p-6">
                <div className="grid gap-5 sm:grid-cols-2">
                  <div className="flex items-start gap-3">
                    <Clock3 className="mt-0.5 h-5 w-5 text-teal" />
                    <div>
                      <p className="text-sm font-semibold text-ink">Opening hours</p>
                      <p className="mt-1 text-sm text-ink-muted">
                        {Object.entries(place.opening_hours || {})
                          .map(([d, h]) => `${d}: ${h}`)
                          .join("\n")}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <BookOpen className="mt-0.5 h-5 w-5 text-teal" />
                    <div>
                      <p className="text-sm font-semibold text-ink">Detailed visiting info</p>
                      <p className="mt-1 text-sm leading-relaxed text-ink-muted">{place.visiting_info || "Open through the day."}</p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* NEARBY */}
            <section>
              <SectionTitle kicker="Around the corner" title="Nearby heritage, makers & food" />
              <div className="space-y-5">
                {nearby && (nearby.places.length > 0 || nearby.artisans.length > 0 || nearby.food.length > 0 || nearby.experiences.length > 0 || nearby.events.length > 0) ? (
                  <>
                    {nearby.places.length > 0 && (
                      <NearbyRow title="More to explore" icon={<Landmark className="h-4 w-4" />}>
                        {nearby.places.map((n) => (
                          <NearbyCard key={n.id} to={`/places/${n.id}`} img={n.image_url} title={n.name} sub={`${cat(n.category).label} · ${n.distance_km} km`} by={n.activity} />
                        ))}
                      </NearbyRow>
                    )}
                    {nearby.artisans.length > 0 && (
                      <NearbyRow title="Local makers" icon={<Compass className="h-4 w-4" />}>
                        {nearby.artisans.map((n) => (
                          <NearbyCard key={n.id} to={`/artisans/${n.id}`} img={n.image_url} title={n.name} sub={`${n.craft} · ${n.distance_km} km`} />
                        ))}
                      </NearbyRow>
                    )}
                    {nearby.food.length > 0 && (
                      <NearbyRow title="Food" icon={<Utensils className="h-4 w-4" />}>
                        {nearby.food.map((n) => (
                          <NearbyCard key={n.id} to={`/artisans/${n.id}`} img={n.image_url} title={n.name} sub={`${n.kind} · ${n.distance_km} km`} />
                        ))}
                      </NearbyRow>
                    )}
                    {nearby.experiences.length > 0 && (
                      <NearbyRow title="Experiences" icon={<Ticket className="h-4 w-4" />}>
                        {nearby.experiences.map((n) => (
                          <NearbyCard key={n.id} to={`/experiences/${n.id}`} img={undefined} title={n.title} sub={`${n.duration_minutes} min · ₹${n.price} · ${n.distance_km} km`} />
                        ))}
                      </NearbyRow>
                    )}
                    {nearby.events.length > 0 && (
                      <NearbyRow title="Festival events" icon={<PartyPopper className="h-4 w-4" />}>
                        {nearby.events.map((n) => (
                          <NearbyCard key={n.id} to={`/festivals?e=${n.id}`} img={undefined} title={n.name} sub={n.start_date} />
                        ))}
                      </NearbyRow>
                    )}
                  </>
                ) : (
                  <p className="text-sm text-ink-muted">Nothing nearby recorded yet.</p>
                )}
              </div>
            </section>
          </div>

          {/* SIDEBAR */}
          <aside className="space-y-5">
            <Tile className="p-0 overflow-hidden">
              <div className="relative">
                <Img src={place.image_urls?.[1] || place.image_urls?.[0]} alt={place.name} className="h-36" />
                {place.crowd_level && (
                  <span className={clsx("chip absolute left-3 top-3", cm.tone)}>
                    <Users className="h-3 w-3" /> {cm.label} now
                  </span>
                )}
              </div>
              <div className="p-5">
                <p className="text-xs font-bold uppercase tracking-wider text-ink-faint">Quick facts</p>
                <div className="mt-3 space-y-3">
                  {facts.map((f) => (
                    <div key={f.label} className="flex gap-3">
                      <span className="mt-0.5 text-teal">{f.icon}</span>
                      <div>
                        <p className="text-[10px] font-semibold uppercase tracking-wide text-ink-faint">{f.label}</p>
                        <p className="text-sm font-medium text-ink">{f.value}</p>
                      </div>
                    </div>
                  ))}
                </div>
                {place.opening_hours && (
                  <div className="mt-4 rounded-xl bg-sand-100 p-3 text-xs text-ink-soft">
                    <p className="font-bold text-ink">Today's hours</p>
                    {Object.entries(place.opening_hours).slice(0, 3).map(([d, h]) => (
                      <p key={d} className="mt-1 flex justify-between"><span>{d}</span><span>{h}</span></p>
                    ))}
                  </div>
                )}
                {place.est_capacity && (
                  <div className="mt-4">
                    <div className="h-2 overflow-hidden rounded-full bg-sand-200">
                      <div
                        className={clsx("h-full rounded-full", place.crowd_level === "critical" ? "bg-red-600" : place.crowd_level === "high" ? "bg-orange-500" : place.crowd_level === "moderate" ? "bg-amber-400" : "bg-emerald-500")}
                        style={{ width: `${Math.min(100, Math.round((place.occupancy_ratio ?? 0) * 100))}%` }}
                      />
                    </div>
                    <p className="mt-1.5 flex items-center justify-between text-[11px] text-ink-muted">
                      <span>Capacity used</span>
                      <span>{Math.round((place.occupancy_ratio ?? 0) * 100)}%</span>
                    </p>
                  </div>
                )}
              </div>
            </Tile>

            <Tile>
              <p className="text-xs font-bold uppercase tracking-wider text-ink-faint">Share the story</p>
              <p className="mt-1 text-sm text-ink-muted">
                Community-verified content. Audio narration available in English, हिन्दी &amp; ગુજરાતી.
              </p>
              <div className="mt-3 flex items-center gap-2 text-xs text-teal-deep">
                <BadgeCheck className="h-4 w-4" /> Curated with local historians
              </div>
            </Tile>

            <Link to="/map" className="flex items-center justify-between rounded-2xl bg-teal-deep p-4 text-sm font-semibold text-white shadow-card transition hover:bg-teal">
              <span className="flex items-center gap-2"><Compass className="h-4 w-4" /> Open live map</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </aside>
        </div>
      </div>
    </div>
  );
}

function NearbyRow({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div>
      <p className="mb-2.5 flex items-center gap-2 text-sm font-bold text-ink">
        <span className="text-teal">{icon}</span> {title}
      </p>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {children}
      </div>
    </div>
  );
}

function NearbyCard({ to, img, title, sub, by }: { to: string; img?: string; title: string; sub: string; by?: string }) {
  return (
    <Link to={to} className="group w-52 shrink-0 overflow-hidden rounded-2xl bg-white shadow-card transition hover:-translate-y-0.5 hover:shadow-lift">
      {img && <Img src={img} alt={title} className="h-24" />}
      <div className="p-3">
        <p className="truncate font-display text-sm font-semibold text-ink group-hover:text-teal-deep">{title}</p>
        <p className="mt-0.5 text-[11px] text-ink-muted">{sub}</p>
        {by && <p className="mt-1 line-clamp-1 text-[11px] text-teal">{by}</p>}
      </div>
    </Link>
  );
}