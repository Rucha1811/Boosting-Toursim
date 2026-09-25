import { useState } from "react";
import { Plus, BellRing, Megaphone, TriangleAlert } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { AuthorityAlert, Announcement, Marker } from "../lib/types";
import { PageHead, Load, severityTone } from "./shared";
import { Button, Modal } from "../components/ui";

function Toggle({ on, onClick }: { on: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={clsx("relative h-6 w-11 rounded-full transition", on ? "bg-emerald-500" : "bg-stone-300")}
      aria-label="toggle"
    >
      <span className={clsx("absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition", on ? "left-[22px]" : "left-0.5")} />
    </button>
  );
}

export default function AlertsPage() {
  const { toast } = useToast();
  const { data: alerts, refresh: refreshA } = usePoll<AuthorityAlert[]>(() => endpoints.alerts(), 30000);
  const { data: anns, refresh: refreshAnn } = usePoll<Announcement[]>(() => endpoints.announcements(), 30000);
  const { data: markers } = usePoll<Marker[]>(() => endpoints.markers(), 60000);
  const [openA, setOpenA] = useState(false);
  const [openAnn, setOpenAnn] = useState(false);
  const [fa, setFa] = useState({ title: "", message: "", category: "crowd", severity: "medium", place_id: "" });
  const [fAnn, setFAnn] = useState({ title: "", body: "", category: "general", important: true });
  const [busy, setBusy] = useState(false);

  const places = (markers ?? []).filter((m) => m.type === "place");

  const createAlert = async () => {
    if (!fa.title || !fa.message) return toast("Title and message required", "error");
    setBusy(true);
    try {
      await endpoints.createAlert({ ...fa, place_id: fa.place_id ? Number(fa.place_id) : null });
      toast("Alert published — visitors see it immediately.");
      setOpenA(false);
      setFa({ title: "", message: "", category: "crowd", severity: "medium", place_id: "" });
      refreshA();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed", "error");
    } finally {
      setBusy(false);
    }
  };

  const toggleAlert = async (a: AuthorityAlert) => {
    try {
      await endpoints.updateAlert(a.id, { is_active: !a.is_active });
      refreshA();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed", "error");
    }
  };

  const createAnn = async () => {
    if (!fAnn.title || !fAnn.body) return toast("Title and message required", "error");
    setBusy(true);
    try {
      await endpoints.createAnnouncement(fAnn);
      toast("Announcement published.");
      setOpenAnn(false);
      setFAnn({ title: "", body: "", category: "general", important: true });
      refreshAnn();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed", "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <PageHead
        kicker="Visitor communications"
        title="Alerts & notices"
        sub="Anything published here appears instantly on the public map and home page."
        right={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setOpenAnn(true)}><Megaphone className="h-4 w-4" /> Notice</Button>
            <Button onClick={() => setOpenA(true)}><Plus className="h-4 w-4" /> Alert</Button>
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-5">
          <h3 className="flex items-center gap-2 font-display text-lg font-semibold text-ink">
            <BellRing className="h-5 w-5 text-saffron-deep" /> Active alerts
          </h3>
          {!alerts?.length && <p className="mt-3 text-sm text-ink-muted">No alerts yet.</p>}
          <div className="mt-3 space-y-2">
            {(alerts ?? []).map((a) => (
              <div key={a.id} className="rounded-xl bg-sand-50 p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="flex items-center gap-2 text-sm font-semibold text-ink">
                    <TriangleAlert className="h-4 w-4 text-blush" /> {a.title}
                  </p>
                  <Toggle on={a.is_active} onClick={() => toggleAlert(a)} />
                </div>
                <p className="mt-1 text-xs text-ink-muted">{a.message}</p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  <span className={clsx("chip", severityTone(a.severity))}>{a.severity}</span>
                  <span className="chip bg-white text-ink-muted">{a.category}</span>
                  {a.place_name && <span className="chip bg-white text-ink-muted">at {a.place_name}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-5">
          <h3 className="flex items-center gap-2 font-display text-lg font-semibold text-ink">
            <Megaphone className="h-5 w-5 text-teal" /> Notices
          </h3>
          {!anns?.length && <p className="mt-3 text-sm text-ink-muted">No notices yet.</p>}
          <div className="mt-3 space-y-2">
            {(anns ?? []).map((a) => (
              <div key={a.id} className="rounded-xl bg-sand-50 p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-ink">{a.title}</p>
                  {a.important && <span className="chip bg-marigold-light text-amber-800">Important</span>}
                </div>
                <p className="mt-1 text-xs text-ink-muted">{a.body}</p>
                <p className="mt-2 text-[10px] text-ink-faint">{new Date(a.created_at).toLocaleString("en-IN")}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <Modal open={openA} onClose={() => setOpenA(false)} title="Publish an alert">
        <div className="space-y-3">
          <input className="input" placeholder="Title *" value={fa.title} onChange={(e) => setFa({ ...fa, title: e.target.value })} />
          <textarea className="input min-h-20 resize-none" placeholder="Message for visitors *" value={fa.message} onChange={(e) => setFa({ ...fa, message: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <select className="input capitalize" value={fa.category} onChange={(e) => setFa({ ...fa, category: e.target.value })}>
              {["crowd", "weather", "safety", "transport", "infrastructure"].map((c) => <option key={c}>{c}</option>)}
            </select>
            <select className="input capitalize" value={fa.severity} onChange={(e) => setFa({ ...fa, severity: e.target.value })}>
              {["info", "medium", "high", "critical"].map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
          <select className="input" value={fa.place_id} onChange={(e) => setFa({ ...fa, place_id: e.target.value })}>
            <option value="">Attach to a place (optional)</option>
            {places.map((p) => <option key={p.entity_id} value={p.entity_id}>{p.name}</option>)}
          </select>
          <Button onClick={createAlert} disabled={busy} className="w-full" size="lg">{busy ? "Publishing…" : "Publish now"}</Button>
        </div>
      </Modal>

      <Modal open={openAnn} onClose={() => setOpenAnn(false)} title="Post a notice">
        <div className="space-y-3">
          <input className="input" placeholder="Notice title *" value={fAnn.title} onChange={(e) => setFAnn({ ...fAnn, title: e.target.value })} />
          <textarea className="input min-h-24 resize-none" placeholder="Notice body *" value={fAnn.body} onChange={(e) => setFAnn({ ...fAnn, body: e.target.value })} />
          <label className="flex items-center gap-2 text-sm text-ink-soft">
            <input type="checkbox" checked={fAnn.important} onChange={(e) => setFAnn({ ...fAnn, important: e.target.checked })} />
            Mark as important (highlighted)
          </label>
          <Button onClick={createAnn} disabled={busy} className="w-full" size="lg">{busy ? "Posting…" : "Post notice"}</Button>
        </div>
      </Modal>
    </div>
  );
}