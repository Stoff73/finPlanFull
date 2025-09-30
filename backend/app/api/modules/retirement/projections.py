"""
Retirement Projections Endpoint

Multi-year retirement income and pension pot projections:
- Pension growth projections
- Retirement income forecasting
- Contribution impact analysis
- State pension integration
- Tax-free cash calculations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


class RetirementProjectionRequest(BaseModel):
    current_age: int = Field(..., ge=18, le=75, description="Current age")
    retirement_age: int = Field(..., ge=50, le=75, description="Target retirement age")
    annual_contribution: Optional[float] = Field(0, description="Annual pension contribution")
    growth_rate: Optional[float] = Field(5.0, description="Expected annual growth rate (%)")
    inflation_rate: Optional[float] = Field(2.5, description="Expected inflation rate (%)")
    withdrawal_rate: Optional[float] = Field(4.0, description="Annual withdrawal rate in retirement (%)")
    include_state_pension: Optional[bool] = Field(True, description="Include state pension")


@router.post("/calculate", response_model=Dict[str, Any])
def calculate_retirement_projection(
    request: RetirementProjectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate detailed retirement projections.

    Projects pension pot growth, retirement income, and sustainability.
    """

    # Validation
    if request.retirement_age <= request.current_age:
        raise HTTPException(
            status_code=400,
            detail="Retirement age must be greater than current age"
        )

    # Get current pension value
    pensions = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'retirement',
        Product.status == 'active'
    ).all()

    current_pension_value = sum(p.value or 0 for p in pensions)

    # Parameters
    years_to_retirement = request.retirement_age - request.current_age
    annual_contribution = request.annual_contribution or 0
    growth_rate = request.growth_rate / 100  # Convert to decimal
    inflation_rate = request.inflation_rate / 100
    withdrawal_rate = request.withdrawal_rate / 100

    # --- Accumulation Phase (to retirement) ---
    accumulation_projections = []
    pension_value = current_pension_value

    for year in range(years_to_retirement + 1):
        age = request.current_age + year

        # Add contributions at start of year
        pension_value += annual_contribution

        # Apply growth
        pension_value *= (1 + growth_rate)

        accumulation_projections.append({
            "year": year,
            "age": age,
            "pension_value": round(pension_value, 2),
            "contributions_to_date": round(annual_contribution * (year + 1), 2),
            "investment_growth": round(pension_value - current_pension_value - (annual_contribution * (year + 1)), 2)
        })

    # Final pension pot at retirement
    final_pension_pot = pension_value

    # Tax-free cash (25% of pot, max £268,275 in 2024/25)
    tax_free_cash = min(final_pension_pot * 0.25, 268275)
    remaining_pot_after_tfc = final_pension_pot - tax_free_cash

    # --- Decumulation Phase (in retirement) ---
    # Annual income from pension (withdrawal rate applied to remaining pot)
    annual_pension_income = remaining_pot_after_tfc * withdrawal_rate

    # State pension (2024/25 full state pension: £11,502)
    state_pension_age = 67
    state_pension_amount = 11502 if request.include_state_pension else 0

    # Total retirement income
    total_annual_income = annual_pension_income + state_pension_amount

    # Sustainability analysis (how long will pension last?)
    decumulation_projections = []
    remaining_pot = remaining_pot_after_tfc

    for year in range(30):  # Project 30 years into retirement
        age = request.retirement_age + year

        if remaining_pot <= 0:
            break

        # Withdraw this year
        withdrawal = remaining_pot * withdrawal_rate
        remaining_pot -= withdrawal

        # Apply growth to remaining pot
        remaining_pot *= (1 + growth_rate - inflation_rate)  # Real growth

        # State pension (starts at state pension age)
        state_pension = state_pension_amount if age >= state_pension_age else 0

        decumulation_projections.append({
            "year": year,
            "age": age,
            "remaining_pot": round(max(0, remaining_pot), 2),
            "annual_withdrawal": round(withdrawal, 2),
            "state_pension": state_pension,
            "total_income": round(withdrawal + state_pension, 2)
        })

    # Sustainability assessment
    years_pot_lasts = len(decumulation_projections)

    if years_pot_lasts >= 30:
        sustainability = "excellent"
        sustainability_message = "Your pension pot should last throughout your retirement (30+ years)."
    elif years_pot_lasts >= 20:
        sustainability = "good"
        sustainability_message = f"Your pension pot should last approximately {years_pot_lasts} years."
    elif years_pot_lasts >= 10:
        sustainability = "moderate"
        sustainability_message = f"Your pension pot may only last {years_pot_lasts} years. Consider reducing withdrawal rate."
    else:
        sustainability = "poor"
        sustainability_message = f"Your pension pot may only last {years_pot_lasts} years. Review your retirement strategy urgently."

    # --- Summary ---
    summary = {
        "current_pension_value": current_pension_value,
        "projected_pension_at_retirement": round(final_pension_pot, 2),
        "total_contributions": round(annual_contribution * years_to_retirement, 2),
        "investment_growth": round(final_pension_pot - current_pension_value - (annual_contribution * years_to_retirement), 2),
        "tax_free_cash": round(tax_free_cash, 2),
        "remaining_pot_after_tfc": round(remaining_pot_after_tfc, 2),
        "annual_pension_income": round(annual_pension_income, 2),
        "state_pension_income": state_pension_amount,
        "total_retirement_income": round(total_annual_income, 2),
        "years_to_retirement": years_to_retirement,
        "years_pot_lasts": years_pot_lasts,
        "sustainability": sustainability,
        "sustainability_message": sustainability_message
    }

    return {
        "summary": summary,
        "accumulation_phase": accumulation_projections,
        "decumulation_phase": decumulation_projections,
        "assumptions": {
            "current_age": request.current_age,
            "retirement_age": request.retirement_age,
            "annual_contribution": annual_contribution,
            "growth_rate": request.growth_rate,
            "inflation_rate": request.inflation_rate,
            "withdrawal_rate": request.withdrawal_rate,
            "state_pension_age": state_pension_age,
            "state_pension_amount": state_pension_amount
        },
        "calculated_at": datetime.utcnow().isoformat()
    }


@router.get("/quick", response_model=Dict[str, Any])
def get_quick_projection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quick retirement projection using default assumptions.

    Uses user's current pension value and standard assumptions.
    """

    # Get current pension value
    pensions = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'retirement',
        Product.status == 'active'
    ).all()

    current_pension_value = sum(p.value or 0 for p in pensions)

    # Get user age and retirement age from profile
    current_age = 40
    retirement_age = 65

    if current_user.extra_metadata and isinstance(current_user.extra_metadata, dict):
        current_age = current_user.extra_metadata.get('age', 40)
        retirement_age = current_user.extra_metadata.get('retirement_age', 65)

    # Get total annual contributions
    total_contributions = 0
    for pension in pensions:
        if pension.extra_metadata and isinstance(pension.extra_metadata, dict):
            total_contributions += pension.extra_metadata.get('annual_contribution', 0)

    # Simple projection (5% growth, 4% withdrawal)
    years_to_retirement = max(0, retirement_age - current_age)

    # Future value calculation
    future_value = current_pension_value
    for _ in range(years_to_retirement):
        future_value += total_contributions
        future_value *= 1.05  # 5% growth

    # Retirement income (4% withdrawal)
    annual_income = future_value * 0.04
    state_pension = 11502  # Full UK state pension 2024/25
    total_income = annual_income + state_pension

    return {
        "current_pension_value": current_pension_value,
        "projected_pension_at_retirement": round(future_value, 2),
        "annual_retirement_income": round(annual_income, 2),
        "state_pension": state_pension,
        "total_annual_income": round(total_income, 2),
        "years_to_retirement": years_to_retirement,
        "current_age": current_age,
        "retirement_age": retirement_age
    }