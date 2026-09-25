"""Multi-destination resolution.

Architecture-first: every public read endpoint already accepts a
`destination_id` query parameter; the write surface (authority + business
portals) resolves the active destination via an optional `X-Destination-Id`
header. Everything falls back to the canonical demo destination (Vadodara =
id 1) so the existing single-city flow keeps working unchanged.
"""
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import Destination

DEFAULT_DESTINATION_ID = 1


def normalized_dest_id(db: Session, raw: Optional[int]) -> int:
    """Return a valid destination id.

    None -> default destination. Explicit-but-unknown -> 404 (precision over
    silent fallback).
    """
    if raw is None or raw <= 0:
        return DEFAULT_DESTINATION_ID
    if not db.query(Destination).filter(Destination.id == raw).first():
        raise HTTPException(status_code=404, detail="Destination not found")
    return raw