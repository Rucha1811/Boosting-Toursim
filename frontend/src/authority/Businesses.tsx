import { useState } from "react";
import { Store, BadgeCheck, Ticket } from "lucide-react";
import { clsx } from "clsx";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useToast } from "../state/toast";
import type { Business } from "../lib/types";
import { PageHead, Load } from "./shared";
import { Button } from "../components/ui";

export default function BusinessesPage() {
  const { toast } = useToast();
  const { data, loading, error, refresh } = usePoll<Business[]>(() => endpoints.businessesAdmin(), 30000);
  const [kind, setKind] = useState("all");

  const list = (data ?? []).filter((b) => kind === "all" || b.kind === kind);

  const toggleVerify = async (b: Business) => {
    try {
      await endpoints.updateBusinessAdmin(b.id, { is_verified: !b.is_verified });
      toast(`${b.name} verification ${!b.is_verified ? "on" : "off"}.`);
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed", "error");
    }
  };

  const toggleStatus = async (b: Business) => {
    const status = b.status === "Open" ? "Closed" : "Open";
    try {
      await endpoints.updateBusinessAdmin(b.id, { status });
      toast(`${b.name}: ${status}.`);
      refresh();
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed", "error");
    }
  };

  return (
    <div>
      <PageHead
        kicker="Community commerce"
        title="Businesses & artisans"
        sub="Verify local businesses and control their operating status — changes reflect instantly on public pages."
      />
      <div className="mb-4 flex flex-wrap gap-2">
        {["all", "artisan", "food", "restaurant", "hotel", "homestay"].map((k) => (
          <button key={k} onClick={() => setKind(k)} className={clsx("rounded-full px-3.5 py-1.5 text-xs font-semibold capitalize", kind === k ? "bg-teal text-white" : "bg-white text-ink-soft")}>
            {k}
          </button>
        ))}
      </div>
      <Load data={data} loading={loading} error={error}>
        {() => (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {list.map((b) => (
              <div key={b.id} className="card p-5">
                <div className="flex items-start justify-between gap-2">
                  <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-teal/10 text-teal-deep"><Store className="h-5 w-5" /></span>
                  <span className={clsx("chip", b.status === "Open" ? "bg-emerald-100 text-emerald-800" : "bg-stone-200 text-ink-faint")}>{b.status}</span>
                </div>
                <h3 className="mt-3 font-display text-lg font-semibold text-ink">{b.name}</h3>
                <p className="text-[11px] uppercase tracking-wide text-ink-faint">{b.kind} · {b.craft}</p>
                <p className="mt-2 line-clamp-2 text-xs text-ink-muted">{b.story}</p>
                <div className="mt-3 flex items-center gap-3 text-[11px] text-ink-muted">
                  <span className="flex items-center gap-1"><BadgeCheck className={clsx("h-3.5 w-3.5", b.is_verified ? "text-teal" : "text-ink-faint")} /> {b.is_verified ? "Verified" : "Unverified"}</span>
                  <span className="flex items-center gap-1"><Ticket className="h-3.5 w-3.5" /> {b.experiences?.length ?? 0} experiences</span>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => toggleVerify(b)}>{b.is_verified ? "Unverify" : "Verify"}</Button>
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => toggleStatus(b)}>{b.status === "Open" ? "Close" : "Reopen"}</Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Load>
    </div>
  );
}