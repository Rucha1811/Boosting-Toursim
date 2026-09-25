import { useState } from "react";
import { TrendingUp, Sparkles, Zap } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { Forecast } from "../lib/types";
import { fmtNum } from "../lib/catalog";
import { PageHead, Load } from "./shared";
import { Button } from "../components/ui";

export default function ForecastPage() {
  const { toast } = useToast();
  const { data, loading, error, refresh } = usePoll<Forecast[]>(() => endpoints.forecasts(), 60000);
  const [date, setDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().slice(0, 10);
  });
  const [busy, setBusy] = useState(false);

  const gen = async () => {
    setBusy(true);
    try {
      const f = await endpoints.generateForecast({ date });
      toast(`Forecast generated for ${f.date}: ${fmtNum(f.expected_visitors)} visitors.`);
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Forecast failed.", "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <PageHead
        kicker="AI planning"
        title="Visitor forecasts"
        sub="Heuristic + seasonal ensemble models blend weekdays, weather and festivals into tomorrow's numbers."
        right={
          <div className="flex items-center gap-2">
            <input type="date" className="input !w-44" value={date} onChange={(e) => setDate(e.target.value)} />
            <Button onClick={gen} disabled={busy}><Zap className="h-4 w-4" /> {busy ? "Forecasting…" : "Generate"}</Button>
          </div>
        }
      />
      <Load data={data} loading={loading} error={error}>
        {(list) => (
          <div className="grid gap-4 md:grid-cols-2">
            {list.map((f) => (
              <div key={f.id} className="card p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-ink-faint">{f.date} · {f.event_name}</p>
                    <p className="mt-1 font-display text-4xl font-bold text-ink">{fmtNum(f.expected_visitors)}</p>
                    <p className="mt-1 text-xs text-ink-muted">
                      Peak {f.expected_peak_start}–{f.expected_peak_end} · {Math.round((f.confidence ?? 0) * 100)}% confidence
                    </p>
                  </div>
                  <span className={clsx("chip", f.is_demo ? "bg-marigold-light text-amber-800" : "bg-emerald-100 text-emerald-800")}>
                    {f.method}
                  </span>
                </div>
                {f.high_footfall_zones?.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {f.high_footfall_zones.map((z) => (
                      <span key={z.zone} className="chip bg-saffron-light text-saffron-deep">{z.zone}: {fmtNum(z.expected)}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {list.length === 0 && (
              <div className="card col-span-2 flex flex-col items-center gap-3 p-12 text-center">
                <TrendingUp className="h-10 w-10 text-ink-faint" />
                <p className="text-sm text-ink-muted">No forecast yet — hit Generate to create tomorrow's plan.</p>
              </div>
            )}
          </div>
        )}
      </Load>
    </div>
  );
}