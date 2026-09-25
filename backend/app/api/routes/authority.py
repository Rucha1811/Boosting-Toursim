"""Tourism authority platform."""
import asyncio
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.destinations import DEFAULT_DESTINATION_ID, normalized_dest_id
from ...models import (
    AlternativeRecommendation,
    Announcement,
    AuthorityAlert,
    Business,
    CommunityReport,
    CrowdData,
    Destination,
    EmergencyFacility,
    Event,
    Festival,
    FootfallData,
    ParkingArea,
    Place,
    RoadClosure,
    TourismForecast,
    TransportFacility,
)
from ...schemas import (
    ActionRecommendation,
    AnnouncementIn,
    AnnouncementOut,
    AuthorityAlertIn,
    AuthorityAlertOut,
    CommunityReportOut,
    CrowdAssessmentOut,
    DashboardOverview,
    DestinationOut,
    EmergencyOut,
    EventIn,
    EventOut,
    FestivalOut,
    ForecastOut,
    ParkingOut,
    RecommendationOut,
    ReportStatusUpdate,
    RoadClosureIn,
    RoadClosureOut,
    TransportOut,
)
from ...services.alternatives import recommend_alternatives
from ...services.crowd import assess as crowd_assess
from ...services.forecast import ForecastContext, ForecastService
from ...services.ws import broadcast_business, broadcast_public
from ..deps import get_header_destination_id, require_roles

router = APIRouter(prefix="/authority", tags=["authority"])

AUTH_ROLES = ("authority_admin", "authority_officer")

forecast_service = ForecastService()


# ---------------------------------------------------------------------------
# Overview command center
# ---------------------------------------------------------------------------

@router.get("/overview", response_model=DashboardOverview)
def overview(destination_id: int = Query(DEFAULT_DESTINATION_ID), db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    dest_id = normalized_dest_id(db, destination_id)
    dest = db.query(Destination).filter(Destination.id == dest_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="No destination configured")

    places = db.query(Place).filter(Place.destination_id == dest_id).all()
    current_visitors = 0
    notable = []
    for p in places:
        c = db.query(CrowdData).filter(CrowdData.place_id == p.id).order_by(CrowdData.timestamp.desc()).first()
        v = c.visitor_count if c else 0
        current_visitors += v
        notable.append(
            {
                "place_id": p.id,
                "name": p.name,
                "visitors": v,
                "capacity": p.est_capacity,
                "level": c.level if c else "low",
                "ratio": round(v / p.est_capacity, 2) if p.est_capacity else 0,
            }
        )
    notable.sort(key=lambda r: -r["visitors"])

    hotels = db.query(Business).filter(Business.destination_id == dest_id, Business.kind.in_(["hotel", "homestay"])).all()
    occupancy = _hotel_occupancy(db, dest_id)

    active_events = db.query(Event).filter(Event.destination_id == dest_id, Event.status.in_(["live", "scheduled"])).all()

    festival_obj = (
        db.query(Festival)
        .filter(Festival.destination_id == dest_id, Festival.status.in_(["live", "upcoming", "scheduled"]))
        .order_by(Festival.start_date)
        .first()
    )

    total_reports = db.query(CommunityReport).filter(CommunityReport.destination_id == dest_id).count()
    resolved = db.query(CommunityReport).filter(CommunityReport.destination_id == dest_id, CommunityReport.status == "Resolved").count()
    open_reports = total_reports - resolved
    recent_reports = db.query(CommunityReport).filter(CommunityReport.destination_id == dest_id).order_by(CommunityReport.id.desc()).limit(6).all()

    active_alerts = db.query(AuthorityAlert).filter(AuthorityAlert.destination_id == dest_id, AuthorityAlert.is_active == True).all()  # noqa: E712

    today = datetime.utcnow().strftime("%Y-%m-%d")
    forecast = _build_forecast(db, dest_id, today, festival_obj)

    parking = db.query(ParkingArea).filter(ParkingArea.destination_id == dest_id).all()
    park_pct = sum(p.available for p in parking) / sum(p.capacity for p in parking) if parking else 0
    parking_status = "Available" if park_pct > 0.35 else "Limited" if park_pct > 0.15 else "Critical"
    closures = db.query(RoadClosure).filter(RoadClosure.destination_id == dest_id).all()
    traffic_status = "Normal" if not closures and festival_obj is None else "Advisory Active"

    return DashboardOverview(
        current_visitors=current_visitors,
        estimated_inflow_today=round(forecast.expected_visitors) if forecast else 0,
        expected_inflow_today=round(forecast.expected_visitors) if forecast else 0,
        notable_places=notable[:8],
        hotel_occupancy_pct=occupancy,
        registered_hotels=len(hotels),
        active_events=[EventOut.model_validate(e) for e in active_events[:6]],
        festival=FestivalOut.model_validate(festival_obj) if festival_obj else None,
        traffic_status=traffic_status,
        parking_status=parking_status,
        open_reports=open_reports,
        resolved_reports=resolved,
        active_alerts=len(active_alerts),
        recent_alerts=[AuthorityAlertOut.model_validate(a) for a in active_alerts[:6]],
        recent_reports=[_report_brief(r) for r in recent_reports],
        forecast=ForecastOut.model_validate(forecast) if forecast else None,
        is_demo=True,
    )


def _report_brief(r: CommunityReport) -> dict:
    return {
        "id": r.id,
        "title": r.title,
        "category": r.category,
        "status": r.status,
        "ai_classification": r.ai_classification,
        "created_at": r.created_at.isoformat(),
    }


# ---------------------------------------------------------------------------
# Live map for the command center
# ---------------------------------------------------------------------------

@router.get("/live-map", response_model=dict)
def live_map(destination_id: int = Query(DEFAULT_DESTINATION_ID), db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    dest_id = normalized_dest_id(db, destination_id)
    places = db.query(Place).filter(Place.destination_id == dest_id).all()

    concentration = []
    for p in places:
        c = db.query(CrowdData).filter(CrowdData.place_id == p.id).order_by(CrowdData.timestamp.desc()).first()
        v = c.visitor_count if c else 0
        concentration.append(
            {
                "place_id": p.id,
                "name": p.name,
                "lat": p.lat,
                "lng": p.lng,
                "visitors": v,
                "capacity": p.est_capacity,
                "level": c.level if c else "low",
                "category": p.category,
            }
        )

    closures = [
        {"id": r.id, "name": r.name, "road_name": r.road_name, "start_time": r.start_time, "end_time": r.end_time,
         "alternate_route": r.alternate_route, "status": r.status, "lat": r.lat, "lng": r.lng}
        for r in db.query(RoadClosure).filter(RoadClosure.destination_id == dest_id, RoadClosure.status == "active").all()
    ]

    reports = [
        {"id": r.id, "title": r.title, "category": r.category, "status": r.status, "lat": r.lat, "lng": r.lng,
         "ai_classification": r.ai_classification}
        for r in db.query(CommunityReport).filter(CommunityReport.destination_id == dest_id).order_by(CommunityReport.id.desc()).limit(40).all()
    ]

    events = [
        {"id": e.id, "name": e.name, "category": e.category, "status": e.status, "expected_visitors": e.expected_visitors,
         "capacity": e.capacity, "lat": e.lat, "lng": e.lng, "start_date": e.start_date, "start_time": e.start_time}
        for e in db.query(Event).filter(Event.destination_id == dest_id, Event.status.in_(["live", "scheduled"])).all()
    ]

    parking = [
        {"id": p.id, "name": p.name, "available": p.available, "capacity": p.capacity, "is_temporary": p.is_temporary,
         "lat": p.lat, "lng": p.lng}
        for p in db.query(ParkingArea).filter(ParkingArea.destination_id == dest_id).all()
    ]

    return {
        "concentration": concentration,
        "road_closures": closures,
        "reports": reports,
        "events": events,
        "parking": parking,
        "emergency": [
            {"id": e.id, "name": e.name, "kind": e.kind, "lat": e.lat, "lng": e.lng, "phone": e.phone}
            for e in db.query(EmergencyFacility).filter(EmergencyFacility.destination_id == dest_id).all()
        ],
        "source": "simulation",
    }


# ---------------------------------------------------------------------------
# Footfall & crowd analytics
# ---------------------------------------------------------------------------

@router.get("/analytics", response_model=dict)
def analytics(
    days: int = Query(30),
    destination_id: int = Query(DEFAULT_DESTINATION_ID),
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
):
    from sqlalchemy import func

    dest_id = normalized_dest_id(db, destination_id)
    rows = (
        db.query(func.date(FootfallData.timestamp).label("d"), func.sum(FootfallData.visitor_count).label("total"))
        .filter(FootfallData.destination_id == dest_id, FootfallData.source == "simulation")
        .group_by(func.date(FootfallData.timestamp))
        .order_by(func.date(FootfallData.timestamp))
        .all()
    )
    daily = [{"date": str(d), "visitors": t or 0} for d, t in rows[-days:]]

    # Hourly profile (aggregated in Python for SQLite/Postgres portability)
    recent = (
        db.query(FootfallData)
        .filter(FootfallData.destination_id == dest_id)
        .order_by(FootfallData.timestamp.desc())
        .limit(6000)
        .all()
    )
    hour_map = defaultdict(list)
    for f in recent:
        hour_map[f.timestamp.hour].append(f.visitor_count)
    hourly = [{"hour": h, "avg": round(sum(v) / len(v))} for h, v in sorted(hour_map.items())]

    levels = Counter()
    for p in db.query(Place).filter(Place.destination_id == dest_id).all():
        c = db.query(CrowdData).filter(CrowdData.place_id == p.id).order_by(CrowdData.timestamp.desc()).first()
        levels[c.level if c else "low"] += 1

    cat_rows = defaultdict(int)
    for p in db.query(Place).filter(Place.destination_id == dest_id).all():
        c = db.query(CrowdData).filter(CrowdData.place_id == p.id).order_by(CrowdData.timestamp.desc()).first()
        cat_rows[p.category] += c.visitor_count if c else 0

    place_share = []
    total_v = sum(cat_rows.values()) or 1
    for p in db.query(Place).filter(Place.destination_id == dest_id).all():
        c = db.query(CrowdData).filter(CrowdData.place_id == p.id).order_by(CrowdData.timestamp.desc()).first()
        v = c.visitor_count if c else 0
        place_share.append(
            {
                "place_id": p.id,
                "name": p.name,
                "visitors": v,
                "share": round(v / total_v, 3),
                "level": c.level if c else "low",
            }
        )
    place_share.sort(key=lambda r: -r["visitors"])

    return {
        "daily": daily,
        "hourly": hourly,
        "crowd_distribution": dict(levels),
        "category_visitors": dict(cat_rows),
        "place_share": place_share[:10],
        "is_demo": True,
        "note": "Simulated historical and live datasets for demonstration.",
    }


# ---------------------------------------------------------------------------
# Forecasts
# ---------------------------------------------------------------------------

def _build_forecast(db: Session, dest_id: int, date_str: str = "", festival_obj=None) -> Optional[TourismForecast]:
    if not date_str:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
    festival_obj = festival_obj or (
        db.query(Festival).filter(Festival.destination_id == dest_id, Festival.status.in_(["live", "upcoming", "scheduled"])).first()
    )

    history = [
        f.visitor_count
        for f in db.query(FootfallData).filter(FootfallData.destination_id == dest_id).order_by(FootfallData.timestamp.desc()).limit(240).all()
    ]
    occupancy = _hotel_occupancy(db, dest_id)

    is_festival = festival_obj is not None and festival_obj.status in ("live", "upcoming", "scheduled")
    multiplier = (festival_obj.expected_visitors / 25000) if festival_obj and festival_obj.expected_visitors else 1.0
    multiplier = max(1.0, multiplier)

    result = forecast_service.forecast(
        ForecastContext(
            destination_id=dest_id,
            date=date_str,
            event_name=festival_obj.name if festival_obj else "",
            is_festival=is_festival,
            festival_peak_multiplier=multiplier,
            historical=history[-120:],
            place_capacity=0,
            hotel_occupancy_pct=occupancy,
        )
    )

    zones = [
        {"zone": "Zone A — Old City Heritage Core", "expected": round(result.expected_visitors * 0.34)},
        {"zone": "Zone B — Laxmi Vilas Palace & museum belt", "expected": round(result.expected_visitors * 0.28)},
        {"zone": "Zone C — Sayaji Baug & river edge", "expected": round(result.expected_visitors * 0.22)},
        {"zone": "Zone D — Navratri grounds (Gotri)", "expected": round(result.expected_visitors * 0.16)},
    ]
    fc = TourismForecast(
        destination_id=dest_id,
        date=date_str,
        event_name=festival_obj.name if festival_obj else "",
        expected_visitors=min(result.expected_visitors, 150000),
        expected_peak_start=result.expected_peak_start,
        expected_peak_end=result.expected_peak_end,
        confidence=result.confidence,
        high_footfall_zones=zones,
        method=result.method,
        is_demo=True,
    )
    db.add(fc)
    db.commit()
    db.refresh(fc)
    return fc


@router.get("/forecast", response_model=List[ForecastOut])
def list_forecasts(
    days: int = Query(14),
    destination_id: int = Query(DEFAULT_DESTINATION_ID),
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
):
    dest_id = normalized_dest_id(db, destination_id)
    existing = db.query(TourismForecast).filter(TourismForecast.destination_id == dest_id).order_by(TourismForecast.id.desc()).limit(days).all()
    if existing:
        return existing
    return [_build_forecast(db, dest_id)]


@router.post("/forecast/generate", response_model=ForecastOut)
def generate_forecast(
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
    dest_id: int = Depends(get_header_destination_id),
):
    date_str = payload.get("date") or datetime.utcnow().strftime("%Y-%m-%d")
    return _build_forecast(db, dest_id, date_str)


# ---------------------------------------------------------------------------
# Crowd management
# ---------------------------------------------------------------------------

@router.get("/crowd-assessment", response_model=List[CrowdAssessmentOut])
def crowd_assessment(destination_id: int = Query(DEFAULT_DESTINATION_ID), db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    dest_id = normalized_dest_id(db, destination_id)
    out = []
    for p in db.query(Place).filter(Place.destination_id == dest_id).all():
        c = db.query(CrowdData).filter(CrowdData.place_id == p.id).order_by(CrowdData.timestamp.desc()).first()
        current = c.visitor_count if c else 0
        cap = p.est_capacity or 1
        result = crowd_assess(cap, current, current)
        out.append(
            CrowdAssessmentOut(
                place_id=p.id,
                place_name=p.name,
                capacity=cap,
                current_visitors=current,
                occupancy_ratio=round(current / cap, 2),
                level=result["level"],
                risk=result["risk"],
                expected_visitors=current,
                status_label=result["risk"],
                actions=[ActionRecommendation(action=str(a["action"]), detail=str(a["detail"])) for a in result["actions"]],
            )
        )
    out.sort(key=lambda r: -r.occupancy_ratio)
    return out


@router.get("/places/{place_id}/crowd", response_model=CrowdAssessmentOut)
def place_crowd(place_id: int, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    p = db.query(Place).filter(Place.id == place_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Place not found")
    c = db.query(CrowdData).filter(CrowdData.place_id == p.id).order_by(CrowdData.timestamp.desc()).first()
    current = c.visitor_count if c else 0
    cap = p.est_capacity or 1
    result = crowd_assess(cap, current, current)
    return CrowdAssessmentOut(
        place_id=p.id,
        place_name=p.name,
        capacity=cap,
        current_visitors=current,
        occupancy_ratio=round(current / cap, 2),
        level=result["level"],
        risk=result["risk"],
        expected_visitors=current,
        status_label=result["risk"],
        actions=[ActionRecommendation(action=str(a["action"]), detail=str(a["detail"])) for a in result["actions"]],
    )


# ---------------------------------------------------------------------------
# Demand redistribution (alternative attractions)
# ---------------------------------------------------------------------------

@router.post("/places/{place_id}/recommend-alternatives", response_model=list)
def recommend_alts(place_id: int, radius_km: float = Query(5.0), db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    source = db.query(Place).filter(Place.id == place_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Place not found")
    return recommend_alternatives(db, source, radius_km=radius_km)


@router.post("/recommendations", response_model=RecommendationOut, status_code=201)
def create_recommendation(
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
):
    source = db.query(Place).filter(Place.id == payload["place_id"]).first()
    if not source:
        raise HTTPException(status_code=404, detail="Place not found")
    alts = recommend_alternatives(db, source, radius_km=5.0)
    rec = AlternativeRecommendation(
        destination_id=source.destination_id,
        source_place_id=source.id,
        expected_visitors=payload.get("expected_visitors", 0),
        capacity=payload.get("capacity", 0),
        status="pending",
        suggested_place_ids=[a["place_id"] for a in alts],
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return _rec_out(db, rec)


@router.get("/recommendations", response_model=List[RecommendationOut])
def list_recommendations(db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    recs = db.query(AlternativeRecommendation).order_by(AlternativeRecommendation.id.desc()).limit(20).all()
    return [_rec_out(db, r) for r in recs]


@router.post("/recommendations/{rec_id}/approve", response_model=RecommendationOut)
def approve_recommendation(rec_id: int, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    rec = db.query(AlternativeRecommendation).filter(AlternativeRecommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.status = "approved"
    rec.approved_by = user.email
    db.commit()
    db.refresh(rec)
    source = db.query(Place).filter(Place.id == rec.source_place_id).first()
    payload = {
        "recommendation_id": rec.id,
        "source_place": source.name if source else "",
        "source_place_id": rec.source_place_id,
        "alternatives": _alt_brief(db, rec),
    }
    asyncio.run(broadcast_public("recommendation_approved", payload))
    return _rec_out(db, rec)


def _alt_brief(db, rec):
    brief = []
    for pid in (rec.suggested_place_ids or []):
        alt = db.query(Place).filter(Place.id == pid).first()
        if alt:
            brief.append({"id": alt.id, "name": alt.name, "category": alt.category})
    return brief


def _rec_out(db, rec: AlternativeRecommendation) -> RecommendationOut:
    source = db.query(Place).filter(Place.id == rec.source_place_id).first()
    alts = []
    for pid in (rec.suggested_place_ids or []):
        alt = db.query(Place).filter(Place.id == pid).first()
        if alt:
            alts.append({"place_id": alt.id, "name": alt.name, "category": alt.category, "summary": alt.summary})
    return RecommendationOut(
        id=rec.id,
        destination_id=rec.destination_id,
        source_place_id=rec.source_place_id,
        source_place_name=source.name if source else "",
        expected_visitors=rec.expected_visitors,
        capacity=rec.capacity,
        status=rec.status,
        created_at=rec.created_at,
        alternatives=alts,
    )


# ---------------------------------------------------------------------------
# Events CRUD
# ---------------------------------------------------------------------------

@router.get("/events", response_model=List[EventOut])
def list_events_admin(destination_id: int = Query(DEFAULT_DESTINATION_ID), db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    dest_id = normalized_dest_id(db, destination_id)
    events = db.query(Event).filter(Event.destination_id == dest_id).order_by(Event.start_date.desc()).all()
    return [EventOut.model_validate(e) for e in events]


@router.post("/events", response_model=EventOut, status_code=201)
def create_event(
    payload: EventIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
    dest_id: int = Depends(get_header_destination_id),
):
    ev = Event(destination_id=dest_id, **payload.model_dump())
    db.add(ev)
    db.commit()
    db.refresh(ev)
    asyncio.run(broadcast_public("event_new", {"id": ev.id, "name": ev.name}))
    return EventOut.model_validate(ev)


@router.patch("/events/{event_id}", response_model=EventOut)
def update_event(event_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    for k, v in payload.items():
        if hasattr(ev, k):
            setattr(ev, k, v)
    db.commit()
    db.refresh(ev)
    asyncio.run(broadcast_public("event_update", {"id": ev.id, "name": ev.name, "status": ev.status}))
    return EventOut.model_validate(ev)


@router.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if ev:
        db.delete(ev)
        db.commit()


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

@router.post("/alerts", response_model=AuthorityAlertOut, status_code=201)
def create_alert(
    payload: AuthorityAlertIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
    dest_id: int = Depends(get_header_destination_id),
):
    alert = AuthorityAlert(destination_id=dest_id, created_by=user.email, **payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    import asyncio

    asyncio.run(
        broadcast_public(
            "alert_new",
            {"id": alert.id, "category": alert.category, "title": alert.title, "message": alert.message, "severity": alert.severity},
        )
    )
    return AuthorityAlertOut.model_validate(alert)


@router.get("/alerts", response_model=List[AuthorityAlertOut])
def list_alerts(
    active_only: bool = False,
    destination_id: int = Query(DEFAULT_DESTINATION_ID),
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
):
    dest_id = normalized_dest_id(db, destination_id)
    qy = db.query(AuthorityAlert).filter(AuthorityAlert.destination_id == dest_id)
    if active_only:
        qy = qy.filter(AuthorityAlert.is_active == True)  # noqa: E712
    return qy.order_by(AuthorityAlert.id.desc()).limit(50).all()


@router.patch("/alerts/{alert_id}", response_model=AuthorityAlertOut)
def update_alert(alert_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    alert = db.query(AuthorityAlert).filter(AuthorityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for k, v in payload.items():
        if hasattr(alert, k):
            setattr(alert, k, v)
    db.commit()
    db.refresh(alert)
    import asyncio

    asyncio.run(broadcast_public("alert_update", {"id": alert.id, "is_active": alert.is_active}))
    return AuthorityAlertOut.model_validate(alert)


# ---------------------------------------------------------------------------
# Road closures
# ---------------------------------------------------------------------------

@router.post("/closures", response_model=RoadClosureOut, status_code=201)
def create_closure(
    payload: RoadClosureIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
    dest_id: int = Depends(get_header_destination_id),
):
    c = RoadClosure(destination_id=dest_id, **payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    import asyncio

    asyncio.run(
        broadcast_public(
            "closure_new",
            {"id": c.id, "name": c.name, "road_name": c.road_name, "end_time": c.end_time, "alternate_route": c.alternate_route},
        )
    )
    return RoadClosureOut.model_validate(c)


@router.get("/closures", response_model=List[RoadClosureOut])
def list_closures(destination_id: int = Query(DEFAULT_DESTINATION_ID), db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    dest_id = normalized_dest_id(db, destination_id)
    return db.query(RoadClosure).filter(RoadClosure.destination_id == dest_id).order_by(RoadClosure.id.desc()).all()


@router.patch("/closures/{closure_id}", response_model=RoadClosureOut)
def update_closure(closure_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    c = db.query(RoadClosure).filter(RoadClosure.id == closure_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Closure not found")
    for k, v in payload.items():
        if hasattr(c, k):
            setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return RoadClosureOut.model_validate(c)


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------

@router.post("/announcements", response_model=AnnouncementOut, status_code=201)
def create_announcement(
    payload: AnnouncementIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
    dest_id: int = Depends(get_header_destination_id),
):
    a = Announcement(destination_id=dest_id, published_by=user.email, **payload.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    import asyncio

    asyncio.run(broadcast_public("announcement_new", {"id": a.id, "title": a.title, "important": a.important}))
    return AnnouncementOut.model_validate(a)


@router.get("/announcements", response_model=List[AnnouncementOut])
def list_announcements(destination_id: int = Query(DEFAULT_DESTINATION_ID), db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    dest_id = normalized_dest_id(db, destination_id)
    return db.query(Announcement).filter(Announcement.destination_id == dest_id).order_by(Announcement.id.desc()).limit(50).all()


@router.patch("/announcements/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(announcement_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Announcement not found")
    for k, v in payload.items():
        if hasattr(a, k):
            setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return AnnouncementOut.model_validate(a)


# ---------------------------------------------------------------------------
# Report workflow
# ---------------------------------------------------------------------------

@router.patch("/reports/{report_id}/status", response_model=CommunityReportOut)
def update_report_status(
    report_id: int,
    payload: ReportStatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
):
    r = db.query(CommunityReport).filter(CommunityReport.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    r.status = payload.status
    if payload.admin_note:
        r.admin_note = payload.admin_note
    db.commit()
    db.refresh(r)
    from .reports import _report_out

    return _report_out(r)


# ---------------------------------------------------------------------------
# Infrastructure management
# ---------------------------------------------------------------------------

@router.patch("/parking/{parking_id}", response_model=ParkingOut)
def update_parking(parking_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    p = db.query(ParkingArea).filter(ParkingArea.id == parking_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Parking not found")
    for k, v in payload.items():
        if hasattr(p, k):
            setattr(p, k, v)
    db.commit()
    db.refresh(p)
    import asyncio

    asyncio.run(broadcast_public("parking_update", {"id": p.id, "name": p.name, "available": p.available}))
    return ParkingOut.model_validate(p)


@router.post("/parking", response_model=ParkingOut, status_code=201)
def create_parking(payload: dict, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES)), dest_id: int = Depends(get_header_destination_id)):
    cap = int(payload.get("capacity") or 100)
    p = ParkingArea(
        destination_id=payload.get("destination_id") or dest_id,
        name=payload.get("name") or "Temporary parking",
        lat=float(payload.get("lat") or 22.3),
        lng=float(payload.get("lng") or 73.18),
        capacity=cap,
        available=int(payload.get("available") or cap),
        notes=payload.get("notes") or "",
        is_temporary=payload.get("category") == "temporary",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    import asyncio

    asyncio.run(
        broadcast_public("parking_update", {"id": p.id, "name": p.name, "available": p.available, "is_temporary": p.is_temporary})
    )
    return ParkingOut.model_validate(p)


@router.get("/parking", response_model=List[ParkingOut])
def list_parking(destination_id: int = Query(DEFAULT_DESTINATION_ID), db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    dest_id = normalized_dest_id(db, destination_id)
    return db.query(ParkingArea).filter(ParkingArea.destination_id == dest_id).all()


@router.post("/transport", response_model=TransportOut, status_code=201)
def create_transport(
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
    dest_id: int = Depends(get_header_destination_id),
):
    obj = TransportFacility(destination_id=payload.get("destination_id") or dest_id, **{k: v for k, v in payload.items() if k != "destination_id"})
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return TransportOut.model_validate(obj)


@router.post("/emergency", response_model=EmergencyOut, status_code=201)
def create_emergency(
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
    dest_id: int = Depends(get_header_destination_id),
):
    obj = EmergencyFacility(destination_id=payload.get("destination_id") or dest_id, **{k: v for k, v in payload.items() if k != "destination_id"})
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return EmergencyOut.model_validate(obj)


# ---------------------------------------------------------------------------
# Businesses oversight
# ---------------------------------------------------------------------------

@router.get("/businesses", response_model=list)
def authority_businesses(
    kind: Optional[str] = None,
    destination_id: int = Query(DEFAULT_DESTINATION_ID),
    db: Session = Depends(get_db),
    user=Depends(require_roles(*AUTH_ROLES)),
):
    dest_id = normalized_dest_id(db, destination_id)
    qy = db.query(Business).filter(Business.destination_id == dest_id)
    if kind:
        qy = qy.filter(Business.kind == kind)
    from .discovery import _business_out

    return [_business_out(db, b) for b in qy.limit(100).all()]


@router.patch("/businesses/{business_id}", response_model=dict)
def authority_update_business(business_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    b = db.query(Business).filter(Business.id == business_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
    for k, v in payload.items():
        if hasattr(b, k):
            setattr(b, k, v)
    db.commit()
    db.refresh(b)
    return {"id": b.id, "name": b.name, "kind": b.kind, "status": b.status, "is_verified": b.is_verified, "featured": b.featured}


# ---------------------------------------------------------------------------
# Hotels aggregate
# ---------------------------------------------------------------------------

def _hotel_occupancy(db, dest_id) -> int:
    """Aggregate accommodation occupancy: base estimate + festival surge.
    Simulated/demo estimate clearly bounded 40–97%."""
    festival = db.query(Festival).filter(Festival.destination_id == dest_id, Festival.status == "live").first()
    base = 61
    if festival:
        base += 28
    hour = datetime.utcnow().hour
    if 18 <= hour <= 22:
        base += 5
    if hour < 6:
        base += 3
    return min(97, max(40, base))


@router.get("/hotels/aggregate", response_model=dict)
def hotels_aggregate(destination_id: int = Query(DEFAULT_DESTINATION_ID), db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    dest_id = normalized_dest_id(db, destination_id)
    reg = db.query(Business).filter(Business.destination_id == dest_id, Business.kind.in_(["hotel", "homestay"])).count()
    pct = _hotel_occupancy(db, dest_id)
    return {
        "registered_hotels": reg,
        "occupancy_pct": pct,
        "expected_occupancy_pct": min(97, pct + 9),
        "available_rooms": max(0, round((100 - pct) / 100 * (reg * 60))),
        "is_demo": True,
    }


@router.get("/destinations", response_model=list)
def authority_destinations(db: Session = Depends(get_db), user=Depends(require_roles(*AUTH_ROLES))):
    return [DestinationOut.model_validate(d) for d in db.query(Destination).all()]