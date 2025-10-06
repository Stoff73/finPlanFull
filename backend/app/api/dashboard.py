"""
Main Dashboard API endpoints.

Aggregates data from all 5 modules for the main dashboard overview.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from decimal import Decimal
from collections import defaultdict

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def decimal_to_float(value: Any) -> Any:
    """Convert Decimal values to float for JSON serialization."""
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, dict):
        return {k: decimal_to_float(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [decimal_to_float(item) for item in value]
    return value


def get_currency_symbol(currency: str) -> str:
    """Get currency symbol for a given currency code."""
    symbols = {
        'GBP': '£',
        'ZAR': 'R',
        'EUR': '€',
        'USD': '$',
    }
    return symbols.get(currency, currency)


def format_currency_value(amount: float, currency: str) -> str:
    """Format amount with correct currency symbol."""
    symbol = get_currency_symbol(currency)
    return f"{symbol}{amount:,.0f}"


def aggregate_by_currency(products: List[Product]) -> Dict[str, float]:
    """Aggregate product values grouped by currency."""
    totals = defaultdict(float)
    for p in products:
        currency = p.currency or 'GBP'
        totals[currency] += (p.current_value or 0)
    return dict(totals)


def format_multi_currency(currency_totals: Dict[str, float]) -> str:
    """Format multiple currency totals for display."""
    if not currency_totals:
        return "£0"

    # Sort by total value (assuming rough conversions for display order)
    sorted_currencies = sorted(currency_totals.items(), key=lambda x: x[1], reverse=True)

    # If only one currency, return simple format
    if len(sorted_currencies) == 1:
        currency, amount = sorted_currencies[0]
        return format_currency_value(amount, currency)

    # For multiple currencies, show the primary one with indicator
    parts = [format_currency_value(amount, curr) for curr, amount in sorted_currencies]
    return " + ".join(parts)


@router.get("/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get complete dashboard overview with data from all 5 modules.

    Returns:
        Dict containing:
        - protection: Protection module summary
        - savings: Savings module summary
        - pension: Pension module summary
        - investment: Investment module summary
        - iht: IHT module summary
        - overall: Overall financial summary
    """
    try:
        # Get products by module
        protection_products = db.query(Product).filter(
            Product.user_id == current_user.id,
            Product.module == "protection"
        ).all()

        savings_products = db.query(Product).filter(
            Product.user_id == current_user.id,
            Product.module == "savings"
        ).all()

        pension_products = db.query(Product).filter(
            Product.user_id == current_user.id,
            Product.module == "retirement"
        ).all()

        investment_products = db.query(Product).filter(
            Product.user_id == current_user.id,
            Product.module == "investment"
        ).all()

        # Aggregate by currency for each module
        protection_by_currency = aggregate_by_currency(
            [p for p in protection_products if p.product_type == "protection"]
        )
        savings_by_currency = aggregate_by_currency(savings_products)
        pension_by_currency = aggregate_by_currency(pension_products)
        investment_by_currency = aggregate_by_currency(investment_products)

        # Calculate summaries with formatted currency values
        protection_summary = {
            "total_coverage": sum(protection_by_currency.values()),
            "total_coverage_formatted": format_multi_currency(protection_by_currency),
            "active_policies": len(protection_products),
            "monthly_premiums": 0,  # Calculate from annual_charge
        }

        savings_summary = {
            "total_balance": sum(savings_by_currency.values()),
            "total_balance_formatted": format_multi_currency(savings_by_currency),
            "accounts": len(savings_products),
            "monthly_savings": 0,  # Not tracked in current model
        }

        pension_summary = {
            "total_value": sum(pension_by_currency.values()),
            "total_value_formatted": format_multi_currency(pension_by_currency),
            "schemes": len(pension_products),
            "monthly_contributions": 0,  # Not tracked in current model
        }

        # For investments, also handle initial investment separately
        investment_initial_by_currency = defaultdict(float)
        for p in investment_products:
            currency = p.currency or 'GBP'
            investment_initial_by_currency[currency] += (p.initial_investment or 0)

        investment_summary = {
            "total_value": sum(investment_by_currency.values()),
            "total_value_formatted": format_multi_currency(investment_by_currency),
            "holdings": len(investment_products),
            "invested": sum(investment_initial_by_currency.values()),
            "invested_formatted": format_multi_currency(dict(investment_initial_by_currency)),
        }

        # IHT summary (placeholder - requires separate calculation)
        iht_summary = {
            "estate_value": 0,
            "iht_liability": 0,
            "nil_rate_band_used": 0,
        }

        # Overall summary
        total_assets = (
            protection_summary["total_coverage"] +
            savings_summary["total_balance"] +
            pension_summary["total_value"] +
            investment_summary["total_value"]
        )

        overall_summary = {
            "total_assets": total_assets,
            "total_products": len(protection_products) + len(savings_products) + len(pension_products) + len(investment_products),
            "monthly_outgoings": protection_summary["monthly_premiums"],
            "monthly_contributions": savings_summary["monthly_savings"] + pension_summary["monthly_contributions"],
        }

        # Convert to frontend-expected format
        dashboard_data = {
            "modules": [
                {
                    "module": "protection",
                    "headlineMetric": {
                        "label": "Total Coverage",
                        "value": protection_summary['total_coverage_formatted']
                    },
                    "supportingMetrics": [
                        {"label": "Active Policies", "value": str(protection_summary['active_policies'])},
                        {"label": "Monthly Premiums", "value": format_currency_value(protection_summary['monthly_premiums'], 'GBP')}
                    ],
                    "status": "good" if protection_summary['active_policies'] > 0 else "attention",
                    "statusMessage": "Coverage is active" if protection_summary['active_policies'] > 0 else "No active policies"
                },
                {
                    "module": "savings",
                    "headlineMetric": {
                        "label": "Total Savings",
                        "value": savings_summary['total_balance_formatted']
                    },
                    "supportingMetrics": [
                        {"label": "Accounts", "value": str(savings_summary['accounts'])},
                        {"label": "Monthly Savings", "value": format_currency_value(savings_summary['monthly_savings'], 'GBP')}
                    ],
                    "status": "good" if savings_summary['total_balance'] > 0 else "attention",
                    "statusMessage": "Savings on track" if savings_summary['total_balance'] > 0 else "Start saving"
                },
                {
                    "module": "investment",
                    "headlineMetric": {
                        "label": "Portfolio Value",
                        "value": investment_summary['total_value_formatted']
                    },
                    "supportingMetrics": [
                        {"label": "Holdings", "value": str(investment_summary['holdings'])},
                        {"label": "Invested", "value": investment_summary['invested_formatted']}
                    ],
                    "status": "good" if investment_summary['total_value'] > 0 else "attention",
                    "statusMessage": "Portfolio active" if investment_summary['total_value'] > 0 else "Start investing"
                },
                {
                    "module": "retirement",
                    "headlineMetric": {
                        "label": "Pension Value",
                        "value": pension_summary['total_value_formatted']
                    },
                    "supportingMetrics": [
                        {"label": "Schemes", "value": str(pension_summary['schemes'])},
                        {"label": "Monthly Contributions", "value": format_currency_value(pension_summary['monthly_contributions'], 'GBP')}
                    ],
                    "status": "good" if pension_summary['total_value'] > 0 else "attention",
                    "statusMessage": "Retirement planning active" if pension_summary['total_value'] > 0 else "Start pension planning"
                },
                {
                    "module": "iht",
                    "headlineMetric": {
                        "label": "Estate Value",
                        "value": format_currency_value(iht_summary['estate_value'], 'GBP')
                    },
                    "supportingMetrics": [
                        {"label": "IHT Liability", "value": format_currency_value(iht_summary['iht_liability'], 'GBP')},
                        {"label": "Nil Rate Band Used", "value": f"{iht_summary['nil_rate_band_used']:.0%}"}
                    ],
                    "status": "good" if iht_summary['iht_liability'] == 0 else "attention",
                    "statusMessage": "No IHT liability" if iht_summary['iht_liability'] == 0 else "Consider IHT planning"
                }
            ],
            "overallStatus": {
                "netWorth": decimal_to_float(total_assets),
                "monthlyIncome": 0,  # TODO: Add income tracking
                "monthlyExpenses": decimal_to_float(overall_summary['monthly_outgoings']),
                "monthlySavings": decimal_to_float(overall_summary['monthly_contributions'])
            }
        }

        return dashboard_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")