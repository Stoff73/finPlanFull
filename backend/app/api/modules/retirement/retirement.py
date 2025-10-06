"""
Retirement Module API Router

Provides dashboard and summary endpoints for the Retirement module.
Aggregates pension data, retirement projections, and income planning.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, date

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
def get_retirement_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive retirement dashboard data for the current user.

    Returns:
    - Total pension pot value
    - Projected retirement income
    - Retirement age and timeline
    - Annual Allowance usage
    - Contribution summary
    - Retirement readiness status
    """

    # Get all pension products for the user
    pensions = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'retirement',
        Product.status == 'active'
    ).all()

    # Calculate total pension value
    total_pension_value = sum(p.value or 0 for p in pensions)

    # Calculate total annual contributions
    total_annual_contributions = 0
    total_employer_contributions = 0
    total_personal_contributions = 0

    for pension in pensions:
        if pension.extra_metadata and isinstance(pension.extra_metadata, dict):
            annual_contrib = pension.extra_metadata.get('annual_contribution', 0)
            employer_contrib = pension.extra_metadata.get('employer_contribution', 0)
            personal_contrib = pension.extra_metadata.get('personal_contribution', 0)

            total_annual_contributions += annual_contrib
            total_employer_contributions += employer_contrib
            total_personal_contributions += personal_contrib

    # Get retirement age (default to 65 if not set)
    retirement_age = 65
    current_age = 40  # Default - in real app, get from user profile

    if current_user.extra_metadata and isinstance(current_user.extra_metadata, dict):
        retirement_age = current_user.extra_metadata.get('retirement_age', 65)
        current_age = current_user.extra_metadata.get('age', 40)

    years_to_retirement = max(0, retirement_age - current_age)

    # Simple retirement income projection (4% withdrawal rate)
    projected_annual_income = total_pension_value * 0.04 if total_pension_value > 0 else 0

    # State pension (full UK state pension 2024/25)
    state_pension_age = 67
    state_pension_amount = 11502  # £11,502 per year (2024/25)

    # Annual Allowance tracking (£60,000 standard allowance)
    annual_allowance = 60000
    aa_used = total_annual_contributions
    aa_remaining = max(0, annual_allowance - aa_used)
    aa_usage_percentage = (aa_used / annual_allowance * 100) if annual_allowance > 0 else 0

    # Check for MPAA (Money Purchase Annual Allowance)
    mpaa_triggered = False
    for pension in pensions:
        if pension.extra_metadata and isinstance(pension.extra_metadata, dict):
            if pension.extra_metadata.get('mpaa_triggered', False):
                mpaa_triggered = True
                annual_allowance = 10000  # MPAA reduces to £10,000
                aa_remaining = max(0, annual_allowance - aa_used)
                aa_usage_percentage = (aa_used / annual_allowance * 100) if annual_allowance > 0 else 0
                break

    # Retirement readiness assessment
    # Target: 70% of pre-retirement income (assumed £50k)
    target_annual_income = 35000  # 70% of £50k
    retirement_income_with_state = projected_annual_income + (state_pension_amount if years_to_retirement <= (state_pension_age - current_age) else 0)
    income_gap = target_annual_income - retirement_income_with_state

    if total_pension_value == 0:
        status = "not_started"
        message = "You haven't started saving for retirement yet. It's never too late to begin!"
    elif retirement_income_with_state >= target_annual_income:
        status = "on_track"
        message = f"You're on track for a comfortable retirement with £{retirement_income_with_state:,.0f} projected annual income."
    elif income_gap <= 5000:
        status = "nearly_there"
        message = f"You're nearly on track! Just £{income_gap:,.0f} more annual income needed to reach your target."
    elif income_gap <= 15000:
        status = "needs_improvement"
        message = f"You're making progress but need £{income_gap:,.0f} more annual income. Consider increasing contributions."
    else:
        status = "attention_needed"
        message = f"You're short £{income_gap:,.0f} annual income from your target. Review your retirement strategy urgently."

    # Pension breakdown by type
    pension_breakdown = {}
    for pension in pensions:
        p_type = pension.product_type or 'other'
        pension_breakdown[p_type] = pension_breakdown.get(p_type, 0) + (pension.value or 0)

    return {
        "total_pension_value": total_pension_value,
        "pension_count": len(pensions),
        "pension_breakdown": pension_breakdown,
        "annual_contributions": {
            "total": total_annual_contributions,
            "employer": total_employer_contributions,
            "personal": total_personal_contributions,
        },
        "retirement_planning": {
            "current_age": current_age,
            "retirement_age": retirement_age,
            "years_to_retirement": years_to_retirement,
            "state_pension_age": state_pension_age,
        },
        "projected_income": {
            "annual_pension_income": round(projected_annual_income, 2),
            "state_pension": state_pension_amount,
            "total_retirement_income": round(retirement_income_with_state, 2),
            "target_income": target_annual_income,
            "income_gap": round(income_gap, 2) if income_gap > 0 else 0,
        },
        "annual_allowance": {
            "allowance": annual_allowance,
            "used": aa_used,
            "remaining": aa_remaining,
            "usage_percentage": round(aa_usage_percentage, 1),
            "mpaa_triggered": mpaa_triggered,
        },
        "pensions": [
            {
                "id": p.id,
                "name": p.name,
                "product_type": p.product_type,
                "value": p.value,
                "currency": p.currency or "GBP",
                "provider": p.provider or "Unknown",
                "reference_number": p.reference_number or str(p.id),
            }
            for p in pensions
        ],
        "status": status,
        "message": message,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/summary", response_model=Dict[str, Any])
def get_retirement_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quick retirement summary for main dashboard card.

    Returns key metrics only:
    - Total pension value
    - Pension count
    - Projected retirement income
    - Status
    """

    # Get all pension products
    pensions = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'retirement',
        Product.status == 'active'
    ).all()

    # Calculate total value
    total_value = sum(p.value or 0 for p in pensions)
    pension_count = len(pensions)

    # Simple income projection
    projected_annual_income = total_value * 0.04 if total_value > 0 else 0

    # Quick status
    target_income = 35000
    if total_value == 0:
        status = "not_started"
    elif projected_annual_income >= target_income:
        status = "on_track"
    elif projected_annual_income >= target_income * 0.8:
        status = "nearly_there"
    else:
        status = "needs_improvement"

    return {
        "total_pension_value": total_value,
        "pension_count": pension_count,
        "projected_annual_income": round(projected_annual_income, 2),
        "status": status
    }