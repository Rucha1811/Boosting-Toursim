import L from "leaflet";

const GLYPH: Record<string, string> = {
  place: "M",
  business: "✦",
  experience: "✪",
  parking: "P",
  transport: "T",
  emergency: "!",
  event: "★",
  closure: "⊘",
  report: "⚑",
};

export function pinIcon(
  color: string,
  kind = "place",
  size: "sm" | "md" | "lg" = "md",
  crowd?: string,
): L.DivIcon {
  const dim = size === "lg" ? 40 : size === "md" ? 34 : 26;
  const glyph = GLYPH[kind] ?? "•";
  let ring = "";
  if (crowd === "critical") ring = "box-shadow:0 0 0 4px rgba(239,68,68,.35)";
  else if (crowd === "high") ring = "box-shadow:0 0 0 4px rgba(249,115,22,.32)";
  else if (crowd === "moderate") ring = "box-shadow:0 0 0 3px rgba(245,158,11,.25)";
  const html = `<div style="
    width:${dim}px;height:${dim}px;
    border-radius:50% 50% 50% 0;
    transform:rotate(-45deg);
    background:${color};
    border:2px solid #fff;
    display:flex;align-items:center;justify-content:center;
    ${ring}
  "><span style="
    transform:rotate(45deg);
    color:#fff;font-weight:800;
    font-size:${size === "lg" ? 15 : size === "md" ? 13 : 11}px;
    font-family:Inter,sans-serif;
  ">${glyph}</span></div>`;
  return L.divIcon({ className: "leaflet-div-icon", html, iconSize: [dim, dim], iconAnchor: [dim / 2, dim], popupAnchor: [0, -dim + 4] });
}

export function heatPin(defused = false): L.DivIcon {
  const dim = 22;
  const html = `<div style="
    width:${dim}px;height:${dim}px;border-radius:999px;
    background:${defused ? "#34d399" : "#f87171"};
    border:2px solid rgba(255,255,255,.85);
    box-shadow:0 2px 10px rgba(0,0,0,.25);
  "></div>`;
  return L.divIcon({ className: "leaflet-div-icon", html, iconSize: [dim, dim] });
}

export const defaultCenter: [number, number] = [22.3072, 73.1812];
export const defaultZoom = 13;