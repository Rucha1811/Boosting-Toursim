import { useState } from "react";
import { Plus, TrafficCone, CheckCircle2 } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { RoadClosure } from "../lib/types";
import { PageHead, Load } from "./shared";
import { Button, Modal } from "../components/ui";

export default function ClosuresPage() {
  const { toast } = useToast();
  const { data, loading, error, refresh } = usePoll<RoadClosure[]>(() => endpoints.closures(), 30000);
  const [open, setOpen] = useState(false);
  const [f, setF] = useState({ name: "", road_name: "", start_time: "", end_time: "", alternate_route: "", description: "" });
  const [busy, setBusy] = useState(false);

  const create = async () => {
    if (!f.name) return toast("Give the closure a name.", "error");
    setBusy(true);
    try {
      await endpoints.createClosure({ ...f, status: "active" });
      toast("Road closure published with detour info.");
      setOpen(false);
      setF({ name: "", road_name: "", start_time: "", end_time: "", alternate_route: "", description: "" });
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed", "error");
    } finally {
      setBusy(false);
    }
  };

  const normalize = async (c: RoadClosure) => {
    try {
      await endpoints.updateClosure(c.id, { status: "Normal" });
      toast(`${c.road_name} reopened — visitors updated.`);
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed", "error");
    }
  };

  return (
    <div>
      <PageHead
        kicker="Mobility"
        title="Road closures & detours"
        sub="Every closure auto-renders on the public map with an alternate route."
        right={<Button onClick={() => setOpen(true)}><Plus className="h-4 w-4" /> New closure</Button>}
      />
      <Load data={data} loading={loading} error={error}>
        {(closures) => (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {closures.map((c) => (
              <div key={c.id} className={clsx("card p-5", c.status !== "Normal" && "border-orange-200")}>
                <div className="flex items-start justify-between gap-2">
                  <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-orange-100 text-orange-600"><TrafficCone className="h-5 w-5" /></span>
                  <span className={clsx("chip", c.status === "Normal" ? "bg-emerald-100 text-emerald-800" : "bg-orange-100 text-orange-700")}>{c.status}</span>
                </div>
                <h3 className="mt-3 font-display text-lg font-semibold text-ink">{c.road_name || c.name}</h3>
                <p className="mt-1 text-xs text-ink-muted">{c.description}</p>
                <div className="mt-3 space-y-1 text-[11px] text-ink-muted">
                  <p>{c.start_time}{c.end_time ? ` – ${c.end_time}` : ""}</p>
                  {c.alternate_route && <p className="flex items-start gap-1"><span className="text-teal">Detour</span> {c.alternate_route}</p>}
                </div>
                {c.status !== "Normal" && (
                  <Button variant="outline" size="sm" className="mt-4" onClick={() => normalize(c)}>
                    <CheckCircle2 className="h-3.5 w-3.5" /> Mark normal
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </Load>

      <Modal open={open} onClose={() => setOpen(false)} title="Plan a road closure">
        <div className="space-y-3">
          <input className="input" placeholder="Closure name *" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
          <input className="input" placeholder="Road name" value={f.road_name} onChange={(e) => setF({ ...f, road_name: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input" type="datetime-local" value={f.start_time} onChange={(e) => setF({ ...f, start_time: e.target.value })} />
            <input className="input" type="datetime-local" value={f.end_time} onChange={(e) => setF({ ...f, end_time: e.target.value })} />
          </div>
          <input className="input" placeholder="Alternate route *" value={f.alternate_route} onChange={(e) => setF({ ...f, alternate_route: e.target.value })} />
          <textarea className="input min-h-20 resize-none" placeholder="Why / details" value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} />
          <Button onClick={create} disabled={busy} className="w-full" size="lg">{busy ? "Publishing…" : "Publish closure"}</Button>
        </div>
      </Modal>
    </div>
  );
}