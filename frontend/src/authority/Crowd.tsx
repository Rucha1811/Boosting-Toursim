import { useEffect, useMemo, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import {
  Users,
  ShieldAlert,
  Compass,
  CheckCircle2,
  Loader2,
  ArrowRight,
  MapPin,
  Zap,
} from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { CrowdAssessment, RecommendationOut } from "../lib/types";
import { fmtNum, crowdMeta } from "../lib/catalog";
import { PageHead, Load, levelTone, severityTone } from "./shared";

interface Alt {
  place_id: number;
  name: string;
  category: string;
  distance_km: number;
  current_activity: string;
  reason: string;
}

export default function CrowdPage() {
  const { toast } = useToast();
  const [params] = useSearchParams();
  const { data: assessments, error, loading } = usePoll<CrowdAssessment[]>(() => endpoints.crowdAssessment(), 20000);
  const { data: recs, loading: lr, refresh: refreshRecs } = usePoll<RecommendationOut[]>(() => endpoints.recommendations(), 30000);
  const [sel, setSel] = useState<number | null>(Number(params.get("place")) || null);
  const [alts, setAlts] = useState<Alt[] | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const active = useMemo(() => (assessments ?? []).find((a) => a.place_id === sel) ?? null, [assessments, sel]);

  useEffect(() => {
    setAlts(null);
  }, [sel]);

  const suggest = async () => {
    if (!sel) return;
    setAnalyzing(true);
    try {
      const alts = await endpoints.recommendAlternatives(sel);
      setAlts(alts);
    } catch (e) {
      toast(e instanceof Error ? e.message : "Could not fetch alternatives.", "error");
    } finally {
      setAnalyzing(false);
    }
  };

  const approve = async (rid: number) => {
    try {
      await endpoints.approveRecommendation(rid);
      toast("Recommendation approved — visitors now see it live!");
      refreshRecs();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Approval failed.", "error");
    }
  };

  const createAndApprove = async () => {
    if (!sel || !active) return;
    try {
      const created = await endpoints.createRecommendation({
        place_id: sel,
        expected_visitors: active.expected_visitors,
        capacity: active.capacity,
        alternatives: alts?.map((a) => a.place_id) ?? [],
      });
      await endpoints.approveRecommendation(created.id);
      toast(`Redirect approved for ${created.source_place_name} — public app updated.`);
      setAlts(null);
      refreshRecs();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Could not create recommendation.", "error");
    }
  };

  return (
    <div>
      <PageHead
        kicker="Crowd management"
        title="Redirect crowds smoothly"
        sub="See risk per venue, auto-suggest nearby alternatives and push authority-approved guidance to visitors live."
      />

      <div className="grid gap-5 lg:grid-cols-[1fr_420px]">
        {/* Venues list */}
        <div className="space-y-3">
          <Load data={assessments} loading={loading} error={error}>
            {(list) =>
              list.map((a) => (
                <button
                  key={a.place_id}
                  onClick={() => setSel(a.place_id)}
                  className={clsx(
                    "card w-full p-4 text-left transition hover:shadow-lift",
                    sel === a.place_id && "ring-2 ring-teal/40",
                  )}
                >
                  <div className="flex flex-wrap items-center gap-3">
                    <span className={clsx("chip", levelTone(a.level))}>{a.level}</span>
                    <div className="min-w-0 flex-1">
                      <p className="font-display text-base font-semibold text-ink">{a.place_name}</p>
                      <p className="text-[11px] text-ink-muted">
                        {fmtNum(a.current_visitors)} visitors · cap {fmtNum(a.capacity)} · {Math.round(a.occupancy_ratio * 100)}% full
                      </p>
                    </div>
                    {a.risk && a.risk !== "Low Risk" && (
                      <span className={clsx("chip", severityTone(a.risk.startsWith("CRITICAL") ? "critical" : "high"))}>
                        <ShieldAlert className="h-3 w-3" /> {a.risk}
                      </span>
                    )}
                  </div>
                  {a.actions?.slice(0, 2).map((x, i) => (
                    <p key={i} className="mt-2 text-[11px] text-ink-muted">◦ {x.action}</p>
                  ))}
                </button>
              ))
            }
          </Load>
        </div>

        {/* Detail panel */}
        <div className="space-y-4">
          {active ? (
            <>
              <div className={clsx("card overflow-hidden", active.level === "critical" || active.level === "high" ? "border-red-300" : "")}>
                <div className="bg-gradient-to-r from-teal-deep to-teal p-4 text-white">
                  <p className="text-[11px] uppercase tracking-wider text-sand-200">Analyzed venue</p>
                  <h3 className="font-display text-xl font-bold">{active.place_name}</h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <span className="chip bg-white/20 text-white">{active.level}</span>
                    <span className="chip bg-white/20 text-white">{fmtNum(active.expected_visitors)} expected</span>
                  </div>
                </div>
                <div className="space-y-3 p-4">
                  <div>
                    <div className="flex items-center justify-between text-[11px] text-ink-muted">
                      <span>Capacity utilisation</span>
                      <span>{Math.round(active.occupancy_ratio * 100)}%</span>
                    </div>
                    <div className="mt-1 h-2.5 overflow-hidden rounded-full bg-sand-200">
                      <div
                        className={clsx("h-full rounded-full", active.level === "critical" ? "bg-red-600" : active.level === "high" ? "bg-orange-500" : active.level === "moderate" ? "bg-amber-400" : "bg-emerald-500")}
                        style={{ width: `${Math.min(100, active.occupancy_ratio * 100)}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <p className="text-xs font-bold text-ink">Suggested operations</p>
                    {active.actions.map((x, i) => (
                      <p key={i} className="mt-1 text-xs text-ink-soft">
                        <span className="text-saffron-deep">•</span> {x.action}
                      </p>
                    ))}
                  </div>
                  <div className="flex flex-col gap-2 border-t border-ink/5 pt-3">
                    <button onClick={suggest} disabled={analyzing} className="btn btn-outline btn-md">
                      {analyzing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
                      Suggest alternatives
                    </button>
                    <Link to={`/authority/analytics?p=${active.place_id}`} className="btn btn-ghost btn-md">See analytics for this venue</Link>
                  </div>
                </div>
              </div>

              {alts && (
                <div className="card border border-saffron/40 p-4">
                  <div className="flex items-center gap-2">
                    <Compass className="h-5 w-5 text-saffron-deep" />
                    <p className="text-sm font-bold text-ink">Suggested alternatives</p>
                  </div>
                  <p className="mt-1 text-[11px] text-ink-muted">Ranked by distance × spare capacity.</p>
                  <div className="mt-3 space-y-2">
                    {alts.slice(0, 4).map((a) => (
                      <div key={a.place_id} className="rounded-xl bg-sand-50 p-3">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-semibold text-ink">{a.name}</p>
                          <span className="text-[11px] text-ink-muted">{a.distance_km} km</span>
                        </div>
                        <p className="mt-0.5 text-[11px] text-teal">{a.current_activity}</p>
                        <p className="mt-0.5 text-[11px] text-ink-muted">{a.reason}</p>
                      </div>
                    ))}
                  </div>
                  <button onClick={createAndApprove} className="btn btn-saffron btn-md mt-4 w-full">
                    <CheckCircle2 className="h-4 w-4" /> Create & approve redirect
                  </button>
                  <p className="mt-2 text-center text-[11px] text-ink-muted">
                    Approved guidance appears instantly on the public app.
                  </p>
                </div>
              )}
            </>
          ) : (
            <div className="card flex flex-col items-center gap-3 p-10 text-center">
              <Users className="h-10 w-10 text-ink-faint" />
              <p className="text-sm text-ink-muted">Select a venue to analyze and redirect crowds.</p>
            </div>
          )}

          {/* Past recommendations */}
          <div className="card p-4">
            <p className="text-sm font-bold text-ink">Active redirects</p>
            {lr && !recs ? (
              <p className="mt-2 text-xs text-ink-muted">Loading…</p>
            ) : (recs ?? []).length === 0 ? (
              <p className="mt-2 text-xs text-ink-muted">None yet — create the first redirect above.</p>
            ) : (
              <div className="mt-3 space-y-2">
                {(recs ?? []).map((r) => (
                  <div key={r.id} className={clsx("rounded-xl p-3", r.status === "approved" ? "bg-emerald-50" : "bg-amber-50")}>
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-ink">{r.source_place_name}</p>
                      <span className={clsx("chip", r.status === "approved" ? "bg-emerald-200 text-emerald-900" : "bg-amber-200 text-amber-900")}>{r.status}</span>
                    </div>
                    <p className="mt-1 text-[11px] text-ink-muted">
                      {r.alternatives?.length ?? 0} alternatives · {fmtNum(r.expected_visitors)} expected vs cap {fmtNum(r.capacity)}
                    </p>
                    {r.status !== "approved" && (
                      <button onClick={() => approve(r.id)} className="btn btn-saffron btn-sm mt-2">
                        Approve & publish
                      </button>
                    )}
                    {r.status === "approved" && (
                      <p className="mt-1.5 flex items-center gap-1 text-[11px] text-emerald-700">
                        <CheckCircle2 className="h-3.5 w-3.5" /> Live on the public app now
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}