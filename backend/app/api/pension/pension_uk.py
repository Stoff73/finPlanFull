from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.db.base import get_db
from app.models.user import User
from app.api.auth.auth import get_current_user

router = APIRouter(prefix="/pension", tags=["UK Pension"])


class AnnualAllowanceRequest(BaseModel):
    annual_income: float
    bonus_income: float = 0
    other_income: float = 0
    personal_contribution_monthly: float
    employer_contribution_monthly: float
    relief_at_source_contributions: float = 0
    salary_sacrifice_post_2015: float = 0
    mpaa_triggered: bool = False
    tax_year: str = "2025/26"


class AnnualAllowanceResponse(BaseModel):
    standard_aa: float = 60000
    tapered_aa: Optional[float] = None
    available_aa: float
    used_aa: float
    remaining_aa: float
    aa_charge: Optional[float] = None
    is_tapered: bool = False
    mpaa_triggered: bool = False
    mpaa_limit: Optional[float] = None
    carry_forward_available: float = 0
    threshold_income: float
    adjusted_income: float


class TaperCalculationRequest(BaseModel):
    net_income: float
    relief_at_source_contributions: float = 0
    employer_pension_contributions: float = 0
    salary_sacrifice_post_2015: float = 0
    lump_sum_death_benefits: float = 0


class TaperCalculationResponse(BaseModel):
    threshold_income: float
    adjusted_income: float
    taper_applies: bool
    taper_reduction: float
    final_aa: float
    calculation_steps: List[str]


class CarryForwardRequest(BaseModel):
    user_id: Optional[int] = None
    current_year_input: float
    previous_years_data: List[Dict[str, Any]] = []  # If not provided, use defaults


class CarryForwardYear(BaseModel):
    tax_year: str
    annual_allowance: float
    amount_used: float
    available: float
    expires: str


class CarryForwardResponse(BaseModel):
    total_carry_forward: float
    carry_forward_years: List[CarryForwardYear]
    current_year_aa: float
    total_available_aa: float
    can_use_carry_forward: bool
    mpaa_restriction: bool = False


class TaxReliefRequest(BaseModel):
    gross_contribution_annual: float
    tax_rate: str  # basic, higher, additional, scotland_starter, scotland_basic, etc.
    contribution_method: str = "relief_at_source"  # relief_at_source, net_pay, salary_sacrifice
    is_scottish_taxpayer: bool = False


class TaxReliefResponse(BaseModel):
    gross_contribution: float
    basic_rate_relief: float
    higher_rate_relief: float
    additional_rate_relief: float
    total_relief: float
    net_cost: float
    effective_relief_rate: float
    ni_savings: Optional[float] = None  # For salary sacrifice


class MPAAStatusRequest(BaseModel):
    has_accessed_flexibly: bool
    access_date: Optional[date] = None
    access_type: Optional[str] = None  # UFPLS, flexi_drawdown, etc.
    current_dc_contributions: float = 0
    current_db_accrual: float = 0


class MPAAStatusResponse(BaseModel):
    mpaa_triggered: bool
    mpaa_limit: float = 10000
    alternative_aa_for_db: float = 50000
    dc_contribution_room: float
    db_accrual_room: float
    can_use_carry_forward_dc: bool = False
    can_use_carry_forward_db: bool = True
    warnings: List[str] = []


class AutoEnrolmentRequest(BaseModel):
    annual_earnings: float
    age: int
    already_enrolled: bool = False


class AutoEnrolmentResponse(BaseModel):
    eligible: bool
    earnings_trigger: float = 10000
    qualifying_earnings_lower: float = 6240
    qualifying_earnings_upper: float = 50270
    qualifying_earnings: float
    minimum_total_contribution: float
    minimum_employer_contribution: float
    minimum_employee_contribution: float
    statutory_rates: Dict[str, float]


class PensionInputPeriod(BaseModel):
    scheme_name: str
    scheme_type: str  # DC, DB, Hybrid
    input_amount: float
    employer_contribution: float
    member_contribution: float
    tax_relief_claimed: float


class ComprehensivePensionRequest(BaseModel):
    # Income details
    employment_income: float
    self_employment_income: float = 0
    rental_income: float = 0
    dividend_income: float = 0
    other_income: float = 0

    # Contribution details
    pension_schemes: List[PensionInputPeriod]

    # Status flags
    mpaa_triggered: bool = False
    has_protection: bool = False
    protection_type: Optional[str] = None

    # Tax year
    tax_year: str = "2025/26"


class ComprehensivePensionResponse(BaseModel):
    # Annual Allowance
    annual_allowance_analysis: AnnualAllowanceResponse

    # Taper
    taper_analysis: Optional[TaperCalculationResponse] = None

    # MPAA
    mpaa_status: Optional[MPAAStatusResponse] = None

    # Carry forward
    carry_forward_analysis: CarryForwardResponse

    # Tax relief
    tax_relief_summary: TaxReliefResponse

    # Auto-enrolment
    auto_enrolment_status: AutoEnrolmentResponse

    # Recommendations
    recommendations: List[str] = []
    warnings: List[str] = []


@router.post("/annual-allowance/calculate", response_model=AnnualAllowanceResponse)
async def calculate_annual_allowance(
    request: AnnualAllowanceRequest,
    current_user: User = Depends(get_current_user)
):
    """Calculate Annual Allowance including taper and MPAA considerations"""

    # Calculate total income
    total_income = request.annual_income + request.bonus_income + request.other_income

    # Calculate annual contributions
    annual_personal = request.personal_contribution_monthly * 12
    annual_employer = request.employer_contribution_monthly * 12
    total_input = annual_personal + annual_employer

    # Step 1: Calculate threshold income
    threshold_income = total_income - request.relief_at_source_contributions
    if request.salary_sacrifice_post_2015 > 0:
        threshold_income += request.salary_sacrifice_post_2015  # Add back post-2015 sacrifice

    # Step 2: Calculate adjusted income
    adjusted_income = total_income + annual_employer

    # Step 3: Determine if taper applies
    standard_aa = 60000  # 2025/26 rate
    final_aa = standard_aa
    is_tapered = False
    taper_reduction = 0

    if threshold_income > 200000 and adjusted_income > 260000:
        is_tapered = True
        excess = adjusted_income - 260000
        taper_reduction = min(excess / 2, 50000)  # Max reduction to £10k minimum
        final_aa = max(standard_aa - taper_reduction, 10000)

    # Step 4: Apply MPAA if triggered
    if request.mpaa_triggered:
        # DC contributions limited to £10,000
        mpaa_limit = 10000
        if total_input > mpaa_limit:
            final_aa = mpaa_limit  # For DC only

    # Step 5: Calculate carry forward (simplified - would query DB in production)
    carry_forward_available = 0
    if not request.mpaa_triggered or total_input <= 10000:
        # Example carry forward calculation
        carry_forward_available = 45000  # Would calculate from historical data

    # Calculate available AA
    available_aa = final_aa + carry_forward_available

    # Calculate AA charge if exceeded
    aa_charge = None
    if total_input > available_aa:
        excess = total_input - available_aa
        # AA charge is at marginal tax rate (simplified)
        if adjusted_income > 150000:
            aa_charge = excess * 0.45
        elif adjusted_income > 50270:
            aa_charge = excess * 0.40
        else:
            aa_charge = excess * 0.20

    return AnnualAllowanceResponse(
        standard_aa=standard_aa,
        tapered_aa=final_aa if is_tapered else None,
        available_aa=available_aa,
        used_aa=total_input,
        remaining_aa=max(available_aa - total_input, 0),
        aa_charge=aa_charge,
        is_tapered=is_tapered,
        mpaa_triggered=request.mpaa_triggered,
        mpaa_limit=10000 if request.mpaa_triggered else None,
        carry_forward_available=carry_forward_available,
        threshold_income=threshold_income,
        adjusted_income=adjusted_income
    )


@router.post("/taper/calculate", response_model=TaperCalculationResponse)
async def calculate_taper(
    request: TaperCalculationRequest,
    current_user: User = Depends(get_current_user)
):
    """Calculate tapered annual allowance with detailed steps"""

    steps = []

    # Step 1: Calculate threshold income
    threshold_income = request.net_income
    steps.append(f"Start with net income: £{request.net_income:,.0f}")

    if request.relief_at_source_contributions > 0:
        threshold_income -= request.relief_at_source_contributions
        steps.append(f"Deduct relief at source contributions: £{request.relief_at_source_contributions:,.0f}")

    if request.salary_sacrifice_post_2015 > 0:
        threshold_income += request.salary_sacrifice_post_2015
        steps.append(f"Add back post-2015 salary sacrifice: £{request.salary_sacrifice_post_2015:,.0f}")

    if request.lump_sum_death_benefits > 0:
        threshold_income -= request.lump_sum_death_benefits
        steps.append(f"Deduct lump sum death benefits: £{request.lump_sum_death_benefits:,.0f}")

    steps.append(f"Threshold income: £{threshold_income:,.0f}")

    # Step 2: Calculate adjusted income
    adjusted_income = request.net_income + request.employer_pension_contributions
    steps.append(f"Adjusted income (net + employer contributions): £{adjusted_income:,.0f}")

    # Step 3: Determine if taper applies
    taper_applies = threshold_income > 200000 and adjusted_income > 260000

    if not taper_applies:
        if threshold_income <= 200000:
            steps.append("Taper does not apply - threshold income ≤ £200,000")
        else:
            steps.append("Taper does not apply - adjusted income ≤ £260,000")
        return TaperCalculationResponse(
            threshold_income=threshold_income,
            adjusted_income=adjusted_income,
            taper_applies=False,
            taper_reduction=0,
            final_aa=60000,
            calculation_steps=steps
        )

    # Step 4: Calculate taper reduction
    excess = adjusted_income - 260000
    taper_reduction = min(excess / 2, 50000)
    final_aa = max(60000 - taper_reduction, 10000)

    steps.append(f"Excess over £260,000: £{excess:,.0f}")
    steps.append(f"Taper reduction (£1 for every £2): £{taper_reduction:,.0f}")
    steps.append(f"Final annual allowance: £{final_aa:,.0f}")

    return TaperCalculationResponse(
        threshold_income=threshold_income,
        adjusted_income=adjusted_income,
        taper_applies=True,
        taper_reduction=taper_reduction,
        final_aa=final_aa,
        calculation_steps=steps
    )


@router.post("/carry-forward/calculate", response_model=CarryForwardResponse)
async def calculate_carry_forward(
    request: CarryForwardRequest,
    current_user: User = Depends(get_current_user)
):
    """Calculate available carry forward from previous 3 years"""

    # In production, this would query actual historical data
    # For now, use example data or provided data

    if not request.previous_years_data:
        # Default example data
        carry_forward_years = [
            CarryForwardYear(
                tax_year="2024/25",
                annual_allowance=60000,
                amount_used=35000,
                available=25000,
                expires="2028/29"
            ),
            CarryForwardYear(
                tax_year="2023/24",
                annual_allowance=60000,
                amount_used=50000,
                available=10000,
                expires="2027/28"
            ),
            CarryForwardYear(
                tax_year="2022/23",
                annual_allowance=40000,
                amount_used=30000,
                available=10000,
                expires="2026/27"
            )
        ]
    else:
        carry_forward_years = []
        for year_data in request.previous_years_data:
            carry_forward_years.append(CarryForwardYear(
                tax_year=year_data["tax_year"],
                annual_allowance=year_data.get("annual_allowance", 60000),
                amount_used=year_data.get("amount_used", 0),
                available=year_data.get("annual_allowance", 60000) - year_data.get("amount_used", 0),
                expires=year_data.get("expires", "")
            ))

    total_carry_forward = sum(year.available for year in carry_forward_years)
    current_year_aa = 60000  # Standard for 2025/26

    return CarryForwardResponse(
        total_carry_forward=total_carry_forward,
        carry_forward_years=carry_forward_years,
        current_year_aa=current_year_aa,
        total_available_aa=current_year_aa + total_carry_forward,
        can_use_carry_forward=True,  # Simplified - would check MPAA status
        mpaa_restriction=False
    )


@router.post("/tax-relief/calculate", response_model=TaxReliefResponse)
async def calculate_tax_relief(
    request: TaxReliefRequest,
    current_user: User = Depends(get_current_user)
):
    """Calculate tax relief on pension contributions"""

    gross_contribution = request.gross_contribution_annual
    basic_rate_relief = 0
    higher_rate_relief = 0
    additional_rate_relief = 0
    ni_savings = None

    if request.is_scottish_taxpayer:
        # Scottish tax rates
        tax_rates = {
            "starter": 0.19,
            "basic": 0.20,
            "intermediate": 0.21,
            "higher": 0.42,
            "top": 0.47
        }
    else:
        # Rest of UK tax rates
        if request.tax_rate == "basic":
            basic_rate_relief = gross_contribution * 0.20
        elif request.tax_rate == "higher":
            basic_rate_relief = gross_contribution * 0.20
            higher_rate_relief = gross_contribution * 0.20  # Additional 20%
        elif request.tax_rate == "additional":
            basic_rate_relief = gross_contribution * 0.20
            additional_rate_relief = gross_contribution * 0.25  # Additional 25%

    total_relief = basic_rate_relief + higher_rate_relief + additional_rate_relief

    # Salary sacrifice NI savings
    if request.contribution_method == "salary_sacrifice":
        # Employee NI saving (13.8% on earnings between £12,570 and £50,270, 2% above)
        # Simplified calculation
        ni_savings = gross_contribution * 0.138  # Approximate
        total_relief += ni_savings

    net_cost = gross_contribution - total_relief
    effective_relief_rate = (total_relief / gross_contribution) * 100 if gross_contribution > 0 else 0

    return TaxReliefResponse(
        gross_contribution=gross_contribution,
        basic_rate_relief=basic_rate_relief,
        higher_rate_relief=higher_rate_relief,
        additional_rate_relief=additional_rate_relief,
        total_relief=total_relief,
        net_cost=net_cost,
        effective_relief_rate=effective_relief_rate,
        ni_savings=ni_savings
    )


@router.post("/mpaa/status", response_model=MPAAStatusResponse)
async def check_mpaa_status(
    request: MPAAStatusRequest,
    current_user: User = Depends(get_current_user)
):
    """Check MPAA status and impact on contributions"""

    warnings = []

    if not request.has_accessed_flexibly:
        return MPAAStatusResponse(
            mpaa_triggered=False,
            dc_contribution_room=60000,  # Full AA available
            db_accrual_room=60000,
            can_use_carry_forward_dc=True,
            can_use_carry_forward_db=True
        )

    # MPAA is triggered
    mpaa_limit = 10000
    alternative_aa = 50000  # For DB schemes when MPAA applies

    dc_room = max(mpaa_limit - request.current_dc_contributions, 0)
    db_room = max(alternative_aa - request.current_db_accrual, 0)

    if request.current_dc_contributions > mpaa_limit:
        warnings.append(f"DC contributions exceed MPAA limit by £{request.current_dc_contributions - mpaa_limit:,.0f}")

    if request.access_type:
        warnings.append(f"MPAA triggered by: {request.access_type}")

    return MPAAStatusResponse(
        mpaa_triggered=True,
        mpaa_limit=mpaa_limit,
        alternative_aa_for_db=alternative_aa,
        dc_contribution_room=dc_room,
        db_accrual_room=db_room,
        can_use_carry_forward_dc=False,
        can_use_carry_forward_db=True,
        warnings=warnings
    )


@router.post("/auto-enrolment/check", response_model=AutoEnrolmentResponse)
async def check_auto_enrolment(
    request: AutoEnrolmentRequest,
    current_user: User = Depends(get_current_user)
):
    """Check auto-enrolment eligibility and requirements"""

    # 2025/26 thresholds
    earnings_trigger = 10000
    lower_limit = 6240
    upper_limit = 50270

    # Check eligibility
    eligible = (
        request.annual_earnings >= earnings_trigger and
        request.age >= 22 and
        request.age < 66  # State Pension age (simplified)
    )

    # Calculate qualifying earnings
    if request.annual_earnings <= lower_limit:
        qualifying_earnings = 0
    elif request.annual_earnings >= upper_limit:
        qualifying_earnings = upper_limit - lower_limit
    else:
        qualifying_earnings = request.annual_earnings - lower_limit

    # Minimum contributions (8% total on qualifying earnings)
    min_total = qualifying_earnings * 0.08
    min_employer = qualifying_earnings * 0.03
    min_employee = qualifying_earnings * 0.05  # Including tax relief

    statutory_rates = {
        "total_percentage": 8.0,
        "employer_percentage": 3.0,
        "employee_percentage": 5.0
    }

    return AutoEnrolmentResponse(
        eligible=eligible,
        earnings_trigger=earnings_trigger,
        qualifying_earnings_lower=lower_limit,
        qualifying_earnings_upper=upper_limit,
        qualifying_earnings=qualifying_earnings,
        minimum_total_contribution=min_total,
        minimum_employer_contribution=min_employer,
        minimum_employee_contribution=min_employee,
        statutory_rates=statutory_rates
    )


@router.post("/comprehensive/analysis", response_model=ComprehensivePensionResponse)
async def comprehensive_pension_analysis(
    request: ComprehensivePensionRequest,
    current_user: User = Depends(get_current_user)
):
    """Comprehensive UK pension analysis combining all calculations"""

    # Calculate total income
    total_income = (
        request.employment_income +
        request.self_employment_income +
        request.rental_income +
        request.dividend_income +
        request.other_income
    )

    # Calculate total pension inputs
    total_member_contributions = sum(scheme.member_contribution for scheme in request.pension_schemes)
    total_employer_contributions = sum(scheme.employer_contribution for scheme in request.pension_schemes)
    total_input = sum(scheme.input_amount for scheme in request.pension_schemes)

    # Annual Allowance calculation
    aa_request = AnnualAllowanceRequest(
        annual_income=request.employment_income,
        bonus_income=0,
        other_income=request.self_employment_income + request.rental_income + request.dividend_income,
        personal_contribution_monthly=total_member_contributions / 12,
        employer_contribution_monthly=total_employer_contributions / 12,
        mpaa_triggered=request.mpaa_triggered,
        tax_year=request.tax_year
    )
    aa_response = await calculate_annual_allowance(aa_request, current_user)

    # Taper calculation (if high earner)
    taper_response = None
    if total_income > 200000:
        taper_request = TaperCalculationRequest(
            net_income=total_income,
            employer_pension_contributions=total_employer_contributions
        )
        taper_response = await calculate_taper(taper_request, current_user)

    # MPAA status
    mpaa_response = None
    if request.mpaa_triggered:
        dc_contributions = sum(
            scheme.input_amount for scheme in request.pension_schemes
            if scheme.scheme_type == "DC"
        )
        db_accrual = sum(
            scheme.input_amount for scheme in request.pension_schemes
            if scheme.scheme_type == "DB"
        )

        mpaa_request = MPAAStatusRequest(
            has_accessed_flexibly=True,
            current_dc_contributions=dc_contributions,
            current_db_accrual=db_accrual
        )
        mpaa_response = await check_mpaa_status(mpaa_request, current_user)

    # Carry forward
    cf_request = CarryForwardRequest(
        current_year_input=total_input
    )
    cf_response = await calculate_carry_forward(cf_request, current_user)

    # Tax relief
    tax_rate = "basic"
    if total_income > 150000:
        tax_rate = "additional"
    elif total_income > 50270:
        tax_rate = "higher"

    tr_request = TaxReliefRequest(
        gross_contribution_annual=total_member_contributions,
        tax_rate=tax_rate
    )
    tr_response = await calculate_tax_relief(tr_request, current_user)

    # Auto-enrolment
    ae_request = AutoEnrolmentRequest(
        annual_earnings=request.employment_income,
        age=35  # Would get from user profile
    )
    ae_response = await check_auto_enrolment(ae_request, current_user)

    # Generate recommendations
    recommendations = []
    warnings = []

    if aa_response.aa_charge and aa_response.aa_charge > 0:
        warnings.append(f"Annual Allowance charge of £{aa_response.aa_charge:,.0f} applies")
        recommendations.append("Consider reducing contributions or using carry forward")

    if aa_response.remaining_aa > 10000:
        recommendations.append(f"You have £{aa_response.remaining_aa:,.0f} of unused Annual Allowance")

    if taper_response and taper_response.taper_applies:
        recommendations.append("Consider salary sacrifice to reduce adjusted income below £260,000")

    if mpaa_response and mpaa_response.mpaa_triggered:
        warnings.append("MPAA is active - DC contributions limited to £10,000")

    if not ae_response.eligible:
        recommendations.append("You may want to consider voluntary pension contributions")

    return ComprehensivePensionResponse(
        annual_allowance_analysis=aa_response,
        taper_analysis=taper_response,
        mpaa_status=mpaa_response,
        carry_forward_analysis=cf_response,
        tax_relief_summary=tr_response,
        auto_enrolment_status=ae_response,
        recommendations=recommendations,
        warnings=warnings
    )