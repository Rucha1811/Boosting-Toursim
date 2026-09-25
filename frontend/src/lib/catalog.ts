import type { LucideIcon } from "lucide-react";
import {
  Landmark,
  ScrollText,
  Church,
  Utensils,
  Theater,
  Store,
  HandHeart,
  Hotel,
  Home,
  Compass,
  ShoppingBag,
  Car,
  TramFront,
  Siren,
  Flower2,
  MapPin,
  PartyPopper,
  Ticket,
  Sparkles,
} from "lucide-react";

export interface CategoryMeta {
  key: string;
  label: string;
  color: string;
  dot: string;
  icon: LucideIcon;
}

export const CATEGORIES: CategoryMeta[] = [
  { key: "heritage", label: "Heritage", color: "#e0762c", dot: "bg-saffron", icon: Landmark },
  { key: "history", label: "History", color: "#7c5cbf", dot: "bg-purple-600", icon: ScrollText },
  { key: "temple", label: "Temple & Faith", color: "#e8a710", dot: "bg-marigold", icon: Church },
  { key: "museum", label: "Museum", color: "#c2454f", dot: "bg-blush", icon: MapPin },
  { key: "market", label: "Market", color: "#8b5e34", dot: "bg-amber-800", icon: Store },
  { key: "food", label: "Local Food", color: "#d64541", dot: "bg-red-600", icon: Utensils },
  { key: "culture", label: "Cultural Venue", color: "#e35d6a", dot: "bg-rose-500", icon: Theater },
  { key: "artisans", label: "Artisans", color: "#0e5d54", dot: "bg-teal", icon: HandHeart },
  { key: "restaurant", label: "Restaurant", color: "#c3482f", dot: "bg-orange-700", icon: Utensils },
  { key: "hotel", label: "Hotel", color: "#3b6ea5", dot: "bg-blue-700", icon: Hotel },
  { key: "homestay", label: "Homestay", color: "#2f855a", dot: "bg-green-700", icon: Home },
  { key: "guide", label: "Local Guide", color: "#149e9e", dot: "bg-teal-600", icon: Compass },
  { key: "shopping", label: "Shopping", color: "#b07cb5", dot: "bg-fuchsia-600", icon: ShoppingBag },
  { key: "parking", label: "Parking", color: "#4a7fb5", dot: "bg-sky-600", icon: Car },
  { key: "transport", label: "Transport", color: "#5b7c99", dot: "bg-slate-500", icon: TramFront },
  { key: "emergency", label: "Emergency", color: "#c0392b", dot: "bg-red-700", icon: Siren },
  { key: "public_facility", label: "Public Facility", color: "#8a8578", dot: "bg-stone-500", icon: MapPin },
  { key: "garden", label: "Gardens & Parks", color: "#2e7d4f", dot: "bg-emerald-600", icon: Flower2 },
  { key: "landmark", label: "Landmark", color: "#b03a2e", dot: "bg-red-500", icon: MapPin },
  { key: "hidden_gem", label: "Hidden Gem", color: "#a67c00", dot: "bg-yellow-600", icon: Sparkles },
  { key: "event", label: "Festival & Event", color: "#c22f7a", dot: "bg-pink-600", icon: PartyPopper },
  { key: "experience", label: "Experience", color: "#c22f7a", dot: "bg-pink-600", icon: Ticket },
];

export function cat(key: string): CategoryMeta {
  return (
    CATEGORIES.find((c) => c.key === key) || {
      key,
      label: "Place",
      color: "#6b7280",
      dot: "bg-gray-500",
      icon: MapPin,
    }
  );
}

export function crowdMeta(level: string): { label: string; tone: string; ring: string } {
  switch (level) {
    case "critical":
      return { label: "Very busy", tone: "bg-red-600 text-white", ring: "border-red-600" };
    case "high":
      return { label: "Heavy activity", tone: "bg-orange-500 text-white", ring: "border-orange-500" };
    case "moderate":
      return { label: "Moderate", tone: "bg-amber-400 text-black", ring: "border-amber-400" };
    default:
      return { label: "Light crowd", tone: "bg-emerald-500 text-white", ring: "border-emerald-500" };
  }
}

export function statusTone(status: string): string {
  switch (status) {
    case "Open":
      return "bg-emerald-600 text-white";
    case "Closed":
      return "bg-stone-500 text-white";
    case "Limited Capacity":
      return "bg-amber-400 text-black";
    case "Fully Booked":
      return "bg-blush text-white";
    case "Special Event":
      return "bg-saffron text-white";
    default:
      return "bg-stone-200 text-ink";
  }
}

export const REPORT_STATUS_TONES: Record<string, string> = {
  Reported: "bg-stone-200 text-ink",
  "Under Review": "bg-sky-100 text-sky-800",
  Assigned: "bg-violet-100 text-violet-800",
  "In Progress": "bg-amber-100 text-amber-800",
  Resolved: "bg-emerald-100 text-emerald-800",
};

export const REPORT_CATEGORIES = [
  { key: "traffic", label: "Traffic" },
  { key: "parking", label: "Parking" },
  { key: "waste", label: "Waste" },
  { key: "infrastructure", label: "Infrastructure" },
  { key: "safety", label: "Safety concern" },
  { key: "overcrowding", label: "Overcrowding" },
  { key: "other", label: "Other" },
];

export function fmtInr(n: number): string {
  return `₹${n >= 1000 ? Math.round(n / 100) / 10 + "k" : n}`;
}

export function fmtNum(n: number): string {
  if (n >= 100000) return `${(n / 1000).toFixed(0)}k`;
  if (n >= 1000) return `${Math.round(n / 100) / 10}k`;
  return String(Math.round(n));
}

export function fmtDateShort(iso?: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  return isNaN(d.getTime()) ? iso.slice(0, 10) : d.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
}