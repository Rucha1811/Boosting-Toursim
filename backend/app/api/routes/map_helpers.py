from sqlalchemy.orm import Session

from ...models import Business, CrowdData, Experience, Event, Place
from ...schemas import AudioStoryOut, PlaceDetailOut
from ...services.geo import haversine


def latest_crowd(db: Session, place_id: int):
    return (
        db.query(CrowdData)
        .filter(CrowdData.place_id == place_id)
        .order_by(CrowdData.timestamp.desc())
        .first()
    )


def place_with_dynamic(db: Session, place: Place) -> PlaceDetailOut:
    crowd = latest_crowd(db, place.id)
    current = crowd.visitor_count if crowd else 0
    capacity = place.est_capacity or 1
    return PlaceDetailOut(
        id=place.id,
        destination_id=place.destination_id,
        name=place.name,
        category=place.category,
        subcategory=place.subcategory,
        summary=place.summary,
        description=place.description,
        history=place.history,
        cultural_significance=place.cultural_significance,
        architecture=place.architecture,
        stories=place.stories,
        traditions=place.traditions,
        visiting_info=place.visiting_info,
        address=place.address,
        lat=place.lat,
        lng=place.lng,
        image_urls=place.image_urls or [],
        historical_period=place.historical_period,
        opening_hours=place.opening_hours or {},
        entry_fee=place.entry_fee,
        best_time=place.best_time,
        is_hidden=place.is_hidden,
        is_featured=place.is_featured,
        est_capacity=place.est_capacity,
        listener_count=len(place.audio_stories or []),
        audio_stories=[AudioStoryOut.model_validate(s) for s in (place.audio_stories or [])],
        current_visitors=current,
        crowd_level=crowd.level if crowd else "low",
        occupancy_ratio=round(current / capacity, 3) if capacity else 0.0,
    )


def nearby_place_ranking(db: Session, place: Place, radius_km: float = 4.0) -> dict:
    """What can a visitor also experience near this place? Groups responses
    by business/piece type so the detail page can render a rich 'nearby' block."""
    places = db.query(Place).filter(
        Place.destination_id == place.destination_id, Place.id != place.id
    ).all()
    artisans = db.query(Business).filter(Business.destination_id == place.destination_id).all()
    experiences = db.query(Experience).filter(Experience.destination_id == place.destination_id).all()
    events = db.query(Event).filter(Event.destination_id == place.destination_id).all()

    def _dist(lat, lng):
        return round(haversine(place.lat, place.lng, lat, lng), 1)

    def _activity(b):
        c = latest_crowd(db, b.id)
        return c.level if c else "low"

    nearby_places = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "summary": p.summary,
            "distance_km": _dist(p.lat, p.lng),
            "image_url": (p.image_urls or [""])[0],
            "activity": _activity(p),
        }
        for p in places
        if _dist(p.lat, p.lng) <= radius_km
    ]
    nearby_places.sort(key=lambda r: r["distance_km"])

    return {
        "places": nearby_places[:8],
        "artisans": [
            {
                "id": a.id,
                "name": a.name,
                "craft": a.craft or a.craft_type,
                "distance_km": _dist(a.lat, a.lng),
                "image_url": (a.image_urls or [""])[0],
                "status": a.status,
            }
            for a in artisans
            if _dist(a.lat, a.lng) <= radius_km
        ][:6],
        "food": [
            {
                "id": a.id,
                "name": a.name,
                "kind": a.kind,
                "distance_km": _dist(a.lat, a.lng),
                "image_url": (a.image_urls or [""])[0],
            }
            for a in artisans
            if a.kind in ("restaurant", "food") and _dist(a.lat, a.lng) <= radius_km
        ][:6],
        "experiences": [
            {
                "id": x.id,
                "title": x.title,
                "duration_minutes": x.duration_minutes,
                "price": x.price,
                "distance_km": _dist(x.lat or place.lat, x.lng or place.lng),
            }
            for x in experiences
            if _dist(x.lat or place.lat, x.lng or place.lng) <= radius_km + 1.0
        ][:6],
        "events": [
            {
                "id": e.id,
                "name": e.name,
                "start_date": e.start_date,
                "distance_km": _dist(e.lat or place.lat, e.lng or place.lng),
            }
            for e in events
            if _dist(e.lat or place.lat, e.lng or place.lng) <= radius_km + 1.0
        ][:5],
    }