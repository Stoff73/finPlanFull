"""
Monte Carlo Retirement Simulations

Probabilistic retirement outcome modeling:
- Monte Carlo simulation of retirement scenarios
- Success probability calculation
- Risk analysis under market volatility
- Multiple scenario outcomes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import random

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


class MonteCarloRequest(BaseModel):
    current_age: int = Field(..., ge=18, le=75, description="Current age")
    retirement_age: int = Field(..., ge=50, le=75, description="Target retirement age")
    retirement_years: int = Field(30, ge=10, le=50, description="Years in retirement")
    annual_contribution: Optional[float] = Field(0, description="Annual pension contribution")
    annual_expense: Optional[float] = Field(35000, description="Annual expense in retirement")
    mean_return: Optional[float] = Field(7.0, description="Expected mean annual return (%)")
    std_deviation: Optional[float] = Field(15.0, description="Standard deviation of returns (%)")
    simulations: Optional[int] = Field(1000, ge=100, le=10000, description="Number of simulations")
    include_state_pension: Optional[bool] = Field(True, description="Include state pension")


@router.post("/run", response_model=Dict[str, Any])
def run_monte_carlo_simulation(
    request: MonteCarloRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run Monte Carlo simulation for retirement planning.

    Simulates thousands of possible market scenarios to assess
    probability of retirement success.
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

    starting_balance = sum(p.value or 0 for p in pensions)

    if starting_balance == 0 and request.annual_contribution == 0:
        raise HTTPException(
            status_code=400,
            detail="Starting balance and annual contribution cannot both be zero"
        )

    # Parameters
    years_to_retirement = request.retirement_age - request.current_age
    mean_return = request.mean_return / 100
    std_dev = request.std_deviation / 100
    state_pension = 11502 if request.include_state_pension else 0

    # Run simulations
    simulation_results = []
    success_count = 0

    for sim in range(request.simulations):
        balance = starting_balance

        # Accumulation phase
        for year in range(years_to_retirement):
            # Add contribution
            balance += request.annual_contribution

            # Random return (normal distribution)
            annual_return = random.gauss(mean_return, std_dev)
            balance *= (1 + annual_return)

        # Decumulation phase
        final_balance = balance
        success = True

        for year in range(request.retirement_years):
            # Withdraw expenses (minus state pension)
            withdrawal = max(0, request.annual_expense - state_pension)
            balance -= withdrawal

            if balance < 0:
                success = False
                break

            # Random return
            annual_return = random.gauss(mean_return, std_dev)
            balance *= (1 + annual_return)

        if success:
            success_count += 1

        simulation_results.append({
            "simulation": sim + 1,
            "final_balance_at_retirement": round(final_balance, 2),
            "ending_balance": round(max(0, balance), 2),
            "success": success
        })

    # Calculate statistics
    success_rate = (success_count / request.simulations) * 100

    final_balances = [s["final_balance_at_retirement"] for s in simulation_results]
    ending_balances = [s["ending_balance"] for s in simulation_results]

    # Sort for percentile calculations
    final_balances_sorted = sorted(final_balances)
    ending_balances_sorted = sorted(ending_balances)

    def percentile(data, p):
        index = int(len(data) * p / 100)
        return data[min(index, len(data) - 1)]

    statistics = {
        "success_rate": round(success_rate, 1),
        "total_simulations": request.simulations,
        "successful_simulations": success_count,
        "failed_simulations": request.simulations - success_count,
        "balance_at_retirement": {
            "10th_percentile": round(percentile(final_balances_sorted, 10), 2),
            "25th_percentile": round(percentile(final_balances_sorted, 25), 2),
            "median": round(percentile(final_balances_sorted, 50), 2),
            "75th_percentile": round(percentile(final_balances_sorted, 75), 2),
            "90th_percentile": round(percentile(final_balances_sorted, 90), 2),
        },
        "ending_balance": {
            "10th_percentile": round(percentile(ending_balances_sorted, 10), 2),
            "25th_percentile": round(percentile(ending_balances_sorted, 25), 2),
            "median": round(percentile(ending_balances_sorted, 50), 2),
            "75th_percentile": round(percentile(ending_balances_sorted, 75), 2),
            "90th_percentile": round(percentile(ending_balances_sorted, 90), 2),
        }
    }

    # Interpretation
    if success_rate >= 90:
        confidence = "very_high"
        message = f"Excellent! {success_rate:.0f}% success rate means you have very high confidence in your retirement plan."
    elif success_rate >= 75:
        confidence = "high"
        message = f"Good! {success_rate:.0f}% success rate means you have high confidence, but there's room for improvement."
    elif success_rate >= 60:
        confidence = "moderate"
        message = f"{success_rate:.0f}% success rate is moderate. Consider increasing contributions or reducing expenses."
    elif success_rate >= 40:
        confidence = "low"
        message = f"{success_rate:.0f}% success rate is low. Your retirement plan needs significant improvements."
    else:
        confidence = "very_low"
        message = f"Only {success_rate:.0f}% success rate. Your current plan is unlikely to support your retirement goals."

    # Recommendations
    recommendations = []

    if success_rate < 75:
        recommendations.append({
            "priority": "high",
            "category": "contributions",
            "message": f"Consider increasing annual contributions. Even £100/month more can significantly improve success rate."
        })

    if success_rate < 60:
        recommendations.append({
            "priority": "high",
            "category": "expenses",
            "message": f"Review retirement expenses of £{request.annual_expense:,.0f}. Reducing by 10-20% would improve outcomes."
        })

    if success_rate >= 90:
        recommendations.append({
            "priority": "low",
            "category": "optimization",
            "message": "Your plan looks strong! Consider tax optimization strategies or charitable giving."
        })

    if request.retirement_years > 25 and success_rate < 80:
        recommendations.append({
            "priority": "medium",
            "category": "longevity",
            "message": f"Planning for {request.retirement_years} years is prudent for longevity, but requires more savings."
        })

    return {
        "statistics": statistics,
        "confidence": confidence,
        "message": message,
        "recommendations": recommendations,
        "sample_scenarios": simulation_results[:10],  # Return first 10 as examples
        "assumptions": {
            "starting_balance": starting_balance,
            "current_age": request.current_age,
            "retirement_age": request.retirement_age,
            "retirement_years": request.retirement_years,
            "annual_contribution": request.annual_contribution,
            "annual_expense": request.annual_expense,
            "mean_return": request.mean_return,
            "std_deviation": request.std_deviation,
            "state_pension": state_pension,
            "simulations": request.simulations
        },
        "calculated_at": datetime.utcnow().isoformat()
    }


@router.get("/quick", response_model=Dict[str, Any])
def get_quick_monte_carlo(
    simulations: int = 1000,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run quick Monte Carlo simulation with default assumptions.

    Uses user's current pension value and standard retirement assumptions.
    """

    # Get current pension value
    pensions = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'retirement',
        Product.status == 'active'
    ).all()

    starting_balance = sum(p.value or 0 for p in pensions)

    if starting_balance == 0:
        return {
            "message": "No pension balance found. Add pensions to run simulation.",
            "success_rate": 0
        }

    # Get user age from profile
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

    # Run simulation with defaults
    years_to_retirement = max(0, retirement_age - current_age)
    retirement_years = 30
    annual_expense = 35000
    state_pension = 11502
    mean_return = 0.07
    std_dev = 0.15

    success_count = 0

    for _ in range(simulations):
        balance = starting_balance

        # Accumulation
        for _ in range(years_to_retirement):
            balance += total_contributions
            annual_return = random.gauss(mean_return, std_dev)
            balance *= (1 + annual_return)

        # Decumulation
        success = True
        for _ in range(retirement_years):
            withdrawal = max(0, annual_expense - state_pension)
            balance -= withdrawal

            if balance < 0:
                success = False
                break

            annual_return = random.gauss(mean_return, std_dev)
            balance *= (1 + annual_return)

        if success:
            success_count += 1

    success_rate = (success_count / simulations) * 100

    return {
        "success_rate": round(success_rate, 1),
        "simulations": simulations,
        "current_pension_value": starting_balance,
        "years_to_retirement": years_to_retirement,
        "message": f"{success_rate:.0f}% probability of successful retirement based on {simulations} simulations."
    }