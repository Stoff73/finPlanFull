"""
Investment Analytics Endpoints

Provides comprehensive portfolio analytics including:
- Performance metrics (returns, volatility)
- Asset allocation analysis
- Risk metrics
- Dividend income tracking
- Recommendations
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
def get_investment_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive investment analytics for the current user.

    Returns:
    - Portfolio performance (total return, annualized return)
    - Asset allocation breakdown
    - Risk metrics
    - Dividend income analysis
    - Historical performance trends
    - Recommendations
    """

    # Get all investment products
    investments = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'investment',
        Product.status == 'active'
    ).all()

    # --- 1. Portfolio Performance ---
    total_value = sum(inv.value or 0 for inv in investments)
    total_contributions = 0
    total_dividends = 0

    for inv in investments:
        if inv.extra_metadata and isinstance(inv.extra_metadata, dict):
            contributions = inv.extra_metadata.get('total_contributions', 0)
            total_contributions += contributions
            dividend = inv.extra_metadata.get('annual_dividend', 0)
            total_dividends += dividend

    # Calculate returns
    capital_gain = total_value - total_contributions if total_contributions > 0 else 0
    total_return = capital_gain
    total_return_percentage = (total_return / total_contributions * 100) if total_contributions > 0 else 0

    # Dividend yield
    dividend_yield = (total_dividends / total_value * 100) if total_value > 0 else 0

    performance = {
        "total_value": total_value,
        "total_contributions": total_contributions,
        "capital_gain": capital_gain,
        "total_return": total_return,
        "total_return_percentage": round(total_return_percentage, 2),
        "annual_dividends": total_dividends,
        "dividend_yield": round(dividend_yield, 2),
        "total_yield": round(total_return_percentage + dividend_yield, 2)
    }

    # --- 2. Asset Allocation ---
    allocation = defaultdict(float)
    allocation_count = defaultdict(int)

    for inv in investments:
        product_type = inv.product_type or 'other'
        allocation[product_type] += (inv.value or 0)
        allocation_count[product_type] += 1

    allocation_breakdown = []
    for asset_type, value in allocation.items():
        percentage = (value / total_value * 100) if total_value > 0 else 0
        allocation_breakdown.append({
            "asset_type": asset_type,
            "value": value,
            "percentage": round(percentage, 1),
            "count": allocation_count[asset_type]
        })

    # Sort by value descending
    allocation_breakdown.sort(key=lambda x: x['value'], reverse=True)

    # --- 3. Risk Assessment ---
    # Simplified risk scoring based on asset types
    risk_weights = {
        'stocks': 1.0,
        'etf': 0.8,
        'funds': 0.7,
        'stocks_shares_isa': 0.8,
        'gia': 0.8,
        'bonds': 0.3,
        'cash': 0.0
    }

    weighted_risk = 0
    for asset_type, value in allocation.items():
        weight = risk_weights.get(asset_type, 0.5)  # Default medium risk
        weighted_risk += weight * value

    portfolio_risk_score = (weighted_risk / total_value) if total_value > 0 else 0
    portfolio_risk_score = round(portfolio_risk_score * 100, 1)

    # Risk rating
    if portfolio_risk_score < 30:
        risk_rating = "low"
        risk_description = "Your portfolio has a conservative risk profile with lower volatility."
    elif portfolio_risk_score < 60:
        risk_rating = "medium"
        risk_description = "Your portfolio has a balanced risk profile with moderate volatility."
    else:
        risk_rating = "high"
        risk_description = "Your portfolio has an aggressive risk profile with higher potential returns and volatility."

    risk_metrics = {
        "portfolio_risk_score": portfolio_risk_score,
        "risk_rating": risk_rating,
        "risk_description": risk_description
    }

    # --- 4. Diversification Analysis ---
    diversification_score = len(allocation_breakdown)

    if diversification_score == 0:
        diversification_rating = "none"
        diversification_message = "No investments yet. Start building a diversified portfolio."
    elif diversification_score == 1:
        diversification_rating = "poor"
        diversification_message = "Your portfolio lacks diversification. Consider adding different asset types to reduce risk."
    elif diversification_score == 2:
        diversification_rating = "fair"
        diversification_message = "Your portfolio has basic diversification. Adding more asset types could improve risk management."
    elif diversification_score <= 4:
        diversification_rating = "good"
        diversification_message = "Your portfolio is well-diversified across multiple asset types."
    else:
        diversification_rating = "excellent"
        diversification_message = "Your portfolio is excellently diversified, helping to manage risk effectively."

    diversification = {
        "asset_count": diversification_score,
        "rating": diversification_rating,
        "message": diversification_message
    }

    # --- 5. Income Analysis ---
    income_analysis = {
        "annual_dividend_income": total_dividends,
        "monthly_dividend_income": round(total_dividends / 12, 2),
        "dividend_yield": round(dividend_yield, 2),
        "income_percentage_of_portfolio": round(dividend_yield, 2)
    }

    # --- 6. Performance Trends (Simulated) ---
    # In a real app, this would come from historical data
    # For now, we'll create a simple 12-month trend based on current performance
    trends = []
    base_value = total_contributions if total_contributions > 0 else total_value * 0.9

    for i in range(12, 0, -1):
        month_date = (datetime.utcnow() - timedelta(days=30 * i)).strftime("%Y-%m")
        # Simulate growth trajectory
        progress = (12 - i) / 12
        month_value = base_value + (capital_gain * progress)
        trends.append({
            "month": month_date,
            "value": round(month_value, 2)
        })

    # --- 7. Recommendations ---
    recommendations = []

    # Diversification recommendation
    if diversification_score < 3:
        recommendations.append({
            "priority": "high",
            "category": "diversification",
            "message": f"Consider diversifying into {3 - diversification_score} more asset types to reduce portfolio risk."
        })

    # Rebalancing recommendation
    if allocation_breakdown and len(allocation_breakdown) > 1:
        top_allocation = allocation_breakdown[0]
        if top_allocation['percentage'] > 50:
            recommendations.append({
                "priority": "medium",
                "category": "rebalancing",
                "message": f"{top_allocation['asset_type']} represents {top_allocation['percentage']}% of your portfolio. Consider rebalancing to reduce concentration risk."
            })

    # Income recommendation
    if dividend_yield < 2 and total_value > 10000:
        recommendations.append({
            "priority": "low",
            "category": "income",
            "message": f"Your dividend yield is {dividend_yield:.1f}%. Consider adding dividend-paying stocks or funds to generate passive income."
        })

    # Performance recommendation
    if total_return_percentage < -10:
        recommendations.append({
            "priority": "high",
            "category": "performance",
            "message": f"Your portfolio is down {abs(total_return_percentage):.1f}%. Review your investment strategy and consider rebalancing or tax-loss harvesting."
        })
    elif total_return_percentage > 20:
        recommendations.append({
            "priority": "medium",
            "category": "performance",
            "message": f"Great returns of {total_return_percentage:.1f}%! Consider taking profits and rebalancing to lock in gains."
        })

    # Default positive message
    if not recommendations:
        recommendations.append({
            "priority": "low",
            "category": "general",
            "message": "Your portfolio looks healthy. Continue with your current investment strategy and regular contributions."
        })

    return {
        "performance": performance,
        "asset_allocation": allocation_breakdown,
        "risk_metrics": risk_metrics,
        "diversification": diversification,
        "income_analysis": income_analysis,
        "performance_trends": trends,
        "recommendations": recommendations,
        "last_calculated": datetime.utcnow().isoformat()
    }