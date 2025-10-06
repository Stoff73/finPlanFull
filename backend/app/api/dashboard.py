"""
Main Dashboard API endpoints.

Aggregates data from all 5 modules for the main dashboard overview.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from decimal import Decimal

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

        # Calculate summaries
        protection_summary = {
            "total_coverage": sum(p.product_value or 0 for p in protection_products if p.product_category == "life"),
            "active_policies": len(protection_products),
            "monthly_premiums": sum(p.contribution or 0 for p in protection_products),
        }

        savings_summary = {
            "total_balance": sum(p.product_value or 0 for p in savings_products),
            "accounts": len(savings_products),
            "monthly_savings": sum(p.contribution or 0 for p in savings_products),
        }

        pension_summary = {
            "total_value": sum(p.product_value or 0 for p in pension_products),
            "schemes": len(pension_products),
            "monthly_contributions": sum(p.contribution or 0 for p in pension_products),
        }

        investment_summary = {
            "total_value": sum(p.product_value or 0 for p in investment_products),
            "holdings": len(investment_products),
            "invested": sum(p.product_value or 0 for p in investment_products),
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
                        "value": f"£{protection_summary['total_coverage']:,.0f}"
                    },
                    "supportingMetrics": [
                        {"label": "Active Policies", "value": str(protection_summary['active_policies'])},
                        {"label": "Monthly Premiums", "value": f"£{protection_summary['monthly_premiums']:,.2f}"}
                    ],
                    "status": "good" if protection_summary['active_policies'] > 0 else "attention",
                    "statusMessage": "Coverage is active" if protection_summary['active_policies'] > 0 else "No active policies"
                },
                {
                    "module": "savings",
                    "headlineMetric": {
                        "label": "Total Savings",
                        "value": f"£{savings_summary['total_balance']:,.0f}"
                    },
                    "supportingMetrics": [
                        {"label": "Accounts", "value": str(savings_summary['accounts'])},
                        {"label": "Monthly Savings", "value": f"£{savings_summary['monthly_savings']:,.2f}"}
                    ],
                    "status": "good" if savings_summary['total_balance'] > 0 else "attention",
                    "statusMessage": "Savings on track" if savings_summary['total_balance'] > 0 else "Start saving"
                },
                {
                    "module": "investment",
                    "headlineMetric": {
                        "label": "Portfolio Value",
                        "value": f"£{investment_summary['total_value']:,.0f}"
                    },
                    "supportingMetrics": [
                        {"label": "Holdings", "value": str(investment_summary['holdings'])},
                        {"label": "Invested", "value": f"£{investment_summary['invested']:,.0f}"}
                    ],
                    "status": "good" if investment_summary['total_value'] > 0 else "attention",
                    "statusMessage": "Portfolio active" if investment_summary['total_value'] > 0 else "Start investing"
                },
                {
                    "module": "retirement",
                    "headlineMetric": {
                        "label": "Pension Value",
                        "value": f"£{pension_summary['total_value']:,.0f}"
                    },
                    "supportingMetrics": [
                        {"label": "Schemes", "value": str(pension_summary['schemes'])},
                        {"label": "Monthly Contributions", "value": f"£{pension_summary['monthly_contributions']:,.2f}"}
                    ],
                    "status": "good" if pension_summary['total_value'] > 0 else "attention",
                    "statusMessage": "Retirement planning active" if pension_summary['total_value'] > 0 else "Start pension planning"
                },
                {
                    "module": "iht",
                    "headlineMetric": {
                        "label": "Estate Value",
                        "value": f"£{iht_summary['estate_value']:,.0f}"
                    },
                    "supportingMetrics": [
                        {"label": "IHT Liability", "value": f"£{iht_summary['iht_liability']:,.0f}"},
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