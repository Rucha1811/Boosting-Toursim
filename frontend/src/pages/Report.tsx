import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import L from "leaflet";
import {
  Flag,
  CheckCircle2,
  Clock3,
  MapPin,
  Loader2,
  CircleUser,
  ShieldAlert,
} from "lucide-react";
import { clsx } from "clsx";
import { useToast } from "../state/toast";
import { useAuth } from "../state/auth";
import { useDestination } from "../state/destination";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { defaultCenter } from "../lib/leaflet";
import { REPORT_CATEGORIES, REPORT_STATUS_TONES } from "../lib/catalog";
import type { CommunityReport } from "../lib/types";
import { SectionTitle, Button, Spinner, ErrorNote, EmptyState } from "../components/ui";

export function ReportPage() {
  const { user } = useAuth();
  const { current, currentId } = useDestination();
  const { toast } = useToast();
  const [form, setForm] = useState({ category: "traffic", title: "", description: "" });
  const [pos, setPos] = useState<[number, number] | null>(null);
  const [sending, setSending] = useState(false);

  if (!user) {
    return (
      <div className="animate-fade-up mx-auto max-w-2xl px-6 py-16 text-center">
        <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-saffron-light text-saffron-deep">
          <Flag className="h-7 w-7" />
        </span>
        <h1 className="mt-4 font-display text-2xl font-bold text-ink">Help your city welcome visitors</h1>
        <p className="mx-auto mt-2 max-w-md text-sm text-ink-muted">
          Sign in as a resident or tourist to report what you see, so the tourism authority can act on it.
        </p>
        <Link to="/login" className="btn btn-primary btn-lg mt-6">Sign in to report</Link>
      </div>
    );
  }

  const submit = async () => {
    if (!form.title || !form.description) {
      toast("Add a title and a short description.", "error");
      return;
    }
    if (!pos) {
      toast("Tap a location on the map to place your report.", "error");
      return;
    }
    setSending(true);
    try {
      const r = await endpoints.createReport({
        category: form.category,
        title: form.title,
        description: form.description,
        lat: pos[0],
        lng: pos[1],
      });
      toast(`Report #${r.id} filed. AI classified it as "${r.ai_classification}".`);
      setForm({ category: "traffic", title: "", description: "" });
      setPos(null);
    } catch (e) {
      toast(e instanceof Error ? e.message : "Could not file report.", "error");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="animate-fade-up mx-auto max-w-4xl px-6 py-10">
      <SectionTitle
        kicker="Community eyes"
        title="Report an issue for visitors"
        sub="Chipped pavement, overflowing bin, traffic snarl at a heritage gate — flag it once, and the authority sees and routes it."
      />
      <form
        className="card space-y-4 p-6"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">Category</label>
            <select className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {REPORT_CATEGORIES.map((c) => (
                <option key={c.key} value={c.key}>{c.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Short title</label>
            <input className="input" placeholder="Broken paver near Mandvi Gate" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
        </div>
        <div>
          <label className="label">What did you see?</label>
          <textarea className="input min-h-24 resize-none" placeholder="Describe what's happening and what you'd want fixed…" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </div>
        <div>
          <label className="label">Tap the spot on the map</label>
          <div className="h-64 overflow-hidden rounded-2xl border border-ink/10">
            <MapContainer
              key={`report-${currentId}`}
              center={current ? [current.center_lat, current.center_lng] : defaultCenter}
              zoom={current ? Math.max(11, current.zoom) : 14}
              className="h-full w-full"
              scrollWheelZoom={false}
            >
              <TileLayer attribution='&copy; OpenStreetMap' url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />
              <ClickCatcher onPick={(ll) => setPos(ll)} />
              {pos && <Marker position={pos} icon={markIcon} />}
            </MapContainer>
          </div>
          <p className={clsx("mt-1.5 text-xs", pos ? "text-teal-deep" : "text-ink-faint")}>
            <MapPin className="mr-1 inline h-3.5 w-3.5" />
            {pos ? `Pin placed at ${pos[0].toFixed(4)}, ${pos[1].toFixed(4)}` : "No pin placed yet"}
          </p>
        </div>
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-ink-muted">
            Based on our AI classifier this looks like:{" "}
            <span className="chip bg-teal/10 text-teal-deep capitalize">{form.category.replace("_", " ")}</span>
          </p>
          <Button type="submit" disabled={sending} size="lg">
            {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Flag className="h-4 w-4" />}
            File report
          </Button>
        </div>
      </form>
    </div>
  );
}

const markIcon = L.divIcon({
  className: "leaflet-div-icon",
  html: '<div style="width:26px;height:26px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);background:#c2454f;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.3)"></div>',
  iconSize: [26, 26],
  iconAnchor: [13, 26],
});

function ClickCatcher({ onPick }: { onPick: (ll: [number, number]) => void }) {
  useMapEvents({
    click(e) {
      onPick([e.latlng.lat, e.latlng.lng]);
    },
  });
  return null;
}

export function MyReportsPage() {
  const { user } = useAuth();
  const { data: reports, loading, error, refresh } = usePoll<CommunityReport[]>(() => endpoints.myReports(), 30000);
  const { toast } = useToast();

  if (!user) {
    return (
      <div className="animate-fade-up mx-auto max-w-2xl px-6 py-16 text-center">
        <CircleUser className="mx-auto h-12 w-12 text-ink-faint" />
        <h1 className="mt-4 font-display text-2xl font-bold text-ink">Sign in to see your reports</h1>
        <Link to="/login" className="btn btn-primary btn-lg mt-6">Sign in</Link>
      </div>
    );
  }

  return (
    <div className="animate-fade-up mx-auto max-w-4xl px-6 py-10">
      <div className="flex items-center justify-between">
        <SectionTitle kicker={`${user.name.split(" ")[0]}'s reports`} title="Your reported issues" />
        <Link to="/report" className="btn btn-primary btn-md">+ New report</Link>
      </div>
      {loading && <Spinner />}
      {error && <ErrorNote text={error} />}
      {!loading && !error && (reports ?? []).length === 0 && (
        <EmptyState icon={<Flag className="h-6 w-6" />} title="Nothing reported yet" sub="When you flag something on the map it shows up here with live status." />
      )}
      <div className="space-y-3">
        {(reports ?? []).map((r) => (
          <div key={r.id} className="card p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="chip bg-sand-200 capitalize text-ink">{r.category.replace("_", " ")}</span>
                  {r.ai_classification && r.ai_classification !== r.category && (
                    <span className="chip bg-teal/10 text-teal-deep">AI: {r.ai_classification.replace("_", " ")}</span>
                  )}
                  {r.ai_confidence != null && <span className="text-[10px] text-ink-faint">{(r.ai_confidence * 100).toFixed(0)}% conf.</span>}
                </div>
                <h3 className="mt-2 font-display text-lg font-semibold text-ink">{r.title}</h3>
                <p className="mt-1 text-sm text-ink-muted">{r.description}</p>
              </div>
              <span className={clsx("chip", REPORT_STATUS_TONES[r.status] ?? REPORT_STATUS_TONES.Reported)}>
                {r.status === "Resolved" ? <CheckCircle2 className="h-3 w-3" /> : <Clock3 className="h-3 w-3" />} {r.status}
              </span>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-4 border-t border-ink/5 pt-3 text-[11px] text-ink-muted">
              <span className="flex items-center gap-1"><ShieldAlert className="h-3.5 w-3.5" /> Filed {new Date(r.created_at).toLocaleString("en-IN")}</span>
              {r.lat != null && (
                <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {r.lat.toFixed(4)}, {r.lng?.toFixed(4)}</span>
              )}
              {r.admin_note && <span className="rounded-full bg-sand-100 px-3 py-1 text-ink-soft">Officer note: {r.admin_note}</span>}
            </div>
          </div>
        ))}
      </div>
      {(reports ?? []).length > 0 && (
        <button onClick={refresh} className="btn btn-outline btn-sm mt-4">Refresh statuses</button>
      )}
    </div>
  );
}