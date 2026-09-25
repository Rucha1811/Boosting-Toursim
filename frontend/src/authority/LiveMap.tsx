import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import { Users, Flag, TrafficCone, ParkingCircle, Siren, PartyPopper, Loader2 } from "lucide-react";
import { usePoll } from "../hooks/usePoll";
import { endpoints } from "../lib/api";
import { useDestination } from "../state/destination";
import type { LiveMapData } from "../lib/types";
import { pinIcon, defaultCenter, defaultZoom } from "../lib/leaflet";
import { levelTone } from "./shared";
import { PageHead } from "./shared";
import { Spinner, ErrorNote } from "../components/ui";

export default function LiveMapPage() {
  const { current, currentId } = useDestination();
  const { data, loading, error } = usePoll<LiveMapData>(() => endpoints.liveMap(), 15000, [currentId]);

  return (
    <div className="flex h-full flex-col">
      <PageHead
        kicker="Geospatial command"
        title="Live operations map"
        sub="Concentration circles scale with live visitors. Dots refresh every ~15s."
        right={
          <span className="chip bg-emerald-100 text-emerald-800">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
            </span>
            {data ? `${data.concentration.length} venues streaming` : "connecting…"}
          </span>
        }
      />

      <div className="flex flex-1 gap-4">
        <div className="relative h-[70vh] min-h-[480px] flex-1 overflow-hidden rounded-2xl border border-ink/10 shadow-card">
          <MapContainer
            key={`opmap-${currentId}`}
            center={current ? [current.center_lat, current.center_lng] : defaultCenter}
            zoom={current ? current.zoom : defaultZoom}
            className="h-full w-full"
          >
            <TileLayer attribution='&copy; OpenStreetMap' url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {loading && !data && <div className="z-[500]"><Spinner /></div>}
            {error && !data && <div className="z-[500]"><ErrorNote text={error} /></div>}
            {data?.concentration.map((c) => (
              <Circle
                key={c.place_id}
                center={[c.lat, c.lng]}
                radius={Math.max(120, 3200 * (c.visitors / Math.max(1, c.capacity)) + (c.level === "critical" ? 2400 : c.level === "high" ? 1300 : 300))}
                pathOptions={{
                  color: c.level === "critical" ? "#dc2626" : c.level === "high" ? "#f97316" : c.level === "moderate" ? "#f59e0b" : "#10b981",
                  weight: c.level === "critical" || c.level === "high" ? 2 : 1,
                  fillOpacity: c.level === "critical" ? 0.42 : c.level === "high" ? 0.32 : 0.18,
                }}
              >
                <Popup>
                  <div className="text-xs">
                    <p className="font-bold text-ink">{c.name}</p>
                    <p className={levelTone(c.level)}>{c.level}</p>
                    <p>{c.visitors} visitors · cap {c.capacity}</p>
                    <Link to={`/authority/crowd?place=${c.place_id}`} className="font-semibold text-teal-deep">Manage crowd →</Link>
                  </div>
                </Popup>
              </Circle>
            ))}
            {data?.concentration.map((c) => (
              <Marker key={c.place_id} position={[c.lat, c.lng]} icon={pinIcon("#1d1a16", "place", "sm")}>
                <Popup>
                  <p className="text-xs font-bold">{c.name}</p>
                </Popup>
              </Marker>
            ))}
            {data?.events
              .filter((e) => e.lat != null && e.lng != null)
              .map((e) => (
                <Marker key={`ev-${e.id}`} position={[e.lat!, e.lng!]} icon={pinIcon("#c22f7a", "event", "md")}>
                  <Popup>
                    <p className="text-xs font-bold">{e.name}</p>
                    <p className="text-[11px]">{e.start_time} · {e.location_name}</p>
                  </Popup>
                </Marker>
              ))}
            {data?.parking.map((p) => (
              <Marker key={`pk-${p.id}`} position={[p.lat, p.lng]} icon={pinIcon("#0284c7", "parking", "sm")}>
                <Popup><p className="text-xs font-bold">{p.name}</p><p className="text-[11px]">{p.available}/{p.capacity} bays</p></Popup>
              </Marker>
            ))}
            {data?.reports
              .filter((r) => r.lat != null && r.lng != null)
              .map((r) => (
                <Marker key={`rp-${r.id}`} position={[r.lat!, r.lng!]} icon={pinIcon("#c2454f", "report", "sm")}>
                  <Popup><p className="text-xs font-bold">{r.title}</p><p className="text-[11px]">{r.status} · {r.category}</p></Popup>
                </Marker>
              ))}
            {data?.road_closures
              .filter((c) => c.lat != null && c.lng != null)
              .map((c) => (
                <Marker key={`cl-${c.id}`} position={[c.lat!, c.lng!]} icon={pinIcon("#1d4ed8", "closure", "sm")}>
                  <Popup><p className="text-xs font-bold">{c.road_name}</p><p className="text-[11px]">{c.alternate_route}</p></Popup>
                </Marker>
              ))}
            {data?.emergency.map((e) => (
              <Marker key={`em-${e.id}`} position={[e.lat, e.lng]} icon={pinIcon("#b91c1c", "emergency", "sm")}>
                <Popup><p className="text-xs font-bold">{e.name}</p><p className="text-[11px]">{e.kind} · {e.phone}</p></Popup>
              </Marker>
            ))}
          </MapContainer>

          {/* Legend */}
          <div className="absolute left-3 top-3 z-[500] rounded-2xl bg-white/90 p-3 text-[11px] shadow-lift backdrop-blur">
            {[
              ["#10b981", "Low", "0–40%"],
              ["#f59e0b", "Moderate", "40–70%"],
              ["#f97316", "High", "70–90%"],
              ["#dc2626", "Critical", "90%+"],
            ].map(([c, l, r]) => (
              <p key={l} className="flex items-center gap-2 py-0.5">
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: c }} /> {l} <span className="text-ink-faint">({r} capacity)</span>
              </p>
            ))}
            <div className="my-1.5 border-t border-ink/10" />
            <p className="flex items-center gap-2"><UserDot color="#c22f7a" /> Festival event</p>
            <p className="flex items-center gap-2"><UserDot color="#0284c7" /> Temporary parking</p>
            <p className="flex items-center gap-2"><UserDot color="#c2454f" /> Community report</p>
            <p className="flex items-center gap-2"><UserDot color="#1d4ed8" /> Road closure</p>
            <p className="flex items-center gap-2"><UserDot color="#b91c1c" /> Emergency facility</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function UserDot({ color }: { color: string }) {
  return <span className="h-2.5 w-2.5 rotate-45 rounded-[2px]" style={{ background: color }} />;
}