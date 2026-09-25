import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Plus, Inbox, Package, Send, CheckCircle2 } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { Business, Enquiry, Product } from "../lib/types";
import { PageHead } from "../authority/shared";
import { Spinner, ErrorNote, Button, Modal, EmptyState } from "../components/ui";

export default function BusinessManage() {
  const { id } = useParams();
  const bid = Number(id);
  const { toast } = useToast();
  const { data: biz, loading, error, refresh } = usePoll<Business | null>(async () => (await endpoints.myBusinesses()).find((b) => b.id === bid) ?? null, 30000, [bid]);
  const { data: enquiries, refresh: refreshEq } = usePoll<Enquiry[]>(() => endpoints.businessEnquiries(bid), 20000, [bid]);
  const [openP, setOpenP] = useState(false);
  const [pf, setPf] = useState({ name: "", description: "", price: 0, unit: "", material: "", available: true, image_url: "" });
  const [busy, setBusy] = useState(false);

  const addProduct = async () => {
    if (!pf.name) return toast("Product needs a name.", "error");
    setBusy(true);
    try {
      await endpoints.addProduct(bid, { ...pf });
      toast("Product added to your profile.");
      setOpenP(false);
      setPf({ name: "", description: "", price: 0, unit: "", material: "", available: true, image_url: "" });
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed.", "error");
    } finally {
      setBusy(false);
    }
  };

  const toggleProduct = async (p: Product) => {
    try {
      await endpoints.updateProduct(bid, p.id, { available: !p.available });
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed.", "error");
    }
  };

  const markEnquiry = async (enq: Enquiry, status: string) => {
    try {
      await endpoints.updateEnquiry(bid, enq.id, { status });
      toast(`Enquiry ${status}.`);
      refreshEq();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed.", "error");
    }
  };

  if (loading && !biz) return <Spinner />;
  if (error && !biz) return <ErrorNote text={error} />;
  if (!biz) return <ErrorNote text="Business not found" />;

  return (
    <div>
      <PageHead
        kicker="Manage"
        title={biz.name}
        sub={`${biz.kind} · ${biz.craft} · ${biz.price_range || "—"}`}
        right={
          <Link to={`/artisans/${biz.id}`} className="btn btn-outline btn-md">View public profile</Link>
        }
      />

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Products */}
        <div className="card p-5">
          <div className="flex items-center justify-between">
            <h3 className="flex items-center gap-2 font-display text-lg font-semibold text-ink"><Package className="h-5 w-5 text-teal" /> Products</h3>
            <Button size="sm" onClick={() => setOpenP(true)}><Plus className="h-4 w-4" /> Add</Button>
          </div>
          {(biz.products ?? []).length === 0 ? (
            <EmptyState icon={<Package className="h-6 w-6" />} title="No products yet" sub="Add your wares so visitors can browse and enquire." />
          ) : (
            <div className="mt-4 space-y-2">
              {biz.products.map((p) => (
                <div key={p.id} className="flex items-center gap-3 rounded-xl bg-sand-50 p-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-ink">{p.name}</p>
                    <p className="text-[11px] text-ink-muted">{p.unit} · {p.material}</p>
                  </div>
                  <span className="text-sm font-bold text-teal-deep">₹{p.price}</span>
                  <button
                    onClick={() => toggleProduct(p)}
                    className={clsx("chip", p.available ? "bg-emerald-100 text-emerald-800" : "bg-stone-200 text-ink-faint")}
                  >
                    {p.available ? "In stock" : "Sold out"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Enquiries */}
        <div className="card p-5">
          <h3 className="flex items-center gap-2 font-display text-lg font-semibold text-ink"><Inbox className="h-5 w-5 text-saffron-deep" /> Enquiries</h3>
          {(enquiries ?? []).length === 0 ? (
            <EmptyState icon={<Inbox className="h-6 w-6" />} title="No enquiries yet" sub="When visitors ask about your work, it lands here." />
          ) : (
            <div className="mt-4 space-y-2">
              {(enquiries ?? []).map((e) => (
                <div key={e.id} className="rounded-xl bg-sand-50 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-ink">{e.visitor_name}</p>
                    <span className={clsx("chip", e.status === "replied" ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800")}>{e.status}</span>
                  </div>
                  <p className="mt-1 text-xs text-ink-muted">{e.message}</p>
                  <p className="mt-1 text-[11px] text-ink-faint">
                    {e.visitor_email}{e.visitor_phone ? ` · ${e.visitor_phone}` : ""}{e.event_date ? ` · ${e.event_date}` : ""}
                  </p>
                  {e.status !== "replied" && (
                    <Button variant="outline" size="sm" className="mt-2" onClick={() => markEnquiry(e, "replied")}>
                      <CheckCircle2 className="h-3.5 w-3.5" /> Mark replied
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
          {enquiries && enquiries.length > 0 && (
            <p className="mt-3 flex items-center gap-1.5 text-[11px] text-ink-muted"><Send className="h-3 w-3" /> Replies flow through on your registered contact.</p>
          )}
        </div>
      </div>

      <Modal open={openP} onClose={() => setOpenP(false)} title="Add a product">
        <div className="space-y-3">
          <input className="input" placeholder="Product name *" value={pf.name} onChange={(e) => setPf({ ...pf, name: e.target.value })} />
          <textarea className="input min-h-20 resize-none" placeholder="Description" value={pf.description} onChange={(e) => setPf({ ...pf, description: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input" type="number" placeholder="Price ₹" value={pf.price} onChange={(e) => setPf({ ...pf, price: Number(e.target.value) })} />
            <input className="input" placeholder="Unit (e.g. piece)" value={pf.unit} onChange={(e) => setPf({ ...pf, unit: e.target.value })} />
          </div>
          <input className="input" placeholder="Material" value={pf.material} onChange={(e) => setPf({ ...pf, material: e.target.value })} />
          <input className="input" placeholder="Image URL (optional)" value={pf.image_url} onChange={(e) => setPf({ ...pf, image_url: e.target.value })} />
          <label className="flex items-center gap-2 text-sm text-ink-soft">
            <input type="checkbox" checked={pf.available} onChange={(e) => setPf({ ...pf, available: e.target.checked })} /> Available now
          </label>
          <Button onClick={addProduct} disabled={busy} className="w-full" size="lg">{busy ? "Saving…" : "Add product"}</Button>
        </div>
      </Modal>
    </div>
  );
}