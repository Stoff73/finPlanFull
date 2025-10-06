"""Savings Module API Router

Handles savings/cash planning functionality including:
- Dashboard metrics aggregation
- Summary data for main dashboard
- Emergency fund tracking
- Savings rate analysis
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


@router.get("/dashboard")
async def get_savings_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive savings module dashboard data

    Returns:
        - Total savings balance
        - Account count
        - Emergency fund status (months of expenses covered)
        - Savings rate
        - Account breakdown by type
        - Recent account changes
    """
    # Query all savings accounts/products for this user
    # Note: Banking products will be migrated to module='savings'
    savings_products = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == "savings",
        Product.status == "active"
    ).all()

    # Calculate total balance
    total_balance = sum(
        float(product.value or 0)
        for product in savings_products
    )

    # Calculate balance breakdown by account type
    balance_by_type = {}
    for product in savings_products:
        account_type = product.product_type or "savings_account"
        if account_type not in balance_by_type:
            balance_by_type[account_type] = {
                "count": 0,
                "total_balance": 0.0,
                "interest_rate": 0.0  # Average interest rate
            }

        balance_by_type[account_type]["count"] += 1
        balance_by_type[account_type]["total_balance"] += float(product.value or 0)

        # Calculate average interest rate if available
        if product.extra_metadata and isinstance(product.extra_metadata, dict):
            interest_rate = product.extra_metadata.get("interest_rate", 0)
            if interest_rate:
                balance_by_type[account_type]["interest_rate"] += float(interest_rate)

    # Calculate average interest rates
    for account_type in balance_by_type:
        count = balance_by_type[account_type]["count"]
        if count > 0:
            balance_by_type[account_type]["interest_rate"] /= count

    # Calculate emergency fund status
    # Placeholder: Would need user's monthly expenses
    # For now, assume £3,000 monthly expenses
    assumed_monthly_expenses = 3000
    emergency_fund_months = total_balance / assumed_monthly_expenses if assumed_monthly_expenses > 0 else 0

    # Determine emergency fund status
    if emergency_fund_months >= 6:
        emergency_fund_status = "excellent"
    elif emergency_fund_months >= 3:
        emergency_fund_status = "adequate"
    elif emergency_fund_months >= 1:
        emergency_fund_status = "needs_improvement"
    else:
        emergency_fund_status = "insufficient"

    # Calculate savings rate (placeholder - would need income/expense data)
    savings_rate = 0  # Percentage of income saved

    # Get savings goals from ModuleGoal
    from app.models.module_goal import ModuleGoal
    goals = db.query(ModuleGoal).filter(
        ModuleGoal.user_id == current_user.id,
        ModuleGoal.module == "savings"
    ).all()

    return {
        "metrics": {
            "total_savings": total_balance,
            "total_accounts": len(savings_products),
            "emergency_fund": total_balance,
            "emergency_fund_goal": assumed_monthly_expenses * 6,
            "monthly_savings": 0  # Placeholder - would calculate from transactions
        },
        "accounts": [
            {
                "id": p.id,
                "product_name": p.name,
                "provider": p.provider,
                "product_value": float(p.value or 0),
                "currency": p.currency or "GBP",
                "interest_rate": p.extra_metadata.get("interest_rate", 0) if p.extra_metadata else 0,
                "account_type": p.product_type or "savings_account",
                "start_date": p.created_at.isoformat() if p.created_at else None,
            }
            for p in savings_products
        ],
        "goals": [
            {
                "id": g.id,
                "module": g.module,
                "goal_name": g.goal_name,
                "target_amount": float(g.target_amount or 0),
                "current_amount": float(g.current_amount or 0),
                "target_date": g.target_date.isoformat() if g.target_date else None
            }
            for g in goals
        ],
        "analytics": {
            "savings_rate": savings_rate,
            "avg_monthly_deposit": 0  # Placeholder
        }
    }


@router.get("/summary")
async def get_savings_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get quick savings summary for main dashboard card

    Returns:
        - Total balance
        - Account count
        - Emergency fund status
        - Status indicator
    """
    # Query active savings products
    savings_products = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == "savings",
        Product.status == "active"
    ).all()

    # Calculate totals
    total_balance = sum(float(p.value or 0) for p in savings_products)

    # Emergency fund calculation (using assumed expenses)
    assumed_monthly_expenses = 3000
    emergency_fund_months = total_balance / assumed_monthly_expenses if assumed_monthly_expenses > 0 else 0

    # Determine status
    if emergency_fund_months >= 6:
        status = "excellent"
    elif emergency_fund_months >= 3:
        status = "adequate"
    elif emergency_fund_months >= 1:
        status = "attention_needed"
    else:
        status = "insufficient"

    return {
        "total_balance": total_balance,
        "account_count": len(savings_products),
        "emergency_fund_months": round(emergency_fund_months, 1),
        "status": status,
        "message": _get_status_message(status, total_balance, emergency_fund_months)
    }


def _get_status_message(status: str, balance: float, months: float) -> str:
    """Generate user-friendly status message following STYLEGUIDE.md narrative approach"""
    if status == "insufficient":
        return "You don't have much in savings yet. Consider building an emergency fund for unexpected expenses."
    elif status == "attention_needed":
        return f"You have {months:.1f} months of expenses saved. Aim for 3-6 months for a solid emergency fund."
    elif status == "adequate":
        return f"Good work! You have {months:.1f} months of expenses saved. Consider reaching 6 months for optimal security."
    else:
        return f"Excellent! You have {months:.1f} months of expenses saved - your emergency fund is strong."