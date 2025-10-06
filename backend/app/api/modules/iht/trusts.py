"""
IHT Trusts Management Endpoint

Trust management for IHT planning:
- Trust CRUD operations
- Trust type tracking (discretionary, bare, interest in possession)
- 10-year periodic charge calculations
- Exit charge calculations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.iht import Trust

router = APIRouter()


class TrustCreate(BaseModel):
    trust_name: str = Field(..., description="Trust name")
    trust_type: str = Field(..., description="Trust type: discretionary, bare, interest_in_possession")
    trust_value: float = Field(..., description="Current trust value")
    creation_date: date = Field(..., description="Trust creation date")
    settlor_name: Optional[str] = Field(None, description="Settlor (creator) name")
    trustees: Optional[str] = Field(None, description="Trustee names")
    beneficiaries: Optional[str] = Field(None, description="Beneficiary names")
    notes: Optional[str] = Field(None, description="Additional notes")


class TrustUpdate(BaseModel):
    trust_name: Optional[str] = None
    trust_type: Optional[str] = None
    trust_value: Optional[float] = None
    creation_date: Optional[date] = None
    settlor_name: Optional[str] = None
    trustees: Optional[str] = None
    beneficiaries: Optional[str] = None
    notes: Optional[str] = None


@router.get("", response_model=List[Dict[str, Any]])
def get_trusts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all trusts for the current user.
    """

    trusts = db.query(Trust).filter(
        Trust.user_id == current_user.id
    ).order_by(Trust.creation_date.desc()).all()

    result = []
    for trust in trusts:
        # Calculate years since creation
        today = date.today()
        years_since_creation = (today - trust.creation_date).days / 365.25 if trust.creation_date else 0

        # Calculate next 10-year charge date (for discretionary trusts)
        next_charge_date = None
        if trust.trust_type == 'discretionary' and trust.creation_date:
            years_to_next_charge = 10 - (years_since_creation % 10)
            next_charge_date = trust.creation_date + timedelta(days=int(years_to_next_charge * 365.25))

        result.append({
            "id": trust.id,
            "trust_name": trust.trust_name,
            "trust_type": trust.trust_type,
            "trust_value": trust.trust_value,
            "creation_date": trust.creation_date.isoformat() if trust.creation_date else None,
            "settlor_name": trust.settlor_name,
            "trustees": trust.trustees,
            "beneficiaries": trust.beneficiaries,
            "notes": trust.notes,
            "years_since_creation": round(years_since_creation, 1),
            "next_10_year_charge": next_charge_date.isoformat() if next_charge_date else None,
            "created_at": trust.created_at.isoformat() if trust.created_at else None
        })

    return result


@router.post("", response_model=Dict[str, Any])
def create_trust(
    trust_data: TrustCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new trust record.
    """

    new_trust = Trust(
        user_id=current_user.id,
        trust_name=trust_data.trust_name,
        trust_type=trust_data.trust_type,
        trust_value=trust_data.trust_value,
        creation_date=trust_data.creation_date,
        settlor_name=trust_data.settlor_name,
        trustees=trust_data.trustees,
        beneficiaries=trust_data.beneficiaries,
        notes=trust_data.notes
    )

    db.add(new_trust)
    db.commit()
    db.refresh(new_trust)

    return {
        "id": new_trust.id,
        "trust_name": new_trust.trust_name,
        "trust_type": new_trust.trust_type,
        "trust_value": new_trust.trust_value,
        "creation_date": new_trust.creation_date.isoformat() if new_trust.creation_date else None,
        "created_at": new_trust.created_at.isoformat() if new_trust.created_at else None
    }


@router.get("/{trust_id}", response_model=Dict[str, Any])
def get_trust(
    trust_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific trust by ID.
    """

    trust = db.query(Trust).filter(
        Trust.id == trust_id,
        Trust.user_id == current_user.id
    ).first()

    if not trust:
        raise HTTPException(status_code=404, detail="Trust not found")

    return {
        "id": trust.id,
        "trust_name": trust.trust_name,
        "trust_type": trust.trust_type,
        "trust_value": trust.trust_value,
        "creation_date": trust.creation_date.isoformat() if trust.creation_date else None,
        "settlor_name": trust.settlor_name,
        "trustees": trust.trustees,
        "beneficiaries": trust.beneficiaries,
        "notes": trust.notes,
        "created_at": trust.created_at.isoformat() if trust.created_at else None,
        "updated_at": trust.updated_at.isoformat() if trust.updated_at else None
    }


@router.put("/{trust_id}", response_model=Dict[str, Any])
def update_trust(
    trust_id: int,
    trust_data: TrustUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing trust.
    """

    trust = db.query(Trust).filter(
        Trust.id == trust_id,
        Trust.user_id == current_user.id
    ).first()

    if not trust:
        raise HTTPException(status_code=404, detail="Trust not found")

    # Update fields
    if trust_data.trust_name is not None:
        trust.trust_name = trust_data.trust_name
    if trust_data.trust_type is not None:
        trust.trust_type = trust_data.trust_type
    if trust_data.trust_value is not None:
        trust.trust_value = trust_data.trust_value
    if trust_data.creation_date is not None:
        trust.creation_date = trust_data.creation_date
    if trust_data.settlor_name is not None:
        trust.settlor_name = trust_data.settlor_name
    if trust_data.trustees is not None:
        trust.trustees = trust_data.trustees
    if trust_data.beneficiaries is not None:
        trust.beneficiaries = trust_data.beneficiaries
    if trust_data.notes is not None:
        trust.notes = trust_data.notes

    trust.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(trust)

    return {
        "id": trust.id,
        "trust_name": trust.trust_name,
        "trust_type": trust.trust_type,
        "trust_value": trust.trust_value,
        "creation_date": trust.creation_date.isoformat() if trust.creation_date else None,
        "updated_at": trust.updated_at.isoformat() if trust.updated_at else None
    }


@router.delete("/{trust_id}", response_model=Dict[str, str])
def delete_trust(
    trust_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a trust record.
    """

    trust = db.query(Trust).filter(
        Trust.id == trust_id,
        Trust.user_id == current_user.id
    ).first()

    if not trust:
        raise HTTPException(status_code=404, detail="Trust not found")

    db.delete(trust)
    db.commit()

    return {"message": f"Trust '{trust.trust_name}' deleted successfully"}


@router.post("/{trust_id}/periodic-charge", response_model=Dict[str, Any])
def calculate_periodic_charge(
    trust_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate 10-year periodic charge for discretionary trust.

    UK IHT rules: Discretionary trusts face a 10-year periodic charge
    of up to 6% on trust value above nil-rate band.
    """

    trust = db.query(Trust).filter(
        Trust.id == trust_id,
        Trust.user_id == current_user.id
    ).first()

    if not trust:
        raise HTTPException(status_code=404, detail="Trust not found")

    if trust.trust_type != 'discretionary':
        raise HTTPException(
            status_code=400,
            detail="Periodic charges only apply to discretionary trusts"
        )

    # Calculate years since creation
    today = date.today()
    years_since_creation = (today - trust.creation_date).days / 365.25 if trust.creation_date else 0

    # 10-year anniversaries
    anniversaries_passed = int(years_since_creation / 10)

    # Nil-rate band (£325,000 in 2024/25)
    nil_rate_band = 325000

    # Chargeable value
    chargeable_value = max(0, trust.trust_value - nil_rate_band)

    # Periodic charge rate: 30% of lifetime rate (40%), applied to chargeable value
    # Effective rate: 6% maximum (30% × 40% ÷ 2)
    charge_rate = 0.06

    periodic_charge = chargeable_value * charge_rate

    # Next charge date
    next_anniversary = 10 * (anniversaries_passed + 1)
    years_to_next = next_anniversary - years_since_creation
    next_charge_date = trust.creation_date + timedelta(days=int(next_anniversary * 365.25))

    return {
        "trust_name": trust.trust_name,
        "trust_value": trust.trust_value,
        "nil_rate_band": nil_rate_band,
        "chargeable_value": chargeable_value,
        "charge_rate": charge_rate * 100,
        "periodic_charge": round(periodic_charge, 2),
        "years_since_creation": round(years_since_creation, 1),
        "anniversaries_passed": anniversaries_passed,
        "next_charge_date": next_charge_date.isoformat() if next_charge_date else None,
        "years_to_next_charge": round(years_to_next, 1),
        "calculated_at": datetime.utcnow().isoformat()
    }