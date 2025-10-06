"""
IHT Gifts Management Endpoint

Gift tracking and 7-year rule management:
- Gift CRUD operations
- Taper relief calculations
- PET (Potentially Exempt Transfer) tracking
- 7-year timeline visualization data
- Annual exemption tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.iht import Gift

router = APIRouter()


class GiftCreate(BaseModel):
    recipient_name: str = Field(..., description="Recipient name")
    recipient_relationship: str = Field(..., description="Relationship to donor")
    amount: float = Field(..., description="Gift amount")
    gift_date: date = Field(..., description="Date of gift")
    gift_type: str = Field("PET", description="Gift type: PET, CLT, exempt")
    description: Optional[str] = Field(None, description="Gift description")


class GiftUpdate(BaseModel):
    recipient_name: Optional[str] = None
    recipient_relationship: Optional[str] = None
    amount: Optional[float] = None
    gift_date: Optional[date] = None
    gift_type: Optional[str] = None
    description: Optional[str] = None


@router.get("", response_model=List[Dict[str, Any]])
def get_gifts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all gifts for the current user.

    Returns gifts with taper relief calculations.
    """

    gifts = db.query(Gift).filter(
        Gift.user_id == current_user.id
    ).order_by(Gift.gift_date.desc()).all()

    today = date.today()
    seven_years_ago = today - timedelta(days=7*365)

    result = []
    for gift in gifts:
        # Calculate years since gift
        years_since_gift = (today - gift.gift_date).days / 365.25 if gift.gift_date else 0

        # Determine if within 7-year period
        within_7_years = gift.gift_date >= seven_years_ago if gift.gift_date else False

        # Calculate taper relief (for PETs)
        taper_relief = _calculate_taper_relief(years_since_gift) if gift.gift_type == 'PET' else 0

        # IHT due if donor dies now (for PETs within 7 years)
        iht_if_dies_now = 0
        if within_7_years and gift.gift_type == 'PET':
            # Simplified: assume gift exceeds nil-rate band
            taxable_amount = gift.amount
            iht_if_dies_now = taxable_amount * 0.40 * (1 - taper_relief / 100)

        result.append({
            "id": gift.id,
            "recipient_name": gift.recipient_name,
            "recipient_relationship": gift.recipient_relationship,
            "amount": gift.amount,
            "gift_date": gift.gift_date.isoformat() if gift.gift_date else None,
            "gift_type": gift.gift_type,
            "description": gift.description,
            "years_since_gift": round(years_since_gift, 1),
            "within_7_years": within_7_years,
            "taper_relief": taper_relief,
            "iht_if_dies_now": round(iht_if_dies_now, 2),
            "exempt_date": (gift.gift_date + timedelta(days=7*365)).isoformat() if gift.gift_date else None,
            "created_at": gift.created_at.isoformat() if gift.created_at else None
        })

    return result


@router.post("", response_model=Dict[str, Any])
def create_gift(
    gift_data: GiftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a new gift.

    Creates gift record for 7-year rule tracking.
    """

    new_gift = Gift(
        user_id=current_user.id,
        recipient_name=gift_data.recipient_name,
        recipient_relationship=gift_data.recipient_relationship,
        amount=gift_data.amount,
        gift_date=gift_data.gift_date,
        gift_type=gift_data.gift_type,
        description=gift_data.description
    )

    db.add(new_gift)
    db.commit()
    db.refresh(new_gift)

    # Calculate initial taper info
    today = date.today()
    years_since_gift = (today - gift_data.gift_date).days / 365.25
    taper_relief = _calculate_taper_relief(years_since_gift) if gift_data.gift_type == 'PET' else 0

    return {
        "id": new_gift.id,
        "recipient_name": new_gift.recipient_name,
        "amount": new_gift.amount,
        "gift_date": new_gift.gift_date.isoformat(),
        "gift_type": new_gift.gift_type,
        "years_since_gift": round(years_since_gift, 1),
        "taper_relief": taper_relief,
        "exempt_date": (gift_data.gift_date + timedelta(days=7*365)).isoformat(),
        "created_at": new_gift.created_at.isoformat() if new_gift.created_at else None
    }


@router.get("/{gift_id}", response_model=Dict[str, Any])
def get_gift(
    gift_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific gift by ID.
    """

    gift = db.query(Gift).filter(
        Gift.id == gift_id,
        Gift.user_id == current_user.id
    ).first()

    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    today = date.today()
    years_since_gift = (today - gift.gift_date).days / 365.25 if gift.gift_date else 0
    taper_relief = _calculate_taper_relief(years_since_gift) if gift.gift_type == 'PET' else 0

    return {
        "id": gift.id,
        "recipient_name": gift.recipient_name,
        "recipient_relationship": gift.recipient_relationship,
        "amount": gift.amount,
        "gift_date": gift.gift_date.isoformat() if gift.gift_date else None,
        "gift_type": gift.gift_type,
        "description": gift.description,
        "years_since_gift": round(years_since_gift, 1),
        "taper_relief": taper_relief,
        "created_at": gift.created_at.isoformat() if gift.created_at else None,
        "updated_at": gift.updated_at.isoformat() if gift.updated_at else None
    }


@router.put("/{gift_id}", response_model=Dict[str, Any])
def update_gift(
    gift_id: int,
    gift_data: GiftUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing gift.
    """

    gift = db.query(Gift).filter(
        Gift.id == gift_id,
        Gift.user_id == current_user.id
    ).first()

    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    # Update fields
    if gift_data.recipient_name is not None:
        gift.recipient_name = gift_data.recipient_name
    if gift_data.recipient_relationship is not None:
        gift.recipient_relationship = gift_data.recipient_relationship
    if gift_data.amount is not None:
        gift.amount = gift_data.amount
    if gift_data.gift_date is not None:
        gift.gift_date = gift_data.gift_date
    if gift_data.gift_type is not None:
        gift.gift_type = gift_data.gift_type
    if gift_data.description is not None:
        gift.description = gift_data.description

    gift.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(gift)

    today = date.today()
    years_since_gift = (today - gift.gift_date).days / 365.25 if gift.gift_date else 0
    taper_relief = _calculate_taper_relief(years_since_gift) if gift.gift_type == 'PET' else 0

    return {
        "id": gift.id,
        "recipient_name": gift.recipient_name,
        "amount": gift.amount,
        "gift_date": gift.gift_date.isoformat() if gift.gift_date else None,
        "gift_type": gift.gift_type,
        "years_since_gift": round(years_since_gift, 1),
        "taper_relief": taper_relief,
        "updated_at": gift.updated_at.isoformat() if gift.updated_at else None
    }


@router.delete("/{gift_id}", response_model=Dict[str, str])
def delete_gift(
    gift_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a gift record.
    """

    gift = db.query(Gift).filter(
        Gift.id == gift_id,
        Gift.user_id == current_user.id
    ).first()

    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    db.delete(gift)
    db.commit()

    return {"message": f"Gift to {gift.recipient_name} deleted successfully"}


@router.get("/timeline/data", response_model=Dict[str, Any])
def get_gift_timeline(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get gift timeline data for visualization.

    Returns gifts organized by year with taper relief status.
    """

    gifts = db.query(Gift).filter(
        Gift.user_id == current_user.id
    ).order_by(Gift.gift_date).all()

    today = date.today()
    seven_years_ago = today - timedelta(days=7*365)

    # Organize by year
    timeline = []
    for year_offset in range(8):  # 0-7 years ago
        year_date = today - timedelta(days=year_offset*365)
        year_start = year_date.replace(month=1, day=1)
        year_end = year_date.replace(month=12, day=31)

        year_gifts = [
            g for g in gifts
            if g.gift_date and year_start <= g.gift_date <= year_end
        ]

        total_gifts = sum(g.amount for g in year_gifts)
        years_ago = year_offset

        # Calculate taper relief for this year
        taper_relief = _calculate_taper_relief(years_ago + 0.5)  # Mid-year approximation

        timeline.append({
            "year": year_date.year,
            "years_ago": years_ago,
            "gift_count": len(year_gifts),
            "total_amount": total_gifts,
            "taper_relief": taper_relief,
            "within_7_years": years_ago < 7,
            "gifts": [
                {
                    "id": g.id,
                    "recipient": g.recipient_name,
                    "amount": g.amount,
                    "date": g.gift_date.isoformat() if g.gift_date else None
                }
                for g in year_gifts
            ]
        })

    return {
        "timeline": timeline,
        "total_gifts_7_years": sum(g.amount for g in gifts if g.gift_date and g.gift_date >= seven_years_ago),
        "total_gifts_all_time": sum(g.amount for g in gifts),
        "gifts_at_risk_count": len([g for g in gifts if g.gift_date and g.gift_date >= seven_years_ago and g.gift_type == 'PET'])
    }


def _calculate_taper_relief(years_since_gift: float) -> float:
    """
    Calculate taper relief percentage based on years since gift.

    UK IHT taper relief (for gifts within 7 years of death):
    - 0-3 years: 0% relief
    - 3-4 years: 20% relief
    - 4-5 years: 40% relief
    - 5-6 years: 60% relief
    - 6-7 years: 80% relief
    - 7+ years: 100% relief (exempt)
    """

    if years_since_gift < 3:
        return 0
    elif years_since_gift < 4:
        return 20
    elif years_since_gift < 5:
        return 40
    elif years_since_gift < 6:
        return 60
    elif years_since_gift < 7:
        return 80
    else:
        return 100  # Fully exempt