from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth & users
# ---------------------------------------------------------------------------

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str
    phone: str = ""
    role: str = "tourist"  # tourist | resident | business | artisan | authority_officer


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    phone: str = ""
    role: str
    verified: bool = False

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


# ---------------------------------------------------------------------------
# Places
# ---------------------------------------------------------------------------

class AudioStoryIn(BaseModel):
    language: str = "en"
    title: str
    narrative: str
    duration_sec: int = 90


class AudioStoryOut(BaseModel):
    id: int
    place_id: int
    language: str
    title: str
    narrative: str
    duration_sec: int

    model_config = {"from_attributes": True}


class PlaceIn(BaseModel):
    name: str
    category: str = "heritage"
    subcategory: str = ""
    summary: str = ""
    description: str = ""
    history: str = ""
    cultural_significance: str = ""
    architecture: str = ""
    stories: str = ""
    traditions: str = ""
    visiting_info: str = ""
    address: str = ""
    lat: float
    lng: float
    image_urls: List[str] = []
    historical_period: str = ""
    opening_hours: dict = {}
    entry_fee: str = "Free"
    best_time: str = ""
    is_hidden: bool = False
    is_featured: bool = False
    est_capacity: int = 1000


class PlaceOut(BaseModel):
    id: int
    destination_id: int
    name: str
    category: str
    subcategory: str
    summary: str
    description: str
    history: str
    cultural_significance: str
    architecture: str
    stories: str
    traditions: str
    visiting_info: str
    address: str
    lat: float
    lng: float
    image_urls: List[str]
    historical_period: str
    opening_hours: dict
    entry_fee: str
    best_time: str
    is_hidden: bool
    is_featured: bool
    est_capacity: int
    listener_count: int = 0

    model_config = {"from_attributes": True}


class PlaceBrief(BaseModel):
    id: int
    name: str
    category: str
    summary: str
    lat: float
    lng: float
    image_urls: List[str]
    is_featured: bool

    model_config = {"from_attributes": True}


class PlaceDetailOut(PlaceOut):
    audio_stories: List[AudioStoryOut] = []
    current_visitors: int = 0
    crowd_level: str = "low"
    occupancy_ratio: float = 0.0


# ---------------------------------------------------------------------------
# Businesses / artisans
# ---------------------------------------------------------------------------

class ProductIn(BaseModel):
    name: str
    description: str = ""
    price: float = 0
    unit: str = ""
    material: str = ""
    image_url: str = ""
    available: bool = True


class ProductOut(BaseModel):
    id: int
    business_id: int
    name: str
    description: str
    price: float
    unit: str
    material: str
    image_url: str
    available: bool

    model_config = {"from_attributes": True}


class BusinessIn(BaseModel):
    name: str
    kind: str = "artisan"
    craft: str = ""
    craft_type: str = ""
    story: str = ""
    description: str = ""
    cultural_significance: str = ""
    address: str = ""
    lat: float
    lng: float
    image_urls: List[str] = []
    opening_hours: dict = {}
    contact: str = ""
    price_range: str = ""
    established_year: str = ""
    workshop_available: bool = False
    status: str = "Open"
    destination_id: Optional[int] = None


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    story: Optional[str] = None
    description: Optional[str] = None
    cultural_significance: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    image_urls: Optional[List[str]] = None
    opening_hours: Optional[dict] = None
    contact: Optional[str] = None
    price_range: Optional[str] = None
    established_year: Optional[str] = None
    workshop_available: Optional[bool] = None
    status: Optional[str] = None
    craft: Optional[str] = None
    craft_type: Optional[str] = None


class BusinessBrief(BaseModel):
    id: int
    name: str
    kind: str
    craft: str
    craft_type: str
    story: str
    description: str
    address: str
    lat: float
    lng: float
    image_urls: List[str]
    contact: str
    price_range: str
    workshop_available: bool
    status: str
    is_verified: bool
    featured: bool

    model_config = {"from_attributes": True}


class BusinessOut(BusinessBrief):
    cultural_significance: str
    established_year: str
    opening_hours: dict
    owner_id: Optional[int] = None
    products: List[ProductOut] = []
    experiences: List["ExperienceOut"] = []


class ExperienceIn(BaseModel):
    title: str
    category: str = "cultural"
    description: str = ""
    location: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None
    duration_minutes: int = 60
    price: float = 0
    price_note: str = ""
    availability: str = "Daily 9 AM - 6 PM"
    capacity: int = 15
    image_urls: List[str] = []
    featured: bool = False


class ExperienceOut(BaseModel):
    id: int
    destination_id: int
    provider_business_id: Optional[int] = None
    title: str
    category: str
    description: str
    location: str
    lat: Optional[float]
    lng: Optional[float]
    duration_minutes: int
    price: float
    price_note: str
    availability: str
    capacity: int
    image_urls: List[str]
    featured: bool
    provider_name: Optional[str] = ""

    model_config = {"from_attributes": True}


class EnquiryIn(BaseModel):
    business_id: Optional[int] = None
    experience_id: Optional[int] = None
    visitor_name: str = ""
    visitor_email: str = ""
    visitor_phone: str = ""
    message: str
    event_date: str = ""


class EnquiryOut(BaseModel):
    id: int
    business_id: Optional[int] = None
    visitor_name: str
    visitor_email: str
    visitor_phone: str
    message: str
    event_date: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Festivals / events
# ---------------------------------------------------------------------------

class FestivalOut(BaseModel):
    id: int
    destination_id: int
    name: str
    subtitle: str
    description: str
    start_date: str
    end_date: str
    status: str
    hero_image_url: str
    schedule_json: dict
    expected_visitors: int
    is_festival_mode: bool
    capacity: int

    model_config = {"from_attributes": True}


class EventIn(BaseModel):
    name: str
    category: str = "cultural"
    description: str = ""
    location_name: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None
    start_date: str
    end_date: str = ""
    start_time: str = "18:00"
    end_time: str = "22:00"
    expected_visitors: int = 0
    capacity: int = 0
    required_resources: List[str] = []
    traffic_impact: str = "Low"
    parking_requirements: str = ""
    status: str = "scheduled"


class EventOut(BaseModel):
    id: int
    destination_id: int
    festival_id: Optional[int] = None
    name: str
    category: str
    description: str
    location_name: str
    lat: Optional[float]
    lng: Optional[float]
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    expected_visitors: int
    capacity: int
    required_resources: List[str]
    traffic_impact: str
    parking_requirements: str
    status: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Live data
# ---------------------------------------------------------------------------

class ParkingAreaOut(BaseModel):
    id: int
    destination_id: int
    name: str
    lat: float
    lng: float
    capacity: int
    available: int
    is_temporary: bool
    notes: str

    model_config = {"from_attributes": True}


ParkingOut = ParkingAreaOut


class TransportOut(BaseModel):
    id: int
    destination_id: int
    name: str
    kind: str
    lat: float
    lng: float
    details: str

    model_config = {"from_attributes": True}


class EmergencyOut(BaseModel):
    id: int
    destination_id: int
    name: str
    kind: str
    lat: float
    lng: float
    phone: str
    details: str

    model_config = {"from_attributes": True}


class CrowdOut(BaseModel):
    place_id: Optional[int]
    event_id: Optional[int]
    level: str
    visitor_count: int
    capacity: int
    timestamp: datetime
    source: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Community reports
# ---------------------------------------------------------------------------

class CommunityReportIn(BaseModel):
    category: str = "traffic"
    title: str
    description: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None
    image_url: str = ""
    destination_id: Optional[int] = None


class CommunityReportOut(BaseModel):
    id: int
    destination_id: int
    category: str
    title: str
    description: str
    user_id: Optional[int]
    lat: Optional[float]
    lng: Optional[float]
    image_url: str
    status: str
    admin_note: str
    ai_classification: str
    ai_confidence: float
    reporter_name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportStatusUpdate(BaseModel):
    status: str
    admin_note: str = ""


# ---------------------------------------------------------------------------
# Alerts / announcements / closures
# ---------------------------------------------------------------------------

class AuthorityAlertIn(BaseModel):
    category: str = "crowd"
    place_id: Optional[int] = None
    title: str
    message: str
    severity: str = "info"
    is_active: bool = True
    starts_at: str = ""
    ends_at: str = ""


class AuthorityAlertOut(BaseModel):
    id: int
    destination_id: int
    place_id: Optional[int]
    category: str
    title: str
    message: str
    severity: str
    is_active: bool
    starts_at: str
    ends_at: str
    created_by: str

    model_config = {"from_attributes": True}


class AnnouncementIn(BaseModel):
    category: str = "general"
    title: str
    body: str
    important: bool = False


class AnnouncementOut(BaseModel):
    id: int
    destination_id: int
    category: str
    title: str
    body: str
    important: bool
    published_by: str
    created_at: datetime
    active: bool

    model_config = {"from_attributes": True}


class RoadClosureIn(BaseModel):
    name: str
    description: str = ""
    road_name: str = ""
    start_time: str = ""
    end_time: str = ""
    alternate_route: str = ""
    status: str = "active"
    lat: Optional[float] = None
    lng: Optional[float] = None


class RoadClosureOut(BaseModel):
    id: int
    destination_id: int
    name: str
    description: str
    road_name: str
    start_time: str
    end_time: str
    alternate_route: str
    status: str
    lat: Optional[float]
    lng: Optional[float]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Forecasts & recommendations
# ---------------------------------------------------------------------------

class ForecastOut(BaseModel):
    id: int
    destination_id: int
    place_id: Optional[int] = None
    place_name: Optional[str] = None
    date: str
    event_name: str = ""
    expected_visitors: int
    expected_peak_start: str
    expected_peak_end: str
    confidence: float
    high_footfall_zones: List[Any]
    method: str
    is_demo: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class AlternativeIn(BaseModel):
    place_id: int
    expected_visitors: int = 0
    capacity: int = 0


class RecommendationOut(BaseModel):
    id: int
    destination_id: int
    source_place_id: int
    source_place_name: str
    expected_visitors: int
    capacity: int
    status: str
    created_at: datetime
    alternatives: List[Any]

    model_config = {"from_attributes": True}


class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    role_channel: str
    meta: dict
    read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ActionRecommendation(BaseModel):
    action: str
    detail: str


class CrowdAssessmentOut(BaseModel):
    place_id: int
    place_name: str
    capacity: int
    current_visitors: int
    occupancy_ratio: float
    level: str
    risk: str
    expected_visitors: int
    status_label: str
    actions: List[ActionRecommendation]


class DestinationOut(BaseModel):
    id: int
    name: str
    tagline: str
    district: str
    state: str
    description: str
    image_url: str
    center_lat: float
    center_lng: float
    zoom: int

    model_config = {"from_attributes": True}


class DestinationSummary(DestinationOut):
    place_count: int = 0
    artisan_count: int = 0
    experience_count: int = 0
    event_count: int = 0
    hotel_count: int = 0


class DashboardOverview(BaseModel):
    current_visitors: int
    estimated_inflow_today: int
    expected_inflow_today: int
    notable_places: List[Any]
    hotel_occupancy_pct: int
    registered_hotels: int
    active_events: List[Any]
    festival: Optional[Any]
    traffic_status: str
    parking_status: str
    open_reports: int
    resolved_reports: int
    active_alerts: int
    recent_alerts: List[Any]
    recent_reports: List[Any]
    forecast: Optional[Any]
    is_demo: bool


class AlternativeSuggestion(BaseModel):
    place_id: int
    name: str
    category: str
    distance_km: float
    current_activity: str  # low | moderate | high
    reason: str
    image_url: str = ""


class AssistantResponse(BaseModel):
    answer: str
    intents: List[str]
    references: List[dict]


class Feedback(BaseModel):
    type: str
    place_id: int
    response_id: str = ""
    message: str

    model_config = {"from_attributes": True}


class NotificationPatch(BaseModel):
    read: bool = True


class WSMessage(BaseModel):
    channel: str
    event: str
    data: dict


# Allow forward refs
TokenOut.model_rebuild()
BusinessOut.model_rebuild()