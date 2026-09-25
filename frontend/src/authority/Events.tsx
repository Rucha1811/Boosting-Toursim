import { useState } from "react";
import { PartyPopper, Plus, Trash2, Calendar, MapPin, Users } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { Event } from "../lib/types";
import { fmtNum } from "../lib/catalog";
import { PageHead, Load } from "./shared";
import { Button, Modal } from "../components/ui";

const BLANK = { name: "", category: "cultural", location_name: "", start_date: "2026-10-11", end_date: "2026-10-20", start_time: "18:00", end_time: "22:00", expected_visitors: 500, capacity: 1200, description: "" };

export default function EventsPage() {
  const { toast } = useToast();
  const { data, loading, error, refresh } = usePoll<Event[]>(() => endpoints.eventsAdmin(), 30000);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ ...BLANK });
  const [busy, setBusy] = useState(false);

  const create = async () => {
    if (!form.name) return toast("Give the event a name.", "error");
    setBusy(true);
    try {
      await endpoints.createEvent(form);
      toast("Event created — visible on the festival programme and live map.");
      setOpen(false);
      setForm({ ...BLANK });
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Could not create event.", "error");
    } finally {
      setBusy(false);
    }
  };

  const toggle = async (ev: Event) => {
    const status = ev.status === "Open" ? "Postponed" : "Open";
    try {
      await endpoints.updateEvent(ev.id, { status });
      toast(`${ev.name}: marked ${status}.`);
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Update failed.", "error");
    }
  };

  const remove = async (ev: Event) => {
    try {
      await endpoints.deleteEvent(ev.id);
      toast(`Removed ${ev.name}.`);
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Could not delete.", "error");
    }
  };

  return (
    <div>
      <PageHead
        kicker="Only during festivals"
        title="Festival & events"
        sub="Events are mapped live, with expected crowd and traffic notes forwarded to the public."
        right={<Button onClick={() => setOpen(true)}><Plus className="h-4 w-4" /> New event</Button>}
      />
      <Load data={data} loading={loading} error={error}>
        {(events) => (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {events.map((e) => (
              <div key={e.id} className="card flex flex-col p-5">
                <div className="flex items-start justify-between gap-2">
                  <span className="chip bg-blush-light text-blush">{e.category}</span>
                  <span className={clsx("chip", e.status === "Open" ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800")}>{e.status}</span>
                </div>
                <h3 className="mt-3 font-display text-lg font-semibold text-ink">{e.name}</h3>
                <p className="mt-1 line-clamp-2 text-xs text-ink-muted">{e.description}</p>
                <div className="mt-3 space-y-1.5 text-xs text-ink-muted">
                  <p className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5 text-teal" /> {e.location_name}</p>
                  <p className="flex items-center gap-1.5"><Calendar className="h-3.5 w-3.5 text-teal" /> {e.start_date} · {e.start_time}–{e.end_time}</p>
                  <p className="flex items-center gap-1.5"><Users className="h-3.5 w-3.5 text-teal" /> {fmtNum(e.expected_visitors)} expected</p>
                </div>
                <div className="mt-4 flex gap-2 border-t border-ink/5 pt-3">
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => toggle(e)}>
                    {e.status === "Open" ? "Mark postponed" : "Reopen"}
                  </Button>
                  <button onClick={() => remove(e)} className="rounded-full p-2 text-ink-faint hover:bg-blush-light hover:text-blush"><Trash2 className="h-4 w-4" /></button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Load>

      <Modal open={open} onClose={() => setOpen(false)} title="Create an event">
        <div className="space-y-3">
          <input className="input" placeholder="Event name *" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input capitalize" placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
            <input className="input" placeholder="Location" value={form.location_name} onChange={(e) => setForm({ ...form, location_name: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <input className="input" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
            <input className="input" type="time" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <input className="input" type="number" placeholder="Expected visitors" value={form.expected_visitors} onChange={(e) => setForm({ ...form, expected_visitors: Number(e.target.value) })} />
            <input className="input" type="number" placeholder="Capacity" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: Number(e.target.value) })} />
          </div>
          <textarea className="input min-h-20 resize-none" placeholder="Short description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <Button onClick={create} disabled={busy} className="w-full" size="lg">{busy ? "Creating…" : "Publish event"}</Button>
        </div>
      </Modal>
    </div>
  );
}