"""Protection Needs Analysis API

Calculates recommended protection coverage based on:
- Income replacement needs
- Debt coverage
- Future expenses (education, etc.)
- Existing coverage
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


class NeedsAnalysisRequest(BaseModel):
    """Input parameters for protection needs analysis"""
    annual_income: float = Field(..., gt=0, description="Annual gross income")
    dependents: int = Field(default=0, ge=0, description="Number of dependents")
    outstanding_debts: float = Field(default=0, ge=0, description="Total outstanding debts (mortgage, loans, etc.)")
    existing_savings: float = Field(default=0, ge=0, description="Existing savings and investments")
    monthly_expenses: float = Field(default=0, ge=0, description="Monthly household expenses")
    years_of_income_replacement: int = Field(default=10, ge=1, le=30, description="Years of income to replace")
    education_fund_required: float = Field(default=0, ge=0, description="Future education costs")
    final_expenses: float = Field(default=10000, ge=0, description="Estimated funeral and final expenses")
    spouse_income: float = Field(default=0, ge=0, description="Spouse's annual income")


@router.post("")
async def calculate_protection_needs(
    request: NeedsAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate recommended protection coverage based on user's financial situation

    Uses the Human Life Value method combined with debt coverage approach
    """
    # Get existing protection coverage
    existing_coverage = _get_existing_coverage(current_user.id, db)

    # Calculate income replacement needs
    income_replacement = _calculate_income_replacement(
        request.annual_income,
        request.years_of_income_replacement,
        request.spouse_income
    )

    # Calculate debt coverage needs
    debt_coverage = request.outstanding_debts

    # Calculate future expenses
    future_expenses = request.education_fund_required + request.final_expenses

    # Calculate emergency fund (6 months expenses)
    emergency_fund = request.monthly_expenses * 6

    # Total needs
    total_needs = (
        income_replacement +
        debt_coverage +
        future_expenses +
        emergency_fund
    )

    # Subtract existing assets
    net_needs = max(0, total_needs - request.existing_savings)

    # Calculate coverage gap
    coverage_gap = net_needs - existing_coverage["total_coverage"]

    # Generate recommendations
    recommendations = _generate_needs_recommendations(
        coverage_gap,
        request.dependents,
        existing_coverage
    )

    # Calculate monthly premium estimate (rough approximation)
    estimated_monthly_premium = _estimate_monthly_premium(
        coverage_gap,
        30  # Assume age 30 for simplicity - would ideally get from user profile
    )

    return {
        "analysis": {
            "income_replacement_needs": income_replacement,
            "debt_coverage_needs": debt_coverage,
            "future_expenses_needs": future_expenses,
            "emergency_fund_needs": emergency_fund,
            "total_needs": total_needs,
            "existing_savings": request.existing_savings,
            "net_protection_needs": net_needs
        },
        "existing_coverage": existing_coverage,
        "coverage_gap": {
            "amount": coverage_gap,
            "percentage": (coverage_gap / net_needs * 100) if net_needs > 0 else 0,
            "status": "sufficient" if coverage_gap <= 0 else "insufficient"
        },
        "recommendations": recommendations,
        "estimated_cost": {
            "monthly_premium": estimated_monthly_premium,
            "annual_premium": estimated_monthly_premium * 12,
            "notes": "Premium estimates are approximate and depend on age, health, and policy type"
        }
    }


def _get_existing_coverage(user_id: int, db: Session) -> Dict[str, Any]:
    """Get user's existing protection coverage"""
    products = db.query(Product).filter(
        Product.user_id == user_id,
        Product.module == "protection",
        Product.status == "active"
    ).all()

    total_coverage = sum(float(p.value or 0) for p in products)

    coverage_by_type = {}
    for product in products:
        product_type = product.product_type or "other"
        if product_type not in coverage_by_type:
            coverage_by_type[product_type] = 0
        coverage_by_type[product_type] += float(product.value or 0)

    return {
        "total_coverage": total_coverage,
        "policy_count": len(products),
        "coverage_by_type": coverage_by_type
    }


def _calculate_income_replacement(
    annual_income: float,
    years: int,
    spouse_income: float
) -> float:
    """
    Calculate income replacement needs

    Uses simplified present value calculation (no discounting for simplicity)
    Adjusts for spouse income if present
    """
    # If spouse has income, reduce replacement needs
    income_to_replace = annual_income

    if spouse_income > 0:
        # Reduce by spouse's contribution (assuming they can cover 50% of household)
        income_to_replace = annual_income * 0.7  # 70% replacement if spouse works

    return income_to_replace * years


def _generate_needs_recommendations(
    coverage_gap: float,
    dependents: int,
    existing_coverage: Dict[str, Any]
) -> List[Dict[str, str]]:
    """Generate specific recommendations based on needs analysis"""
    recommendations = []

    if coverage_gap <= 0:
        recommendations.append({
            "priority": "info",
            "message": "Your existing coverage appears adequate for your current needs",
            "action": "Review annually as circumstances change"
        })
        return recommendations

    # Coverage gap exists
    if dependents > 0:
        recommendations.append({
            "priority": "high",
            "message": f"You have a protection gap of £{coverage_gap:,.0f} with {dependents} dependent(s)",
            "action": "Consider term life insurance for income replacement"
        })
    else:
        recommendations.append({
            "priority": "medium",
            "message": f"You have a protection gap of £{coverage_gap:,.0f}",
            "action": "Consider life insurance for debt coverage and final expenses"
        })

    # Check for coverage types
    coverage_by_type = existing_coverage["coverage_by_type"]

    if "critical_illness" not in coverage_by_type:
        recommendations.append({
            "priority": "medium",
            "message": "You don't have critical illness cover",
            "action": "Consider critical illness insurance to cover serious illness scenarios"
        })

    if "income_protection" not in coverage_by_type:
        recommendations.append({
            "priority": "medium",
            "message": "You don't have income protection",
            "action": "Consider income protection to cover salary if unable to work due to illness/injury"
        })

    # Suggest review
    recommendations.append({
        "priority": "low",
        "message": "Protection needs change over time",
        "action": "Re-run this analysis annually or after major life events (marriage, children, house purchase)"
    })

    return recommendations


def _estimate_monthly_premium(coverage_amount: float, age: int) -> float:
    """
    Estimate monthly premium for life insurance

    Very rough approximation: £1-2 per £1000 coverage per month for healthy non-smoker
    Rate increases with age
    """
    if coverage_amount <= 0:
        return 0

    # Base rate per £1000 of coverage
    base_rate = 1.0

    # Age adjustment (simplified)
    if age < 30:
        age_multiplier = 0.8
    elif age < 40:
        age_multiplier = 1.0
    elif age < 50:
        age_multiplier = 1.5
    else:
        age_multiplier = 2.5

    coverage_in_thousands = coverage_amount / 1000
    monthly_premium = coverage_in_thousands * base_rate * age_multiplier

    return round(monthly_premium, 2)


@router.get("/simple")
async def get_simple_needs_estimate(
    annual_income: float,
    dependents: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Quick protection needs estimate using rule of thumb

    Rule: 10x annual income for life insurance if you have dependents,
          5x annual income if no dependents
    """
    existing_coverage = _get_existing_coverage(current_user.id, db)

    # Apply rule of thumb
    multiplier = 10 if dependents > 0 else 5
    recommended_coverage = annual_income * multiplier

    coverage_gap = recommended_coverage - existing_coverage["total_coverage"]

    return {
        "quick_estimate": {
            "recommended_coverage": recommended_coverage,
            "rule_used": f"{multiplier}x annual income",
            "existing_coverage": existing_coverage["total_coverage"],
            "coverage_gap": coverage_gap,
            "status": "sufficient" if coverage_gap <= 0 else "insufficient"
        },
        "note": "This is a simplified estimate. For a detailed analysis, provide full financial information."
    }