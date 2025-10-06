"""
Investment Module API Router

Provides dashboard and summary endpoints for the Investment module.
Aggregates investment portfolio data, performance metrics, and asset allocation.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
def get_investment_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive investment dashboard data for the current user.

    Returns:
    - Total portfolio value
    - Asset allocation breakdown
    - Performance metrics (returns, dividends)
    - Investment accounts summary
    - Risk metrics
    - Recommendations
    """

    # Get all investment products for the user
    investments = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'investment',
        Product.status == 'active'
    ).all()

    # Calculate total portfolio value
    total_value = sum(inv.value or 0 for inv in investments)

    # Calculate asset allocation by product type
    allocation = {}
    for inv in investments:
        product_type = inv.product_type or 'other'
        allocation[product_type] = allocation.get(product_type, 0) + (inv.value or 0)

    # Calculate allocation percentages
    allocation_percentages = {}
    if total_value > 0:
        for asset_type, value in allocation.items():
            allocation_percentages[asset_type] = round((value / total_value) * 100, 1)

    # Calculate total annual dividends
    total_dividends = 0
    for inv in investments:
        if inv.extra_metadata and isinstance(inv.extra_metadata, dict):
            annual_dividend = inv.extra_metadata.get('annual_dividend', 0)
            total_dividends += annual_dividend

    # Calculate dividend yield
    dividend_yield = (total_dividends / total_value * 100) if total_value > 0 else 0

    # Calculate total contributions (if tracked)
    total_contributions = 0
    for inv in investments:
        if inv.extra_metadata and isinstance(inv.extra_metadata, dict):
            contributions = inv.extra_metadata.get('total_contributions', 0)
            total_contributions += contributions

    # Calculate gain/loss
    gain_loss = total_value - total_contributions if total_contributions > 0 else 0
    gain_loss_percentage = (gain_loss / total_contributions * 100) if total_contributions > 0 else 0

    # Count investment accounts
    account_count = len(investments)

    # Status determination
    if total_value == 0:
        status = "no_investments"
        message = "You haven't added any investments yet. Start building your portfolio to grow your wealth."
    elif gain_loss_percentage > 10:
        status = "excellent"
        message = f"Your portfolio is performing excellently with {gain_loss_percentage:.1f}% returns. Keep up the good work!"
    elif gain_loss_percentage > 0:
        status = "good"
        message = f"Your portfolio is performing well with {gain_loss_percentage:.1f}% gains. Continue your investment strategy."
    elif gain_loss_percentage > -5:
        status = "neutral"
        message = f"Your portfolio has small losses of {abs(gain_loss_percentage):.1f}%. Market fluctuations are normal in investing."
    else:
        status = "attention_needed"
        message = f"Your portfolio is down {abs(gain_loss_percentage):.1f}%. Consider reviewing your investment strategy."

    return {
        "total_value": total_value,
        "total_contributions": total_contributions,
        "gain_loss": gain_loss,
        "gain_loss_percentage": round(gain_loss_percentage, 2),
        "annual_dividends": total_dividends,
        "dividend_yield": round(dividend_yield, 2),
        "account_count": account_count,
        "asset_allocation": allocation,
        "allocation_percentages": allocation_percentages,
        "investments": [
            {
                "id": inv.id,
                "name": inv.name,
                "product_type": inv.product_type,
                "value": inv.value,
                "currency": inv.currency or "GBP",
                "provider": inv.provider or "Unknown",
                "reference_number": inv.reference_number or str(inv.id),
            }
            for inv in investments
        ],
        "status": status,
        "message": message,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/summary", response_model=Dict[str, Any])
def get_investment_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quick investment summary for main dashboard card.

    Returns key metrics only:
    - Total portfolio value
    - Account count
    - Status (good, attention_needed, etc.)
    """

    # Get all investment products
    investments = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'investment',
        Product.status == 'active'
    ).all()

    # Calculate total value
    total_value = sum(inv.value or 0 for inv in investments)
    account_count = len(investments)

    # Calculate gain/loss for status
    total_contributions = 0
    for inv in investments:
        if inv.extra_metadata and isinstance(inv.extra_metadata, dict):
            contributions = inv.extra_metadata.get('total_contributions', 0)
            total_contributions += contributions

    gain_loss_percentage = 0
    if total_contributions > 0:
        gain_loss = total_value - total_contributions
        gain_loss_percentage = (gain_loss / total_contributions * 100)

    # Determine status
    if total_value == 0:
        status = "no_investments"
    elif gain_loss_percentage > 10:
        status = "excellent"
    elif gain_loss_percentage > 0:
        status = "good"
    elif gain_loss_percentage > -5:
        status = "neutral"
    else:
        status = "attention_needed"

    return {
        "total_value": total_value,
        "account_count": account_count,
        "gain_loss_percentage": round(gain_loss_percentage, 2),
        "status": status
    }