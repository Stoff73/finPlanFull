from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import date, datetime
import numpy as np
from app.db.base import get_db
from app.models.user import User
from app.models.pension import (
    EnhancedPension, PensionInputPeriod, CarryForward,
    PensionProjection, LifetimeAllowanceTracking,
    SchemeType, ReliefMethod
)
from app.api.auth.auth import get_current_user

router = APIRouter(prefix="/pension/optimization", tags=["Pension Optimization"])


class OptimizationRequest(BaseModel):
    target_retirement_age: int = 65
    target_retirement_income: float = 40000
    current_age: int
    current_income: float
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    maximize_tax_relief: bool = True
    use_salary_sacrifice: bool = False
    include_state_pension: bool = True
    inflation_rate: float = 2.5


class OptimizationResponse(BaseModel):
    recommended_monthly_contribution: float
    recommended_employer_contribution: float
    recommended_relief_method: str
    projected_retirement_value: float
    projected_annual_income: float
    total_tax_savings: float
    years_to_retirement: int
    success_probability: float
    recommendations: List[str]
    warnings: List[str]
    scenario_comparison: List[Dict[str, Any]]


class ContributionOptimizer(BaseModel):
    current_contribution: float
    available_aa: float
    carry_forward_available: float
    tax_rate: str  # basic, higher, additional
    employer_match_rate: float
    employer_match_cap: Optional[float]


class ProjectionRequest(BaseModel):
    schemes: List[int]  # List of scheme IDs
    retirement_age: int = 65
    growth_scenario: str = "moderate"  # conservative, moderate, optimistic
    inflation_rate: float = 2.5
    monte_carlo_runs: int = 1000


class LifetimeAllowanceRequest(BaseModel):
    planned_crystallization_age: int = 65
    take_tax_free_cash: bool = True
    tax_free_cash_percentage: float = 25.0
    has_protection: bool = False
    protection_type: Optional[str] = None


class RetirementReadinessScore(BaseModel):
    overall_score: int  # 0-100
    income_replacement_ratio: float
    years_of_income_covered: float
    diversification_score: int
    fee_efficiency_score: int
    tax_efficiency_score: int
    risk_alignment_score: int
    recommendations: List[str]


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_pension_contributions(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize pension contributions based on goals and constraints"""

    years_to_retirement = request.target_retirement_age - request.current_age

    # Get current schemes
    schemes = db.query(EnhancedPension).filter(
        EnhancedPension.user_id == current_user.id,
        EnhancedPension.is_active == True
    ).all()

    # Calculate current total contributions
    current_monthly_total = sum(s.monthly_member_contribution + s.monthly_employer_contribution for s in schemes)

    # Determine tax band
    tax_rate = determine_tax_rate(request.current_income)

    # Calculate required contributions for target income
    required_pot = calculate_required_pot(
        request.target_retirement_income,
        request.target_retirement_age,
        request.include_state_pension
    )

    # Current value of all schemes
    current_total_value = sum(s.current_value for s in schemes)

    # Calculate required monthly contribution
    growth_rate = get_growth_rate_for_risk(request.risk_tolerance)
    required_monthly = calculate_required_monthly_contribution(
        target_value=required_pot,
        current_value=current_total_value,
        years=years_to_retirement,
        growth_rate=growth_rate,
        inflation_rate=request.inflation_rate
    )

    # Optimize for tax relief
    if request.maximize_tax_relief:
        optimal_contribution = optimize_for_tax_relief(
            required_monthly,
            request.current_income,
            tax_rate
        )
    else:
        optimal_contribution = required_monthly

    # Determine optimal relief method
    if request.use_salary_sacrifice:
        recommended_relief_method = "salary_sacrifice"
        ni_savings = optimal_contribution * 0.138  # Employee NI
    else:
        recommended_relief_method = "relief_at_source"
        ni_savings = 0

    # Calculate tax savings
    if tax_rate == "basic":
        tax_relief = optimal_contribution * 12 * 0.20
    elif tax_rate == "higher":
        tax_relief = optimal_contribution * 12 * 0.40
    else:  # additional
        tax_relief = optimal_contribution * 12 * 0.45

    total_tax_savings = tax_relief + (ni_savings * 12)

    # Generate scenarios
    scenarios = generate_contribution_scenarios(
        current_total_value,
        years_to_retirement,
        growth_rate,
        request.current_income
    )

    # Calculate success probability
    success_prob = calculate_success_probability(
        optimal_contribution,
        years_to_retirement,
        growth_rate,
        required_pot,
        current_total_value
    )

    # Generate recommendations
    recommendations = []
    warnings = []

    if optimal_contribution > request.current_income / 12 * 0.4:
        warnings.append("Recommended contribution exceeds 40% of monthly income")

    if request.current_age < 40:
        recommendations.append("Consider increasing equity allocation for long-term growth")

    if tax_rate in ["higher", "additional"]:
        recommendations.append("Maximize pension contributions to benefit from higher rate tax relief")

    if not request.use_salary_sacrifice and tax_rate != "basic":
        recommendations.append("Consider salary sacrifice to save on National Insurance")

    # Check annual allowance
    annual_contribution = optimal_contribution * 12
    if annual_contribution > 60000:
        warnings.append(f"Recommended contribution of £{annual_contribution:,.0f} exceeds annual allowance")
        recommendations.append("Consider using carry forward from previous years")

    return OptimizationResponse(
        recommended_monthly_contribution=optimal_contribution,
        recommended_employer_contribution=min(optimal_contribution * 0.3, 500),  # Typical employer contribution
        recommended_relief_method=recommended_relief_method,
        projected_retirement_value=required_pot,
        projected_annual_income=request.target_retirement_income,
        total_tax_savings=total_tax_savings,
        years_to_retirement=years_to_retirement,
        success_probability=success_prob,
        recommendations=recommendations,
        warnings=warnings,
        scenario_comparison=scenarios
    )


@router.post("/projection", response_model=Dict[str, Any])
async def create_pension_projection(
    request: ProjectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create detailed pension projection with Monte Carlo simulation"""

    # Get schemes
    schemes = db.query(EnhancedPension).filter(
        EnhancedPension.user_id == current_user.id,
        EnhancedPension.id.in_(request.schemes)
    ).all()

    if not schemes:
        raise HTTPException(status_code=404, detail="No schemes found")

    # Current values and contributions
    total_current_value = sum(s.current_value for s in schemes)
    total_monthly_contribution = sum(s.monthly_member_contribution + s.monthly_employer_contribution for s in schemes)

    # Growth parameters
    if request.growth_scenario == "conservative":
        mean_return = 0.04
        volatility = 0.08
    elif request.growth_scenario == "optimistic":
        mean_return = 0.08
        volatility = 0.15
    else:  # moderate
        mean_return = 0.06
        volatility = 0.12

    # Run Monte Carlo simulation
    simulations = []
    current_age = 35  # Would get from user profile
    years = request.retirement_age - current_age

    for _ in range(request.monte_carlo_runs):
        value = total_current_value
        annual_contribution = total_monthly_contribution * 12

        for year in range(years):
            # Random return
            annual_return = np.random.normal(mean_return, volatility)
            # Growth
            value = value * (1 + annual_return) + annual_contribution
            # Increase contributions by inflation
            annual_contribution *= (1 + request.inflation_rate / 100)

        simulations.append(value)

    simulations = np.array(simulations)

    # Calculate percentiles
    percentiles = {
        "p10": np.percentile(simulations, 10),
        "p25": np.percentile(simulations, 25),
        "p50": np.percentile(simulations, 50),
        "p75": np.percentile(simulations, 75),
        "p90": np.percentile(simulations, 90)
    }

    # Success metrics
    target_value = total_current_value * 10  # Simple target
    success_rate = (simulations >= target_value).mean()

    # Year-by-year projection (deterministic)
    projection_data = []
    value = total_current_value
    annual_contribution = total_monthly_contribution * 12

    for year in range(years + 1):
        age = current_age + year
        projection_data.append({
            "year": year,
            "age": age,
            "value": round(value, 2),
            "contributions": round(annual_contribution * year, 2),
            "growth": round(value - total_current_value - (annual_contribution * year), 2)
        })

        if year < years:
            value = value * (1 + mean_return) + annual_contribution
            annual_contribution *= (1 + request.inflation_rate / 100)

    # Save projection
    projection = PensionProjection(
        user_id=current_user.id,
        scenario_name=f"{request.growth_scenario} projection",
        retirement_age=request.retirement_age,
        current_age=current_age,
        projection_years=years,
        annual_growth_rate=mean_return * 100,
        inflation_rate=request.inflation_rate,
        monthly_contribution=total_monthly_contribution,
        projected_value=percentiles["p50"],
        projected_tax_free_cash=percentiles["p50"] * 0.25,
        projected_annual_income=percentiles["p50"] * 0.04,  # 4% withdrawal rate
        success_probability=success_rate * 100,
        percentile_10=percentiles["p10"],
        percentile_50=percentiles["p50"],
        percentile_90=percentiles["p90"],
        projection_data={"yearly": projection_data}
    )

    db.add(projection)
    db.commit()

    return {
        "projection_id": projection.id,
        "percentiles": percentiles,
        "success_rate": success_rate,
        "mean_value": float(simulations.mean()),
        "std_dev": float(simulations.std()),
        "projection_data": projection_data,
        "monte_carlo_summary": {
            "runs": request.monte_carlo_runs,
            "mean_return": mean_return,
            "volatility": volatility
        }
    }


@router.post("/lifetime-allowance", response_model=Dict[str, Any])
async def check_lifetime_allowance(
    request: LifetimeAllowanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check lifetime allowance position and tax implications"""

    # Get or create LTA tracking
    lta_tracking = db.query(LifetimeAllowanceTracking).filter(
        LifetimeAllowanceTracking.user_id == current_user.id
    ).first()

    if not lta_tracking:
        lta_tracking = LifetimeAllowanceTracking(
            user_id=current_user.id
        )
        db.add(lta_tracking)
        db.commit()

    # Get all schemes
    schemes = db.query(EnhancedPension).filter(
        EnhancedPension.user_id == current_user.id,
        EnhancedPension.is_active == True
    ).all()

    total_value = sum(s.current_value for s in schemes)

    # Project to crystallization age
    current_age = 35  # Would get from user profile
    years_to_crystallization = request.planned_crystallization_age - current_age
    projected_value = total_value * (1.05 ** years_to_crystallization)  # 5% growth assumption

    # Calculate tax-free cash
    if request.take_tax_free_cash:
        tax_free_amount = min(projected_value * request.tax_free_cash_percentage / 100, lta_tracking.lsa_available)
    else:
        tax_free_amount = 0

    # Check against allowances
    lsa_used = tax_free_amount
    lsa_remaining = lta_tracking.lsa_available - lsa_used

    warnings = []
    recommendations = []

    if lsa_used > lta_tracking.lsa_available:
        excess = lsa_used - lta_tracking.lsa_available
        tax_on_excess = excess * 0.45  # Assumed tax rate
        warnings.append(f"Tax-free cash exceeds LSA by £{excess:,.0f} - tax due: £{tax_on_excess:,.0f}")

    if projected_value > 1073100:  # Standard LSDBA
        recommendations.append("Consider applying for protection if eligible")

    # Protected amounts
    if request.has_protection and request.protection_type:
        protected_amounts = {
            "FP2016": 1250000,
            "IP2016": 1250000,
            "FP2014": 1500000,
            "IP2014": 1500000
        }
        protected_amount = protected_amounts.get(request.protection_type, 1073100)
    else:
        protected_amount = None

    return {
        "current_total_value": total_value,
        "projected_value_at_crystallization": projected_value,
        "tax_free_cash_available": tax_free_amount,
        "lsa_remaining": lsa_remaining,
        "lsdba_position": projected_value / 1073100 * 100,  # Percentage of LSDBA
        "has_protection": request.has_protection,
        "protected_amount": protected_amount,
        "warnings": warnings,
        "recommendations": recommendations,
        "tax_implications": {
            "tax_free_amount": tax_free_amount,
            "taxable_amount": projected_value - tax_free_amount,
            "estimated_tax": calculate_pension_tax(projected_value - tax_free_amount)
        }
    }


@router.get("/readiness-score", response_model=RetirementReadinessScore)
async def calculate_retirement_readiness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    target_retirement_age: int = 65
):
    """Calculate comprehensive retirement readiness score"""

    # Get all schemes
    schemes = db.query(EnhancedPension).filter(
        EnhancedPension.user_id == current_user.id,
        EnhancedPension.is_active == True
    ).all()

    if not schemes:
        return RetirementReadinessScore(
            overall_score=0,
            income_replacement_ratio=0,
            years_of_income_covered=0,
            diversification_score=0,
            fee_efficiency_score=0,
            tax_efficiency_score=0,
            risk_alignment_score=0,
            recommendations=["Start contributing to a pension scheme"]
        )

    # Calculate metrics
    total_value = sum(s.current_value for s in schemes)
    total_contributions = sum(s.monthly_member_contribution + s.monthly_employer_contribution for s in schemes) * 12

    # Income replacement (assume current income is 50000)
    current_income = 50000
    projected_income = total_value * 0.04  # 4% withdrawal rate
    income_replacement_ratio = projected_income / current_income

    # Years of income covered
    years_covered = total_value / (current_income * 0.7)  # Assume 70% income need

    # Diversification score
    scheme_types = set(s.scheme_type for s in schemes)
    diversification_score = min(len(scheme_types) * 33, 100)

    # Fee efficiency
    avg_charges = sum(s.annual_management_charge + s.platform_charge for s in schemes) / len(schemes)
    if avg_charges < 0.5:
        fee_score = 100
    elif avg_charges < 0.75:
        fee_score = 80
    elif avg_charges < 1.0:
        fee_score = 60
    else:
        fee_score = 40

    # Tax efficiency
    using_salary_sacrifice = any(s.salary_sacrifice_active for s in schemes)
    tax_score = 100 if using_salary_sacrifice else 70

    # Risk alignment (simplified)
    risk_score = 80  # Would calculate based on asset allocation

    # Overall score
    overall_score = int(
        income_replacement_ratio * 25 +
        min(years_covered / 25, 1) * 25 +
        diversification_score * 0.15 +
        fee_score * 0.15 +
        tax_score * 0.1 +
        risk_score * 0.1
    )

    # Recommendations
    recommendations = []

    if income_replacement_ratio < 0.7:
        recommendations.append("Increase contributions to improve income replacement")

    if not using_salary_sacrifice:
        recommendations.append("Consider salary sacrifice to improve tax efficiency")

    if avg_charges > 0.75:
        recommendations.append("Review scheme charges - consider lower cost options")

    if len(schemes) < 2:
        recommendations.append("Consider diversifying across multiple schemes")

    if total_contributions < current_income * 0.15:
        recommendations.append("Aim for at least 15% of income in pension contributions")

    return RetirementReadinessScore(
        overall_score=min(overall_score, 100),
        income_replacement_ratio=income_replacement_ratio,
        years_of_income_covered=years_covered,
        diversification_score=diversification_score,
        fee_efficiency_score=fee_score,
        tax_efficiency_score=tax_score,
        risk_alignment_score=risk_score,
        recommendations=recommendations
    )


# Helper functions
def determine_tax_rate(income: float) -> str:
    """Determine UK tax rate band"""
    if income <= 12570:
        return "none"
    elif income <= 50270:
        return "basic"
    elif income <= 125140:
        return "higher"
    else:
        return "additional"


def calculate_required_pot(target_income: float, retirement_age: int, include_state_pension: bool) -> float:
    """Calculate required pension pot for target income"""
    if include_state_pension:
        state_pension = 11502  # Full new state pension 2025/26
        required_private = max(0, target_income - state_pension)
    else:
        required_private = target_income

    # Using 4% withdrawal rate
    return required_private * 25


def get_growth_rate_for_risk(risk_tolerance: str) -> float:
    """Get expected growth rate based on risk tolerance"""
    rates = {
        "conservative": 0.04,
        "moderate": 0.06,
        "aggressive": 0.08
    }
    return rates.get(risk_tolerance, 0.06)


def calculate_required_monthly_contribution(
    target_value: float,
    current_value: float,
    years: int,
    growth_rate: float,
    inflation_rate: float
) -> float:
    """Calculate required monthly contribution to reach target"""
    months = years * 12
    real_rate = (growth_rate - inflation_rate / 100) / 12

    if real_rate == 0:
        return (target_value - current_value) / months

    future_value_current = current_value * (1 + real_rate) ** months
    remaining_needed = target_value - future_value_current

    if remaining_needed <= 0:
        return 0

    # PMT formula
    monthly = remaining_needed * real_rate / ((1 + real_rate) ** months - 1)
    return max(0, monthly)


def optimize_for_tax_relief(base_contribution: float, income: float, tax_rate: str) -> float:
    """Optimize contribution for maximum tax relief"""
    # Maximize within annual allowance
    annual_allowance = 60000

    if tax_rate == "higher":
        # Optimize to stay within higher rate band
        higher_rate_threshold = 50270
        if income > higher_rate_threshold:
            max_for_relief = income - higher_rate_threshold
            optimal_annual = min(max_for_relief, annual_allowance)
            return min(base_contribution, optimal_annual / 12)

    elif tax_rate == "additional":
        # Maximize relief at 45%
        return min(base_contribution * 1.2, annual_allowance / 12)

    return base_contribution


def generate_contribution_scenarios(
    current_value: float,
    years: int,
    growth_rate: float,
    income: float
) -> List[Dict[str, Any]]:
    """Generate different contribution scenarios"""
    scenarios = []

    for pct in [5, 10, 15, 20]:
        monthly = income * pct / 100 / 12
        final_value = project_value(current_value, monthly, years, growth_rate)

        scenarios.append({
            "contribution_pct": pct,
            "monthly_amount": monthly,
            "final_value": final_value,
            "annual_income": final_value * 0.04
        })

    return scenarios


def project_value(current: float, monthly: float, years: int, rate: float) -> float:
    """Project future value with monthly contributions"""
    months = years * 12
    monthly_rate = rate / 12

    if monthly_rate == 0:
        return current + monthly * months

    future_value = current * (1 + monthly_rate) ** months
    contribution_value = monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)

    return future_value + contribution_value


def calculate_success_probability(
    monthly_contribution: float,
    years: int,
    growth_rate: float,
    target: float,
    current: float
) -> float:
    """Calculate probability of reaching target"""
    projected = project_value(current, monthly_contribution, years, growth_rate)
    ratio = projected / target

    if ratio >= 1:
        return min(0.95, 0.7 + ratio * 0.1)
    else:
        return max(0.2, ratio * 0.7)


def calculate_pension_tax(taxable_amount: float) -> float:
    """Calculate tax on pension income"""
    tax = 0

    # Personal allowance
    if taxable_amount > 12570:
        # Basic rate
        basic_band = min(taxable_amount - 12570, 37700)
        tax += basic_band * 0.20

    if taxable_amount > 50270:
        # Higher rate
        higher_band = min(taxable_amount - 50270, 74870)
        tax += higher_band * 0.40

    if taxable_amount > 125140:
        # Additional rate
        additional_band = taxable_amount - 125140
        tax += additional_band * 0.45

    return tax