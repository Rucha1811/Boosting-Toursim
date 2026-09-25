const BASE = "/api";

/** Module-level active destination id. The React destination context calls
 *  setCurrentDestinationId() on switch; every request reads it live so polls
 *  and non-hook callers stay in sync without prop drilling. */
export let currentDestinationId = (() => {
  const raw = typeof localStorage !== "undefined" ? localStorage.getItem("virsa_dest_id") : null;
  const n = raw ? Number(raw) : 1;
  return Number.isInteger(n) && n > 0 ? n : 1;
})();

export function setCurrentDestinationId(id: number) {
  currentDestinationId = id;
}

export function getSavedDestinationId(): number {
  return currentDestinationId;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export function getToken(): string | null {
  return localStorage.getItem("virsa_token");
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem("virsa_token", token);
  else localStorage.removeItem("virsa_token");
}

async function request<T>(path: string, options: RequestInit = {}, auth = true): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  headers["X-Destination-Id"] = String(currentDestinationId);
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (res.status === 204) return undefined as T;
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = body?.detail || body?.message || `Request failed (${res.status})`;
    throw new ApiError(res.status, typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body as T;
}

export const api = {
  get: <T>(path: string, auth = true) => request<T>(path, {}, auth),
  post: <T>(path: string, body?: unknown, auth = true) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body ?? {}) }, auth),
  patch: <T>(path: string, body?: unknown, auth = true) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body ?? {}) }, auth),
  del: <T>(path: string, auth = true) => request<T>(path, { method: "DELETE" }, auth),
};

const qs = (params: Record<string, string | number | boolean | undefined>) => {
  const sp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
  });
  const s = sp.toString();
  return s ? `?${s}` : "";
};

export const endpoints = {
  destinations: () => api.get< import("./types").Destination[] >("/destinations"),
  place: (id: number) => api.get< import("./types").Place >(`/places/${id}`),
  nearby: (id: number) => api.get< import("./types").NearbyBundle >(`/places/${id}/nearby`),
  artisans: () => api.get< import("./types").Business[] >(`/artisans${qs({ destination_id: currentDestinationId })}`),
  artisan: (id: number) => api.get< import("./types").Business >(`/artisans/${id}`),
  experiences: () => api.get< import("./types").Experience[] >(`/experiences${qs({ destination_id: currentDestinationId })}`),
  festivals: () => api.get< import("./types").Festival[] >(`/festivals${qs({ destination_id: currentDestinationId })}`),
  festival: (id: number) =>
    api.get<{ festival: import("./types").Festival; events: import("./types").Event[] }>(`/festivals/${id}`),
  events: () => api.get< import("./types").Event[] >(`/events${qs({ destination_id: currentDestinationId })}`),
  hotels: () => api.get< import("./types").Business[] >(`/hotels${qs({ destination_id: currentDestinationId })}`),
  hotelsAggregate: () =>
    api.get<Record<string, unknown>>(`/hotels/aggregate${qs({ destination_id: currentDestinationId })}`),
  markers: (categories?: string[]) =>
    api.get< import("./types").Marker[] >(`/map/markers${qs({ categories: categories?.join(","), destination_id: currentDestinationId })}`),
  mapInfo: () => api.get< import("./types").DynamicInfo >(`/map/info${qs({ destination_id: currentDestinationId })}`),
  assistant: (question: string, destination_id = currentDestinationId) =>
    api.post< import("./types").AssistantAnswer >("/assistant/ask", { question, destination_id }),
  createReport: (body: Record<string, unknown>) =>
    api.post< import("./types").CommunityReport >("/reports", { destination_id: currentDestinationId, ...body }),
  myReports: () => api.get< import("./types").CommunityReport[] >("/reports/mine"),
  createEnquiry: (body: Record<string, unknown>) => api.post("/enquiries", body),

  overview: () => api.get< import("./types").Overview >(`/authority/overview${qs({ destination_id: currentDestinationId })}`),
  liveMap: () => api.get< import("./types").LiveMapData >(`/authority/live-map${qs({ destination_id: currentDestinationId })}`),
  analytics: () => api.get<Record<string, unknown>>(`/authority/analytics${qs({ destination_id: currentDestinationId })}`),
  crowdAssessment: () => api.get< import("./types").CrowdAssessment[] >(`/authority/crowd-assessment${qs({ destination_id: currentDestinationId })}`),
  placeCrowd: (id: number) => api.get< import("./types").CrowdAssessment >(`/authority/places/${id}/crowd`),
  recommendAlternatives: (placeId: number) =>
    api.post< { place_id: number; name: string; category: string; distance_km: number; current_activity: string; reason: string }[] >(
      `/authority/places/${placeId}/recommend-alternatives`,
    ),
  createRecommendation: (body: Record<string, unknown>) =>
    api.post< import("./types").RecommendationOut >("/authority/recommendations", body),
  recommendations: () => api.get< import("./types").RecommendationOut[] >("/authority/recommendations"),
  approveRecommendation: (id: number) =>
    api.post< import("./types").RecommendationOut >(`/authority/recommendations/${id}/approve`),
  eventsAdmin: () => api.get< import("./types").Event[] >(`/authority/events${qs({ destination_id: currentDestinationId })}`),
  createEvent: (b: Record<string, unknown>) => api.post< import("./types").Event >("/authority/events", b),
  updateEvent: (id: number, b: Record<string, unknown>) =>
    api.patch< import("./types").Event >(`/authority/events/${id}`, b),
  deleteEvent: (id: number) => api.del(`/authority/events/${id}`),
  alerts: () => api.get< import("./types").AuthorityAlert[] >(`/authority/alerts${qs({ destination_id: currentDestinationId })}`),
  createAlert: (b: Record<string, unknown>) => api.post< import("./types").AuthorityAlert >("/authority/alerts", b),
  updateAlert: (id: number, b: Record<string, unknown>) =>
    api.patch< import("./types").AuthorityAlert >(`/authority/alerts/${id}`, b),
  closures: () => api.get< import("./types").RoadClosure[] >(`/authority/closures${qs({ destination_id: currentDestinationId })}`),
  createClosure: (b: Record<string, unknown>) => api.post< import("./types").RoadClosure >("/authority/closures", b),
  updateClosure: (id: number, b: Record<string, unknown>) =>
    api.patch< import("./types").RoadClosure >(`/authority/closures/${id}`, b),
  announcements: () => api.get< import("./types").Announcement[] >(`/authority/announcements${qs({ destination_id: currentDestinationId })}`),
  createAnnouncement: (b: Record<string, unknown>) =>
    api.post< import("./types").Announcement >("/authority/announcements", b),
  reports: () => api.get< import("./types").CommunityReport[] >(`/reports${qs({ destination_id: currentDestinationId })}`),
  updateReportStatus: (id: number, b: Record<string, unknown>) =>
    api.patch< import("./types").CommunityReport >(`/authority/reports/${id}/status`, b),
  parkingAdmin: () => api.get< import("./types").TemporaryParking[] >(`/authority/parking${qs({ destination_id: currentDestinationId })}`),
  createParking: (b: Record<string, unknown>) => api.post< import("./types").TemporaryParking >("/authority/parking", b),
  updateParking: (id: number, b: Record<string, unknown>) =>
    api.patch< import("./types").TemporaryParking >(`/authority/parking/${id}`, b),
  hotelsAggregateAdmin: () => api.get<Record<string, unknown>>(`/authority/hotels/aggregate${qs({ destination_id: currentDestinationId })}`),
  businessesAdmin: () => api.get< import("./types").Business[] >(`/authority/businesses${qs({ destination_id: currentDestinationId })}`),
  updateBusinessAdmin: (id: number, b: Record<string, unknown>) =>
    api.patch<Record<string, unknown>>(`/authority/businesses/${id}`, b),
  forecasts: () => api.get< import("./types").Forecast[] >(`/authority/forecast${qs({ destination_id: currentDestinationId })}`),
  generateForecast: (b: Record<string, unknown>) => api.post< import("./types").Forecast >("/authority/forecast/generate", b),

  myBusinesses: () => api.get< import("./types").Business[] >("/businesses/my"),
  createBusiness: (b: Record<string, unknown>) => api.post< import("./types").Business >("/businesses", b),
  updateBusiness: (id: number, b: Record<string, unknown>) =>
    api.patch< import("./types").Business >(`/businesses/${id}`, b),
  businessEnquiries: (id: number) => api.get< import("./types").Enquiry[] >(`/businesses/${id}/enquiries`),
  updateEnquiry: (businessId: number, id: number, b: Record<string, unknown>) =>
    api.patch< import("./types").Enquiry >(`/businesses/${businessId}/enquiries/${id}`, b),
  addProduct: (businessId: number, b: Record<string, unknown>) =>
    api.post< import("./types").Product >(`/businesses/${businessId}/products`, b),
  updateProduct: (businessId: number, productId: number, b: Record<string, unknown>) =>
    api.patch< import("./types").Product >(`/businesses/${businessId}/products/${productId}`, b),
};