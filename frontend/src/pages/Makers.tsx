import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { HandHeart, MapPin, BadgeCheck, ArrowRight, Wheat, Search } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { getDestCopy, destShort } from "../lib/destCopy";
import { useDestination } from "../state/destination";
import type { Business } from "../lib/types";
import Img from "../components/Img";
import { SectionTitle, Spinner, ErrorNote } from "../components/ui";

const CRAFTS = [
  { key: "All", label: "All makers" },
  { key: "Beadwork", label: "Beadwork" },
  { key: "Pithora", label: "Pithora art" },
  { key: "Weaving", label: "Weaving" },
  { key: "Food", label: "Food makers" },
  { key: "Pottery", label: "Pottery" },
];

export default function MakersPage() {
  const { current, currentId } = useDestination();
  const dc = getDestCopy(currentId);
  const { data: artisans, loading, error } = usePoll<Business[]>(() => endpoints.artisans(), 60000, [currentId]);
  const [craft, setCraft] = useState("All");
  const [q, setQ] = useState("");

  const list = useMemo(() => {
    let l = artisans ?? [];
    if (craft !== "All") l = l.filter((b) => (b.craft || "").toLowerCase().includes(craft.toLowerCase()) || (b.kind || "").toLowerCase().includes(craft.toLowerCase()));
    if (q.trim()) l = l.filter((b) => `${b.name} ${b.story} ${b.craft}`.toLowerCase().includes(q.toLowerCase()));
    return l;
  }, [artisans, craft, q]);

  return (
    <div className="animate-fade-up mx-auto max-w-7xl px-6 py-10">
      <header className="max-w-2xl">
        <p className="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-saffron-deep">Meet the makers</p>
        <h1 className="font-display text-3xl font-bold text-ink sm:text-4xl">
          Hands that keep {destShort(current)}'s soul alive
        </h1>
        <p className="mt-2 text-sm text-ink-muted">{dc.makersLine}</p>
      </header>

      <div className="mt-8 flex flex-wrap items-center gap-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search a craft or name…" className="input !w-64 pl-9" />
        </div>
        <div className="flex flex-wrap gap-1.5">
          {CRAFTS.map((c) => (
            <button
              key={c.key}
              onClick={() => setCraft(c.key)}
              className={clsx("rounded-full px-3.5 py-1.5 text-xs font-semibold transition", craft === c.key ? "bg-teal text-white" : "bg-white text-ink-soft hover:bg-sand-200")}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {loading && <Spinner />}
      {error && <ErrorNote text={error} />}

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {list.map((b) => (
          <Link key={b.id} to={`/artisans/${b.id}`} className="card group overflow-hidden transition hover:-translate-y-1 hover:shadow-lift">
            <div className="relative">
              <Img src={b.image_urls?.[0]} alt={b.name} className="h-48" />
              <span className="chip absolute left-3 top-3 bg-white/90 text-ink backdrop-blur">{b.craft}</span>
              {b.is_verified && (
                <span className="chip absolute right-3 top-3 bg-teal text-white"><BadgeCheck className="h-3 w-3" /> Verified</span>
              )}
            </div>
            <div className="p-5">
              <h3 className="font-display text-xl font-semibold text-ink group-hover:text-teal-deep">{b.name}</h3>
              <p className="mt-1 line-clamp-2 text-sm text-ink-muted">{b.story}</p>
              <div className="mt-3 flex items-center gap-3 text-xs text-ink-muted">
                <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {b.price_range}</span>
                {b.workshop_available && (
                  <span className="flex items-center gap-1 text-teal-deep"><Wheat className="h-3.5 w-3.5" /> Workshop open</span>
                )}
              </div>
              <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-teal transition group-hover:gap-2.5">
                Visit the workshop <ArrowRight className="h-4 w-4" />
              </span>
            </div>
          </Link>
        ))}
      </div>
      {!loading && list.length === 0 && (
        <p className="mt-10 text-center text-sm text-ink-muted">No makers match that search yet.</p>
      )}
    </div>
  );
}