"""Protection Analytics API

Provides detailed analytics for protection planning:
- Coverage analysis
- Premium efficiency metrics
- Coverage trends over time
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


@router.get("")
async def get_protection_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive protection analytics

    Returns:
        - Coverage analysis by type
        - Premium efficiency metrics
        - Coverage trends
        - Recommendations
    """
    # Get all protection products (including archived for historical analysis)
    all_products = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == "protection"
    ).all()

    active_products = [p for p in all_products if p.status == "active"]

    # Coverage Analysis
    coverage_analysis = _analyze_coverage(active_products)

    # Premium Efficiency
    premium_efficiency = _analyze_premium_efficiency(active_products)

    # Coverage Trends (last 12 months)
    coverage_trends = _analyze_coverage_trends(all_products)

    # Generate recommendations
    recommendations = _generate_recommendations(
        active_products,
        coverage_analysis,
        premium_efficiency
    )

    return {
        "coverage_analysis": coverage_analysis,
        "premium_efficiency": premium_efficiency,
        "coverage_trends": coverage_trends,
        "recommendations": recommendations,
        "last_updated": datetime.utcnow().isoformat()
    }


def _analyze_coverage(products: List[Product]) -> Dict[str, Any]:
    """Analyze coverage breakdown and adequacy"""
    if not products:
        return {
            "total_coverage": 0,
            "coverage_by_type": {},
            "largest_policy": None,
            "policy_count": 0
        }

    total_coverage = sum(float(p.value or 0) for p in products)

    # Coverage by type
    coverage_by_type = defaultdict(lambda: {"coverage": 0, "count": 0, "percentage": 0})

    for product in products:
        product_type = product.product_type or "other"
        coverage_by_type[product_type]["coverage"] += float(product.value or 0)
        coverage_by_type[product_type]["count"] += 1

    # Calculate percentages
    for product_type in coverage_by_type:
        coverage_by_type[product_type]["percentage"] = (
            coverage_by_type[product_type]["coverage"] / total_coverage * 100
            if total_coverage > 0 else 0
        )

    # Find largest policy
    largest_policy = max(products, key=lambda p: float(p.value or 0))

    return {
        "total_coverage": total_coverage,
        "coverage_by_type": dict(coverage_by_type),
        "largest_policy": {
            "name": largest_policy.name,
            "type": largest_policy.product_type,
            "coverage": float(largest_policy.value or 0)
        },
        "policy_count": len(products)
    }


def _analyze_premium_efficiency(products: List[Product]) -> Dict[str, Any]:
    """Analyze premium costs and efficiency"""
    if not products:
        return {
            "total_monthly_premium": 0,
            "total_annual_premium": 0,
            "premium_per_100k_coverage": 0,
            "most_expensive_policy": None
        }

    total_premium = 0.0
    premiums_by_type = defaultdict(float)

    for product in products:
        if product.extra_metadata and isinstance(product.extra_metadata, dict):
            premium = float(product.extra_metadata.get("monthly_premium", 0))
            total_premium += premium

            product_type = product.product_type or "other"
            premiums_by_type[product_type] += premium

    # Calculate efficiency: cost per £100k coverage
    total_coverage = sum(float(p.value or 0) for p in products)
    premium_per_100k = (
        (total_premium / (total_coverage / 100000))
        if total_coverage > 0 else 0
    )

    # Find most expensive policy
    most_expensive = None
    if products:
        most_expensive_product = max(
            products,
            key=lambda p: float(
                p.extra_metadata.get("monthly_premium", 0)
                if p.extra_metadata else 0
            )
        )
        most_expensive = {
            "name": most_expensive_product.name,
            "type": most_expensive_product.product_type,
            "monthly_premium": float(
                most_expensive_product.extra_metadata.get("monthly_premium", 0)
                if most_expensive_product.extra_metadata else 0
            )
        }

    return {
        "total_monthly_premium": total_premium,
        "total_annual_premium": total_premium * 12,
        "premium_per_100k_coverage": round(premium_per_100k, 2),
        "premiums_by_type": dict(premiums_by_type),
        "most_expensive_policy": most_expensive
    }


def _analyze_coverage_trends(products: List[Product]) -> Dict[str, Any]:
    """Analyze coverage changes over time"""
    # Group products by month created
    monthly_coverage = defaultdict(lambda: {"coverage": 0, "count": 0})

    # Get last 12 months
    now = datetime.utcnow()
    twelve_months_ago = now - timedelta(days=365)

    for product in products:
        if product.created_at and product.created_at >= twelve_months_ago:
            month_key = product.created_at.strftime("%Y-%m")
            monthly_coverage[month_key]["coverage"] += float(product.value or 0)
            monthly_coverage[month_key]["count"] += 1

    # Convert to sorted list
    trend_data = [
        {
            "month": month,
            "coverage": data["coverage"],
            "policy_count": data["count"]
        }
        for month, data in sorted(monthly_coverage.items())
    ]

    return {
        "monthly_data": trend_data,
        "trend": "increasing" if len(trend_data) > 1 and trend_data[-1]["coverage"] > trend_data[0]["coverage"] else "stable"
    }


def _generate_recommendations(
    products: List[Product],
    coverage_analysis: Dict[str, Any],
    premium_efficiency: Dict[str, Any]
) -> List[Dict[str, str]]:
    """Generate actionable recommendations"""
    recommendations = []

    # Check if they have any protection
    if not products:
        recommendations.append({
            "priority": "high",
            "category": "coverage",
            "message": "You don't have any protection policies. Consider life insurance if you have dependents.",
            "action": "Run a protection needs analysis to determine appropriate coverage"
        })
        return recommendations

    # Check coverage adequacy (simplified - would need user income data)
    total_coverage = coverage_analysis["total_coverage"]
    if total_coverage < 100000:
        recommendations.append({
            "priority": "medium",
            "category": "coverage",
            "message": "Your total coverage is below typical recommendations.",
            "action": "Consider reviewing your protection needs, especially if you have dependents"
        })

    # Check premium efficiency
    premium_per_100k = premium_efficiency["premium_per_100k_coverage"]
    if premium_per_100k > 50:  # Example threshold
        recommendations.append({
            "priority": "low",
            "category": "cost",
            "message": "Your premiums are relatively high compared to coverage.",
            "action": "Consider shopping around for better rates when policies come up for renewal"
        })

    # Check for policy diversity
    coverage_by_type = coverage_analysis["coverage_by_type"]
    if len(coverage_by_type) == 1:
        recommendations.append({
            "priority": "low",
            "category": "diversification",
            "message": "You only have one type of protection.",
            "action": "Consider adding critical illness or income protection for comprehensive coverage"
        })

    # If no recommendations, add positive feedback
    if not recommendations:
        recommendations.append({
            "priority": "info",
            "category": "status",
            "message": "Your protection coverage looks good!",
            "action": "Review your coverage annually to ensure it keeps pace with your needs"
        })

    return recommendations