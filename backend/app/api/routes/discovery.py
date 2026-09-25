"""Public discovery APIs: destinations, places, artisans, experiences,
events, festivals, hotels."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.destinations import normalized_dest_id
from ...models import (
    Business,
    CrowdData,
    Destination,
    Event,
    Experience,
    Festival,
    Place,
    Product,
)
from ...schemas import (
    BusinessOut,
    DestinationSummary,
    EventOut,
    ExperienceOut,
    FestivalOut,
    PlaceBrief,
    PlaceDetailOut,
    PlaceOut,
)
from .map_helpers import nearby_place_ranking, place_with_dynamic

router = APIRouter(tags=["public"])


# ---------------------------------------------------------------------------
# Destinations
# ---------------------------------------------------------------------------

@router.get("/destinations", response_model=List[DestinationSummary])
def list_destinations(db: Session = Depends(get_db)):
    dests = db.query(Destination).filter(Destination.is_active == True).all()  # noqa: E712
    out = []
    for d in dests:
        out.append(_destination_summary(db, d))
    return out


@router.get("/destinations/{destination_id}", response_model=DestinationSummary)
def get_destination(destination_id: int, db: Session = Depends(get_db)):
    d = db.query(Destination).filter(Destination.id == destination_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Destination not found")
    return _destination_summary(db, d)


def _destination_summary(db, d):
    return DestinationSummary(
        id=d.id,
        name=d.name,
        tagline=d.tagline,
        district=d.district,
        state=d.state,
        description=d.description,
        image_url=d.image_url,
        center_lat=d.center_lat,
        center_lng=d.center_lng,
        zoom=d.zoom,
        place_count=db.query(Place).filter(Place.destination_id == d.id).count(),
        artisan_count=db.query(Business).filter(Business.destination_id == d.id, Business.kind == "artisan").count(),
        experience_count=db.query(Experience).filter(Experience.destination_id == d.id).count(),
        event_count=db.query(Event).filter(Event.destination_id == d.id).count(),
        hotel_count=db.query(Business)
        .filter(Business.destination_id == d.id, Business.kind.in_(["hotel", "homestay"]))
        .count(),
    )


# ---------------------------------------------------------------------------
# Places
# ---------------------------------------------------------------------------

@router.get("/places", response_model=List[PlaceBrief])
def list_places(
    destination_id: int = Query(1),
    category: Optional[str] = None,
    q: Optional[str] = None,
    hidden: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    destination_id = normalized_dest_id(db, destination_id)
    qy = db.query(Place).filter(Place.destination_id == destination_id)
    if category:
        cats = [c.strip() for c in category.split(",")]
        qy = qy.filter(Place.category.in_(cats))
    if hidden is not None:
        qy = qy.filter(Place.is_hidden == hidden)
    if q:
        qy = qy.filter(Place.name.ilike(f"%{q}%"))
    places = qy.all()
    return [
        PlaceBrief(
            id=p.id, name=p.name, category=p.category, summary=p.summary,
            lat=p.lat, lng=p.lng, image_urls=p.image_urls or [], is_featured=p.is_featured,
        )
        for p in places
    ]


@router.get("/places/{place_id}", response_model=PlaceDetailOut)
def get_place(place_id: int, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place_with_dynamic(db, place)


@router.get("/places/{place_id}/nearby", response_model=dict)
def get_place_nearby(place_id: int, radius_km: float = 4.0, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return nearby_place_ranking(db, place, radius_km=radius_km)


# ---------------------------------------------------------------------------
# Artisans & businesses
# ---------------------------------------------------------------------------

@router.get("/artisans", response_model=List[BusinessOut])
def list_artisans(destination_id: int = Query(1), kind: Optional[str] = None, db: Session = Depends(get_db)):
    destination_id = normalized_dest_id(db, destination_id)
    qy = db.query(Business).filter(Business.destination_id == destination_id)
    if kind:
        qy = qy.filter(Business.kind == kind)
    else:
        qy = qy.filter(Business.kind == "artisan")
    out = []
    for b in qy.limit(60).all():
        out.append(_business_out(db, b))
    return out


@router.get("/artisans/{business_id}", response_model=BusinessOut)
def get_artisan(business_id: int, db: Session = Depends(get_db)):
    b = db.query(Business).filter(Business.id == business_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
    return _business_out(db, b)


def _business_out(db, b: Business) -> BusinessOut:
    products = db.query(Product).filter(Product.business_id == b.id).all()
    experiences = db.query(Experience).filter(Experience.provider_business_id == b.id).all()
    return BusinessOut(
        id=b.id, name=b.name, kind=b.kind, craft=b.craft, craft_type=b.craft_type,
        story=b.story, description=b.description, cultural_significance=b.cultural_significance,
        address=b.address, lat=b.lat, lng=b.lng, image_urls=b.image_urls or [],
        contact=b.contact, price_range=b.price_range, workshop_available=b.workshop_available,
        status=b.status, is_verified=b.is_verified, featured=b.featured,
        established_year=b.established_year, opening_hours=b.opening_hours or {},
        owner_id=b.owner_id,
        products=products, experiences=experiences,
    )


# ---------------------------------------------------------------------------
# Experiences
# ---------------------------------------------------------------------------

@router.get("/experiences", response_model=List[ExperienceOut])
def list_experiences(destination_id: int = Query(1), category: Optional[str] = None, db: Session = Depends(get_db)):
    destination_id = normalized_dest_id(db, destination_id)
    qy = db.query(Experience).filter(Experience.destination_id == destination_id)
    if category:
        qy = qy.filter(Experience.category == category)
    out = []
    for x in qy.all():
        _attach_provider(db, x)
        out.append(ExperienceOut.model_validate(x))
    return out


@router.get("/experiences/{experience_id}", response_model=ExperienceOut)
def get_experience(experience_id: int, db: Session = Depends(get_db)):
    x = db.query(Experience).filter(Experience.id == experience_id).first()
    if not x:
        raise HTTPException(status_code=404, detail="Experience not found")
    _attach_provider(db, x)
    return ExperienceOut.model_validate(x)


def _attach_provider(db, x):
    x.provider_name = ""
    if x.provider_business_id:
        prov = db.query(Business).filter(Business.id == x.provider_business_id).first()
        if prov:
            x.provider_name = prov.name
    else:
        x.provider_name = "Local Community Collective"


# ---------------------------------------------------------------------------
# Festivals & events
# ---------------------------------------------------------------------------

@router.get("/festivals", response_model=List[FestivalOut])
def list_festivals(destination_id: int = Query(1), active_only: bool = False, db: Session = Depends(get_db)):
    destination_id = normalized_dest_id(db, destination_id)
    qy = db.query(Festival).filter(Festival.destination_id == destination_id)
    if active_only:
        qy = qy.filter(Festival.status.in_(["live", "upcoming", "scheduled"]))
    return qy.order_by(Festival.start_date).all()


@router.get("/festivals/{festival_id}", response_model=dict)
def get_festival(festival_id: int, db: Session = Depends(get_db)):
    f = db.query(Festival).filter(Festival.id == festival_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Festival not found")
    events = db.query(Event).filter(Event.festival_id == f.id).all()
    return {"festival": FestivalOut.model_validate(f), "events": [EventOut.model_validate(e) for e in events]}


@router.get("/events", response_model=List[EventOut])
def list_events(
    destination_id: int = Query(1),
    upcoming: bool = False,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    destination_id = normalized_dest_id(db, destination_id)
    qy = db.query(Event).filter(Event.destination_id == destination_id)
    if status:
        qy = qy.filter(Event.status == status)
    if upcoming:
        qy = qy.filter(Event.status.in_(["scheduled", "live"]))
    return qy.order_by(Event.start_date).all()


@router.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    e = db.query(Event).filter(Event.id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventOut.model_validate(e)


# ---------------------------------------------------------------------------
# Hotels / homestays
# ---------------------------------------------------------------------------

@router.get("/hotels", response_model=List[BusinessOut])
def list_hotels(destination_id: int = Query(1), db: Session = Depends(get_db)):
    destination_id = normalized_dest_id(db, destination_id)
    out = []
    for b in db.query(Business).filter(
        Business.destination_id == destination_id, Business.kind.in_(["hotel", "homestay"])
    ).all():
        out.append(_business_out(db, b))
    return out


@router.get("/hotels/aggregate")
def hotels_aggregate_public(destination_id: int = Query(1), db: Session = Depends(get_db)):
    from datetime import datetime as _dt

    stays = (
        db.query(Business)
        .filter(Business.destination_id == destination_id, Business.kind.in_(["hotel", "homestay"]))
        .all()
    )
    festival = db.query(Festival).filter(Festival.destination_id == destination_id, Festival.status == "live").first()
    base = 61 + (28 if festival else 0)
    hour = _dt.utcnow().hour
    if 18 <= hour <= 22:
        base += 5
    current = min(97, max(40, base))
    expected = min(99, current + 9)
    total_rooms = len(stays) * 30 or 40
    available = max(0, total_rooms - round(total_rooms * current / 100))
    return {
        "registered_hotels": len(stays),
        "occupancy_pct": current,
        "expected_occupancy_pct": expected,
        "available_rooms": available,
        "is_demo": True,
    }