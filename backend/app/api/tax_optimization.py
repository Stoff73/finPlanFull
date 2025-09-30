"""API endpoints for UK tax optimization recommendations."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.api.auth.auth import get_current_user
from app.models.user import User
from app.db.base import get_db
from app.services.tax_optimizer import TaxOptimizer, TaxYear

router = APIRouter(prefix="/api/tax-optimization", tags=["tax-optimization"])


class TaxPositionRequest(BaseModel):
    """Request model for current tax position analysis."""
    gross_income: float = Field(..., gt=0, description="Total gross income")
    employment_income: float = Field(0, ge=0, description="Employment income (salary)")
    self_employment_income: float = Field(0, ge=0, description="Self-employment income")
    dividend_income: float = Field(0, ge=0, description="Dividend income")
    rental_income: float = Field(0, ge=0, description="Rental income")
    pension_contribution: float = Field(0, ge=0, description="Current pension contributions")
    employer_pension_contribution: float = Field(0, ge=0, description="Employer pension contributions")
    gift_aid_donations: float = Field(0, ge=0, description="Gift Aid charitable donations")


class PensionOptimizationRequest(BaseModel):
    """Request model for pension contribution optimization."""
    gross_income: float = Field(..., gt=0, description="Total gross income")
    current_pension_contribution: float = Field(0, ge=0, description="Current annual pension contribution")
    employer_pension_contribution: float = Field(0, ge=0, description="Employer contribution")
    available_carry_forward: float = Field(0, ge=0, description="Available carry-forward from previous years")


class SalaryDividendRequest(BaseModel):
    """Request model for salary/dividend split optimization."""
    total_remuneration: float = Field(..., gt=0, description="Total remuneration available")
    is_director: bool = Field(True, description="Is company director/shareholder")
    company_profit: Optional[float] = Field(None, description="Company profit before director remuneration")


class ISAOptimizationRequest(BaseModel):
    """Request model for ISA vs taxable investment comparison."""
    available_capital: float = Field(..., gt=0, description="Capital available to invest")
    expected_annual_return: float = Field(0.06, ge=-0.5, le=0.5, description="Expected annual return")
    investment_years: int = Field(10, ge=1, le=50, description="Investment time horizon")
    current_income: float = Field(..., ge=0, description="Current annual income")
    existing_isa_balance: float = Field(0, ge=0, description="Existing ISA balance")


class ComprehensiveOptimizationRequest(BaseModel):
    """Request model for comprehensive tax optimization report."""
    gross_income: float = Field(..., gt=0)
    employment_income: float = Field(..., ge=0)
    dividend_income: float = Field(0, ge=0)
    pension_contribution: float = Field(0, ge=0)
    available_capital: float = Field(0, ge=0)
    is_director: bool = Field(False)


@router.post("/analyze-position", response_model=Dict[str, Any])
async def analyze_tax_position(
    request: TaxPositionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze current tax position and calculate breakdown.

    Returns detailed breakdown of income tax, NI, and dividend tax.
    """
    optimizer = TaxOptimizer()

    # Calculate income tax
    income_tax = optimizer.calculate_income_tax(
        total_income=request.gross_income,
        pension_contributions=request.pension_contribution,
        gift_aid_donations=request.gift_aid_donations
    )

    # Calculate National Insurance
    ni = optimizer.calculate_national_insurance(
        employment_income=request.employment_income,
        is_self_employed=request.self_employment_income > 0
    )

    # Calculate dividend tax
    dividend_tax = optimizer.calculate_dividend_tax(
        dividend_income=request.dividend_income,
        other_income=request.employment_income + request.self_employment_income
    )

    # Calculate total and effective rate
    total_tax = income_tax["total_tax"] + ni["total_ni"] + dividend_tax["total_dividend_tax"]
    effective_rate = (total_tax / request.gross_income * 100) if request.gross_income > 0 else 0

    return {
        "income_breakdown": {
            "gross_income": request.gross_income,
            "employment_income": request.employment_income,
            "self_employment_income": request.self_employment_income,
            "dividend_income": request.dividend_income,
            "rental_income": request.rental_income
        },
        "income_tax": income_tax,
        "national_insurance": ni,
        "dividend_tax": dividend_tax,
        "summary": {
            "total_tax": round(total_tax, 2),
            "total_ni": round(ni["total_ni"], 2),
            "net_income": round(request.gross_income - total_tax, 2),
            "effective_tax_rate": round(effective_rate, 2),
            "marginal_tax_rate": _determine_marginal_rate(request.gross_income, optimizer)
        }
    }


@router.post("/optimize-pension", response_model=Dict[str, Any])
async def optimize_pension_contributions(
    request: PensionOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pension contribution optimization recommendations.

    Analyzes:
    - Annual Allowance usage
    - Tapered Annual Allowance for high earners
    - Tax relief at marginal rate
    - National Insurance savings
    """
    optimizer = TaxOptimizer()

    optimization = optimizer.optimize_pension_contributions(
        gross_income=request.gross_income,
        current_pension_contribution=request.current_pension_contribution,
        employer_pension_contribution=request.employer_pension_contribution
    )

    # Add carry-forward analysis if available
    if request.available_carry_forward > 0:
        optimization["carry_forward_available"] = request.available_carry_forward
        optimization["reasoning"].append(
            f"You have £{request.available_carry_forward:,.0f} carry-forward available from previous years"
        )

    return optimization


@router.post("/optimize-salary-dividend", response_model=Dict[str, Any])
async def optimize_salary_dividend_split(
    request: SalaryDividendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Optimize salary/dividend split for company directors.

    Compares scenarios:
    - All salary
    - Salary to NI threshold + dividends
    - Salary to basic rate + dividends
    """
    optimizer = TaxOptimizer()

    optimization = optimizer.optimize_salary_dividend_split(
        total_remuneration=request.total_remuneration,
        is_director=request.is_director
    )

    # Add context
    optimization["notes"] = [
        "Assumes you are a director of your own limited company",
        "Dividend tax applies to dividends received after using dividend allowance",
        "Consider employer NI (13.8%) saved by taking dividends instead of salary",
        "Must maintain minimum salary for state pension qualifying years (£6,396 for 2024/25)"
    ]

    return optimization


@router.post("/optimize-isa-allocation", response_model=Dict[str, Any])
async def optimize_isa_allocation(
    request: ISAOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare ISA vs taxable investment accounts.

    Analyzes:
    - Tax-free growth in ISA
    - CGT and dividend tax in taxable accounts
    - Long-term value comparison
    """
    optimizer = TaxOptimizer()

    optimization = optimizer.optimize_isa_vs_taxable(
        available_capital=request.available_capital,
        expected_annual_return=request.expected_annual_return,
        investment_years=request.investment_years,
        current_income=request.current_income
    )

    # Add ISA types information
    optimization["isa_types"] = {
        "cash_isa": "Savings with tax-free interest",
        "stocks_shares_isa": "Investments with tax-free growth and dividends",
        "lifetime_isa": "£1 government bonus for every £4 saved (max £1,000/year, age 18-39)",
        "innovative_finance_isa": "Peer-to-peer lending with tax-free returns"
    }

    optimization["total_allowance_2024_25"] = 20000

    if request.existing_isa_balance > 0:
        optimization["remaining_allowance"] = max(0, 20000 - request.available_capital)

    return optimization


@router.post("/comprehensive-report", response_model=Dict[str, Any])
async def generate_comprehensive_report(
    request: ComprehensiveOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive tax optimization report with all recommendations.

    Provides prioritized list of tax-saving opportunities across:
    - Pension contributions
    - ISA utilization
    - Salary/dividend optimization
    - Tax-efficient investment allocation
    """
    optimizer = TaxOptimizer()

    report = optimizer.generate_comprehensive_report(
        gross_income=request.gross_income,
        employment_income=request.employment_income,
        dividend_income=request.dividend_income,
        pension_contribution=request.pension_contribution,
        available_capital=request.available_capital
    )

    # Add additional context
    report["tax_year"] = "2024/25"
    report["key_thresholds"] = {
        "personal_allowance": 12570,
        "basic_rate_threshold": 50270,
        "higher_rate_threshold": 125140,
        "ni_threshold": 12570,
        "dividend_allowance": 500,
        "cgt_allowance": 3000,
        "isa_allowance": 20000,
        "pension_annual_allowance": 60000
    }

    # Add salary/dividend optimization if director
    if request.is_director:
        salary_div_opt = optimizer.optimize_salary_dividend_split(
            total_remuneration=request.employment_income,
            is_director=True
        )
        if salary_div_opt["potential_saving"] > 0:
            report["recommendations"].append({
                "category": "Salary/Dividend Split",
                "priority": "High",
                "saving": salary_div_opt["potential_saving"],
                "action": f"Optimize to: Salary £{salary_div_opt['scenarios'][1]['salary']:,.0f}, Dividends £{salary_div_opt['scenarios'][1]['dividends']:,.0f}",
                "details": [f"Recommended: {salary_div_opt['recommended']}"]
            })
            report["potential_savings"] += salary_div_opt["potential_saving"]

    return report


@router.get("/tax-calculators", response_model=Dict[str, Any])
async def get_tax_calculators(
    income: float = Query(..., ge=0, description="Annual income"),
    current_user: User = Depends(get_current_user)
):
    """
    Quick tax calculators for various income levels.

    Provides instant calculations without detailed analysis.
    """
    optimizer = TaxOptimizer()

    income_tax = optimizer.calculate_income_tax(income, 0)
    ni = optimizer.calculate_national_insurance(income)

    return {
        "income": income,
        "income_tax": income_tax["total_tax"],
        "national_insurance": ni["total_ni"],
        "total_deductions": income_tax["total_tax"] + ni["total_ni"],
        "net_income": income - income_tax["total_tax"] - ni["total_ni"],
        "effective_rate": ((income_tax["total_tax"] + ni["total_ni"]) / income * 100) if income > 0 else 0,
        "marginal_rate": _determine_marginal_rate(income, optimizer)
    }


def _determine_marginal_rate(income: float, optimizer: TaxOptimizer) -> float:
    """Determine marginal tax rate for given income."""
    if income <= optimizer.thresholds.personal_allowance:
        return 0.0
    elif income <= optimizer.thresholds.basic_rate_threshold:
        return 20.0 + 8.0  # Income tax + NI
    elif income <= optimizer.thresholds.personal_allowance_taper_start:
        return 40.0 + 2.0  # Income tax + NI above UEL
    elif income <= optimizer.thresholds.higher_rate_threshold:
        return 60.0 + 2.0  # 40% tax + 20% PA taper + 2% NI
    else:
        return 45.0 + 2.0  # Additional rate + NI