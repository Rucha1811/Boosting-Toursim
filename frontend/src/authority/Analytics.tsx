import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Cell, PieChart, Pie, Legend } from "recharts";
import { PageHead, Stat } from "./shared";
import { Load } from "./shared";
import { Users, TrendingUp, Thermometer, Layers } from "lucide-react";
import { fmtNum } from "../lib/catalog";

interface Analytics {
  daily: { date: string; visitors: number }[];
  hourly: { hour: number; avg: number }[];
  crowd_distribution: { low?: number; moderate?: number; high?: number; critical?: number };
  source?: string;
  note?: string;
}

const PIE_COLORS = ["#10b981", "#f59e0b", "#f97316", "#dc2626"];

export default function AnalyticsPage() {
  const { data, loading, error } = usePoll<Analytics>(() => endpoints.analytics() as unknown as Promise<Analytics>, 60000);

  const dist = data?.crowd_distribution ?? {};
  const total = (dist.low ?? 0) + (dist.moderate ?? 0) + (dist.high ?? 0) + (dist.critical ?? 0);
  const pieData = [
    { name: "Low", value: dist.low ?? 0 },
    { name: "Moderate", value: dist.moderate ?? 0 },
    { name: "High", value: dist.high ?? 0 },
    { name: "Critical", value: dist.critical ?? 0 },
  ].filter((d) => d.value > 0);

  return (
    <div>
      <PageHead
        kicker="Footfall intelligence"
        title="Analytics & trends"
        sub="Simulated 60-day history plus live stream. Clearly labelled demo data."
      />

      <Load data={data} loading={loading} error={error}>
        {(a) => (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-3">
              <Stat tone="teal" icon={<TrendingUp className="h-5 w-5" />} label="Days of history" value={a.daily.length} />
              <Stat tone="saffron" icon={<Users className="h-5 w-5" />} label="30-day peak" value={fmtNum(Math.max(0, ...a.daily.map((d) => d.visitors)))} />
              <Stat tone="ink" icon={<Layers className="h-5 w-5" />} label="High-crowd venues now" value={(dist.high ?? 0) + (dist.critical ?? 0)} />
            </div>

            <div className="card p-5">
              <h3 className="mb-4 flex items-center gap-2 font-display text-lg font-semibold text-ink">
                <TrendingUp className="h-5 w-5 text-teal" /> Daily visitors (60 days)
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={a.daily}>
                    <defs>
                      <linearGradient id="gV" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#0e5d54" stopOpacity={0.5} />
                        <stop offset="100%" stopColor="#0e5d54" stopOpacity={0.02} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d: string) => d.slice(5)} minTickGap={28} />
                    <YAxis tick={{ fontSize: 10 }} tickFormatter={(v: number) => `${Math.round(v / 1000)}k`} width={44} />
                    <Tooltip formatter={(v: number) => [`${v.toLocaleString()}`, "visitors"]} labelFormatter={(d: string) => `Date: ${d}`} />
                    <Area type="monotone" dataKey="visitors" stroke="#0e5d54" fill="url(#gV)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <div className="card p-5">
                <h3 className="mb-4 flex items-center gap-2 font-display text-lg font-semibold text-ink">
                  <Thermometer className="h-5 w-5 text-saffron-deep" /> Average by hour of day
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={a.hourly}>
                      <XAxis dataKey="hour" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} tickFormatter={(v: number) => `${Math.round(v / 1000)}k`} width={44} />
                      <Tooltip formatter={(v: number) => [`${v.toLocaleString()}`, "avg visitors"]} labelFormatter={(h) => `${h}:00`} />
                      <Bar dataKey="avg" radius={[6, 6, 0, 0]}>
                        {a.hourly.map((h) => (
                          <Cell key={h.hour} fill={h.hour >= 17 && h.hour <= 20 ? "#e0762c" : "#2f7d73"} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="card p-5">
                <h3 className="mb-4 font-display text-lg font-semibold text-ink">Live crowd distribution</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={3}>
                        {pieData.map((d, i) => (
                          <Cell key={d.name} fill={PIE_COLORS[i]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v: number) => [`${v} place${v === 1 ? "" : "s"}`, "count"]} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                {a.note && <p className="mt-2 text-center text-[11px] text-ink-faint">{a.note}</p>}
              </div>
            </div>
          </div>
        )}
      </Load>
    </div>
  );
}