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

        # Convert all Decimal values to float
        dashboard_data = {
            "protection": decimal_to_float(protection_summary),
            "savings": decimal_to_float(savings_summary),
            "pension": decimal_to_float(pension_summary),
            "investment": decimal_to_float(investment_summary),
            "iht": decimal_to_float(iht_summary),
            "overall": decimal_to_float(overall_summary)
        }

        return dashboard_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")