"""
Alternative attraction recommendation (demand redistribution).

Given an overcrowded attraction, find nearby places with spare capacity and
explain *why* each is a good alternative. Distance is computed with haversine.
"""

from sqlalchemy.orm import Session

from ..models import CrowdData, Place
from .crowd import crowd_level
from .geo import haversine


def recommend_alternatives(db: Session, source: Place, radius_km: float = 4.0, limit: int = 6) -> list:
    places = db.query(Place).filter(
        Place.destination_id == source.destination_id,
        Place.id != source.id,
        Place.category.notin_(["hotel", "homestay", "parking", "transport", "emergency", "public_facility"]),
    ).all()

    rows = []
    for p in places:
        dist = haversine(source.lat, source.lng, p.lat, p.lng)
        if dist > radius_km:
            continue
        latest = (
            db.query(CrowdData)
            .filter(CrowdData.place_id == p.id)
            .order_by(CrowdData.timestamp.desc())
            .first()
        )
        occupancy = (latest.visitor_count / latest.capacity) if (latest and latest.capacity) else 0.0
        current = crowd_level(occupancy)
        spare = max(0.0, 1.0 - occupancy)
        score = spare * 10 - dist * 0.6
        reason = _reason(p, spare, dist)
        rows.append(
            {
                "place_id": p.id,
                "name": p.name,
                "category": p.category,
                "distance_km": round(dist, 1),
                "current_activity": current,
                "occupancy_ratio": round(occupancy, 2),
                "reason": reason,
                "image_url": (p.image_urls or [""])[0],
            }
        )

    rows.sort(key=lambda r: -r["occupancy_ratio"] * -1)  # keep stable
    rows.sort(key=lambda r: (r["current_activity"] == "high", -score))
    return rows[:limit:]


def _reason(p: Place, spare: float, dist: float) -> str:
    parts = []
    if spare >= 0.4:
        parts.append("plenty of visitor capacity available")
    elif spare >= 0.15:
        parts.append("has spare capacity right now")
    else:
        parts.append("moderately busy — visit during off-peak")
    parts.append(f"just {round(dist, 1)} km away")
    if p.is_hidden:
        parts.append("a lesser-known gem worth discovering")
    if p.category == "museum":
        parts.append("indoor, ideal during peak heat hours")
    if p.category == "temple":
        parts.append("supports a calm, cultural visit")
    return ", ".join(parts) + "."