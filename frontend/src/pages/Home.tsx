import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  MapPin,
  ArrowRight,
  Search,
  Users,
  HandHeart,
  Ticket,
  PartyPopper,
  Sparkles,
  Compass,
  BadgeCheck,
  Map,
  BellRing,
  TrendingUp,
  ShieldCheck,
} from "lucide-react";
import { clsx } from "clsx";
import { usePoll, useDynamicInfo } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { cat, crowdMeta, fmtNum, fmtDateShort } from "../lib/catalog";
import { destShort, getDestCopy } from "../lib/destCopy";
import { useDestination } from "../state/destination";
import type { Marker, Business, Experience, Festival } from "../lib/types";
import Img from "../components/Img";
import { SectionTitle, Button } from "../components/ui";
import { ListenButton } from "../components/a11y";
import { useLanguage } from "../state/language";
import { useAuth } from "../state/auth";

function Dashboards() {
  const { user } = useAuth();
  const { t } = useLanguage();

  const isAuthority = user?.role === "authority_admin" || user?.role === "authority_officer";
  const isTrade = user?.role === "business" || user?.role === "artisan";

  const cards = isAuthority
    ? [{ to: "/authority", title: "Authority Command Center", sub: t("dash.authoritySub"), icon: <ShieldCheck className="h-5 w-5" />, tone: "teal" }]
    : isTrade
      ? [{ to: "/business", title: "Business & Artisan Portal", sub: t("dash.businessSub"), icon: <HandHeart className="h-5 w-5" />, tone: "saffron" }]
      : [];

  if (!cards.length) {
    return (
      <section className="mx-auto max-w-7xl px-6 py-14">
        <div className="rounded-3xl border border-ink/10 bg-white p-8 shadow-card sm:p-10">
          <div className="flex flex-wrap items-center justify-between gap-6">
            <div className="max-w-lg">
              <span className="chip bg-teal/10 text-teal-deep">
                <ShieldCheck className="h-3.5 w-3.5" /> {t("dash.kicker")}
              </span>
              <h3 className="mt-3 font-display text-2xl font-bold text-ink sm:text-3xl">{t("dash.title")}</h3>
              <p className="mt-2 text-sm text-ink-muted">{t("dash.sub")}</p>
            </div>
            <Link to="/login" className="btn btn-primary btn-lg shrink-0">
              {t("dash.signin")}
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-7xl px-6 py-14">
      <SectionTitle kicker={t("dash.kicker")} title={t("dash.titleSigned")} />
      <div className="grid gap-5 sm:grid-cols-2">
        {cards.map((c) => (
          <Link
            key={c.to}
            to={c.to}
            className={clsx(
              "card group flex items-start gap-4 p-6 transition hover:-translate-y-1 hover:shadow-lift",
              c.tone === "teal" ? "border-teal/20" : "border-saffron/25",
            )}
          >
            <span
              className={clsx(
                "flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl text-white",
                c.tone === "teal" ? "bg-teal" : "bg-saffron",
              )}
            >
              {c.icon}
            </span>
            <div>
              <h3 className="font-display text-lg font-semibold text-ink group-hover:text-teal-deep">{c.title}</h3>
              <p className="mt-1 text-sm text-ink-muted">{c.sub}</p>
              <span className="mt-3 inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-teal-deep">
                {t("dash.open")} <ArrowRight className="h-3.5 w-3.5" />
              </span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}

export default function HomePage() {
  const navigate = useNavigate();
  const { current, currentId } = useDestination();
  const { t } = useLanguage();
  const dc = getDestCopy(currentId);
  const short = destShort(current);
  const [q, setQ] = useState("");
  const { data: markers } = usePoll<Marker[]>(() => endpoints.markers(), 45000, [currentId]);
  const { data: info } = useDynamicInfo(30000, [currentId]);
  const { data: festivals } = usePoll<Festival[]>(() => endpoints.festivals(), 60000, [currentId]);
  const { data: artisans } = usePoll<Business[]>(() => endpoints.artisans(), 60000, [currentId]);
  const { data: experiences } = usePoll<Experience[]>(() => endpoints.experiences(), 60000, [currentId]);

  const places = useMemo(
    () => (markers ?? []).filter((m) => m.type === "place" && !m.is_hidden),
    [markers],
  );
  const happening = useMemo(
    () => [...places].sort((a, b) => (b.crowd === "critical" || b.crowd === "high" ? 1 : 0) - (a.crowd === "critical" || a.crowd === "high" ? 1 : 0)).slice(0, 4),
    [places],
  );
  const liveFestival = festivals?.find((f) => f.status === "live" || f.status === "upcoming");

  const goSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/map?q=${encodeURIComponent(q)}`);
  };

  return (
    <div className="animate-fade-up">
      {/* HERO */}
      <section className="relative overflow-hidden bg-teal-dark text-white">
        <div className="absolute inset-0 bg-mesh-soft" />
        <div className="absolute inset-0 bg-dots-light opacity-60" />
        <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full border border-saffron/40" />
        <div className="absolute right-24 bottom-10 hidden h-44 w-44 rounded-full border border-sand-200/20 lg:block" />
        <div className="absolute -left-16 top-24 h-56 w-56 rounded-full bg-saffron/10 blur-2xl" />
        <div className="relative mx-auto max-w-7xl px-6 pb-20 pt-16 sm:pt-24">
          <div className="grid items-center gap-10 lg:grid-cols-[1.2fr_1fr]">
            <div>
              <div className="mb-5 flex items-center gap-2">
                <span className="chip bg-saffron/90 text-teal-dark">
                  <MapPin className="h-3.5 w-3.5" /> {short} · {current?.state ?? "Gujarat"}
                </span>
                {liveFestival && (
                  <Link to={`/festivals/${liveFestival.id}`} className="chip bg-white/15 text-white hover:bg-white/25">
                    <PartyPopper className="h-3.5 w-3.5 animate-pulse" /> Festival Mode {liveFestival.status === "live" ? "live" : `· ${fmtDateShort(liveFestival.start_date)}`}
                  </Link>
                )}
              </div>
              <h1 className="font-display text-4xl font-bold leading-[1.05] tracking-tight text-glow-sun sm:text-6xl">
                {t("hero.title")}
              </h1>
              <p className="mt-5 max-w-xl text-base leading-relaxed text-sand-200 sm:text-lg">
                {t("hero.sub").replace("{city}", short)}
              </p>
              <div className="mt-5 flex flex-wrap items-center gap-3">
                <ListenButton
                  text={() => {
                    const title = t("hero.title").replace(/[.।?!]+\s*$/, "");
                    return `${title}. ${t("hero.sub").replace("{city}", short)}`;
                  }}
                  label={t("hero.cta.listen")}
                  variant="saffron"
                />
              </div>
              <form onSubmit={goSearch} className="mt-7 flex max-w-lg overflow-hidden rounded-full bg-white p-1.5 shadow-lift">
                <span className="flex items-center pl-3 text-teal">
                  <Search className="h-5 w-5" />
                </span>
                <input
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder={dc.searchHint}
                  className="w-full bg-transparent px-3 py-2.5 text-sm text-ink outline-none placeholder:text-ink-faint"
                />
                <button className="btn btn-primary btn-md !rounded-full">Explore</button>
              </form>
              <div className="mt-8 flex flex-wrap gap-x-8 gap-y-3 text-xs text-sand-300">
                {[
                  [18, "home.stats.legs"],
                  [3, "home.stats.languages"],
                  [7, "home.stats.festivals"],
                ].map(([n, l]) => (
                  <span key={String(l)}>
                    <strong className="font-display text-xl text-sand-50">{n}+</strong>{" "}
                    <span className="block">{t(String(l))}</span>
                  </span>
                ))}
              </div>
            </div>

            {/* Live strip card */}
            <div className="rounded-3xl border border-white/15 bg-white/10 p-5 backdrop-blur-md">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-sand-200">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
                </span>
                {t("home.happening").replace("{city}", short)}
              </div>
              <div className="mt-4 space-y-2.5">
                {happening.slice(0, 3).map((p) => (
                  <Link
                    key={p.id}
                    to={`/places/${p.entity_id}`}
                    className="flex items-center gap-3 rounded-2xl bg-white/10 p-2.5 transition hover:bg-white/20"
                  >
                    <Img src={p.image} alt={p.name} className="h-11 w-11 shrink-0 rounded-xl" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold">{p.name}</p>
                      <p className="text-[11px] text-sand-300">{cat(p.category).label}</p>
                    </div>
                    {p.crowd && (
                      <span className={clsx("chip", crowdMeta(p.crowd).tone)}>
                        <Users className="h-3 w-3" />
                        {t(
                          p.crowd === "critical"
                            ? "home.crowd.very"
                            : p.crowd === "high"
                              ? "home.crowd.heavy"
                              : p.crowd === "moderate"
                                ? "home.crowd.moderate"
                                : "home.crowd.quiet",
                        )}
                      </span>
                    )}
                  </Link>
                ))}
              </div>
              <Link to="/map" className="mt-4 flex items-center justify-center gap-2 rounded-2xl bg-saffron py-3 text-sm font-bold text-teal-dark transition hover:bg-saffron-deep hover:text-white">
                <Map className="h-4 w-4" /> {t("home.openMap")}
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* FESTIVAL FOCUS */}
      {liveFestival && (
        <section className="mx-auto max-w-7xl px-6 pt-14">
          <Link to={`/festivals/${liveFestival.id}`} className="group relative block overflow-hidden rounded-3xl shadow-lift">
            <Img src={liveFestival.hero_image_url} alt={liveFestival.name} className="h-[220px] sm:h-[280px]" />
            <div className="absolute inset-0 bg-gradient-to-r from-teal-dark/95 via-teal-dark/60 to-transparent" />
            <div className="absolute inset-0 flex flex-col justify-center p-8 sm:p-12">
              <span className="chip w-fit bg-saffron text-teal-dark">
                <PartyPopper className="h-3.5 w-3.5" /> Festival Mode · {liveFestival.status === "live" ? t("home.festival.live") : t("home.festival.starts").replace("{date}", fmtDateShort(liveFestival.start_date))}
              </span>
              <h2 className="mt-4 max-w-xl font-display text-3xl font-bold text-white sm:text-5xl">
                {liveFestival.name}
              </h2>
              <p className="mt-2 max-w-md text-sm text-sand-200">{liveFestival.subtitle}</p>
              <span className="mt-5 inline-flex w-fit items-center gap-2 rounded-full bg-white/15 px-4 py-2 text-sm font-semibold text-white backdrop-blur transition group-hover:bg-white/30">
                {t("home.festival.enter")} <ArrowRight className="h-4 w-4" />
              </span>
            </div>
          </Link>
        </section>
      )}

      {/* EXPLORE SECTIONS */}
      <section className="mx-auto max-w-7xl px-6 py-14">
        <SectionTitle
          kicker={t("home.explore.kicker")}
          title={t("home.explore.title").replace("{city}", short)}
          sub={t("home.explore.sub")}
        />
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {(
            [
              [<Map className="h-5 w-5" />, "Explore the map", "Navigate the heritage spots with live crowd heat.", "/map", "bg-teal-soft text-teal-deep"],
              [<HandHeart className="h-5 w-5" />, "Meet the makers", "Buy direct from living craft workshops.", "/artisans", "bg-saffron-light text-saffron-deep"],
              [<Ticket className="h-5 w-5" />, "Book experiences", "Hands-on workshops, food trails, festival nights.", "/experiences", "bg-blush-light text-blush"],
              [<PartyPopper className="h-5 w-5" />, "Festival calendar", dc.festivalLine, "/festivals", "bg-marigold-light text-amber-700"],
            ] as [React.ReactNode, string, string, string, string][]
          ).map(([icon, t, d, to, bg]) => (
            <Link key={t} to={to} className="card group p-6 transition hover:-translate-y-1 hover:shadow-lift">
              <div className={clsx("flex h-11 w-11 items-center justify-center rounded-2xl", bg)}>{icon}</div>
              <h3 className="mt-4 font-display text-lg font-semibold text-ink group-hover:text-teal-deep">{t}</h3>
              <p className="mt-1 text-sm text-ink-muted">{d}</p>
              <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-teal transition group-hover:gap-2.5">
                Start exploring <ArrowRight className="h-4 w-4" />
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* LIVE FEATURED PLACES */}
      <section className="bg-white">
        <div className="mx-auto max-w-7xl px-6 py-14">
          <SectionTitle
            kicker={t("home.live.kicker")}
            title={t("home.live.title")}
            sub={t("home.live.sub")}
            right={
              <Link to="/map" className="btn btn-outline btn-md">
                <Map className="h-4 w-4" /> {t("home.live.openMap")}
              </Link>
            }
          />
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {happening.map((p) => (
              <Link key={p.id} to={`/places/${p.entity_id}`} className="card group overflow-hidden transition hover:-translate-y-1 hover:shadow-lift">
                <div className="relative">
                  <Img src={p.image} alt={p.name} className="h-44" />
                  {p.crowd && (
                    <span className={clsx("chip absolute left-3 top-3", crowdMeta(p.crowd).tone)}>
                      <Users className="h-3 w-3" /> {crowdMeta(p.crowd).label}
                    </span>
                  )}
                </div>
                <div className="p-4">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-saffron-deep">{cat(p.category).label}</p>
                  <h3 className="mt-1 font-display text-lg font-semibold text-ink group-hover:text-teal-deep">{p.name}</h3>
                  <p className="mt-1 line-clamp-2 text-sm text-ink-muted">{p.subtitle}</p>
                  {p.visitors !== undefined && (
                    <p className="mt-2 flex items-center gap-1.5 text-xs text-ink-muted">
                      <TrendingUp className="h-3.5 w-3.5 text-teal" /> {fmtNum(p.visitors)} {t("home.live.visitors")}
                    </p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* MAKERS STRIP */}
      <section className="mx-auto max-w-7xl px-6 py-14">
        <SectionTitle
          kicker={t("home.makers.kicker")}
          title={t("home.makers.title")}
          sub={t("home.makers.sub")}
          right={<Link to="/artisans" className="btn btn-outline btn-md">{t("home.makers.all")}</Link>}
        />
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {(artisans ?? []).slice(0, 4).map((b) => (
            <Link key={b.id} to={`/artisans/${b.id}`} className="card group overflow-hidden transition hover:-translate-y-1 hover:shadow-lift">
              <Img src={b.image_urls?.[0]} alt={b.name} className="h-36" />
              <div className="p-4">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-teal">{b.craft}</p>
                <h3 className="mt-1 truncate font-display text-base font-semibold text-ink group-hover:text-teal-deep">{b.name}</h3>
                <p className="mt-0.5 line-clamp-2 text-xs text-ink-muted">{b.story}</p>
                {b.is_verified && (
                  <span className="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold text-teal-deep">
                    <BadgeCheck className="h-3.5 w-3.5" /> {t("home.makers.verified")}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* EXPERIENCES */}
      <section className="bg-teal-soft/60">
        <div className="mx-auto max-w-7xl px-6 py-14">
          <SectionTitle
            kicker={t("home.exp.kicker")}
            title={t("home.exp.title")}
            right={<Link to="/experiences" className="btn btn-outline btn-md">{t("home.exp.all")}</Link>}
          />
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {(experiences ?? []).slice(0, 3).map((x) => (
              <Link key={x.id} to={`/experiences/${x.id}`} className="card group overflow-hidden transition hover:-translate-y-1 hover:shadow-lift">
                <Img src={x.image_urls?.[0]} alt={x.title} className="h-40" />
                <div className="p-4">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-blush">{x.category}</p>
                  <h3 className="mt-1 font-display text-lg font-semibold text-ink group-hover:text-teal-deep">{x.title}</h3>
                  <p className="mt-1 line-clamp-2 text-sm text-ink-muted">{x.description}</p>
                  <div className="mt-3 flex items-center justify-between text-xs text-ink-muted">
                    <span>{x.duration_minutes} min</span>
                    <span className="font-semibold text-teal-deep">₹{x.price}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* DASHBOARDS */}
      <Dashboards />

      {/* COMMUNITY CTA */}
      <section className="mx-auto max-w-7xl px-6 py-14">
        <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <div className="rounded-3xl bg-teal-deep p-8 text-white shadow-lift sm:p-10">
            <BellRing className="h-8 w-8 text-marigold" />
            <h3 className="mt-4 font-display text-2xl font-bold sm:text-3xl">
              Tourism works best when residents speak up.
            </h3>
            <p className="mt-2 max-w-md text-sm text-sand-200">
              Spot a broken footpath, an overflowing bin or a traffic snarl at a heritage gate? Flag it — the tourism
              authority sees it, assigns it, and the city keeps your experience honest.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link to="/report" className="btn btn-saffron btn-lg">Report an issue</Link>
              <Link to="/login" className="btn btn-outline btn-lg !border-white/30 !text-white hover:!bg-white/10">For residents</Link>
            </div>
          </div>
          <div className="rounded-3xl bg-white p-8 shadow-card sm:p-10">
            <div className="flex items-center gap-2 text-saffron">
              <Compass className="h-7 w-7" />
            </div>
            <h3 className="mt-4 font-display text-2xl font-bold text-ink sm:text-3xl">Not sure where to start?</h3>
            <p className="mt-2 max-w-sm text-sm text-ink-muted">
              Ask the <span className="font-semibold text-teal-deep">Virsa Guide</span> — an always-on assistant
              grounded in real events, artisans, food and festival times.
            </p>
            <div className="mt-5 rounded-2xl bg-sand-100 p-4 text-sm text-ink-soft">
              <p className="font-display text-lg text-ink">{dc.guideQuote}</p>
              <p className="mt-2">{dc.guideAnswer}</p>
            </div>
            <Link to="/guide" className="btn btn-primary btn-md mt-6">
              <Sparkles className="h-4 w-4" /> Ask the Virsa Guide
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}