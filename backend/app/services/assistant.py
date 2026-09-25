"""
Cultural information assistant.

Answers visitors' questions using ONLY verified data stored on the platform
(places, artisans, experiences, events). No free-text generation: every answer
is assembled from structured records, so answers always stay true to the
destination data.

Intents are detected with lightweight keyword matching over curated
vocabularies — the same interface can later route to an LLM + RAG pipeline
without changing the API contract.
"""

import re
from typing import List, Tuple

from sqlalchemy.orm import Session

from ..models import Business, Event, Experience, Place

INTENT_VOCAB: List[Tuple[str, List[str]]] = [
    ("history", ["history", "heritage", "ancient", "monument", "old", "archaeolog", "historic"]),
    ("artisans", ["artisan", "craft", "artisan", "handicraft", "maker", "workshop", "pottery", "weav", "embroid"]),
    ("food", ["food", "eat", "restaurant", "thali", "snack", "cuisine", "sev", "dhaba", "lunch", "dinner"]),
    ("events", ["event", "festival", "today", "happening", "garba", "navratri", "fair", "celebration"]),
    ("experiences", ["experience", "tour", "workshop", "class", "performance", "storyteller", "walk"]),
    ("nearby", ["near", "nearby", "around", "close", "near me"]),
    ("hotels", ["hotel", "stay", "homestay", "accommoda", "guesthouse", "room"]),
    ("hidden", ["hidden", "secret", "lesser known", "offbeat", "off the beaten"]),
    ("directions", ["direction", "how to reach", "route", "navigate", "transport", "bus", "train"]),
    ("prices", ["price", "cost", "fee", "charge", "entry"]),
    ("timings", ["timing", "open", "close", "hour", "when"]),
    ("guide", ["guide", "tour guide"]),
]

HEADINGS = {
    "history": "History & Heritage",
    "artisans": "Local Artisans & Makers",
    "food": "Local Food",
    "events": "What's Happening",
    "experiences": "Cultural Experiences",
    "nearby": "Nearby places",
    "hotels": "Staying Around",
    "hidden": "Hidden Gems",
    "directions": "Getting There",
    "prices": "Entry & Prices",
    "timings": "Visiting Hours",
    "guide": "Local Guides",
}


def detect_intents(text: str) -> List[str]:
    t = text.lower()
    hits = [name for name, words in INTENT_VOCAB if any(w in t for w in words)]
    return hits or ["history"]


def _place_line(p: Place, idx: int) -> str:
    hours = (
        p.opening_hours.get("display", "") if isinstance(p.opening_hours, dict) else ""
    )
    line = f"{idx}. **{p.name}** — {p.category.replace('_', ' ').title()}"
    if p.historical_period:
        line += f" ({p.historical_period})"
    if hours:
        line += f". Hours: {hours}"
    if p.entry_fee and p.entry_fee != "Free":
        line += f". Entry: {p.entry_fee}"
    return line


def answer(db: Session, destination_id: int, text: str) -> dict:
    intents = detect_intents(text)
    sections = []
    references = []

    for intent in intents:
        heading = HEADINGS[intent]
        section_lines = []

        if intent == "history":
            places = (
                db.query(Place)
                .filter(Place.destination_id == destination_id, Place.category.in_(["heritage", "history", "temple", "museum", "landmark"]))
                .limit(5)
                .all()
            )
            for i, p in enumerate(places, 1):
                section_lines.append(_place_line(p, i))
                snippet = p.history or p.summary
                if snippet:
                    section_lines[-1] += f"  {snippet[:180]}"
                    references.append({"place_id": p.id, "name": p.name, "type": "place"})

        elif intent == "artisans":
            arts = db.query(Business).filter(Business.destination_id == destination_id, Business.kind == "artisan").limit(6).all()
            for i, a in enumerate(arts, 1):
                section_lines.append(f"{i}. **{a.name}** — {a.craft or 'traditional craft'}. {a.story[:150] if a.story else ''}")
                references.append({"place_id": None, "business_id": a.id, "name": a.name, "type": "artisan"})

        elif intent == "food":
            foods = db.query(Business).filter(Business.destination_id == destination_id, Business.kind.in_(["restaurant", "food"])).limit(5).all()
            for i, f in enumerate(foods, 1):
                section_lines.append(f"{i}. **{f.name}** — {f.description[:140] if f.description else 'Local favourite'}. {f.address}")
                references.append({"business_id": f.id, "name": f.name, "type": "business"})

        elif intent in ("events", "hidden", "experiences"):
            if intent == "events":
                events = db.query(Event).filter(Event.destination_id == destination_id).limit(6).all()
                for e in events:
                    section_lines.append(f"- **{e.name}** ({e.start_date}{' – ' + e.end_date if e.end_date else ''}), {e.start_time}–{e.end_time}. {e.description[:140]}")
                if not events:
                    section_lines.append("No events scheduled on the platform yet — check the Festivals page.")
            elif intent == "hidden":
                places = db.query(Place).filter(Place.destination_id == destination_id, Place.is_hidden == True).limit(5).all()  # noqa: E712
                if not places:
                    places = db.query(Place).filter(Place.destination_id == destination_id, Place.category == "hidden_gem").limit(5).all()
                for i, p in enumerate(places, 1):
                    section_lines.append(f"{i}. **{p.name}** — {p.summary or p.description[:150]}")
                    references.append({"place_id": p.id, "name": p.name, "type": "place"})
            else:
                exps = db.query(Experience).filter(Experience.destination_id == destination_id).limit(5).all()
                for i, x in enumerate(exps, 1):
                    price = f"₹{int(x.price)}" if x.price else "Ask provider"
                    section_lines.append(f"{i}. **{x.title}** — {x.duration_minutes} min, {x.availability}. {price}.")
                    references.append({"experience_id": x.id, "name": x.title, "type": "experience"})

        elif intent == "nearby":
            places = db.query(Place).filter(Place.destination_id == destination_id).limit(6).all()
            for i, p in enumerate(places, 1):
                section_lines.append(f"{i}. **{p.name}** — {round(p.lat, 3)}, {round(p.lng, 3)}. {p.summary[:120]}")
                references.append({"place_id": p.id, "name": p.name, "type": "place"})

        elif intent == "hotels":
            hotels = db.query(Business).filter(Business.destination_id == destination_id, Business.kind.in_(["hotel", "homestay"])).limit(5).all()
            for i, h in enumerate(hotels, 1):
                section_lines.append(f"{i}. **{h.name}** — {h.description[:120]}. {h.address}")
                references.append({"business_id": h.id, "name": h.name, "type": "hotel"})

        elif intent == "directions":
            section_lines.append("Reach Vadodara Junction railway station or the city BRTS/city bus; most heritage sites lie inside the old city within a few km of the station. Ask about a specific place for exact coordinates.")

        elif intent == "prices":
            places = db.query(Place).filter(Place.destination_id == destination_id, Place.entry_fee != "Free").limit(6).all()
            if places:
                for p in places:
                    section_lines.append(f"- **{p.name}**: {p.entry_fee}")
            else:
                section_lines.append("Most heritage sites here have free entry. Some museums charge a nominal camera/entry fee.")

        elif intent == "timings":
            places = db.query(Place).filter(Place.destination_id == destination_id).limit(6).all()
            for p in places:
                hours = p.opening_hours.get("display", "Open daily") if isinstance(p.opening_hours, dict) else "Open daily"
                section_lines.append(f"- **{p.name}**: {hours}")

        elif intent == "guide":
            guides = db.query(Business).filter(Business.destination_id == destination_id, Business.kind == "guide").limit(4).all()
            for g in guides:
                section_lines.append(f"- **{g.name}** — {g.story[:140] if g.story else 'Local guide'}. {g.contact}")

        if section_lines:
            sections.append((heading, section_lines))

    if not sections:
        sections.append(
            (
                "Explore",
                ["Try asking 'what is historically important near me?', 'show me traditional crafts nearby', 'what cultural events are happening today?'."],
            )
        )

    rendered = "\n\n".join(f"### {h}\n" + "\n".join(ls) for h, ls in sections)
    return {"answer": rendered, "intents": intents, "references": references}