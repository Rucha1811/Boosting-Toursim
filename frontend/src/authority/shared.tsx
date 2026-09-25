import type { ReactNode } from "react";
import { clsx } from "clsx";
import { Tile, Spinner, ErrorNote } from "../components/ui";

export function PageHead({ kicker, title, sub, right }: { kicker?: string; title: ReactNode; sub?: ReactNode; right?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        {kicker && <p className="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-saffron-deep">{kicker}</p>}
        <h1 className="font-display text-2xl font-semibold text-ink sm:text-3xl">{title}</h1>
        {sub && <p className="mt-1 max-w-2xl text-sm text-ink-muted">{sub}</p>}
      </div>
      {right}
    </div>
  );
}

export function Stat({ icon, label, value, sub, tone }: {
  icon: ReactNode;
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  tone?: "teal" | "saffron" | "blush" | "ink";
}) {
  const tones = {
    teal: "bg-teal/10 text-teal-deep",
    saffron: "bg-saffron/15 text-saffron-deep",
    blush: "bg-blush/10 text-blush",
    ink: "bg-ink/5 text-ink",
  };
  return (
    <Tile className="!p-4">
      <div className="flex items-start justify-between">
        <span className={clsx("flex h-10 w-10 items-center justify-center rounded-2xl", tones[tone ?? "teal"])}>{icon}</span>
      </div>
      <p className="mt-3 text-2xl font-bold tracking-tight text-ink">{value}</p>
      <p className="text-xs font-semibold uppercase tracking-wide text-ink-muted">{label}</p>
      {sub && <p className="mt-1 text-[11px] text-ink-faint">{sub}</p>}
    </Tile>
  );
}

export function Load<T>({ data, loading, error, children }: {
  data: T | null;
  loading: boolean;
  error: string | null;
  children: (d: T) => ReactNode;
}) {
  if (loading && !data) return <Spinner />;
  if (error && !data) return <ErrorNote text={error} />;
  if (!data) return null;
  return <>{children(data)}</>;
}

export function severityTone(s: string): string {
  switch (s) {
    case "critical":
      return "bg-red-600 text-white";
    case "high":
      return "bg-orange-500 text-white";
    case "medium":
      return "bg-amber-400 text-black";
    default:
      return "bg-emerald-500 text-white";
  }
}

export function levelTone(s: string): string {
  switch (s) {
    case "critical":
      return "bg-red-600 text-white";
    case "high":
      return "bg-orange-500 text-white";
    case "moderate":
      return "bg-amber-400 text-black";
    default:
      return "bg-emerald-500 text-white";
  }
}