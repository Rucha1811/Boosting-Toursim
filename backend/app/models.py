from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core.database import Base

# ---------------------------------------------------------------------------
# Enumerations (kept as plain strings for portability)
# ---------------------------------------------------------------------------

USER_ROLES = ["tourist", "resident", "business", "artisan", "authority_officer", "authority_admin"]

PLACE_CATEGORIES = [
    "heritage", "history", "temple", "museum", "market", "food", "culture",
    "hotel", "homestay", "guide", "shopping", "parking", "transport",
    "emergency", "public_facility", "hidden_gem", "landmark", "garden",
]

BUSINESS_KINDS = [
    "artisan", "restaurant", "food", "hotel", "homestay", "guide",
    "workshop", "experience_provider", "performer", "retail",
]

EVENT_CATEGORIES = ["cultural", "festival", "sports", "food", "music", "art", "religious", "heritage"]

REPORT_CATEGORIES = ["traffic", "parking", "waste", "infrastructure", "safety", "overcrowding", "other"]

REPORT_STATUSES = ["Reported", "Under Review", "Assigned", "In Progress", "Resolved"]

ALERT_SEVERITIES = ["info", "warning", "critical"]

CROWD_LEVELS = ["low", "moderate", "high", "critical"]

BUSINESS_STATUS = ["Open", "Closed", "Limited Capacity", "Fully Booked", "Special Event"]


# ---------------------------------------------------------------------------
# Users & identity
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String, default="")
    role: Mapped[str] = mapped_column(String, default="tourist")
    avatar_url: Mapped[str] = mapped_column(String, default="")
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    businesses = relationship("Business", back_populates="owner")
    reports = relationship("CommunityReport", back_populates="reporter")
    notifications = relationship("Notification", back_populates="user")


# ---------------------------------------------------------------------------
# Destination
# ---------------------------------------------------------------------------

class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    tagline: Mapped[str] = mapped_column(String, default="")
    district: Mapped[str] = mapped_column(String, default="")
    state: Mapped[str] = mapped_column(String, default="Gujarat")
    description: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String, default="")
    center_lat: Mapped[float] = mapped_column(Float, default=22.3072)
    center_lng: Mapped[float] = mapped_column(Float, default=73.1812)
    zoom: Mapped[int] = mapped_column(Integer, default=13)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    places = relationship("Place", back_populates="destination")


# ---------------------------------------------------------------------------
# Place — the interactive cultural map entity
# ---------------------------------------------------------------------------

class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    name: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[str] = mapped_column(String, default="heritage")
    subcategory: Mapped[str] = mapped_column(String, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    history: Mapped[str] = mapped_column(Text, default="")
    cultural_significance: Mapped[str] = mapped_column(Text, default="")
    architecture: Mapped[str] = mapped_column(Text, default="")
    stories: Mapped[str] = mapped_column(Text, default="")
    traditions: Mapped[str] = mapped_column(Text, default="")
    visiting_info: Mapped[str] = mapped_column(Text, default="")
    address: Mapped[str] = mapped_column(String, default="")
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    image_urls: Mapped[list] = mapped_column(JSON, default=list)
    historical_period: Mapped[str] = mapped_column(String, default="")
    opening_hours: Mapped[dict] = mapped_column(JSON, default=dict)
    entry_fee: Mapped[str] = mapped_column(String, default="Free")
    best_time: Mapped[str] = mapped_column(String, default="")
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    est_capacity: Mapped[int] = mapped_column(Integer, default=1000)
    audio_stories = relationship("AudioStory", back_populates="place", uselist=True)
    destination: Mapped["Destination"] = relationship(back_populates="places")


class AudioStory(Base):
    __tablename__ = "audio_stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id"))
    language: Mapped[str] = mapped_column(String, default="en")  # en | hi | gu
    title: Mapped[str] = mapped_column(String)
    narrative: Mapped[str] = mapped_column(Text)
    duration_sec: Mapped[int] = mapped_column(Integer, default=90)
    place: Mapped["Place"] = relationship(back_populates="audio_stories")


# ---------------------------------------------------------------------------
# Businesses & artisans
# ---------------------------------------------------------------------------

class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    name: Mapped[str] = mapped_column(String, index=True)
    kind: Mapped[str] = mapped_column(String, default="artisan")
    craft: Mapped[str] = mapped_column(String, default="")  # e.g. beadwork, pottery
    craft_type: Mapped[str] = mapped_column(String, default="")
    story: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    cultural_significance: Mapped[str] = mapped_column(Text, default="")
    address: Mapped[str] = mapped_column(String, default="")
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    image_urls: Mapped[list] = mapped_column(JSON, default=list)
    opening_hours: Mapped[dict] = mapped_column(JSON, default=dict)
    contact: Mapped[str] = mapped_column(String, default="")
    price_range: Mapped[str] = mapped_column(String, default="")
    established_year: Mapped[str] = mapped_column(String, default="")
    workshop_available: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String, default="Open")  # BUSINESS_STATUS
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)

    owner = relationship("User", back_populates="businesses")
    products = relationship("Product", back_populates="business")
    experiences = relationship("Experience", back_populates="provider")
    enquiries = relationship("Enquiry", back_populates="business")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Float, default=0)
    unit: Mapped[str] = mapped_column(String, default="")
    material: Mapped[str] = mapped_column(String, default="")
    image_url: Mapped[str] = mapped_column(String, default="")
    available: Mapped[bool] = mapped_column(Boolean, default=True)

    business: Mapped["Business"] = relationship(back_populates="products")


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    provider_business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable=True)
    title: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, default="cultural")
    description: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String, default="")
    lat: Mapped[float] = mapped_column(Float, nullable=True)
    lng: Mapped[float] = mapped_column(Float, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    price: Mapped[float] = mapped_column(Float, default=0)
    price_note: Mapped[str] = mapped_column(String, default="")
    availability: Mapped[str] = mapped_column(String, default="Daily 9 AM - 6 PM")
    capacity: Mapped[int] = mapped_column(Integer, default=15)
    image_urls: Mapped[list] = mapped_column(JSON, default=list)
    booking_link: Mapped[str] = mapped_column(String, default="")
    featured: Mapped[bool] = mapped_column(Boolean, default=False)

    provider: Mapped["Business"] = relationship(back_populates="experiences")


# ---------------------------------------------------------------------------
# Festivals, events
# ---------------------------------------------------------------------------

class Festival(Base):
    __tablename__ = "festivals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    name: Mapped[str] = mapped_column(String)
    subtitle: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    start_date: Mapped[str] = mapped_column(String)
    end_date: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="upcoming")  # upcoming | live | scheduled | past
    hero_image_url: Mapped[str] = mapped_column(String, default="")
    schedule_json: Mapped[dict] = mapped_column(JSON, default=dict)
    expected_visitors: Mapped[int] = mapped_column(Integer, default=0)
    is_festival_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    capacity: Mapped[int] = mapped_column(Integer, default=100000)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    festival_id: Mapped[int] = mapped_column(ForeignKey("festivals.id"), nullable=True)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, default="cultural")  # EVENT_CATEGORIES
    description: Mapped[str] = mapped_column(Text, default="")
    location_name: Mapped[str] = mapped_column(String, default="")
    lat: Mapped[float] = mapped_column(Float, nullable=True)
    lng: Mapped[float] = mapped_column(Float, nullable=True)
    start_date: Mapped[str] = mapped_column(String)
    end_date: Mapped[str] = mapped_column(String, default="")
    start_time: Mapped[str] = mapped_column(String, default="18:00")
    end_time: Mapped[str] = mapped_column(String, default="22:00")
    expected_visitors: Mapped[int] = mapped_column(Integer, default=0)
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    required_resources: Mapped[list] = mapped_column(JSON, default=list)
    traffic_impact: Mapped[str] = mapped_column(String, default="Low")
    parking_requirements: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="scheduled")  # scheduled | live | completed


# ---------------------------------------------------------------------------
# Live / measured data
# ---------------------------------------------------------------------------

class FootfallData(Base):
    __tablename__ = "footfall_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id"), nullable=True, index=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    visitor_count: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String, default="sensor")  # sensor | survey | simulation | estimate


class CrowdData(Base):
    __tablename__ = "crowd_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id"), nullable=True, index=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    level: Mapped[str] = mapped_column(String, default="low")  # CROWD_LEVELS
    visitor_count: Mapped[int] = mapped_column(Integer, default=0)
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String, default="simulation")


# ---------------------------------------------------------------------------
# Civic infrastructure
# ---------------------------------------------------------------------------

class ParkingArea(Base):
    __tablename__ = "parking_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    name: Mapped[str] = mapped_column(String)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    capacity: Mapped[int] = mapped_column(Integer, default=100)
    available: Mapped[int] = mapped_column(Integer, default=100)
    is_temporary: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(String, default="")


class TransportFacility(Base):
    __tablename__ = "transport_facilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    name: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String, default="rail")  # rail | air | bus | auto | brts
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    details: Mapped[str] = mapped_column(Text, default="")


class EmergencyFacility(Base):
    __tablename__ = "emergency_facilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    name: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String, default="hospital")  # hospital | police | fire | first_aid
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    phone: Mapped[str] = mapped_column(String, default="")
    details: Mapped[str] = mapped_column(String, default="")


# ---------------------------------------------------------------------------
# Community & authority communication
# ---------------------------------------------------------------------------

class CommunityReport(Base):
    __tablename__ = "community_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    category: Mapped[str] = mapped_column(String, default="traffic")  # REPORT_CATEGORIES
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, default="")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    lat: Mapped[float] = mapped_column(Float, nullable=True)
    lng: Mapped[float] = mapped_column(Float, nullable=True)
    image_url: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="Reported")  # REPORT_STATUSES
    admin_note: Mapped[str] = mapped_column(String, default="")
    ai_classification: Mapped[str] = mapped_column(String, default="")
    ai_confidence: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reporter: Mapped["User"] = relationship(back_populates="reports")


class AuthorityAlert(Base):
    __tablename__ = "authority_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id"), nullable=True)
    category: Mapped[str] = mapped_column(String, default="crowd")  # crowd | closure | parking | transport | weather | general
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(String, default="info")  # ALERT_SEVERITIES
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    starts_at: Mapped[str] = mapped_column(String, default="")
    ends_at: Mapped[str] = mapped_column(String, default="")
    created_by: Mapped[str] = mapped_column(String, default="admin@demo.com")


class RoadClosure(Base):
    __tablename__ = "road_closures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, default="")
    road_name: Mapped[str] = mapped_column(String, default="")
    start_time: Mapped[str] = mapped_column(String, default="")
    end_time: Mapped[str] = mapped_column(String, default="")
    alternate_route: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="active")  # active | lifted
    lat: Mapped[float] = mapped_column(Float, nullable=True)
    lng: Mapped[float] = mapped_column(Float, nullable=True)


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    category: Mapped[str] = mapped_column(String, default="general")
    title: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(Text, default="")
    important: Mapped[bool] = mapped_column(Boolean, default=False)
    published_by: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


# ---------------------------------------------------------------------------
# Analytics / planning
# ---------------------------------------------------------------------------

class TourismForecast(Base):
    __tablename__ = "tourism_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id"), nullable=True)
    date: Mapped[str] = mapped_column(String)
    event_name: Mapped[str] = mapped_column(String, default="")
    expected_visitors: Mapped[int] = mapped_column(Integer, default=0)
    expected_peak_start: Mapped[str] = mapped_column(String, default="18:00")
    expected_peak_end: Mapped[str] = mapped_column(String, default="22:00")
    confidence: Mapped[float] = mapped_column(Float, default=0.7)
    high_footfall_zones: Mapped[list] = mapped_column(JSON, default=list)
    method: Mapped[str] = mapped_column(String, default="seasonal-ensemble")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AlternativeRecommendation(Base):
    __tablename__ = "alternative_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    source_place_id: Mapped[int] = mapped_column(ForeignKey("places.id"))
    expected_visitors: Mapped[int] = mapped_column(Integer, default=0)
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending | approved | rejected | published
    approved_by: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    suggested_place_ids: Mapped[list] = mapped_column(JSON, default=list)


# ---------------------------------------------------------------------------
# Engagement
# ---------------------------------------------------------------------------

class Enquiry(Base):
    __tablename__ = "enquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[Optional[int]] = mapped_column(ForeignKey("businesses.id"), nullable=True)
    experience_id: Mapped[Optional[int]] = mapped_column(ForeignKey("experiences.id"), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    visitor_name: Mapped[str] = mapped_column(String, default="")
    visitor_email: Mapped[str] = mapped_column(String, default="")
    visitor_phone: Mapped[str] = mapped_column(String, default="")
    message: Mapped[str] = mapped_column(Text, default="")
    event_date: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="New")  # New | Responded | Closed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    business: Mapped["Business"] = relationship(back_populates="enquiries")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    role_channel: Mapped[str] = mapped_column(String, default="public")  # public | authority | business
    title: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(Text, default="")
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="notifications")