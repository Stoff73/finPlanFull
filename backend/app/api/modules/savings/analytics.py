"""Savings Analytics API

Provides detailed analytics for savings planning:
- Savings rate calculation
- Emergency fund adequacy analysis
- Interest earned tracking
- Balance trends over time
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime, timedelta, date
from collections import defaultdict

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models import BankAccount, Transaction

router = APIRouter()


@router.get("")
async def get_savings_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive savings analytics

    Returns:
        - Savings rate analysis
        - Emergency fund adequacy
        - Interest earned tracking
        - Balance trends
        - Recommendations
    """
    # Get all active savings accounts
    accounts = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id,
        BankAccount.is_active == True
    ).all()

    # Get all transactions (last 12 months for trend analysis)
    twelve_months_ago = date.today() - timedelta(days=365)
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= twelve_months_ago
    ).all()

    # Calculate savings rate
    savings_rate_data = _calculate_savings_rate(transactions)

    # Calculate emergency fund adequacy
    emergency_fund_data = _calculate_emergency_fund_adequacy(accounts, transactions)

    # Calculate interest earned
    interest_earned_data = _calculate_interest_earned(accounts)

    # Calculate balance trends
    balance_trends = _calculate_balance_trends(accounts, transactions)

    # Generate recommendations
    recommendations = _generate_recommendations(
        savings_rate_data,
        emergency_fund_data,
        interest_earned_data,
        accounts
    )

    return {
        "savings_rate": savings_rate_data,
        "emergency_fund": emergency_fund_data,
        "interest_earned": interest_earned_data,
        "balance_trends": balance_trends,
        "recommendations": recommendations,
        "last_updated": datetime.utcnow().isoformat()
    }


def _calculate_savings_rate(transactions: List[Transaction]) -> Dict[str, Any]:
    """Calculate savings rate (savings / income)"""
    if not transactions:
        return {
            "monthly_income": 0,
            "monthly_savings": 0,
            "savings_rate": 0,
            "trend": "unknown"
        }

    # Calculate monthly income and expenses
    monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0})

    for transaction in transactions:
        month_key = transaction.date.strftime("%Y-%m")

        if transaction.transaction_type == "income":
            monthly_data[month_key]["income"] += transaction.amount
        else:  # expense
            monthly_data[month_key]["expenses"] += transaction.amount

    # Calculate savings for each month
    for month in monthly_data:
        income = monthly_data[month]["income"]
        expenses = monthly_data[month]["expenses"]
        monthly_data[month]["savings"] = income - expenses

    # Calculate average monthly values
    if monthly_data:
        avg_income = sum(d["income"] for d in monthly_data.values()) / len(monthly_data)
        avg_savings = sum(d["savings"] for d in monthly_data.values()) / len(monthly_data)
        savings_rate = (avg_savings / avg_income * 100) if avg_income > 0 else 0

        # Determine trend (comparing last 3 months to previous 3 months)
        sorted_months = sorted(monthly_data.keys())
        if len(sorted_months) >= 6:
            recent_3 = [monthly_data[m]["savings"] for m in sorted_months[-3:]]
            previous_3 = [monthly_data[m]["savings"] for m in sorted_months[-6:-3]]
            recent_avg = sum(recent_3) / 3
            previous_avg = sum(previous_3) / 3

            if recent_avg > previous_avg * 1.1:
                trend = "increasing"
            elif recent_avg < previous_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
    else:
        avg_income = 0
        avg_savings = 0
        savings_rate = 0
        trend = "unknown"

    return {
        "monthly_income": round(avg_income, 2),
        "monthly_savings": round(avg_savings, 2),
        "savings_rate": round(savings_rate, 1),
        "trend": trend
    }


def _calculate_emergency_fund_adequacy(
    accounts: List[BankAccount],
    transactions: List[Transaction]
) -> Dict[str, Any]:
    """Calculate emergency fund adequacy (months of expenses covered)"""
    # Calculate total liquid savings
    total_balance = sum(acc.current_balance for acc in accounts)

    # Calculate average monthly expenses from transactions
    monthly_expenses = defaultdict(float)

    for transaction in transactions:
        if transaction.transaction_type == "expense":
            month_key = transaction.date.strftime("%Y-%m")
            monthly_expenses[month_key] += transaction.amount

    if monthly_expenses:
        avg_monthly_expenses = sum(monthly_expenses.values()) / len(monthly_expenses)
    else:
        # Fallback assumption
        avg_monthly_expenses = 3000

    # Calculate months covered
    months_covered = total_balance / avg_monthly_expenses if avg_monthly_expenses > 0 else 0

    # Determine status
    if months_covered >= 6:
        status = "excellent"
        target_met = True
    elif months_covered >= 3:
        status = "adequate"
        target_met = True
    elif months_covered >= 1:
        status = "needs_improvement"
        target_met = False
    else:
        status = "insufficient"
        target_met = False

    # Calculate target amount (6 months)
    target_amount = avg_monthly_expenses * 6
    gap = max(0, target_amount - total_balance)

    return {
        "current_balance": total_balance,
        "monthly_expenses": round(avg_monthly_expenses, 2),
        "months_covered": round(months_covered, 1),
        "target_months": 6,
        "target_amount": target_amount,
        "gap": gap,
        "status": status,
        "target_met": target_met
    }


def _calculate_interest_earned(accounts: List[BankAccount]) -> Dict[str, Any]:
    """Calculate total interest earnings potential"""
    total_balance = sum(acc.current_balance for acc in accounts)

    # Calculate weighted average interest rate
    if total_balance > 0:
        weighted_rate = sum(
            acc.current_balance * (acc.interest_rate or 0)
            for acc in accounts
        ) / total_balance
    else:
        weighted_rate = 0

    # Calculate projected annual interest
    projected_annual = total_balance * (weighted_rate / 100)

    # Find best and worst rates
    accounts_with_rates = [acc for acc in accounts if acc.interest_rate and acc.interest_rate > 0]

    if accounts_with_rates:
        best_rate = max(acc.interest_rate for acc in accounts_with_rates)
        worst_rate = min(acc.interest_rate for acc in accounts_with_rates)
    else:
        best_rate = 0
        worst_rate = 0

    return {
        "total_balance": total_balance,
        "weighted_average_rate": round(weighted_rate, 2),
        "projected_annual_interest": round(projected_annual, 2),
        "projected_monthly_interest": round(projected_annual / 12, 2),
        "best_rate": best_rate,
        "worst_rate": worst_rate
    }


def _calculate_balance_trends(
    accounts: List[BankAccount],
    transactions: List[Transaction]
) -> Dict[str, Any]:
    """Calculate balance trends over time"""
    # Group transactions by month
    monthly_balances = {}

    # Get current total balance
    current_balance = sum(acc.current_balance for acc in accounts)

    # Calculate historical balances (working backwards from current)
    sorted_transactions = sorted(transactions, key=lambda t: t.date, reverse=True)

    balance = current_balance
    current_month = date.today().strftime("%Y-%m")
    monthly_balances[current_month] = balance

    for transaction in sorted_transactions:
        # Reverse the transaction effect
        if transaction.transaction_type == "income":
            balance -= transaction.amount
        else:  # expense
            balance += transaction.amount

        month_key = transaction.date.strftime("%Y-%m")
        monthly_balances[month_key] = balance

    # Convert to sorted list (oldest to newest)
    sorted_months = sorted(monthly_balances.keys())
    trend_data = [
        {
            "month": month,
            "balance": round(monthly_balances[month], 2)
        }
        for month in sorted_months[-12:]  # Last 12 months
    ]

    # Determine overall trend
    if len(trend_data) >= 2:
        first_balance = trend_data[0]["balance"]
        last_balance = trend_data[-1]["balance"]

        if last_balance > first_balance * 1.1:
            trend = "increasing"
        elif last_balance < first_balance * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    return {
        "monthly_data": trend_data,
        "trend": trend,
        "current_balance": current_balance
    }


def _generate_recommendations(
    savings_rate: Dict[str, Any],
    emergency_fund: Dict[str, Any],
    interest_earned: Dict[str, Any],
    accounts: List[BankAccount]
) -> List[Dict[str, str]]:
    """Generate actionable recommendations"""
    recommendations = []

    # Check emergency fund
    if emergency_fund["status"] in ["insufficient", "needs_improvement"]:
        recommendations.append({
            "priority": "high",
            "category": "emergency_fund",
            "message": f"Your emergency fund covers {emergency_fund['months_covered']:.1f} months of expenses.",
            "action": f"Aim to save £{emergency_fund['gap']:,.0f} more to reach the 6-month target."
        })

    # Check savings rate
    if savings_rate["savings_rate"] < 10:
        recommendations.append({
            "priority": "medium",
            "category": "savings_rate",
            "message": f"Your savings rate is {savings_rate['savings_rate']:.1f}%.",
            "action": "Aim for at least 10-20% of income saved for financial security."
        })
    elif savings_rate["trend"] == "decreasing":
        recommendations.append({
            "priority": "medium",
            "category": "savings_rate",
            "message": "Your savings rate is declining.",
            "action": "Review your expenses and look for areas to cut back."
        })

    # Check interest rates
    if interest_earned["weighted_average_rate"] < 2:
        recommendations.append({
            "priority": "low",
            "category": "interest",
            "message": f"Your average interest rate is {interest_earned['weighted_average_rate']:.2f}%.",
            "action": "Shop around for better savings accounts to maximize interest earnings."
        })

    # Check account diversification
    if len(accounts) == 1:
        recommendations.append({
            "priority": "low",
            "category": "diversification",
            "message": "You only have one savings account.",
            "action": "Consider opening additional accounts (e.g., ISA, notice account) for better rates and FSCS protection."
        })

    # If everything looks good
    if not recommendations:
        recommendations.append({
            "priority": "info",
            "category": "status",
            "message": "Your savings strategy looks solid!",
            "action": "Keep up the good work and review your progress regularly."
        })

    return recommendations