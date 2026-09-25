import { useState } from "react";
import { Plus, ParkingCircle } from "lucide-react";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { TemporaryParking } from "../lib/types";
import { PageHead, Load } from "./shared";
import { Button, Modal } from "../components/ui";

export default function ParkingPage() {
  const { toast } = useToast();
  const { data, loading, error, refresh } = usePoll<TemporaryParking[]>(() => endpoints.parkingAdmin(), 30000);
  const [open, setOpen] = useState(false);
  const [f, setF] = useState({ name: "", capacity: 0, available: 0, notes: "", lat: 22.3, lng: 73.18 });
  const [busy, setBusy] = useState(false);

  const create = async () => {
    if (!f.name || f.capacity <= 0) return toast("Name and a positive capacity required.", "error");
    setBusy(true);
    try {
      await endpoints.createParking({ ...f, category: "temporary" });
      toast("Temporary parking published to visitors.");
      setOpen(false);
      setF({ name: "", capacity: 0, available: 0, notes: "", lat: 22.3, lng: 73.18 });
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed", "error");
    } finally {
      setBusy(false);
    }
  };

  const update = async (p: TemporaryParking, delta: number) => {
    const available = Math.max(0, Math.min(p.capacity, p.available + delta));
    try {
      await endpoints.updateParking(p.id, { available });
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed", "error");
    }
  };

  return (
    <div>
      <PageHead
        kicker="Festival parking"
        title="Temporary parking"
        sub="Extra bays activated during festivals are shown instantly on the public map."
        right={<Button onClick={() => setOpen(true)}><Plus className="h-4 w-4" /> New lot</Button>}
      />
      <Load data={data} loading={loading} error={error}>
        {(lots) => (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {lots.map((p) => (
              <div key={p.id} className="card p-5">
                <div className="flex items-start justify-between gap-2">
                  <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-sky-100 text-sky-700"><ParkingCircle className="h-5 w-5" /></span>
                  <span className="chip bg-white text-ink-muted">{p.notes}</span>
                </div>
                <h3 className="mt-3 font-display text-lg font-semibold text-ink">{p.name}</h3>
                <div className="mt-3 flex items-end justify-between">
                  <p className="font-display text-3xl font-bold text-ink">{p.available}<span className="text-base text-ink-faint">/{p.capacity}</span></p>
                  <p className="text-xs text-ink-muted">bays free</p>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-sand-200">
                  <div className="h-full bg-sky-600" style={{ width: `${Math.min(100, (p.available / Math.max(1, p.capacity)) * 100)}%` }} />
                </div>
                <div className="mt-4 flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => update(p, -2)}>− 2 used</Button>
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => update(p, 2)}>+ 2 freed</Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Load>

      <Modal open={open} onClose={() => setOpen(false)} title="Activate parking">
        <div className="space-y-3">
          <input className="input" placeholder="Lot name *" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input" type="number" placeholder="Capacity *" value={f.capacity} onChange={(e) => setF({ ...f, capacity: Number(e.target.value) })} />
            <input className="input" type="number" placeholder="Free now" value={f.available} onChange={(e) => setF({ ...f, available: Number(e.target.value) })} />
          </div>
          <input className="input" placeholder="Notes (e.g. near Mandvi Gate)" value={f.notes} onChange={(e) => setF({ ...f, notes: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input" placeholder="Lat" value={f.lat} onChange={(e) => setF({ ...f, lat: Number(e.target.value) })} />
            <input className="input" placeholder="Lng" value={f.lng} onChange={(e) => setF({ ...f, lng: Number(e.target.value) })} />
          </div>
          <Button onClick={create} disabled={busy} className="w-full" size="lg">{busy ? "Opening…" : "Open lot"}</Button>
        </div>
      </Modal>
    </div>
  );
}