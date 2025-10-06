"""
Retirement Pensions Management Endpoints

CRUD operations for pension products and UK pension planning features:
- Pension CRUD (create, read, update, delete)
- Annual Allowance tracking and calculations
- MPAA (Money Purchase Annual Allowance) monitoring
- Taper calculations for high earners
- 3-year carry-forward logic
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


# Pydantic schemas
class PensionProductCreate(BaseModel):
    name: str = Field(..., description="Pension name")
    product_type: str = Field(..., description="Pension type: personal, workplace, sipp, final_salary")
    provider: Optional[str] = Field(None, description="Pension provider")
    value: float = Field(..., description="Current pension value")
    annual_contribution: Optional[float] = Field(0, description="Total annual contribution")
    employer_contribution: Optional[float] = Field(0, description="Employer annual contribution")
    personal_contribution: Optional[float] = Field(0, description="Personal annual contribution")
    tax_relief_method: Optional[str] = Field("relief_at_source", description="Tax relief method")
    mpaa_triggered: Optional[bool] = Field(False, description="MPAA triggered flag")
    notes: Optional[str] = Field(None, description="Additional notes")


class PensionProductUpdate(BaseModel):
    name: Optional[str] = None
    product_type: Optional[str] = None
    provider: Optional[str] = None
    value: Optional[float] = None
    annual_contribution: Optional[float] = None
    employer_contribution: Optional[float] = None
    personal_contribution: Optional[float] = None
    tax_relief_method: Optional[str] = None
    mpaa_triggered: Optional[bool] = None
    notes: Optional[str] = None


class AnnualAllowanceRequest(BaseModel):
    threshold_income: float = Field(..., description="Threshold income (salary + employer contributions)")
    adjusted_income: float = Field(..., description="Adjusted income (threshold + employee contributions)")
    contributions: float = Field(..., description="Total pension contributions for the year")
    tax_year: Optional[str] = Field(None, description="Tax year (e.g., '2024/25')")


@router.get("", response_model=List[Dict[str, Any]])
def get_pensions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pension products for the current user.

    Supports pagination via skip/limit parameters.
    """
    pensions = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'retirement',
        Product.status == 'active'
    ).order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "product_type": p.product_type,
            "provider": p.provider,
            "value": p.value,
            "annual_contribution": p.extra_metadata.get('annual_contribution', 0) if p.extra_metadata else 0,
            "employer_contribution": p.extra_metadata.get('employer_contribution', 0) if p.extra_metadata else 0,
            "personal_contribution": p.extra_metadata.get('personal_contribution', 0) if p.extra_metadata else 0,
            "tax_relief_method": p.extra_metadata.get('tax_relief_method', 'relief_at_source') if p.extra_metadata else 'relief_at_source',
            "mpaa_triggered": p.extra_metadata.get('mpaa_triggered', False) if p.extra_metadata else False,
            "notes": p.extra_metadata.get('notes') if p.extra_metadata else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        }
        for p in pensions
    ]


@router.post("", response_model=Dict[str, Any])
def create_pension(
    pension_data: PensionProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new pension product.

    Sets module='retirement' automatically.
    """

    # Build metadata
    metadata = {
        "annual_contribution": pension_data.annual_contribution or 0,
        "employer_contribution": pension_data.employer_contribution or 0,
        "personal_contribution": pension_data.personal_contribution or 0,
        "tax_relief_method": pension_data.tax_relief_method or 'relief_at_source',
        "mpaa_triggered": pension_data.mpaa_triggered or False,
    }

    if pension_data.notes:
        metadata["notes"] = pension_data.notes

    # Create product
    new_pension = Product(
        user_id=current_user.id,
        module='retirement',
        name=pension_data.name,
        product_type=pension_data.product_type,
        provider=pension_data.provider,
        value=pension_data.value,
        status='active',
        extra_metadata=metadata
    )

    db.add(new_pension)
    db.commit()
    db.refresh(new_pension)

    return {
        "id": new_pension.id,
        "name": new_pension.name,
        "product_type": new_pension.product_type,
        "provider": new_pension.provider,
        "value": new_pension.value,
        **metadata,
        "created_at": new_pension.created_at.isoformat() if new_pension.created_at else None
    }


@router.get("/{pension_id}", response_model=Dict[str, Any])
def get_pension(
    pension_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific pension product by ID.

    Verifies user ownership.
    """
    pension = db.query(Product).filter(
        Product.id == pension_id,
        Product.user_id == current_user.id,
        Product.module == 'retirement'
    ).first()

    if not pension:
        raise HTTPException(status_code=404, detail="Pension not found")

    return {
        "id": pension.id,
        "name": pension.name,
        "product_type": pension.product_type,
        "provider": pension.provider,
        "value": pension.value,
        "annual_contribution": pension.extra_metadata.get('annual_contribution', 0) if pension.extra_metadata else 0,
        "employer_contribution": pension.extra_metadata.get('employer_contribution', 0) if pension.extra_metadata else 0,
        "personal_contribution": pension.extra_metadata.get('personal_contribution', 0) if pension.extra_metadata else 0,
        "tax_relief_method": pension.extra_metadata.get('tax_relief_method') if pension.extra_metadata else 'relief_at_source',
        "mpaa_triggered": pension.extra_metadata.get('mpaa_triggered', False) if pension.extra_metadata else False,
        "notes": pension.extra_metadata.get('notes') if pension.extra_metadata else None,
        "status": pension.status,
        "created_at": pension.created_at.isoformat() if pension.created_at else None,
        "updated_at": pension.updated_at.isoformat() if pension.updated_at else None
    }


@router.put("/{pension_id}", response_model=Dict[str, Any])
def update_pension(
    pension_id: int,
    pension_data: PensionProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing pension product.

    Verifies user ownership before updating.
    """
    pension = db.query(Product).filter(
        Product.id == pension_id,
        Product.user_id == current_user.id,
        Product.module == 'retirement'
    ).first()

    if not pension:
        raise HTTPException(status_code=404, detail="Pension not found")

    # Update fields if provided
    if pension_data.name is not None:
        pension.name = pension_data.name
    if pension_data.product_type is not None:
        pension.product_type = pension_data.product_type
    if pension_data.provider is not None:
        pension.provider = pension_data.provider
    if pension_data.value is not None:
        pension.value = pension_data.value

    # Update metadata
    metadata = pension.extra_metadata or {}

    if pension_data.annual_contribution is not None:
        metadata['annual_contribution'] = pension_data.annual_contribution
    if pension_data.employer_contribution is not None:
        metadata['employer_contribution'] = pension_data.employer_contribution
    if pension_data.personal_contribution is not None:
        metadata['personal_contribution'] = pension_data.personal_contribution
    if pension_data.tax_relief_method is not None:
        metadata['tax_relief_method'] = pension_data.tax_relief_method
    if pension_data.mpaa_triggered is not None:
        metadata['mpaa_triggered'] = pension_data.mpaa_triggered
    if pension_data.notes is not None:
        metadata['notes'] = pension_data.notes

    pension.extra_metadata = metadata
    pension.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(pension)

    return {
        "id": pension.id,
        "name": pension.name,
        "product_type": pension.product_type,
        "provider": pension.provider,
        "value": pension.value,
        **metadata,
        "updated_at": pension.updated_at.isoformat() if pension.updated_at else None
    }


@router.delete("/{pension_id}", response_model=Dict[str, str])
def delete_pension(
    pension_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a pension product (set status to archived).

    Preserves data for historical analysis.
    """
    pension = db.query(Product).filter(
        Product.id == pension_id,
        Product.user_id == current_user.id,
        Product.module == 'retirement'
    ).first()

    if not pension:
        raise HTTPException(status_code=404, detail="Pension not found")

    # Soft delete
    pension.status = 'archived'
    pension.updated_at = datetime.utcnow()

    db.commit()

    return {"message": f"Pension '{pension.name}' archived successfully"}


@router.post("/annual-allowance", response_model=Dict[str, Any])
def calculate_annual_allowance(
    aa_request: AnnualAllowanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate Annual Allowance with taper for high earners (UK 2024/25 rules).

    Annual Allowance: £60,000 standard
    Taper: Reduces by £1 for every £2 over threshold
    Threshold income: £200,000
    Adjusted income: £260,000
    Minimum AA: £10,000
    MPAA: £10,000 (if flexibly accessed pension)
    """

    threshold_income = aa_request.threshold_income
    adjusted_income = aa_request.adjusted_income
    contributions = aa_request.contributions

    # Standard allowance (2024/25)
    standard_aa = 60000
    aa_threshold_income = 200000
    aa_adjusted_income = 260000
    minimum_aa = 10000

    # Calculate taper
    annual_allowance = standard_aa

    if threshold_income > aa_threshold_income and adjusted_income > aa_adjusted_income:
        # Taper applies: reduce by £1 for every £2 over £260k
        excess = adjusted_income - aa_adjusted_income
        taper_reduction = excess / 2
        annual_allowance = max(minimum_aa, standard_aa - taper_reduction)

    # Calculate usage
    aa_used = contributions
    aa_remaining = max(0, annual_allowance - aa_used)
    aa_usage_percentage = (aa_used / annual_allowance * 100) if annual_allowance > 0 else 0

    # Status
    if aa_used > annual_allowance:
        status = "exceeded"
        message = f"You've exceeded your Annual Allowance by £{aa_used - annual_allowance:,.0f}. Tax charges may apply."
    elif aa_usage_percentage > 90:
        status = "nearly_full"
        message = f"You've used {aa_usage_percentage:.0f}% of your Annual Allowance. Only £{aa_remaining:,.0f} remaining."
    elif aa_usage_percentage > 50:
        status = "good"
        message = f"You've used {aa_usage_percentage:.0f}% of your Annual Allowance. £{aa_remaining:,.0f} still available."
    else:
        status = "plenty_remaining"
        message = f"You've only used {aa_usage_percentage:.0f}% of your Annual Allowance. Plenty of room to contribute more."

    # Taper applied?
    taper_applied = threshold_income > aa_threshold_income and adjusted_income > aa_adjusted_income

    return {
        "annual_allowance": annual_allowance,
        "standard_allowance": standard_aa,
        "taper_applied": taper_applied,
        "taper_reduction": standard_aa - annual_allowance if taper_applied else 0,
        "contributions": contributions,
        "allowance_used": aa_used,
        "allowance_remaining": aa_remaining,
        "usage_percentage": round(aa_usage_percentage, 1),
        "status": status,
        "message": message,
        "tax_year": aa_request.tax_year or "2024/25"
    }