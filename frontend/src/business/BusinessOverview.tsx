import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Store, BadgeCheck, Inbox, Plus, Loader2 } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { Business } from "../lib/types";
import { PageHead } from "../authority/shared";
import { Button, Modal, Spinner, ErrorNote, EmptyState } from "../components/ui";

export default function BusinessOverview({ create = false }: { create?: boolean }) {
  const { toast } = useToast();
  const { data, loading, error, refresh } = usePoll<Business[]>(() => endpoints.myBusinesses(), 30000);
  const [open, setOpen] = useState(create);
  const [form, setForm] = useState({ name: "", kind: "artisan", craft: "", craft_type: "", price_range: "", story: "", address: "", lat: 22.3, lng: 73.18 });
  const [busy, setBusy] = useState(false);

  const createBiz = async () => {
    if (!form.name) return toast("Give your business a name.", "error");
    setBusy(true);
    try {
      await endpoints.createBusiness(form);
      toast("Business registered — now visible to visitors!");
      setOpen(false);
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed to register.", "error");
    } finally {
      setBusy(false);
    }
  };

  const toggleStatus = async (b: Business) => {
    const status = b.status === "Open" ? "Closed" : "Open";
    try {
      await endpoints.updateBusiness(b.id, { status });
      toast(`${b.name}: ${status}. Visitors updated.`);
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Update failed.", "error");
    }
  };

  return (
    <div>
      <PageHead
        kicker="Your workspace"
        title="Make your craft discoverable"
        sub="Your profile flows across the public site — map pins, maker cards, product shelves."
        right={<Button onClick={() => setOpen(true)}><Plus className="h-4 w-4" /> Register a business</Button>}
      />

      {loading && <Spinner />}
      {error && <ErrorNote text={error} />}

      {!loading && !error && (data ?? []).length === 0 && (
        <EmptyState
          icon={<Store className="h-6 w-6" />}
          title="No businesses yet"
          sub="Register your craft and start receiving visitor enquiries."
        />
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {(data ?? []).map((b) => (
          <div key={b.id} className="card flex flex-col p-5">
            <div className="flex items-start justify-between gap-2">
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-teal/10 text-teal-deep"><Store className="h-5 w-5" /></span>
              <span className={clsx("chip", b.status === "Open" ? "bg-emerald-100 text-emerald-800" : "bg-stone-200 text-ink-faint")}>
                {b.status}
              </span>
            </div>
            <h3 className="mt-3 font-display text-lg font-semibold text-ink">{b.name}</h3>
            <p className="text-[11px] uppercase tracking-wide text-ink-faint">{b.kind} · {b.craft}</p>
            <p className="mt-2 line-clamp-2 text-xs text-ink-muted">{b.story}</p>
            <div className="mt-3 flex items-center gap-3 text-[11px] text-ink-muted">
              <span className="flex items-center gap-1"><BadgeCheck className={clsx("h-3.5 w-3.5", b.is_verified ? "text-teal" : "text-ink-faint")} /> {b.is_verified ? "Verified" : "Awaiting verification"}</span>
              <span className="flex items-center gap-1"><Inbox className="h-3.5 w-3.5" />{b.experiences?.length ?? 0} experiences</span>
            </div>
            <div className="mt-4 flex gap-2 border-t border-ink/5 pt-3">
              <Link to={`/business/${b.id}`} className="btn btn-primary btn-sm flex-1">
                Manage <ArrowRight className="h-3.5 w-3.5" />
              </Link>
              <Button variant="outline" size="sm" onClick={() => toggleStatus(b)}>{b.status === "Open" ? "Close" : "Open"}</Button>
            </div>
          </div>
        ))}
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title="Register a business">
        <div className="space-y-3">
          <input className="input" placeholder="Business name *" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <select className="input" value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}>
              {["artisan", "food", "restaurant", "homestay", "guide", "hotel"].map((k) => <option key={k}>{k}</option>)}
            </select>
            <input className="input" placeholder="Craft (e.g. Beadwork)" value={form.craft} onChange={(e) => setForm({ ...form, craft: e.target.value })} />
          </div>
          <input className="input" placeholder="Price range (e.g. ₹500 – ₹5,000)" value={form.price_range} onChange={(e) => setForm({ ...form, price_range: e.target.value })} />
          <textarea className="input min-h-20 resize-none" placeholder="Your story — what do you make and why?" value={form.story} onChange={(e) => setForm({ ...form, story: e.target.value })} />
          <input className="input" placeholder="Address" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input" placeholder="Lat" value={form.lat} onChange={(e) => setForm({ ...form, lat: Number(e.target.value) })} />
            <input className="input" placeholder="Lng" value={form.lng} onChange={(e) => setForm({ ...form, lng: Number(e.target.value) })} />
          </div>
          <Button onClick={createBiz} disabled={busy} className="w-full" size="lg">
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Store className="h-4 w-4" />}
            Register
          </Button>
        </div>
      </Modal>
    </div>
  );
}