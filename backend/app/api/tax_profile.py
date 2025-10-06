"""Tax Profile API Router

Handles tax profile management for dual-country (UK/SA) tax planning.

Endpoints:
- GET /api/tax-profile - Get current user's tax profile
- POST /api/tax-profile - Create tax profile
- PUT /api/tax-profile - Update tax profile
- DELETE /api/tax-profile - Delete tax profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.tax_profile import TaxProfile


router = APIRouter()


# Pydantic Schemas

class TaxProfileCreate(BaseModel):
    """Schema for creating a tax profile."""
    domicile: str = Field(..., description="UK, SA, deemed_domicile_uk, other")
    domicile_of_origin: Optional[str] = Field(None, description="Birth domicile")
    domicile_acquired_date: Optional[date] = None

    tax_residency: str = Field(..., description="UK, SA, dual_resident, neither")
    uk_tax_resident: bool = False
    sa_tax_resident: bool = False

    uk_years_of_residency: int = Field(default=0, ge=0)
    sa_years_of_residency: int = Field(default=0, ge=0)

    # UK specific
    uk_remittance_basis_user: bool = False
    uk_remittance_basis_charge_paid: bool = False
    uk_split_year_treatment: bool = False
    uk_split_year_uk_part_start: Optional[date] = None
    uk_split_year_uk_part_end: Optional[date] = None

    # SA specific
    sa_ordinarily_resident: bool = False
    sa_year_of_assessment: Optional[str] = None

    # Days tracking
    uk_days_by_tax_year: Optional[Dict[str, int]] = None
    sa_days_by_tax_year: Optional[Dict[str, int]] = None

    # Migration
    planning_to_relocate: bool = False
    planned_relocation_country: Optional[str] = None
    planned_relocation_date: Optional[date] = None
    planned_relocation_reason: Optional[str] = None

    notes: Optional[str] = None
    professional_advice_received: bool = False
    advisor_name: Optional[str] = None
    advisor_contact: Optional[str] = None


class TaxProfileUpdate(BaseModel):
    """Schema for updating a tax profile."""
    domicile: Optional[str] = None
    domicile_of_origin: Optional[str] = None
    domicile_acquired_date: Optional[date] = None

    tax_residency: Optional[str] = None
    uk_tax_resident: Optional[bool] = None
    sa_tax_resident: Optional[bool] = None

    uk_years_of_residency: Optional[int] = Field(None, ge=0)
    sa_years_of_residency: Optional[int] = Field(None, ge=0)

    current_tax_year_uk_resident: Optional[bool] = None
    current_tax_year_sa_resident: Optional[bool] = None

    uk_remittance_basis_user: Optional[bool] = None
    uk_remittance_basis_charge_paid: Optional[bool] = None
    uk_split_year_treatment: Optional[bool] = None
    uk_split_year_uk_part_start: Optional[date] = None
    uk_split_year_uk_part_end: Optional[date] = None

    sa_ordinarily_resident: Optional[bool] = None
    sa_year_of_assessment: Optional[str] = None

    uk_days_by_tax_year: Optional[Dict[str, int]] = None
    sa_days_by_tax_year: Optional[Dict[str, int]] = None

    uk_srt_automatic_uk_resident: Optional[bool] = None
    uk_srt_automatic_non_resident: Optional[bool] = None
    uk_srt_sufficient_ties: Optional[Dict[str, Any]] = None

    sa_physical_presence_test_met: Optional[bool] = None
    sa_days_current_year: Optional[int] = None
    sa_days_last_5_years_total: Optional[int] = None

    treaty_tie_breaker_country: Optional[str] = None
    treaty_tie_breaker_reason: Optional[str] = None

    migration_history: Optional[List[Dict[str, Any]]] = None

    planning_to_relocate: Optional[bool] = None
    planned_relocation_country: Optional[str] = None
    planned_relocation_date: Optional[date] = None
    planned_relocation_reason: Optional[str] = None

    last_residency_review_date: Optional[date] = None
    next_review_due_date: Optional[date] = None

    notes: Optional[str] = None
    professional_advice_received: Optional[bool] = None
    advisor_name: Optional[str] = None
    advisor_contact: Optional[str] = None


class TaxProfileResponse(BaseModel):
    """Schema for tax profile response."""
    id: int
    user_id: int

    domicile: str
    domicile_of_origin: Optional[str]
    domicile_acquired_date: Optional[date]

    uk_resident_years_count: int
    uk_deemed_domicile_date: Optional[date]

    tax_residency: str
    uk_tax_resident: bool
    sa_tax_resident: bool

    uk_years_of_residency: int
    sa_years_of_residency: int

    current_tax_year_uk_resident: bool
    current_tax_year_sa_resident: bool

    uk_remittance_basis_user: bool
    uk_remittance_basis_charge_paid: bool
    uk_split_year_treatment: bool
    uk_split_year_uk_part_start: Optional[date]
    uk_split_year_uk_part_end: Optional[date]

    sa_ordinarily_resident: bool
    sa_year_of_assessment: Optional[str]

    uk_days_by_tax_year: Optional[Dict[str, int]]
    sa_days_by_tax_year: Optional[Dict[str, int]]

    uk_srt_automatic_uk_resident: bool
    uk_srt_automatic_non_resident: bool
    uk_srt_sufficient_ties: Optional[Dict[str, Any]]

    sa_physical_presence_test_met: bool
    sa_days_current_year: int
    sa_days_last_5_years_total: int

    treaty_tie_breaker_country: Optional[str]
    treaty_tie_breaker_reason: Optional[str]

    migration_history: Optional[List[Dict[str, Any]]]

    planning_to_relocate: bool
    planned_relocation_country: Optional[str]
    planned_relocation_date: Optional[date]
    planned_relocation_reason: Optional[str]

    last_residency_review_date: Optional[date]
    next_review_due_date: Optional[date]

    notes: Optional[str]
    professional_advice_received: bool
    advisor_name: Optional[str]
    advisor_contact: Optional[str]

    created_at: datetime
    updated_at: Optional[datetime]

    # Computed properties
    is_uk_domiciled: bool
    is_sa_domiciled: bool
    is_dual_resident: bool
    effective_tax_country: str

    class Config:
        from_attributes = True


# API Endpoints

@router.get("", response_model=Optional[TaxProfileResponse])
async def get_tax_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's tax profile.

    Returns None if no profile exists.
    """
    tax_profile = db.query(TaxProfile).filter(
        TaxProfile.user_id == current_user.id
    ).first()

    if not tax_profile:
        return None

    # Add computed properties
    response_data = TaxProfileResponse.from_orm(tax_profile)
    response_data.is_uk_domiciled = tax_profile.is_uk_domiciled
    response_data.is_sa_domiciled = tax_profile.is_sa_domiciled
    response_data.is_dual_resident = tax_profile.is_dual_resident
    response_data.effective_tax_country = tax_profile.effective_tax_country

    return response_data


@router.post("", response_model=TaxProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_tax_profile(
    profile_data: TaxProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a tax profile for the current user.

    Raises 400 if profile already exists.
    """
    # Check if profile already exists
    existing_profile = db.query(TaxProfile).filter(
        TaxProfile.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tax profile already exists. Use PUT to update."
        )

    # Create new profile
    tax_profile = TaxProfile(
        user_id=current_user.id,
        **profile_data.dict()
    )

    db.add(tax_profile)
    db.commit()
    db.refresh(tax_profile)

    # Add computed properties
    response_data = TaxProfileResponse.from_orm(tax_profile)
    response_data.is_uk_domiciled = tax_profile.is_uk_domiciled
    response_data.is_sa_domiciled = tax_profile.is_sa_domiciled
    response_data.is_dual_resident = tax_profile.is_dual_resident
    response_data.effective_tax_country = tax_profile.effective_tax_country

    return response_data


@router.put("", response_model=TaxProfileResponse)
async def update_tax_profile(
    profile_update: TaxProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's tax profile.

    Creates a new profile if one doesn't exist.
    """
    tax_profile = db.query(TaxProfile).filter(
        TaxProfile.user_id == current_user.id
    ).first()

    if not tax_profile:
        # Create new profile with provided data
        tax_profile = TaxProfile(
            user_id=current_user.id,
            domicile=profile_update.domicile or "UK",
            tax_residency=profile_update.tax_residency or "UK"
        )
        db.add(tax_profile)

    # Update fields
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tax_profile, field, value)

    db.commit()
    db.refresh(tax_profile)

    # Add computed properties
    response_data = TaxProfileResponse.from_orm(tax_profile)
    response_data.is_uk_domiciled = tax_profile.is_uk_domiciled
    response_data.is_sa_domiciled = tax_profile.is_sa_domiciled
    response_data.is_dual_resident = tax_profile.is_dual_resident
    response_data.effective_tax_country = tax_profile.effective_tax_country

    return response_data


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tax_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's tax profile.

    Raises 404 if no profile exists.
    """
    tax_profile = db.query(TaxProfile).filter(
        TaxProfile.user_id == current_user.id
    ).first()

    if not tax_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax profile not found"
        )

    db.delete(tax_profile)
    db.commit()

    return None


@router.get("/summary")
async def get_tax_profile_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of the user's tax profile for quick display.

    Returns simplified data for dashboard widgets.
    """
    tax_profile = db.query(TaxProfile).filter(
        TaxProfile.user_id == current_user.id
    ).first()

    if not tax_profile:
        return {
            "has_profile": False,
            "message": "No tax profile configured"
        }

    return {
        "has_profile": True,
        "domicile": tax_profile.domicile,
        "tax_residency": tax_profile.tax_residency,
        "effective_tax_country": tax_profile.effective_tax_country,
        "is_dual_resident": tax_profile.is_dual_resident,
        "uk_years_of_residency": tax_profile.uk_years_of_residency,
        "sa_years_of_residency": tax_profile.sa_years_of_residency,
        "last_review_date": tax_profile.last_residency_review_date,
        "next_review_due": tax_profile.next_review_due_date,
        "planning_to_relocate": tax_profile.planning_to_relocate,
        "planned_relocation_country": tax_profile.planned_relocation_country,
    }
