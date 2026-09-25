"""Interactive cultural map API + dynamic tourist information."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.destinations import normalized_dest_id
from ...models import (
    AlternativeRecommendation,
    Announcement,
    AuthorityAlert,
    Business,
    EmergencyFacility,
    Event,
    Experience,
    ParkingArea,
    Place,
    RoadClosure,
    TransportFacility,
)
from .map_helpers import latest_crowd

router = APIRouter(prefix="/map", tags=["map"])

MARKER_SOURCE_CATEGORIES = [
    "heritage", "history", "temple", "museum", "market", "food", "culture",
    "hidden_gem", "landmark", "garden",
]


@router.get("/markers", response_model=list)
def map_markers(
    destination_id: int = Query(1),
    categories: Optional[str] = Query(None, description="comma separated list"),
    db: Session = Depends(get_db),
):
    destination_id = normalized_dest_id(db, destination_id)
    selected = set(categories.split(",")) if categories else None

    markers = []

    def want(cat):
        if selected is None:
            return True
        return cat in selected

    # Cultural places
    if selected is None or selected & set(MARKER_SOURCE_CATEGORIES):
        places = db.query(Place).filter(Place.destination_id == destination_id).all()
        for p in places:
            if not want(p.category):
                continue
            c = latest_crowd(db, p.id)
            markers.append(
                {
                    "id": p.id,
                    "type": "place",
                    "entity_id": p.id,
                    "name": p.name,
                    "category": p.category,
                    "subtitle": p.summary[:90],
                    "lat": p.lat,
                    "lng": p.lng,
                    "image": (p.image_urls or [""])[0],
                    "crowd": c.level if c else "low",
                    "visitors": c.visitor_count if c else 0,
                    "is_hidden": p.is_hidden,
                }
            )

    # Artisans & businesses of interest
    if selected is None or selected & {"artisans", "food", "restaurant", "shopping"}:
        biz = (
            db.query(Business)
            .filter(Business.destination_id == destination_id)
            .all()
        )
        for b in biz:
            cat = b.kind
            if cat == "artisan" and not want("artisans"):
                continue
            if cat in ("restaurant", "food") and not want("food"):
                continue
            if cat in ("hotel", "homestay") and not want("hotel") and not want("homestay"):
                continue
            if cat == "guide" and not want("guide"):
                continue
            if cat in ("workshop", "experience_provider", "performer", "retail") and not want("shopping"):
                continue
            markers.append(
                {
                    "id": b.id,
                    "type": "business",
                    "entity_id": b.id,
                    "name": b.name,
                    "category": cat,
                    "subtitle": (b.craft or b.name)[:90],
                    "lat": b.lat,
                    "lng": b.lng,
                    "image": (b.image_urls or [""])[0],
                    "status": b.status,
                }
            )

    # Experiences
    if selected is None or "experiences" in selected:
        for x in db.query(Experience).filter(Experience.destination_id == destination_id).all():
            markers.append(
                {
                    "id": x.id,
                    "type": "experience",
                    "entity_id": x.id,
                    "name": x.title,
                    "category": "experience",
                    "subtitle": x.availability,
                    "lat": x.lat or 0.0,
                    "lng": x.lng or 0.0,
                    "image": (x.image_urls or [""])[0],
                }
            )

    # Parking
    if selected is None or "parking" in selected:
        for p in db.query(ParkingArea).filter(ParkingArea.destination_id == destination_id).all():
            markers.append(
                {
                    "id": p.id,
                    "type": "parking",
                    "entity_id": p.id,
                    "name": p.name,
                    "category": "parking",
                    "subtitle": f"{p.available}/{p.capacity} spaces available",
                    "lat": p.lat,
                    "lng": p.lng,
                    "temporary": p.is_temporary,
                }
            )

    # Transport
    if selected is None or "transport" in selected:
        for t in db.query(TransportFacility).filter(TransportFacility.destination_id == destination_id).all():
            markers.append(
                {
                    "id": t.id,
                    "type": "transport",
                    "entity_id": t.id,
                    "name": t.name,
                    "category": "transport",
                    "subtitle": t.kind,
                    "lat": t.lat,
                    "lng": t.lng,
                }
            )

    # Emergency
    if selected is None or "emergency" in selected:
        for e in db.query(EmergencyFacility).filter(EmergencyFacility.destination_id == destination_id).all():
            markers.append(
                {
                    "id": e.id,
                    "type": "emergency",
                    "entity_id": e.id,
                    "name": e.name,
                    "category": "emergency",
                    "subtitle": e.kind,
                    "lat": e.lat,
                    "lng": e.lng,
                }
            )

    # Events (live/scheduled)
    if selected is None or "festival" in selected or "events" in selected:
        for ev in db.query(Event).filter(Event.destination_id == destination_id).all():
            if ev.lat is None or ev.lng is None:
                continue
            markers.append(
                {
                    "id": ev.id,
                    "type": "event",
                    "entity_id": ev.id,
                    "name": ev.name,
                    "category": "event",
                    "subtitle": f"{ev.start_date} {ev.start_time}–{ev.end_time}",
                    "lat": ev.lat,
                    "lng": ev.lng,
                    "image": "",
                }
            )

    return markers


def _active_alerts(db, destination_id):
    return (
        db.query(AuthorityAlert)
        .filter(AuthorityAlert.destination_id == destination_id, AuthorityAlert.is_active == True)  # noqa: E712
        .order_by(AuthorityAlert.id.desc())
        .all()
    )


def _attraction_name(db, place_id):
    p = db.query(Place).filter(Place.id == place_id).first()
    return p.name if p else ""


@router.get("/info", response_model=dict)
def dynamic_tourism_info(destination_id: int = Query(1), db: Session = Depends(get_db)):
    destination_id = normalized_dest_id(db, destination_id)
    """Dynamic tourist information — the public counterpart of authority actions.

    Returns alerts, road closures, temporary parking, announcements and any
    approved alternative recommendations so the tourist app can render
    "High Visitor Activity", "Road Closure", "Temporary Parking" notices.
    """
    alerts_raw = _active_alerts(db, destination_id)
    alerts = []
    for a in alerts_raw:
        alert = {
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "severity": a.severity,
            "category": a.category,
            "place_id": a.place_id,
            "place_name": _attraction_name(db, a.place_id) if a.place_id else "",
            "starts_at": a.starts_at,
            "ends_at": a.ends_at,
        }
        # attach current occupancy when the alert references an attraction
        if a.place_id:
            c = latest_crowd(db, a.place_id)
            alert["current_visitors"] = c.visitor_count if c else 0
            alert["capacity"] = c.capacity if c else 0
            alert["level"] = c.level if c else "low"
        alerts.append(alert)

    closures = [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "road_name": r.road_name,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "alternate_route": r.alternate_route,
            "lat": r.lat,
            "lng": r.lng,
        }
        for r in db.query(RoadClosure)
        .filter(RoadClosure.destination_id == destination_id, RoadClosure.status == "active")
        .all()
    ]

    temp_parking = [
        {
            "id": p.id,
            "name": p.name,
            "available": p.available,
            "capacity": p.capacity,
            "notes": p.notes,
            "lat": p.lat,
            "lng": p.lng,
        }
        for p in db.query(ParkingArea)
        .filter(ParkingArea.destination_id == destination_id, ParkingArea.is_temporary == True)  # noqa: E712
        .all()
    ]

    announcements = [
        {
            "id": a.id,
            "title": a.title,
            "body": a.body,
            "category": a.category,
            "important": a.important,
            "created_at": a.created_at.isoformat(),
        }
        for a in db.query(Announcement).filter(Announcement.destination_id == destination_id, Announcement.active == True)  # noqa: E712
        .order_by(Announcement.created_at.desc()).limit(8).all()
    ]

    # Approved alternative recommendations that redirect crowded visitors
    recommendations = []
    recs = (
        db.query(AlternativeRecommendation)
        .filter(
            AlternativeRecommendation.destination_id == destination_id,
            AlternativeRecommendation.status.in_(["approved", "published"]),
        )
        .order_by(AlternativeRecommendation.id.desc())
        .all()
    )

    for rec in recs:
        source = db.query(Place).filter(Place.id == rec.source_place_id).first()
        alternatives = []
        for pid in (rec.suggested_place_ids or [])[:4]:
            alt = db.query(Place).filter(Place.id == pid).first()
            if alt:
                c = latest_crowd(db, alt.id)
                alternatives.append(
                    {
                        "id": alt.id,
                        "name": alt.name,
                        "category": alt.category,
                        "activity": c.level if c else "low",
                        "image": (alt.image_urls or [""])[0],
                        "summary": alt.summary,
                    }
                )
        recommendations.append(
            {
                "id": rec.id,
                "source_place_id": rec.source_place_id,
                "source_place_name": source.name if source else "",
                "expected_visitors": rec.expected_visitors,
                "capacity": rec.capacity,
                "alternatives": alternatives,
            }
        )

    return {
        "alerts": alerts,
        "road_closures": closures,
        "temporary_parking": temp_parking,
        "announcements": announcements,
        "recommendations": recommendations,
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.get("/crowd", response_model=dict)
def crowd_readout(destination_id: int = Query(1), db: Session = Depends(get_db)):
    destination_id = normalized_dest_id(db, destination_id)
    """Live per-attraction crowd readout (also streamed over WebSocket via /tick)."""
    out = {}
    for p in db.query(Place).filter(Place.destination_id == destination_id).all():
        c = latest_crowd(db, p.id)
        out[p.id] = {
            "place_id": p.id,
            "name": p.name,
            "level": c.level if c else "low",
            "visitors": c.visitor_count if c else 0,
            "capacity": p.est_capacity,
            "ratio": round((c.visitor_count / p.est_capacity) if c and p.est_capacity else 0.0, 3),
        }
    return {"readout": out, "source": "simulation", "note": "Simulated live footfall data for demonstration."}