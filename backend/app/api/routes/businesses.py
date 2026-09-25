"""Business & artisan portal."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models import Business, Enquiry, Experience, Product, User
from ...schemas import (
    BusinessIn,
    BusinessOut,
    BusinessUpdate,
    EnquiryOut,
    ExperienceIn,
    ExperienceOut,
    ProductIn,
    ProductOut,
)
from ...services.ws import broadcast_public
from ..deps import get_current_user, get_header_destination_id, require_roles
from .discovery import _business_out

router = APIRouter(prefix="/businesses", tags=["businesses"])

BUSINESS_ROLES = ("business", "artisan")


@router.post("", response_model=BusinessOut, status_code=201)
def create_business(
    payload: BusinessIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*BUSINESS_ROLES)),
    dest_id: int = Depends(get_header_destination_id),
):
    biz = Business(
        owner_id=user.id,
        destination_id=payload.destination_id or dest_id,
        name=payload.name,
        kind=payload.kind,
        craft=payload.craft,
        craft_type=payload.craft_type,
        story=payload.story,
        description=payload.description,
        cultural_significance=payload.cultural_significance,
        address=payload.address,
        lat=payload.lat,
        lng=payload.lng,
        image_urls=payload.image_urls,
        opening_hours=payload.opening_hours,
        contact=payload.contact,
        price_range=payload.price_range,
        established_year=payload.established_year,
        workshop_available=payload.workshop_available,
        status=payload.status,
    )
    db.add(biz)
    db.commit()
    db.refresh(biz)
    import asyncio

    asyncio.run(broadcast_public("business_new", {"id": biz.id, "name": biz.name}))
    return _business_out(db, biz)


@router.get("/my", response_model=List[BusinessOut])
def my_businesses(db: Session = Depends(get_db), user: User = Depends(require_roles(*BUSINESS_ROLES))):
    return [_business_out(db, b) for b in db.query(Business).filter(Business.owner_id == user.id).all()]


@router.patch("/{business_id}", response_model=BusinessOut)
def update_business(
    business_id: int,
    payload: BusinessUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*BUSINESS_ROLES)),
):
    biz = db.query(Business).filter(Business.id == business_id).first()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    if biz.owner_id != user.id and user.role not in ("authority_admin",):
        raise HTTPException(status_code=403, detail="Not your business")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(biz, field, value)
    db.commit()
    db.refresh(biz)
    import asyncio

    asyncio.run(broadcast_public("business_update", {"id": biz.id, "name": biz.name, "status": biz.status}))
    return _business_out(db, biz)


@router.delete("/{business_id}", status_code=204)
def delete_business(business_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*BUSINESS_ROLES))):
    biz = db.query(Business).filter(Business.id == business_id).first()
    if not biz or (biz.owner_id != user.id and user.role != "authority_admin"):
        raise HTTPException(status_code=404, detail="Business not found")
    db.delete(biz)
    db.commit()


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@router.post("/{business_id}/products", response_model=ProductOut, status_code=201)
def add_product(
    business_id: int,
    payload: ProductIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*BUSINESS_ROLES)),
):
    biz = _owned(db, business_id, user)
    prod = Product(business_id=biz.id, **payload.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return ProductOut.model_validate(prod)


@router.patch("/{business_id}/products/{product_id}", response_model=ProductOut)
def update_product(
    business_id: int,
    product_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*BUSINESS_ROLES)),
):
    _owned(db, business_id, user)
    prod = db.query(Product).filter(Product.id == product_id, Product.business_id == business_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in payload.items():
        if hasattr(prod, k):
            setattr(prod, k, v)
    db.commit()
    db.refresh(prod)
    return ProductOut.model_validate(prod)


@router.delete("/{business_id}/products/{product_id}", status_code=204)
def delete_product(
    business_id: int, product_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*BUSINESS_ROLES))
):
    _owned(db, business_id, user)
    prod = db.query(Product).filter(Product.id == product_id, Product.business_id == business_id).first()
    if prod:
        db.delete(prod)
        db.commit()


# ---------------------------------------------------------------------------
# Experiences offered by the business
# ---------------------------------------------------------------------------

@router.post("/{business_id}/experiences", response_model=ExperienceOut, status_code=201)
def add_experience(
    business_id: int,
    payload: ExperienceIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*BUSINESS_ROLES)),
):
    biz = _owned(db, business_id, user)
    x = Experience(destination_id=biz.destination_id, provider_business_id=biz.id, **payload.model_dump())
    db.add(x)
    db.commit()
    db.refresh(x)
    return _experience_out(db, x)


def _experience_out(db, x):
    x.provider_name = ""
    prov = db.query(Business).filter(Business.id == x.provider_business_id).first()
    if prov:
        x.provider_name = prov.name
    return ExperienceOut.model_validate(x)


# ---------------------------------------------------------------------------
# Enquiries received by the business
# ---------------------------------------------------------------------------

@router.get("/{business_id}/enquiries", response_model=List[EnquiryOut])
def business_enquiries(
    business_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*BUSINESS_ROLES)),
):
    _owned(db, business_id, user)
    return db.query(Enquiry).filter(Enquiry.business_id == business_id).order_by(Enquiry.id.desc()).all()


@router.patch("/{business_id}/enquiries/{enquiry_id}", response_model=EnquiryOut)
def update_enquiry(
    business_id: int,
    enquiry_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*BUSINESS_ROLES)),
):
    _owned(db, business_id, user)
    enq = db.query(Enquiry).filter(Enquiry.id == enquiry_id, Enquiry.business_id == business_id).first()
    if not enq:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    if "status" in payload:
        enq.status = payload["status"]
    if "admin_note" in payload:
        enq.message = payload["admin_note"]
    db.commit()
    db.refresh(enq)
    return EnquiryOut.model_validate(enq)


def _owned(db, business_id: int, user: User) -> Business:
    biz = db.query(Business).filter(Business.id == business_id).first()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    if biz.owner_id != user.id and user.role != "authority_admin":
        raise HTTPException(status_code=403, detail="Not your business")
    return biz