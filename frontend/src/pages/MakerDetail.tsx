import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  BadgeCheck,
  MapPin,
  Clock3,
  IndianRupee,
  HandHeart,
  Ticket,
  Phone,
  Package,
  Send,
} from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useAuth } from "../state/auth";
import { useToast } from "../state/toast";
import type { Business } from "../lib/types";
import Img from "../components/Img";
import { SectionTitle, Spinner, ErrorNote, Tile, Button, Modal } from "../components/ui";

const KINDS: Record<string, string> = {
  artisan: "Artisan",
  food: "Food",
  restaurant: "Restaurant",
  hotel: "Hotel",
  homestay: "Homestay",
  guide: "Local guide",
};

export default function MakerDetailPage() {
  const { id } = useParams();
  const bid = Number(id);
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const { data: biz, loading, error } = usePoll<Business>(() => endpoints.artisan(bid), 60000, [bid]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ visitor_name: "", visitor_email: "", visitor_phone: "", message: "", event_date: "" });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [bid]);

  const submit = async () => {
    if (!form.visitor_name || !form.message) {
      toast("Please add your name and a message.", "error");
      return;
    }
    setSending(true);
    try {
      await endpoints.createEnquiry({ business_id: bid, ...form });
      toast("Enquiry sent to the maker. They'll get back to you soon!");
      setModal(false);
      setForm({ visitor_name: "", visitor_email: "", visitor_phone: "", message: "", event_date: "" });
    } catch (e) {
      toast(e instanceof Error ? e.message : "Could not send enquiry.", "error");
    } finally {
      setSending(false);
    }
  };

  if (loading && !biz) return <div className="mx-auto max-w-7xl px-6 py-10"><Spinner /></div>;
  if (error && !biz) return <div className="mx-auto max-w-7xl px-6 py-10"><ErrorNote text={error} /></div>;
  if (!biz) return null;

  const products = biz.products ?? [];
  const exps = biz.experiences ?? [];

  return (
    <div className="animate-fade-up">
      <section className="mx-auto max-w-7xl px-6 py-8">
        <button onClick={() => navigate(-1)} className="btn btn-sm btn-outline mb-5">
          <ArrowLeft className="h-4 w-4" /> Back
        </button>

        <div className="grid gap-8 lg:grid-cols-[1.05fr_1fr]">
          <div>
            <div className="relative overflow-hidden rounded-3xl">
              <Img src={biz.image_urls?.[0]} alt={biz.name} className="h-[300px] sm:h-[400px]" />
              <div className="absolute left-4 top-4 flex gap-2">
                <span className="chip bg-white/90 text-ink backdrop-blur">{KINDS[biz.kind] ?? biz.kind}</span>
                {biz.is_verified && <span className="chip bg-teal text-white"><BadgeCheck className="h-3 w-3" /> Verified</span>}
              </div>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
              {(biz.image_urls ?? []).slice(1, 4).map((u, i) => (
                <Img key={i} src={u} alt="" className="h-28 rounded-2xl" />
              ))}
            </div>

            <section className="mt-8">
              <SectionTitle kicker="In their own words" title={biz.story} />
              <p className="text-[15px] leading-relaxed text-ink-soft">{biz.description}</p>
              {biz.cultural_significance && (
                <p className="mt-3 rounded-2xl bg-teal-soft p-4 text-sm leading-relaxed text-teal-deep">
                  <span className="font-semibold">Cultural significance — </span>
                  {biz.cultural_significance}
                </p>
              )}
            </section>

            {products.length > 0 && (
              <section className="mt-8">
                <SectionTitle kicker="Bring a piece home" title="Products & wares" />
                <div className="grid gap-4 sm:grid-cols-2">
                  {products.map((p) => (
                    <div key={p.id} className="card overflow-hidden">
                      {p.image_url && <Img src={p.image_url} alt={p.name} className="h-32" />}
                      <div className="p-4">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="font-display text-base font-semibold text-ink">{p.name}</h4>
                          <span className="text-sm font-bold text-teal-deep">₹{p.price}</span>
                        </div>
                        <p className="mt-1 text-xs text-ink-muted">{p.description}</p>
                        <span className={clsx("chip mt-2", p.available ? "bg-emerald-100 text-emerald-800" : "bg-stone-200 text-ink-faint")}>
                          {p.available ? "In stock" : "Sold out"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {exps.length > 0 && (
              <section className="mt-8">
                <SectionTitle kicker="Join a session" title="Experiences hosted here" />
                <div className="space-y-3">
                  {exps.map((x) => (
                    <Link key={x.id} to={`/experiences/${x.id}`} className="card flex items-center gap-4 p-4 transition hover:shadow-lift">
                      <Img src={x.image_urls?.[0]} alt={x.title} className="h-16 w-16 shrink-0 rounded-xl" />
                      <div className="min-w-0 flex-1">
                        <p className="font-display text-base font-semibold text-ink">{x.title}</p>
                        <p className="text-xs text-ink-muted">{x.duration_minutes} min · {x.location}</p>
                      </div>
                      <span className="text-sm font-bold text-teal-deep">₹{x.price}</span>
                    </Link>
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* SIDEBAR */}
          <aside className="space-y-5 lg:sticky lg:top-28 lg:self-start">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-saffron-deep">{biz.craft}</p>
              <h1 className="mt-1 font-display text-3xl font-bold text-ink">{biz.name}</h1>
              <p className="mt-1 text-sm text-ink-muted">Est. {biz.established_year || "—"} · {biz.craft_type || biz.craft}</p>
            </div>

            <Tile className="!p-0 overflow-hidden">
              <div className="p-5">
                <div className="flex items-center gap-2 text-xs text-ink-muted">
                  <MapPin className="h-4 w-4 text-teal" /> {biz.address}
                </div>
                <div className="mt-3 flex items-center gap-2 text-xs text-ink-muted">
                  <IndianRupee className="h-4 w-4 text-teal" /> {biz.price_range || "On request"}
                </div>
                {biz.contact && (
                  <a href={`tel:${biz.contact}`} className="mt-3 flex items-center gap-2 text-xs font-medium text-teal-deep">
                    <Phone className="h-4 w-4" /> {biz.contact}
                  </a>
                )}
                {biz.opening_hours && (
                  <div className="mt-4 border-t border-ink/5 pt-3">
                    <p className="flex items-center gap-2 text-xs font-bold text-ink"><Clock3 className="h-4 w-4 text-teal" /> Hours</p>
                    {Object.entries(biz.opening_hours).slice(0, 4).map(([d, h]) => (
                      <p key={d} className="mt-1 flex justify-between text-xs text-ink-muted"><span>{d}</span><span>{h}</span></p>
                    ))}
                  </div>
                )}
                <span className={clsx("chip mt-4", biz.status === "Open" ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800")}>
                  <HandHeart className="h-3 w-3" /> Currently {biz.status}
                </span>
              </div>
              <div className="border-t border-ink/5 bg-sand-50 p-4">
                <Button onClick={() => setModal(true)} className="w-full" size="lg">
                  <Send className="h-4 w-4" /> Plan a visit / enquiry
                </Button>
              </div>
            </Tile>

            {biz.workshop_available && (
              <Tile className="border border-saffron/30 bg-saffron-light/60">
                <p className="text-sm font-bold text-saffron-deep">Workshops available</p>
                <p className="mt-1 text-xs text-ink-soft">Ask about sessions, custom orders and bulk purchases for families and groups.</p>
              </Tile>
            )}
          </aside>
        </div>
      </section>

      <Modal open={modal} onClose={() => setModal(false)} title={`Enquire with ${biz.name}`}>
        <div className="space-y-3">
          {user && (
            <p className="text-xs text-ink-muted">Signed in as <span className="font-semibold text-ink">{user.name}</span></p>
          )}
          <input className="input" placeholder="Your name *" value={form.visitor_name} onChange={(e) => setForm({ ...form, visitor_name: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input" placeholder="Email" value={form.visitor_email} onChange={(e) => setForm({ ...form, visitor_email: e.target.value })} />
            <input className="input" placeholder="Phone" value={form.visitor_phone} onChange={(e) => setForm({ ...form, visitor_phone: e.target.value })} />
          </div>
          <input className="input" placeholder="Planned visit date (optional)" value={form.event_date} onChange={(e) => setForm({ ...form, event_date: e.target.value })} />
          <textarea className="input min-h-28 resize-none" placeholder="What would you like to know? Custom orders, workshop slots, pricing… *" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
          <Button onClick={submit} disabled={sending} className="w-full" size="lg">
            {sending ? "Sending…" : "Send enquiry"}
          </Button>
        </div>
      </Modal>
    </div>
  );
}