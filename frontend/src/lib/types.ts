export type Role =
  | "tourist"
  | "resident"
  | "business"
  | "artisan"
  | "authority_officer"
  | "authority_admin";

export interface User {
  id: number;
  email: string;
  name: string;
  phone: string;
  role: Role;
  verified: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Destination {
  id: number;
  name: string;
  tagline: string;
  district: string;
  state: string;
  description: string;
  image_url: string;
  center_lat: number;
  center_lng: number;
  zoom: number;
  place_count: number;
  artisan_count: number;
  experience_count: number;
  event_count: number;
  hotel_count: number;
}

export type PlaceCategory =
  | "heritage"
  | "history"
  | "temple"
  | "museum"
  | "market"
  | "food"
  | "culture"
  | "hidden_gem"
  | "landmark"
  | "garden";

export interface AudioStory {
  id: number;
  place_id: number;
  language: string;
  title: string;
  narrative: string;
  duration_sec: number;
}

export interface Place {
  id: number;
  destination_id: number;
  name: string;
  category: PlaceCategory;
  subcategory: string;
  summary: string;
  description: string;
  history: string;
  cultural_significance: string;
  architecture: string;
  stories: string;
  traditions: string;
  visiting_info: string;
  address: string;
  lat: number;
  lng: number;
  image_urls: string[];
  historical_period: string;
  opening_hours: Record<string, string>;
  entry_fee: string;
  best_time: string;
  is_hidden: boolean;
  is_featured: boolean;
  est_capacity: number;
  listener_count: number;
  audio_stories: AudioStory[];
  current_visitors: number;
  crowd_level: string;
  occupancy_ratio: number;
}

export interface Product {
  id: number;
  business_id: number;
  name: string;
  description: string;
  price: number;
  unit: string;
  material: string;
  image_url: string;
  available: boolean;
}

export interface Business {
  id: number;
  name: string;
  kind: string;
  craft: string;
  craft_type: string;
  story: string;
  description: string;
  cultural_significance: string;
  address: string;
  lat: number;
  lng: number;
  image_urls: string[];
  contact: string;
  price_range: string;
  workshop_available: boolean;
  status: string;
  is_verified: boolean;
  featured: boolean;
  established_year: string;
  opening_hours: Record<string, string>;
  owner_id?: number | null;
  products: Product[];
  experiences: Experience[];
}

export interface Experience {
  id: number;
  destination_id: number;
  provider_business_id?: number | null;
  title: string;
  category: string;
  description: string;
  location: string;
  lat?: number | null;
  lng?: number | null;
  duration_minutes: number;
  price: number;
  price_note: string;
  availability: string;
  capacity: number;
  image_urls: string[];
  featured: boolean;
  provider_name?: string;
}

export interface Festival {
  id: number;
  name: string;
  subtitle: string;
  description: string;
  start_date: string;
  end_date: string;
  status: string;
  hero_image_url: string;
  schedule_json: Record<string, string>;
  expected_visitors: number;
  is_festival_mode: boolean;
  capacity: number;
}

export interface Event {
  id: number;
  festival_id?: number | null;
  name: string;
  category: string;
  description: string;
  location_name: string;
  lat?: number | null;
  lng?: number | null;
  start_date: string;
  end_date: string;
  start_time: string;
  end_time: string;
  expected_visitors: number;
  capacity: number;
  required_resources: string[];
  traffic_impact: string;
  parking_requirements: string;
  status: string;
}

export interface Marker {
  id: number;
  type: string; // place | business | experience | parking | transport | emergency | event
  entity_id: number;
  name: string;
  category: string;
  subtitle?: string;
  lat: number;
  lng: number;
  image?: string;
  crowd?: string;
  visitors?: number;
  status?: string;
  is_hidden?: boolean;
  temporary?: boolean;
}

export interface AuthorityAlert {
  id: number;
  category: string;
  place_id?: number | null;
  place_name?: string;
  title: string;
  message: string;
  severity: string;
  is_active: boolean;
  starts_at: string;
  ends_at: string;
  current_visitors?: number;
  capacity?: number;
  level?: string;
}

export interface RoadClosure {
  id: number;
  name: string;
  description: string;
  road_name: string;
  start_time: string;
  end_time: string;
  alternate_route: string;
  status: string;
  lat?: number | null;
  lng?: number | null;
}

export interface TemporaryParking {
  id: number;
  name: string;
  available: number;
  capacity: number;
  notes: string;
  lat: number;
  lng: number;
}

export interface Announcement {
  id: number;
  title: string;
  body: string;
  category: string;
  important: boolean;
  created_at: string;
}

export interface Recommendation {
  id: number;
  source_place_id: number;
  source_place_name: string;
  expected_visitors: number;
  capacity: number;
  alternatives: {
    id: number;
    name: string;
    category: string;
    activity?: string;
    image?: string;
    summary?: string;
  }[];
}

export interface DynamicInfo {
  alerts: AuthorityAlert[];
  road_closures: RoadClosure[];
  temporary_parking: TemporaryParking[];
  announcements: Announcement[];
  recommendations: Recommendation[];
  updated_at: string;
}

export interface CommunityReport {
  id: number;
  destination_id: number;
  category: string;
  title: string;
  description: string;
  user_id?: number | null;
  lat?: number | null;
  lng?: number | null;
  image_url: string;
  status: string;
  admin_note: string;
  ai_classification: string;
  ai_confidence: number;
  reporter_name: string;
  created_at: string;
  updated_at: string;
}

export interface NearbyBundle {
  places: {
    id: number;
    name: string;
    category: string;
    summary: string;
    distance_km: number;
    image_url: string;
    activity: string;
  }[];
  artisans: { id: number; name: string; craft: string; distance_km: number; image_url: string; status: string }[];
  food: { id: number; name: string; kind: string; distance_km: number; image_url: string }[];
  experiences: { id: number; title: string; duration_minutes: number; price: number; distance_km: number }[];
  events: { id: number; name: string; start_date: string; distance_km: number }[];
}

export interface CrowdAssessment {
  place_id: number;
  place_name: string;
  capacity: number;
  current_visitors: number;
  occupancy_ratio: number;
  level: string;
  risk: string;
  expected_visitors: number;
  status_label: string;
  actions: { action: string; detail: string }[];
}

export interface Overview {
  current_visitors: number;
  estimated_inflow_today: number;
  expected_inflow_today: number;
  notable_places: {
    place_id: number;
    name: string;
    visitors: number;
    capacity: number;
    level: string;
    ratio: number;
  }[];
  hotel_occupancy_pct: number;
  registered_hotels: number;
  active_events: Event[];
  festival: Festival | null;
  traffic_status: string;
  parking_status: string;
  open_reports: number;
  resolved_reports: number;
  active_alerts: number;
  recent_alerts: AuthorityAlert[];
  recent_reports: { id: number; title: string; category: string; status: string; created_at: string }[];
  forecast: Forecast | null;
  is_demo: boolean;
}

export interface Forecast {
  id: number;
  destination_id: number;
  place_id?: number | null;
  place_name?: string | null;
  date: string;
  event_name: string;
  expected_visitors: number;
  expected_peak_start: string;
  expected_peak_end: string;
  confidence: number;
  high_footfall_zones: { zone: string; expected: number }[];
  method: string;
  is_demo: boolean;
  created_at: string;
}

export interface LiveMapData {
  concentration: {
    place_id: number;
    name: string;
    lat: number;
    lng: number;
    visitors: number;
    capacity: number;
    level: string;
    category: string;
  }[];
  road_closures: RoadClosure[];
  reports: (CommunityReport & {})[];
  events: Event[];
  parking: TemporaryParking[];
  emergency: { id: number; name: string; kind: string; lat: number; lng: number; phone: string }[];
  source: string;
}

export interface Enquiry {
  id: number;
  business_id: number;
  visitor_name: string;
  visitor_email: string;
  visitor_phone: string;
  message: string;
  event_date: string;
  status: string;
  created_at: string;
}

export interface AssistantAnswer {
  answer: string;
  intents: string[];
  references: { place_id?: number; business_id?: number; experience_id?: number; name: string; type: string }[];
}

export interface RecommendationOut {
  id: number;
  destination_id: number;
  source_place_id: number;
  source_place_name: string;
  expected_visitors: number;
  capacity: number;
  status: string;
  created_at: string;
  alternatives: { place_id: number; name: string; category: string; summary?: string }[];
}

export interface Notification {
  id: number;
  title: string;
  body: string;
  role_channel: string;
  meta: Record<string, unknown>;
  read: boolean;
  created_at: string;
}