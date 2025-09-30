from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.db.base import get_db
from app.models.user import User
from app.models.pension import (
    EnhancedPension, PensionInputPeriod, CarryForward,
    PensionProjection, LifetimeAllowanceTracking, AutoEnrolmentTracking,
    SchemeType, ReliefMethod, PensionType, MPAATriggerType
)
from app.api.auth.auth import get_current_user

router = APIRouter(prefix="/pension/schemes", tags=["Pension Schemes"])


# Request/Response Models
class PensionSchemeCreate(BaseModel):
    scheme_name: str
    provider: str
    scheme_type: SchemeType
    pension_type: PensionType
    relief_method: ReliefMethod
    current_value: float = 0
    transfer_value: float = 0
    monthly_member_contribution: float = 0
    monthly_employer_contribution: float = 0
    employer_match_percentage: float = 0
    employer_match_cap: Optional[float] = None
    annual_growth_rate: float = 5.0
    annual_management_charge: float = 0.75
    platform_charge: float = 0
    salary_sacrifice_active: bool = False
    protected_pension_age: Optional[int] = None
    lifetime_allowance_protection: Optional[str] = None
    notes: Optional[str] = None

    # DB specific
    db_accrual_rate: Optional[str] = None
    db_pensionable_salary: Optional[float] = None
    db_years_service: Optional[float] = None


class PensionSchemeUpdate(BaseModel):
    current_value: Optional[float] = None
    monthly_member_contribution: Optional[float] = None
    monthly_employer_contribution: Optional[float] = None
    employer_match_percentage: Optional[float] = None
    employer_match_cap: Optional[float] = None
    annual_growth_rate: Optional[float] = None
    annual_management_charge: Optional[float] = None
    salary_sacrifice_active: Optional[bool] = None
    notes: Optional[str] = None


class PensionSchemeResponse(BaseModel):
    id: int
    scheme_name: str
    provider: str
    scheme_type: str
    pension_type: str
    relief_method: str
    current_value: float
    transfer_value: float
    monthly_member_contribution: float
    monthly_employer_contribution: float
    annual_input: float
    employer_match_percentage: float
    employer_match_cap: Optional[float]
    annual_growth_rate: float
    annual_management_charge: float
    platform_charge: float
    total_annual_charges: float
    salary_sacrifice_active: bool
    mpaa_triggered: bool
    mpaa_trigger_date: Optional[date]
    protected_pension_age: Optional[int]
    lifetime_allowance_protection: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


class PensionInputCreate(BaseModel):
    pension_id: int
    tax_year: str  # e.g., "2025/26"
    member_contribution: float
    employer_contribution: float
    tax_relief_claimed: float = 0
    relief_at_source_amount: float = 0
    salary_sacrifice_amount: float = 0


class MultiSchemeAAResponse(BaseModel):
    schemes: List[Dict[str, Any]]
    total_dc_input: float
    total_db_input: float
    total_input: float
    annual_allowance: float
    tapered_aa: Optional[float]
    mpaa_limit: Optional[float]
    available_aa: float
    remaining_aa: float
    aa_charge: Optional[float]
    carry_forward_available: float
    warnings: List[str]


class SchemeProjectionRequest(BaseModel):
    pension_id: int
    retirement_age: int = 65
    annual_growth_rate: Optional[float] = None
    inflation_rate: float = 2.5
    contribution_increase_rate: float = 3.0
    additional_lump_sum: float = 0


class SchemeOptimizationRequest(BaseModel):
    target_retirement_income: float
    retirement_age: int = 65
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    maximize_tax_relief: bool = True
    use_salary_sacrifice: bool = False


# CRUD Operations
@router.post("/", response_model=PensionSchemeResponse)
async def create_pension_scheme(
    scheme: PensionSchemeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new pension scheme"""

    db_scheme = EnhancedPension(
        user_id=current_user.id,
        **scheme.dict()
    )

    # Calculate initial annual input
    annual_input = (scheme.monthly_member_contribution + scheme.monthly_employer_contribution) * 12
    db_scheme.annual_allowance_used = annual_input

    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)

    # Create initial input period for current tax year
    current_tax_year = get_current_tax_year()
    input_period = PensionInputPeriod(
        user_id=current_user.id,
        pension_id=db_scheme.id,
        tax_year=current_tax_year,
        member_contribution=scheme.monthly_member_contribution * 12,
        employer_contribution=scheme.monthly_employer_contribution * 12,
        total_input_amount=annual_input,
        annual_allowance_used=annual_input
    )
    db.add(input_period)
    db.commit()

    return format_pension_response(db_scheme)


@router.get("/", response_model=List[PensionSchemeResponse])
async def get_all_schemes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_inactive: bool = False
):
    """Get all pension schemes for user"""

    query = db.query(EnhancedPension).filter(EnhancedPension.user_id == current_user.id)

    if not include_inactive:
        query = query.filter(EnhancedPension.is_active == True)

    schemes = query.all()
    return [format_pension_response(scheme) for scheme in schemes]


@router.get("/{scheme_id}", response_model=PensionSchemeResponse)
async def get_pension_scheme(
    scheme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific pension scheme"""

    scheme = db.query(EnhancedPension).filter(
        EnhancedPension.id == scheme_id,
        EnhancedPension.user_id == current_user.id
    ).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Pension scheme not found")

    return format_pension_response(scheme)


@router.put("/{scheme_id}", response_model=PensionSchemeResponse)
async def update_pension_scheme(
    scheme_id: int,
    update_data: PensionSchemeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update pension scheme details"""

    scheme = db.query(EnhancedPension).filter(
        EnhancedPension.id == scheme_id,
        EnhancedPension.user_id == current_user.id
    ).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Pension scheme not found")

    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(scheme, field, value)

    # Recalculate annual input
    if update_data.monthly_member_contribution or update_data.monthly_employer_contribution:
        annual_input = (scheme.monthly_member_contribution + scheme.monthly_employer_contribution) * 12
        scheme.annual_allowance_used = annual_input

    scheme.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(scheme)

    return format_pension_response(scheme)


@router.delete("/{scheme_id}")
async def delete_pension_scheme(
    scheme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a pension scheme"""

    scheme = db.query(EnhancedPension).filter(
        EnhancedPension.id == scheme_id,
        EnhancedPension.user_id == current_user.id
    ).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Pension scheme not found")

    scheme.is_active = False
    scheme.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Pension scheme deactivated"}


# Multi-scheme management
@router.get("/analysis/multi-scheme-aa", response_model=MultiSchemeAAResponse)
async def analyze_multi_scheme_aa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    tax_year: str = Query(default=None, description="Tax year to analyze")
):
    """Analyze Annual Allowance across all schemes"""

    if not tax_year:
        tax_year = get_current_tax_year()

    # Get all active schemes
    schemes = db.query(EnhancedPension).filter(
        EnhancedPension.user_id == current_user.id,
        EnhancedPension.is_active == True
    ).all()

    # Calculate totals
    total_dc_input = 0
    total_db_input = 0
    scheme_details = []
    warnings = []

    for scheme in schemes:
        annual_input = (scheme.monthly_member_contribution + scheme.monthly_employer_contribution) * 12

        if scheme.scheme_type == SchemeType.DC:
            total_dc_input += annual_input
        elif scheme.scheme_type == SchemeType.DB:
            # Calculate DB input (simplified)
            if scheme.db_pensionable_salary and scheme.db_accrual_rate:
                db_input = calculate_db_input(scheme)
                total_db_input += db_input
            else:
                total_db_input += annual_input
        else:  # Hybrid
            total_dc_input += annual_input * 0.5
            total_db_input += annual_input * 0.5

        scheme_details.append({
            "id": scheme.id,
            "name": scheme.scheme_name,
            "type": scheme.scheme_type.value,
            "annual_input": annual_input,
            "is_salary_sacrifice": scheme.salary_sacrifice_active
        })

        if scheme.mpaa_triggered:
            warnings.append(f"MPAA triggered on {scheme.scheme_name} - DC contributions limited to £10,000")

    total_input = total_dc_input + total_db_input

    # Get carry forward
    carry_forward = db.query(func.sum(CarryForward.amount_available)).filter(
        CarryForward.user_id == current_user.id,
        CarryForward.expires_tax_year >= tax_year
    ).scalar() or 0

    # Check for MPAA
    mpaa_triggered = any(s.mpaa_triggered for s in schemes)
    mpaa_limit = 10000 if mpaa_triggered else None

    # Calculate available AA (simplified - would need income data for taper)
    standard_aa = 60000
    available_aa = standard_aa + carry_forward

    if mpaa_triggered and total_dc_input > 10000:
        warnings.append(f"DC contributions of £{total_dc_input:,.0f} exceed MPAA limit of £10,000")
        aa_charge = (total_dc_input - 10000) * 0.45  # Simplified
    else:
        aa_charge = max(0, (total_input - available_aa) * 0.45) if total_input > available_aa else None

    return MultiSchemeAAResponse(
        schemes=scheme_details,
        total_dc_input=total_dc_input,
        total_db_input=total_db_input,
        total_input=total_input,
        annual_allowance=standard_aa,
        tapered_aa=None,  # Would calculate based on income
        mpaa_limit=mpaa_limit,
        available_aa=available_aa,
        remaining_aa=max(0, available_aa - total_input),
        aa_charge=aa_charge,
        carry_forward_available=carry_forward,
        warnings=warnings
    )


@router.post("/mpaa/trigger")
async def trigger_mpaa(
    scheme_id: int,
    trigger_type: MPAATriggerType,
    trigger_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record MPAA trigger event"""

    scheme = db.query(EnhancedPension).filter(
        EnhancedPension.id == scheme_id,
        EnhancedPension.user_id == current_user.id
    ).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Pension scheme not found")

    scheme.mpaa_triggered = True
    scheme.mpaa_trigger_date = trigger_date
    scheme.mpaa_trigger_type = trigger_type
    scheme.updated_at = datetime.utcnow()

    db.commit()

    return {"message": f"MPAA triggered for {scheme.scheme_name} on {trigger_date}"}


@router.post("/input-period", response_model=Dict[str, Any])
async def record_pension_input(
    input_data: PensionInputCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record pension input for a tax year"""

    # Verify scheme belongs to user
    scheme = db.query(EnhancedPension).filter(
        EnhancedPension.id == input_data.pension_id,
        EnhancedPension.user_id == current_user.id
    ).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Pension scheme not found")

    # Check if input period exists
    existing = db.query(PensionInputPeriod).filter(
        PensionInputPeriod.pension_id == input_data.pension_id,
        PensionInputPeriod.tax_year == input_data.tax_year
    ).first()

    if existing:
        # Update existing
        existing.member_contribution = input_data.member_contribution
        existing.employer_contribution = input_data.employer_contribution
        existing.total_input_amount = input_data.member_contribution + input_data.employer_contribution
        existing.tax_relief_claimed = input_data.tax_relief_claimed
        existing.relief_at_source_amount = input_data.relief_at_source_amount
        existing.salary_sacrifice_amount = input_data.salary_sacrifice_amount
        existing.updated_at = datetime.utcnow()
        db.commit()
        return {"message": "Input period updated", "id": existing.id}
    else:
        # Create new
        input_period = PensionInputPeriod(
            user_id=current_user.id,
            pension_id=input_data.pension_id,
            tax_year=input_data.tax_year,
            member_contribution=input_data.member_contribution,
            employer_contribution=input_data.employer_contribution,
            total_input_amount=input_data.member_contribution + input_data.employer_contribution,
            tax_relief_claimed=input_data.tax_relief_claimed,
            relief_at_source_amount=input_data.relief_at_source_amount,
            salary_sacrifice_amount=input_data.salary_sacrifice_amount,
            annual_allowance_used=input_data.member_contribution + input_data.employer_contribution
        )
        db.add(input_period)
        db.commit()
        return {"message": "Input period created", "id": input_period.id}


# Helper functions
def format_pension_response(scheme: EnhancedPension) -> PensionSchemeResponse:
    """Format pension scheme for response"""
    annual_input = (scheme.monthly_member_contribution + scheme.monthly_employer_contribution) * 12
    total_charges = scheme.annual_management_charge + scheme.platform_charge

    return PensionSchemeResponse(
        id=scheme.id,
        scheme_name=scheme.scheme_name,
        provider=scheme.provider,
        scheme_type=scheme.scheme_type.value,
        pension_type=scheme.pension_type.value,
        relief_method=scheme.relief_method.value,
        current_value=scheme.current_value,
        transfer_value=scheme.transfer_value,
        monthly_member_contribution=scheme.monthly_member_contribution,
        monthly_employer_contribution=scheme.monthly_employer_contribution,
        annual_input=annual_input,
        employer_match_percentage=scheme.employer_match_percentage,
        employer_match_cap=scheme.employer_match_cap,
        annual_growth_rate=scheme.annual_growth_rate,
        annual_management_charge=scheme.annual_management_charge,
        platform_charge=scheme.platform_charge,
        total_annual_charges=total_charges,
        salary_sacrifice_active=scheme.salary_sacrifice_active,
        mpaa_triggered=scheme.mpaa_triggered,
        mpaa_trigger_date=scheme.mpaa_trigger_date,
        protected_pension_age=scheme.protected_pension_age,
        lifetime_allowance_protection=scheme.lifetime_allowance_protection,
        is_active=scheme.is_active,
        created_at=scheme.created_at,
        updated_at=scheme.updated_at,
        notes=scheme.notes
    )


def get_current_tax_year() -> str:
    """Get current UK tax year"""
    today = date.today()
    if today.month >= 4 and today.day >= 6:
        return f"{today.year}/{str(today.year + 1)[2:]}"
    else:
        return f"{today.year - 1}/{str(today.year)[2:]}"


def calculate_db_input(scheme: EnhancedPension) -> float:
    """Calculate DB pension input amount"""
    if not scheme.db_pensionable_salary or not scheme.db_accrual_rate:
        return 0

    # Parse accrual rate (e.g., "1/60th" -> 1/60)
    if "/" in scheme.db_accrual_rate:
        parts = scheme.db_accrual_rate.replace("th", "").replace("st", "").replace("nd", "").split("/")
        accrual = float(parts[0]) / float(parts[1])
    else:
        accrual = 1/60  # Default

    # Simplified DB input calculation
    annual_pension_accrual = scheme.db_pensionable_salary * accrual
    return annual_pension_accrual * 16  # Standard factor for DB schemes