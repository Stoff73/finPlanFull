"""API endpoints for multi-year financial projections and forecasting."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal, Any
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.api.auth.auth import get_current_user
from app.models.user import User
from app.db.base import get_db
from app.services.projection_engine import (
    ProjectionEngine,
    ProjectionScenario,
    create_multi_year_projection
)

router = APIRouter(prefix="/api/projections", tags=["projections"])


class FinancialProjectionRequest(BaseModel):
    """Request model for multi-year financial projections."""

    # Starting values
    current_assets: float = Field(..., description="Current total assets")
    current_liabilities: float = Field(..., description="Current total liabilities")
    current_income: float = Field(..., description="Annual income")
    current_expenses: float = Field(..., description="Annual expenses")

    # Projection parameters
    projection_years: int = Field(..., ge=1, le=30, description="Years to project")
    scenario: Literal["conservative", "moderate", "optimistic"] = Field("moderate")

    # Growth assumptions
    income_growth_rate: Optional[float] = Field(None, ge=-0.2, le=0.5, description="Annual income growth rate")
    expense_growth_rate: Optional[float] = Field(None, ge=-0.2, le=0.5, description="Annual expense growth rate")
    asset_return_rate: Optional[float] = Field(None, ge=-0.5, le=0.5, description="Annual asset return rate")

    # Additional factors
    planned_major_expenses: Optional[List[Dict[str, float]]] = Field(default_factory=list)
    planned_income_changes: Optional[List[Dict[str, float]]] = Field(default_factory=list)
    inflation_rate: float = Field(0.025, ge=0, le=0.2, description="Annual inflation rate")

    # Tax considerations
    marginal_tax_rate: float = Field(0.20, ge=0, le=0.5, description="Marginal tax rate")
    capital_gains_rate: float = Field(0.20, ge=0, le=0.4, description="Capital gains tax rate")


class ProjectionResult(BaseModel):
    """Response model for projection results."""
    scenario: str
    projection_years: int
    yearly_data: List[Dict[str, float]]
    summary: Dict[str, float]
    milestones: List[Dict[str, Any]]
    warnings: List[str]


@router.post("/financial", response_model=ProjectionResult)
async def create_financial_projection(
    request: FinancialProjectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a comprehensive multi-year financial projection.

    Projects assets, liabilities, income, expenses, and net worth over time.
    Accounts for:
    - Income and expense growth
    - Asset returns
    - Major planned expenses
    - Inflation
    - Tax implications
    """

    # Set default growth rates based on scenario
    scenario_defaults = {
        "conservative": {
            "income_growth": 0.02,
            "expense_growth": 0.03,
            "asset_return": 0.04
        },
        "moderate": {
            "income_growth": 0.03,
            "expense_growth": 0.025,
            "asset_return": 0.06
        },
        "optimistic": {
            "income_growth": 0.05,
            "expense_growth": 0.02,
            "asset_return": 0.08
        }
    }

    defaults = scenario_defaults[request.scenario]
    income_growth = request.income_growth_rate or defaults["income_growth"]
    expense_growth = request.expense_growth_rate or defaults["expense_growth"]
    asset_return = request.asset_return_rate or defaults["asset_return"]

    # Initialize projection variables
    yearly_data = []
    current_net_worth = request.current_assets - request.current_liabilities
    assets = request.current_assets
    liabilities = request.current_liabilities
    income = request.current_income
    expenses = request.current_expenses

    warnings = []
    milestones = []

    # Run year-by-year projection
    for year in range(1, request.projection_years + 1):
        # Apply growth rates
        income *= (1 + income_growth)
        expenses *= (1 + expense_growth)

        # Apply asset returns
        investment_return = assets * asset_return
        assets += investment_return

        # Check for planned major expenses
        major_expense_this_year = 0
        for expense_event in request.planned_major_expenses:
            if expense_event.get("year") == year:
                major_expense_this_year += expense_event.get("amount", 0)

        # Check for planned income changes
        income_change_this_year = 0
        for income_event in request.planned_income_changes:
            if income_event.get("year") == year:
                income_change_this_year += income_event.get("amount", 0)

        income += income_change_this_year

        # Calculate net cash flow
        tax_on_income = income * request.marginal_tax_rate
        after_tax_income = income - tax_on_income
        total_expenses = expenses + major_expense_this_year
        net_cash_flow = after_tax_income - total_expenses

        # Update assets and liabilities
        if net_cash_flow > 0:
            assets += net_cash_flow
        else:
            # Need to liquidate assets or increase debt
            if assets + net_cash_flow >= 0:
                assets += net_cash_flow
            else:
                # Must take on debt
                debt_needed = abs(net_cash_flow) - assets
                assets = 0
                liabilities += debt_needed
                warnings.append(f"Year {year}: Negative cash flow resulted in additional debt of £{debt_needed:,.0f}")

        # Calculate current net worth
        net_worth = assets - liabilities

        # Apply inflation adjustment for real values
        real_net_worth = net_worth / ((1 + request.inflation_rate) ** year)

        # Track milestones
        if net_worth >= 1000000 and not any(m.get("type") == "millionaire" for m in milestones):
            milestones.append({
                "year": year,
                "type": "millionaire",
                "description": "Net worth reaches £1 million",
                "value": net_worth
            })

        if net_worth <= 0 and current_net_worth > 0:
            warnings.append(f"Year {year}: Net worth becomes negative")
            milestones.append({
                "year": year,
                "type": "negative_net_worth",
                "description": "Net worth becomes negative",
                "value": net_worth
            })

        # Store yearly data
        yearly_data.append({
            "year": year,
            "assets": round(assets, 2),
            "liabilities": round(liabilities, 2),
            "net_worth": round(net_worth, 2),
            "real_net_worth": round(real_net_worth, 2),
            "income": round(income, 2),
            "expenses": round(total_expenses, 2),
            "net_cash_flow": round(net_cash_flow, 2),
            "investment_return": round(investment_return, 2),
            "tax_paid": round(tax_on_income, 2)
        })

    # Calculate summary statistics
    final_year = yearly_data[-1]
    initial_net_worth = request.current_assets - request.current_liabilities
    total_growth = final_year["net_worth"] - initial_net_worth
    growth_percentage = (total_growth / initial_net_worth * 100) if initial_net_worth != 0 else 0

    average_annual_return = (
        ((final_year["net_worth"] / initial_net_worth) ** (1 / request.projection_years) - 1) * 100
        if initial_net_worth > 0 else 0
    )

    total_income = sum(y["income"] for y in yearly_data)
    total_expenses = sum(y["expenses"] for y in yearly_data)
    total_tax = sum(y["tax_paid"] for y in yearly_data)
    total_returns = sum(y["investment_return"] for y in yearly_data)

    summary = {
        "initial_net_worth": round(initial_net_worth, 2),
        "final_net_worth": round(final_year["net_worth"], 2),
        "total_growth": round(total_growth, 2),
        "growth_percentage": round(growth_percentage, 2),
        "average_annual_return": round(average_annual_return, 2),
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "total_tax_paid": round(total_tax, 2),
        "total_investment_returns": round(total_returns, 2),
        "final_real_net_worth": round(final_year["real_net_worth"], 2)
    }

    return ProjectionResult(
        scenario=request.scenario,
        projection_years=request.projection_years,
        yearly_data=yearly_data,
        summary=summary,
        milestones=milestones,
        warnings=warnings
    )


@router.post("/compare-scenarios", response_model=Dict[str, ProjectionResult])
async def compare_projection_scenarios(
    request: FinancialProjectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare financial projections across conservative, moderate, and optimistic scenarios.

    Returns projections for all three scenarios to help with planning.
    """

    results = {}

    for scenario in ["conservative", "moderate", "optimistic"]:
        scenario_request = request.copy()
        scenario_request.scenario = scenario

        result = await create_financial_projection(
            scenario_request,
            current_user,
            db
        )

        results[scenario] = result

    return results


@router.get("/retirement-readiness", response_model=Dict[str, Any])
async def calculate_retirement_readiness(
    current_age: int = Query(..., ge=18, le=100),
    retirement_age: int = Query(..., ge=50, le=100),
    current_savings: float = Query(..., ge=0),
    monthly_contribution: float = Query(..., ge=0),
    expected_return: float = Query(0.06, ge=0, le=0.5),
    desired_retirement_income: float = Query(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate retirement readiness and required savings rate.

    Determines if current savings trajectory will meet retirement income goals.
    """

    years_to_retirement = retirement_age - current_age

    if years_to_retirement <= 0:
        raise HTTPException(status_code=400, detail="Retirement age must be after current age")

    # Calculate future value of current savings
    fv_current_savings = current_savings * ((1 + expected_return) ** years_to_retirement)

    # Calculate future value of monthly contributions (annuity)
    monthly_rate = expected_return / 12
    months = years_to_retirement * 12
    fv_contributions = (
        monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        if monthly_rate > 0 else monthly_contribution * months
    )

    projected_retirement_pot = fv_current_savings + fv_contributions

    # Calculate required pot for desired income (4% withdrawal rate)
    required_pot = desired_retirement_income / 0.04

    # Calculate shortfall/surplus
    difference = projected_retirement_pot - required_pot

    # Calculate required monthly contribution to meet goal
    if difference < 0:
        required_total_fv = required_pot - fv_current_savings
        required_monthly = (
            required_total_fv * monthly_rate / ((1 + monthly_rate) ** months - 1)
            if monthly_rate > 0 else required_total_fv / months
        )
    else:
        required_monthly = 0

    readiness_score = min(100, (projected_retirement_pot / required_pot * 100)) if required_pot > 0 else 100

    return {
        "years_to_retirement": years_to_retirement,
        "projected_retirement_pot": round(projected_retirement_pot, 2),
        "required_retirement_pot": round(required_pot, 2),
        "difference": round(difference, 2),
        "on_track": difference >= 0,
        "readiness_score": round(readiness_score, 2),
        "current_monthly_contribution": round(monthly_contribution, 2),
        "required_monthly_contribution": round(required_monthly, 2),
        "additional_monthly_needed": round(max(0, required_monthly - monthly_contribution), 2),
        "projected_annual_income": round(projected_retirement_pot * 0.04, 2)
    }