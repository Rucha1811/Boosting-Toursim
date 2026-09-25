"""AI cultural assistant + visitor enquiries."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models import Business, Enquiry, Experience, User
from ...schemas import AssistantResponse, EnquiryIn, EnquiryOut
from ...services.assistant import answer
from ..deps import get_current_user_optional

router = APIRouter(tags=["assistant"])


@router.post("/assistant/ask", response_model=AssistantResponse)
def ask_assistant(
    payload: dict,
    destination_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    text = (payload.get("question") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Ask a question first.")
    dest_id = destination_id or payload.get("destination_id") or 1
    result = answer(db, int(dest_id), text)
    return AssistantResponse(
        answer=result["answer"],
        intents=result["intents"],
        references=result["references"],
    )


@router.post("/enquiries", response_model=EnquiryOut, status_code=201)
def create_enquiry(
    payload: EnquiryIn,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    biz_id = payload.business_id
    if payload.experience_id:
        db_exp = db.query(Experience).filter(Experience.id == payload.experience_id).first()
        if not db_exp:
            raise HTTPException(status_code=404, detail="Experience not found")
        if not db_exp.provider_business_id:
            raise HTTPException(status_code=400, detail="This experience isn't linked to a maker yet — reach out via the makers page.")
        biz_id = biz_id or db_exp.provider_business_id
    if not biz_id:
        raise HTTPException(status_code=400, detail="A business or experience is required for an enquiry.")
    if not db.query(Business).filter(Business.id == biz_id).first():
        raise HTTPException(status_code=404, detail="Business not found")
    enq = Enquiry(
        business_id=biz_id,
        experience_id=payload.experience_id,
        user_id=user.id if user else None,
        visitor_name=payload.visitor_name,
        visitor_email=payload.visitor_email,
        visitor_phone=payload.visitor_phone,
        message=payload.message,
        event_date=payload.event_date,
    )
    db.add(enq)
    db.commit()
    db.refresh(enq)
    return EnquiryOut.model_validate(enq)