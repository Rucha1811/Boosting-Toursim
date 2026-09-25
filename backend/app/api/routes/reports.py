"""Community reporting — residents + access for authorities to view."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.destinations import DEFAULT_DESTINATION_ID, normalized_dest_id
from ...models import CommunityReport, User
from ...schemas import CommunityReportIn, CommunityReportOut
from ...services import classifier
from ...services.ws import broadcast_authority
from ..deps import get_current_user, require_roles

router = APIRouter(prefix="/reports", tags=["reports"])


def _report_out(r: CommunityReport) -> CommunityReportOut:
    name = ""
    if r.reporter:
        name = r.reporter.name
    return CommunityReportOut(
        id=r.id,
        destination_id=r.destination_id,
        category=r.category,
        title=r.title,
        description=r.description,
        user_id=r.user_id,
        lat=r.lat,
        lng=r.lng,
        image_url=r.image_url,
        status=r.status,
        admin_note=r.admin_note,
        ai_classification=r.ai_classification,
        ai_confidence=r.ai_confidence,
        reporter_name=name,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.post("", response_model=CommunityReportOut, status_code=201)
def create_report(payload: CommunityReportIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ai_cat, conf = classifier.classify(f"{payload.title} {payload.description}")
    report = CommunityReport(
        destination_id=payload.destination_id or DEFAULT_DESTINATION_ID,
        category=payload.category,
        title=payload.title,
        description=payload.description,
        user_id=user.id,
        lat=payload.lat,
        lng=payload.lng,
        image_url=payload.image_url,
        status="Reported",
        ai_classification=ai_cat,
        ai_confidence=conf,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    import asyncio

    asyncio.run(broadcast_authority("report_new", {"id": report.id, "title": report.title, "category": report.category}))
    return _report_out(report)


@router.get("/mine", response_model=List[CommunityReportOut])
def my_reports(db: Session = Depends(get_db), user=Depends(get_current_user)):
    reports = db.query(CommunityReport).filter(CommunityReport.user_id == user.id).order_by(CommunityReport.id.desc()).limit(30).all()
    return [_report_out(r) for r in reports]


@router.get("", response_model=List[CommunityReportOut])
def list_reports(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    destination_id: int = Query(1),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("authority_admin", "authority_officer")),
):
    destination_id = normalized_dest_id(db, destination_id)
    qy = db.query(CommunityReport).filter(CommunityReport.destination_id == destination_id)
    if status:
        qy = qy.filter(CommunityReport.status == status)
    if category:
        qy = qy.filter(CommunityReport.category == category)
    reports = qy.order_by(CommunityReport.id.desc()).limit(80).all()
    return [_report_out(r) for r in reports]