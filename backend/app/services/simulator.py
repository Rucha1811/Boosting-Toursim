"""
Live tourism data simulator.

Generates plausible footfall + crowd ticks for the demo destination and
broadcasts them over WebSockets so the public map and the authority dashboard
update without a page refresh. All generated point-time data is tagged
source="simulation" so simulated analytics are clearly labelled.

The simulation is a stand-in for a future integration with sensors / mobile
location pings / gate counters.
"""

import asyncio
import json
import logging
import math
import random
from datetime import datetime

from ..core.database import SessionLocal
from ..models import CrowdData, Destination, Event, FootfallData, Place
from .ws import broadcast_authority, broadcast_public, wait_sim_tick

logger = logging.getLogger("virsa.simulator")

FESTIVAL_MULTIPLIER = 2.4


def _diurnal(hour: float, peak_mid: float = 13.0, night_floor: float = 0.12, peak: float = 1.0) -> float:
    return night_floor + (peak - night_floor) * math.exp(-((hour - peak_mid) ** 2) / 14.0)


async def simulator_loop(stop: asyncio.Event):
    logger.info("simulator started")
    while not stop.is_set():
        tick_ts = datetime.utcnow()
        try:
            await asyncio.to_thread(run_tick, tick_ts)
        except Exception as exc:
            logger.warning("simulator tick failed: %s", exc)
        await wait_sim_tick()
        # tick roughly every 5 seconds
        await _sleep_tough(5.0, stop)


async def _sleep_tough(seconds: float, stop: asyncio.Event):
    try:
        await asyncio.wait_for(stop.wait(), timeout=seconds)
    except asyncio.TimeoutError:
        pass


def run_tick(tick_ts: datetime):
    db = SessionLocal()
    try:
        destinations = db.query(Destination).filter(Destination.is_active == True).all()  # noqa: E712
        if not destinations:
            return
        summaries = []
        for dest in destinations:
            events = db.query(Event).filter(Event.destination_id == dest.id, Event.status == "live").all()
            active_events = {e.id: e for e in events}
            festival = any(e.category == "festival" for e in events)
            festival_boost = FESTIVAL_MULTIPLIER if festival else 1.0
            hour = tick_ts.hour + tick_ts.minute / 60.0

            places = db.query(Place).filter(Place.destination_id == dest.id).all()
            footfall = []
            crowds = []
            for p in places:
                noise = random.uniform(0.82, 1.22)
                base_factor = _diurnal(hour) * festival_boost * noise
                visitors = int(p.est_capacity * base_factor * random.uniform(0.9, 1.1))
                visitors = max(20, min(visitors, int(p.est_capacity * 1.6)))
                footfall.append(
                    FootfallData(
                        place_id=p.id,
                        destination_id=dest.id,
                        timestamp=tick_ts,
                        visitor_count=visitors,
                        source="simulation",
                    )
                )
                ratio = visitors / p.est_capacity if p.est_capacity else 0.0
                level = "low" if ratio < 0.35 else ("moderate" if ratio < 0.62 else ("high" if ratio < 0.85 else "critical"))
                crowds.append(
                    CrowdData(
                        place_id=p.id,
                        destination_id=dest.id,
                        timestamp=tick_ts,
                        level=level,
                        visitor_count=visitors,
                        capacity=p.est_capacity,
                        source="simulation",
                    )
                )

            for eid, ev in active_events.items():
                visitors = int(ev.expected_visitors * (0.55 + 0.45 * _diurnal(hour, peak_mid=20.0)))
                crowds.append(
                    CrowdData(
                        place_id=None,
                        event_id=eid,
                        destination_id=dest.id,
                        timestamp=tick_ts,
                        level="high" if visitors > ev.capacity * 0.7 else "moderate",
                        visitor_count=visitors,
                        capacity=ev.capacity or 1,
                        source="simulation",
                    )
                )

            db.add_all(footfall)
            db.add_all(crowds)

            summaries.append(
                {
                    "t": tick_ts.isoformat(),
                    "destination_id": dest.id,
                    "places": [
                        {"place_id": c.place_id, "level": c.level, "visitors": c.visitor_count, "capacity": c.capacity}
                        for c in crowds
                        if c.place_id is not None
                    ],
                    "events": [
                        {"event_id": c.event_id, "level": c.level, "visitors": c.visitor_count}
                        for c in crowds
                        if c.event_id is not None
                    ],
                    "source": "simulation",
                    "festival": festival,
                }
            )

        db.commit()
        for summary in summaries:
            asyncio.run(broadcast_public("tick", summary))
            asyncio.run(broadcast_authority("tick", summary))
    finally:
        db.close()