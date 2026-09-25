import { useState } from "react";
import { Flag, MapPin, ShieldAlert } from "lucide-react";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { CommunityReport } from "../lib/types";
import { REPORT_STATUS_TONES } from "../lib/catalog";
import { PageHead, Load } from "./shared";
import { Button } from "../components/ui";

const STATUSES = ["Reported", "Under Review", "Assigned", "In Progress", "Resolved"];

export default function ReportsPage() {
  const { toast } = useToast();
  const { data, loading, error, refresh } = usePoll<CommunityReport[]>(() => endpoints.reports(), 20000);
  const [notes, setNotes] = useState<Record<number, string>>({});

  const update = async (r: CommunityReport, status: string) => {
    try {
      await endpoints.updateReportStatus(r.id, { status, admin_note: notes[r.id] ?? r.admin_note ?? "" });
      toast(`Report #${r.id} → ${status}.`);
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Update failed.", "error");
    }
  };

  return (
    <div>
      <PageHead
        kicker="Community reports"
        title="Report queue"
        sub="AI pre-classifies each report (confidence shown). Move them through the workflow — status is visible to the resident."
      />
      <Load data={data} loading={loading} error={error}>
        {(reports) => (
          <div className="space-y-3">
            {reports.map((r) => (
              <div key={r.id} className="card p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="chip bg-sand-200 capitalize text-ink">{r.category.replace("_", " ")}</span>
                      {r.ai_classification && r.ai_classification !== r.category && (
                        <span className="chip bg-teal/10 text-teal-deep">AI wrote: {r.ai_classification.replace("_", " ")}</span>
                      )}
                      {r.ai_confidence != null && <span className="text-[10px] text-ink-faint">{Math.round(r.ai_confidence * 100)}% conf</span>}
                    </div>
                    <h3 className="mt-2 font-display text-lg font-semibold text-ink">{r.title}</h3>
                    <p className="mt-1 text-sm text-ink-muted">{r.description}</p>
                    <div className="mt-2 flex flex-wrap items-center gap-3 text-[11px] text-ink-faint">
                      <span>by {r.reporter_name}</span>
                      <span>{new Date(r.created_at).toLocaleString("en-IN")}</span>
                      {r.lat != null && <span className="flex items-center gap-1"><MapPin className="h-3 w-3" /> {r.lat.toFixed(4)}, {r.lng?.toFixed(4)}</span>}
                    </div>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-2">
                    <span className={"chip " + (REPORT_STATUS_TONES[r.status] ?? REPORT_STATUS_TONES.Reported)}>{r.status}</span>
                    <select
                      className="input !w-44 !py-1.5 text-xs"
                      defaultValue=""
                      onChange={(e) => e.target.value && update(r, e.target.value)}
                    >
                      <option value="" disabled>Move to…</option>
                      {STATUSES.filter((s) => s !== r.status).map((s) => <option key={s}>{s}</option>)}
                    </select>
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-ink/5 pt-3">
                  <ShieldAlert className="h-4 w-4 text-saffron-deep" />
                  <input
                    className="input flex-1 !py-1.5 text-xs"
                    placeholder="Officer note (visible to resident)…"
                    value={notes[r.id] ?? r.admin_note ?? ""}
                    onChange={(e) => setNotes((n) => ({ ...n, [r.id]: e.target.value }))}
                  />
                  <Button variant="outline" size="sm" onClick={() => notes[r.id] != null && update(r, r.status)}>Save note</Button>
                </div>
              </div>
            ))}
            {reports.length === 0 && (
              <div className="card flex flex-col items-center gap-3 p-12 text-center">
                <Flag className="h-10 w-10 text-ink-faint" />
                <p className="text-sm text-ink-muted">No reports in the queue.</p>
              </div>
            )}
          </div>
        )}
      </Load>
    </div>
  );
}