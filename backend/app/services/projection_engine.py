"""Financial projection engine for multi-year forecasting."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, date
from enum import Enum


class ScenarioType(str, Enum):
    """Projection scenario types."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    OPTIMISTIC = "optimistic"


@dataclass
class ProjectionScenario:
    """Configuration for a projection scenario."""
    name: str
    income_growth_rate: float
    expense_growth_rate: float
    asset_return_rate: float
    inflation_rate: float


class ProjectionEngine:
    """Engine for creating multi-year financial projections."""

    SCENARIO_DEFAULTS = {
        ScenarioType.CONSERVATIVE: ProjectionScenario(
            name="Conservative",
            income_growth_rate=0.02,
            expense_growth_rate=0.03,
            asset_return_rate=0.04,
            inflation_rate=0.025
        ),
        ScenarioType.MODERATE: ProjectionScenario(
            name="Moderate",
            income_growth_rate=0.03,
            expense_growth_rate=0.025,
            asset_return_rate=0.06,
            inflation_rate=0.025
        ),
        ScenarioType.OPTIMISTIC: ProjectionScenario(
            name="Optimistic",
            income_growth_rate=0.05,
            expense_growth_rate=0.02,
            asset_return_rate=0.08,
            inflation_rate=0.025
        )
    }

    def __init__(self, scenario: ScenarioType = ScenarioType.MODERATE):
        """Initialize projection engine with scenario."""
        self.scenario = self.SCENARIO_DEFAULTS[scenario]

    def project_wealth(
        self,
        initial_wealth: float,
        annual_savings: float,
        years: int,
        return_rate: Optional[float] = None
    ) -> List[Dict[str, float]]:
        """
        Project wealth accumulation over time.

        Args:
            initial_wealth: Starting wealth
            annual_savings: Annual savings amount
            years: Number of years to project
            return_rate: Override default return rate

        Returns:
            List of yearly projections with wealth, contributions, returns
        """
        rate = return_rate or self.scenario.asset_return_rate
        projections = []
        current_wealth = initial_wealth

        for year in range(1, years + 1):
            # Calculate investment return
            investment_return = current_wealth * rate

            # Add savings
            current_wealth += investment_return + annual_savings

            # Calculate real (inflation-adjusted) wealth
            real_wealth = current_wealth / ((1 + self.scenario.inflation_rate) ** year)

            projections.append({
                "year": year,
                "wealth": round(current_wealth, 2),
                "real_wealth": round(real_wealth, 2),
                "investment_return": round(investment_return, 2),
                "annual_savings": round(annual_savings, 2),
                "cumulative_contributions": round(initial_wealth + (annual_savings * year), 2)
            })

        return projections

    def project_cash_flow(
        self,
        initial_income: float,
        initial_expenses: float,
        years: int,
        income_growth: Optional[float] = None,
        expense_growth: Optional[float] = None
    ) -> List[Dict[str, float]]:
        """
        Project cash flow over time.

        Args:
            initial_income: Starting annual income
            initial_expenses: Starting annual expenses
            years: Number of years to project
            income_growth: Override default income growth rate
            expense_growth: Override default expense growth rate

        Returns:
            List of yearly cash flow projections
        """
        inc_rate = income_growth or self.scenario.income_growth_rate
        exp_rate = expense_growth or self.scenario.expense_growth_rate

        projections = []
        income = initial_income
        expenses = initial_expenses

        for year in range(1, years + 1):
            # Apply growth rates
            income *= (1 + inc_rate)
            expenses *= (1 + exp_rate)

            # Calculate cash flow
            net_cash_flow = income - expenses
            savings_rate = (net_cash_flow / income * 100) if income > 0 else 0

            projections.append({
                "year": year,
                "income": round(income, 2),
                "expenses": round(expenses, 2),
                "net_cash_flow": round(net_cash_flow, 2),
                "savings_rate": round(savings_rate, 2)
            })

        return projections


def create_multi_year_projection(
    current_assets: float,
    current_liabilities: float,
    annual_income: float,
    annual_expenses: float,
    years: int,
    scenario: ScenarioType = ScenarioType.MODERATE,
    **kwargs
) -> Dict:
    """
    Create a comprehensive multi-year financial projection.

    Args:
        current_assets: Current total assets
        current_liabilities: Current total liabilities
        annual_income: Annual income
        annual_expenses: Annual expenses
        years: Years to project
        scenario: Projection scenario (conservative, moderate, optimistic)
        **kwargs: Additional parameters (growth rates, planned events, etc.)

    Returns:
        Dictionary containing complete projection results
    """
    engine = ProjectionEngine(scenario)

    # Calculate initial net worth
    initial_net_worth = current_assets - current_liabilities

    # Calculate annual savings
    annual_savings = annual_income - annual_expenses

    # Project wealth
    wealth_projection = engine.project_wealth(
        initial_wealth=initial_net_worth,
        annual_savings=annual_savings,
        years=years,
        return_rate=kwargs.get("asset_return_rate")
    )

    # Project cash flow
    cash_flow_projection = engine.project_cash_flow(
        initial_income=annual_income,
        initial_expenses=annual_expenses,
        years=years,
        income_growth=kwargs.get("income_growth_rate"),
        expense_growth=kwargs.get("expense_growth_rate")
    )

    # Combine projections
    combined_projection = []
    for i in range(years):
        combined_projection.append({
            **wealth_projection[i],
            **cash_flow_projection[i]
        })

    # Calculate summary
    final_year = combined_projection[-1]
    total_growth = final_year["wealth"] - initial_net_worth
    growth_percentage = (total_growth / initial_net_worth * 100) if initial_net_worth != 0 else 0

    summary = {
        "scenario": scenario.value,
        "projection_years": years,
        "initial_net_worth": round(initial_net_worth, 2),
        "final_net_worth": round(final_year["wealth"], 2),
        "total_growth": round(total_growth, 2),
        "growth_percentage": round(growth_percentage, 2),
        "average_savings_rate": round(
            sum(p["savings_rate"] for p in cash_flow_projection) / years, 2
        ),
        "total_contributions": round(initial_net_worth + (annual_savings * years), 2),
        "total_investment_returns": round(
            final_year["wealth"] - initial_net_worth - (annual_savings * years), 2
        )
    }

    return {
        "projection": combined_projection,
        "summary": summary,
        "scenario_details": {
            "name": engine.scenario.name,
            "income_growth": engine.scenario.income_growth_rate,
            "expense_growth": engine.scenario.expense_growth_rate,
            "asset_return": engine.scenario.asset_return_rate,
            "inflation": engine.scenario.inflation_rate
        }
    }