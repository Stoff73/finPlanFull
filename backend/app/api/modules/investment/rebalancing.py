"""
Investment Portfolio Rebalancing Endpoints

Provides portfolio rebalancing analysis and recommendations:
- Current allocation vs. target allocation
- Drift analysis
- Rebalancing actions (buy/sell recommendations)
- Tax-efficient rebalancing strategies
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


# Pydantic schemas
class TargetAllocation(BaseModel):
    asset_type: str = Field(..., description="Asset type (stocks, bonds, cash, etc.)")
    target_percentage: float = Field(..., ge=0, le=100, description="Target allocation percentage")


class RebalancingRequest(BaseModel):
    target_allocations: List[TargetAllocation] = Field(..., description="Target asset allocation")
    drift_threshold: Optional[float] = Field(5.0, description="Rebalancing threshold in percentage points")


@router.post("/analysis", response_model=Dict[str, Any])
def analyze_rebalancing(
    request: RebalancingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze portfolio rebalancing needs.

    Compares current allocation with target allocation and provides
    specific buy/sell recommendations to rebalance the portfolio.
    """

    # Validate target allocations sum to 100%
    total_target = sum(alloc.target_percentage for alloc in request.target_allocations)
    if abs(total_target - 100) > 0.1:
        raise HTTPException(
            status_code=400,
            detail=f"Target allocations must sum to 100% (currently {total_target}%)"
        )

    # Get all investment products
    investments = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'investment',
        Product.status == 'active'
    ).all()

    if not investments:
        raise HTTPException(
            status_code=404,
            detail="No investments found. Add investments before rebalancing."
        )

    # Calculate current allocation
    total_value = sum(inv.value or 0 for inv in investments)

    if total_value == 0:
        raise HTTPException(
            status_code=400,
            detail="Total portfolio value is zero. Cannot rebalance."
        )

    current_allocation = defaultdict(float)
    for inv in investments:
        asset_type = inv.product_type or 'other'
        current_allocation[asset_type] += (inv.value or 0)

    # Build target allocation map
    target_map = {alloc.asset_type: alloc.target_percentage for alloc in request.target_allocations}

    # Calculate allocation comparison
    allocation_analysis = []
    total_drift = 0

    for asset_type in set(list(current_allocation.keys()) + list(target_map.keys())):
        current_value = current_allocation.get(asset_type, 0)
        current_percentage = (current_value / total_value * 100) if total_value > 0 else 0
        target_percentage = target_map.get(asset_type, 0)

        drift = current_percentage - target_percentage
        drift_value = (drift / 100) * total_value

        needs_rebalancing = abs(drift) >= request.drift_threshold

        allocation_analysis.append({
            "asset_type": asset_type,
            "current_value": current_value,
            "current_percentage": round(current_percentage, 2),
            "target_percentage": target_percentage,
            "drift_percentage": round(drift, 2),
            "drift_value": round(drift_value, 2),
            "needs_rebalancing": needs_rebalancing
        })

        total_drift += abs(drift)

    # Sort by absolute drift (highest first)
    allocation_analysis.sort(key=lambda x: abs(x['drift_percentage']), reverse=True)

    # --- Generate rebalancing actions ---
    actions = []

    for alloc in allocation_analysis:
        if not alloc['needs_rebalancing']:
            continue

        drift = alloc['drift_percentage']
        drift_value = abs(alloc['drift_value'])

        if drift > 0:
            # Overweight - need to sell
            actions.append({
                "action": "sell",
                "asset_type": alloc['asset_type'],
                "amount": round(drift_value, 2),
                "percentage": round(abs(drift), 2),
                "reason": f"Reduce {alloc['asset_type']} allocation from {alloc['current_percentage']:.1f}% to {alloc['target_percentage']:.1f}%"
            })
        else:
            # Underweight - need to buy
            actions.append({
                "action": "buy",
                "asset_type": alloc['asset_type'],
                "amount": round(drift_value, 2),
                "percentage": round(abs(drift), 2),
                "reason": f"Increase {alloc['asset_type']} allocation from {alloc['current_percentage']:.1f}% to {alloc['target_percentage']:.1f}%"
            })

    # --- Rebalancing summary ---
    needs_rebalancing = len(actions) > 0
    rebalancing_complexity = "simple" if len(actions) <= 2 else "moderate" if len(actions) <= 4 else "complex"

    summary = {
        "needs_rebalancing": needs_rebalancing,
        "total_drift": round(total_drift / 2, 2),  # Divide by 2 because we count both over and under
        "rebalancing_complexity": rebalancing_complexity,
        "actions_count": len(actions),
        "message": _generate_rebalancing_message(needs_rebalancing, total_drift / 2, rebalancing_complexity)
    }

    # --- Tax-efficient rebalancing tips ---
    tax_tips = []

    if any(action['action'] == 'sell' for action in actions):
        tax_tips.append({
            "tip": "Tax-Loss Harvesting",
            "description": "Consider selling investments with losses first to offset capital gains tax."
        })
        tax_tips.append({
            "tip": "Use ISA Allowance",
            "description": "Sell from general accounts and rebuy in ISA wrapper to avoid CGT (£20k annual allowance)."
        })

    if any(action['action'] == 'buy' for action in actions):
        tax_tips.append({
            "tip": "Use New Contributions",
            "description": "Consider using new monthly contributions to buy underweight assets rather than selling."
        })

    return {
        "summary": summary,
        "total_portfolio_value": total_value,
        "current_allocation": allocation_analysis,
        "rebalancing_actions": actions,
        "tax_tips": tax_tips,
        "drift_threshold": request.drift_threshold,
        "analysis_date": datetime.utcnow().isoformat()
    }


@router.get("/drift", response_model=Dict[str, Any])
def get_portfolio_drift(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio drift analysis without target allocations.

    Shows current allocation and highlights concentration risk.
    """

    # Get all investment products
    investments = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'investment',
        Product.status == 'active'
    ).all()

    if not investments:
        return {
            "message": "No investments found",
            "total_value": 0,
            "allocation": []
        }

    # Calculate current allocation
    total_value = sum(inv.value or 0 for inv in investments)

    allocation = defaultdict(float)
    allocation_count = defaultdict(int)

    for inv in investments:
        asset_type = inv.product_type or 'other'
        allocation[asset_type] += (inv.value or 0)
        allocation_count[asset_type] += 1

    allocation_breakdown = []
    for asset_type, value in allocation.items():
        percentage = (value / total_value * 100) if total_value > 0 else 0

        # Concentration risk flag
        concentration_risk = "high" if percentage > 40 else "medium" if percentage > 25 else "low"

        allocation_breakdown.append({
            "asset_type": asset_type,
            "value": value,
            "percentage": round(percentage, 2),
            "count": allocation_count[asset_type],
            "concentration_risk": concentration_risk
        })

    allocation_breakdown.sort(key=lambda x: x['value'], reverse=True)

    return {
        "total_value": total_value,
        "allocation": allocation_breakdown,
        "analysis_date": datetime.utcnow().isoformat()
    }


def _generate_rebalancing_message(needs_rebalancing: bool, total_drift: float, complexity: str) -> str:
    """Generate user-friendly rebalancing message."""
    if not needs_rebalancing:
        return "Your portfolio is well-balanced. No rebalancing needed at this time."

    if complexity == "simple":
        return f"Your portfolio has drifted by {total_drift:.1f}% from target. Simple rebalancing recommended."
    elif complexity == "moderate":
        return f"Your portfolio has drifted by {total_drift:.1f}% from target. Moderate rebalancing needed across several assets."
    else:
        return f"Your portfolio has drifted significantly by {total_drift:.1f}% from target. Comprehensive rebalancing recommended."