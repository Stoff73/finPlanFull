"""Protection Module API Router

Handles protection/insurance planning functionality including:
- Dashboard metrics aggregation
- Summary data for main dashboard
- Coverage analysis
- Premium tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


@router.get("/dashboard")
async def get_protection_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive protection module dashboard data

    Returns:
        - Total coverage amount
        - Active policies count
        - Total monthly premiums
        - Coverage breakdown by type
        - Recent policy changes
    """
    # Query all protection products for this user
    protection_products = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == "protection",
        Product.status == "active"
    ).all()

    # Calculate total coverage
    total_coverage = sum(
        float(product.value or 0)
        for product in protection_products
    )

    # Calculate total premiums (assuming extra_metadata contains premium info)
    total_premiums = 0.0
    for product in protection_products:
        if product.extra_metadata and isinstance(product.extra_metadata, dict):
            premium = product.extra_metadata.get("monthly_premium", 0)
            total_premiums += float(premium)

    # Coverage breakdown by product type
    coverage_by_type = {}
    for product in protection_products:
        product_type = product.product_type or "other"
        if product_type not in coverage_by_type:
            coverage_by_type[product_type] = {
                "count": 0,
                "total_coverage": 0.0,
                "total_premium": 0.0
            }

        coverage_by_type[product_type]["count"] += 1
        coverage_by_type[product_type]["total_coverage"] += float(product.value or 0)

        if product.extra_metadata and isinstance(product.extra_metadata, dict):
            premium = product.extra_metadata.get("monthly_premium", 0)
            coverage_by_type[product_type]["total_premium"] += float(premium)

    # Calculate coverage adequacy (placeholder - would need user income data)
    # Rule of thumb: 10x annual income for life insurance
    coverage_adequacy = "adequate"  # Would calculate based on user data
    coverage_gap = 0  # Would calculate: recommended_coverage - total_coverage

    # Calculate coverage adequacy percentage (0-100+)
    # Simplified calculation - in production would use actual needs analysis
    recommended_coverage = 100000  # Placeholder - would calculate from user income/needs
    coverage_adequacy_pct = (total_coverage / recommended_coverage * 100) if recommended_coverage > 0 else 0

    return {
        "metrics": {
            "total_coverage": total_coverage,
            "active_policies": len(protection_products),
            "coverage_gap": coverage_gap,
            "monthly_premiums": total_premiums
        },
        "products": [
            {
                "id": p.id,
                "product_name": p.name,
                "provider": p.provider or "Unknown Provider",
                "product_value": float(p.value or 0),
                "contribution": p.extra_metadata.get("monthly_premium", 0) if p.extra_metadata else 0,
                "product_category": p.product_type or "other",
                "start_date": p.start_date.isoformat() if p.start_date else datetime.now().isoformat()
            }
            for p in protection_products
        ],
        "analytics": {
            "coverage_adequacy": coverage_adequacy_pct,
            "premium_trend": []  # Would calculate historical premium data
        }
    }


@router.get("/summary")
async def get_protection_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get quick protection summary for main dashboard card

    Returns:
        - Total coverage
        - Policy count
        - Status indicator (adequate, attention_needed, insufficient)
        - Next premium due date
    """
    # Query active protection products
    protection_products = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == "protection",
        Product.status == "active"
    ).all()

    # Calculate totals
    total_coverage = sum(float(p.value or 0) for p in protection_products)
    total_premium = 0.0

    for product in protection_products:
        if product.extra_metadata and isinstance(product.extra_metadata, dict):
            premium = product.extra_metadata.get("monthly_premium", 0)
            total_premium += float(premium)

    # Determine status (simplified logic - would be more sophisticated)
    status = "adequate"
    if total_coverage == 0:
        status = "insufficient"
    elif total_coverage < 100000:  # Example threshold
        status = "attention_needed"

    # Calculate coverage gap (placeholder)
    coverage_gap = 0  # Would calculate based on needs analysis

    return {
        "total_coverage": total_coverage,
        "policy_count": len(protection_products),
        "monthly_premium": total_premium,
        "status": status,
        "coverage_gap": coverage_gap,
        "message": _get_status_message(status, total_coverage, coverage_gap)
    }


def _get_status_message(status: str, coverage: float, gap: float) -> str:
    """Generate user-friendly status message"""
    if status == "insufficient":
        return "You don't have any active protection policies. Consider reviewing your protection needs."
    elif status == "attention_needed":
        if gap > 0:
            return f"Your coverage may be insufficient. Consider increasing protection by £{gap:,.0f}."
        else:
            return "Your protection coverage is below recommended levels. Review your needs."
    else:
        return f"You have £{coverage:,.0f} in total coverage across your policies."