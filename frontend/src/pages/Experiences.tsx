import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Ticket, Clock3, IndianRupee, MapPin, Users, Send } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useDestination } from "../state/destination";
import { useAuth } from "../state/auth";
import { useToast } from "../state/toast";
import type { Experience } from "../lib/types";
import Img from "../components/Img";
import { SectionTitle, Spinner, ErrorNote, Tile, Button, Modal } from "../components/ui";

const TYPES = ["All", "Craft", "Heritage", "Food", "Adventure", "Nightlife"];

function ExperienceCard({ x }: { x: Experience }) {
  return (
    <Link to={`/experiences/${x.id}`} className="card group overflow-hidden transition hover:-translate-y-1 hover:shadow-lift">
      <div className="relative">
        <Img src={x.image_urls?.[0]} alt={x.title} className="h-44" />
        <span className="chip absolute left-3 top-3 bg-white/90 text-ink backdrop-blur">{x.category}</span>
        <span className="chip absolute right-3 top-3 bg-saffron text-white">₹{x.price}</span>
      </div>
      <div className="p-5">
        <h3 className="font-display text-lg font-semibold text-ink group-hover:text-teal-deep">{x.title}</h3>
        <p className="mt-1 line-clamp-2 text-sm text-ink-muted">{x.description}</p>
        <div className="mt-3 flex flex-wrap gap-3 text-xs text-ink-muted">
          <span className="flex items-center gap-1"><Clock3 className="h-3.5 w-3.5" /> {x.duration_minutes} min</span>
          <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {x.location}</span>
        </div>
      </div>
    </Link>
  );
}

export function ExperiencesPage() {
  const { currentId } = useDestination();
  const { data: exps, loading, error } = usePoll<Experience[]>(() => endpoints.experiences(), 60000, [currentId]);
  const [t, setT] = useState("All");

  const list = useMemo(() => (t === "All" ? exps ?? [] : (exps ?? []).filter((x) => x.category === t)), [exps, t]);

  return (
    <div className="animate-fade-up mx-auto max-w-7xl px-6 py-10">
      <header className="max-w-2xl">
        <p className="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-saffron-deep">Hands-on heritage</p>
        <h1 className="font-display text-3xl font-bold text-ink sm:text-4xl">Experiences you can live, not just visit</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Pottery wheels, weekend garba workshops, food trails and palace walks — hosted by the people who call the
          heritage home.
        </p>
      </header>
      <div className="mt-6 flex flex-wrap gap-2">
        {TYPES.map((x) => (
          <button key={x} onClick={() => setT(x)} className={clsx("rounded-full px-3.5 py-1.5 text-xs font-semibold", t === x ? "bg-teal text-white" : "bg-white text-ink-soft")}>
            {x}
          </button>
        ))}
      </div>
      {loading && <Spinner />}
      {error && <ErrorNote text={error} />}
      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {list.map((x) => <ExperienceCard key={x.id} x={x} />)}
      </div>
      {!loading && list.length === 0 && <p className="mt-10 text-center text-sm text-ink-muted">No experiences match that filter yet.</p>}
    </div>
  );
}

export function ExperienceDetailPage() {
  const { id } = useParams();
  const xid = Number(id);
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const { data: x, loading, error } = usePoll<Experience>(() => endpoints.experiences().then((l) => l.find((i) => i.id === xid)!), 60000, [xid]);
  const { data: all } = usePoll<Experience[]>(() => endpoints.experiences(), 60000);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ visitor_name: "", visitor_email: "", visitor_phone: "", message: "", event_date: "" });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [xid]);

  const related = (all ?? []).filter((i) => i.id !== xid && i.category === x?.category).slice(0, 3);

  const submit = async () => {
    if (!form.visitor_name || !form.message) return toast("Add your name and a message.", "error");
    setSending(true);
    try {
      await endpoints.createEnquiry({ business_id: x?.provider_business_id, experience_id: xid, visitor_name: form.visitor_name, visitor_email: form.visitor_email, visitor_phone: form.visitor_phone, message: form.message, event_date: form.event_date });
      toast("Booking enquiry sent!");
      setModal(false);
    } catch (e) {
      toast(e instanceof Error ? e.message : "Could not send enquiry.", "error");
    } finally {
      setSending(false);
    }
  };

  if (loading && !x) return <div className="mx-auto max-w-7xl px-6 py-10"><Spinner /></div>;
  if (error && !x) return <div className="mx-auto max-w-7xl px-6 py-10"><ErrorNote text={error} /></div>;
  if (!x) return null;

  return (
    <div className="animate-fade-up">
      <section className="relative">
        <Img src={x.image_urls?.[0]} alt={x.title} className="h-[44vh] min-h-[320px]" />
        <div className="absolute inset-0 bg-gradient-to-t from-ink/85 via-transparent to-transparent" />
        <div className="absolute inset-x-0 bottom-0">
          <div className="mx-auto max-w-7xl px-6 pb-6">
            <button onClick={() => navigate(-1)} className="btn btn-sm mb-3 !bg-white/15 !text-white backdrop-blur hover:!bg-white/30">
              <ArrowLeft className="h-4 w-4" /> Back
            </button>
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <span className="chip bg-white/20 text-white backdrop-blur">{x.category}</span>
                <h1 className="mt-2 font-display text-3xl font-bold text-white sm:text-4xl">{x.title}</h1>
                <p className="mt-1 flex items-center gap-1.5 text-sm text-sand-200"><MapPin className="h-4 w-4" /> {x.location}</p>
              </div>
              <div className="rounded-2xl bg-white/15 px-5 py-3 text-white backdrop-blur">
                <p className="text-[11px] uppercase tracking-wide text-sand-200">Per person</p>
                <p className="font-display text-3xl font-bold">₹{x.price}</p>
                {x.price_note && <p className="text-[11px] text-sand-200">{x.price_note}</p>}
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
          <div className="space-y-6">
            <p className="text-[15px] leading-relaxed text-ink-soft">{x.description}</p>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                [<Clock3 className="h-5 w-5" />, "Duration", `${x.duration_minutes} min`],
                [<Users className="h-5 w-5" />, "Group capacity", `${x.capacity} people`],
                [<Ticket className="h-5 w-5" />, "Availability", x.availability],
              ].map(([i, l, v]) => (
                <Tile key={String(l)} className="!p-4">
                  <span className="text-teal">{i}</span>
                  <p className="mt-2 text-[10px] font-semibold uppercase tracking-wide text-ink-faint">{l}</p>
                  <p className="text-sm font-semibold text-ink">{v}</p>
                </Tile>
              ))}
            </div>
            {x.provider_name && (
              <Tile className="flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-ink-faint">Hosted by</p>
                  <p className="font-display text-base font-semibold text-ink">{x.provider_name}</p>
                </div>
                {x.provider_business_id && (
                  <Link to={`/artisans/${x.provider_business_id}`} className="btn btn-outline btn-sm">See their work</Link>
                )}
              </Tile>
            )}
            {related.length > 0 && (
              <>
                <SectionTitle kicker="More like this" title="Keep the day going" />
                <div className="grid gap-4 sm:grid-cols-3">
                  {related.map((r) => (
                    <ExperienceCard key={r.id} x={r} />
                  ))}
                </div>
              </>
            )}
          </div>

          <aside>
            <Tile className="lg:sticky lg:top-28">
              <p className="text-sm font-bold text-ink">Lock your slot</p>
              <p className="mt-1 text-xs text-ink-muted">Send an enquiry to the host — no payment needed for this demo.</p>
              <Button onClick={() => setModal(true)} size="lg" className="mt-4 w-full">
                <Send className="h-4 w-4" /> Enquire to book
              </Button>
              {x.availability && <p className="mt-3 text-center text-[11px] text-ink-muted">Current availability: {x.availability}</p>}
            </Tile>
          </aside>
        </div>
      </div>

      <Modal open={modal} onClose={() => setModal(false)} title={`Enquire · ${x.title}`}>
        <div className="space-y-3">
          {user && <p className="text-xs text-ink-muted">Signed in as <span className="font-semibold text-ink">{user.name}</span></p>}
          <input className="input" placeholder="Your name *" value={form.visitor_name} onChange={(e) => setForm({ ...form, visitor_name: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input" placeholder="Email" value={form.visitor_email} onChange={(e) => setForm({ ...form, visitor_email: e.target.value })} />
            <input className="input" placeholder="Phone" value={form.visitor_phone} onChange={(e) => setForm({ ...form, visitor_phone: e.target.value })} />
          </div>
          <input className="input" placeholder="Preferred date" value={form.event_date} onChange={(e) => setForm({ ...form, event_date: e.target.value })} />
          <textarea className="input min-h-24 resize-none" placeholder="Any questions? *" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
          <Button onClick={submit} disabled={sending} className="w-full" size="lg">{sending ? "Sending…" : "Send enquiry"}</Button>
        </div>
      </Modal>
    </div>
  );
}