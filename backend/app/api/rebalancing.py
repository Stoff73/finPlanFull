"""API endpoints for portfolio rebalancing recommendations."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from app.api.auth.auth import get_current_user
from app.models.user import User
from app.db.base import get_db
from app.services.portfolio_rebalancer import (
    PortfolioRebalancer,
    Holding,
    TargetAllocation
)

router = APIRouter(prefix="/api/rebalancing", tags=["rebalancing"])


class HoldingRequest(BaseModel):
    """Request model for a portfolio holding."""
    asset_class: str = Field(..., description="Asset class (e.g., 'UK Equities', 'US Bonds')")
    ticker: str = Field(..., description="Ticker symbol")
    name: str = Field(..., description="Investment name")
    quantity: float = Field(..., gt=0, description="Number of shares/units")
    current_price: float = Field(..., gt=0, description="Current price per share")
    cost_basis: float = Field(..., ge=0, description="Cost basis per share")
    purchase_date: date = Field(..., description="Purchase date")
    account_type: str = Field(..., description="Account type: ISA, SIPP, or GIA")


class TargetAllocationRequest(BaseModel):
    """Request model for target allocation."""
    asset_class: str = Field(..., description="Asset class")
    target_percentage: float = Field(..., ge=0, le=100, description="Target allocation percentage")


class RebalancingRequest(BaseModel):
    """Request model for rebalancing analysis."""
    holdings: List[HoldingRequest]
    target_allocation: List[TargetAllocationRequest]
    tolerance: Optional[float] = Field(0.05, ge=0, le=1, description="Drift tolerance (e.g., 0.05 = 5%)")
    tax_rate: str = Field('higher', description="Tax rate: 'basic' or 'higher'")
    annual_cgt_used: float = Field(0.0, ge=0, description="CGT allowance already used this year")
    min_trade_value: float = Field(100.0, ge=0, description="Minimum trade value")


class CurrentAllocationRequest(BaseModel):
    """Request model for current allocation analysis."""
    holdings: List[HoldingRequest]


class DriftAnalysisRequest(BaseModel):
    """Request model for drift analysis."""
    holdings: List[HoldingRequest]
    target_allocation: List[TargetAllocationRequest]


class HistoricalDriftRequest(BaseModel):
    """Request model for historical drift analysis."""
    historical_allocations: List[Dict[str, Any]] = Field(
        ...,
        description="List of historical allocations with 'date' and 'allocation' keys"
    )
    target_allocation: List[TargetAllocationRequest]


@router.post("/analyze-current-allocation", response_model=Dict[str, Any])
async def analyze_current_allocation(
    request: CurrentAllocationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze current portfolio allocation.

    Returns breakdown by asset class and total portfolio value.
    """
    rebalancer = PortfolioRebalancer()

    # Convert request to Holding objects
    holdings = [
        Holding(
            asset_class=h.asset_class,
            ticker=h.ticker,
            name=h.name,
            quantity=h.quantity,
            current_price=h.current_price,
            cost_basis=h.cost_basis,
            purchase_date=h.purchase_date,
            account_type=h.account_type
        )
        for h in request.holdings
    ]

    portfolio_value = rebalancer.calculate_portfolio_value(holdings)
    current_allocation = rebalancer.calculate_current_allocation(holdings)

    # Calculate holdings by asset class
    holdings_by_class = {}
    for holding in holdings:
        if holding.asset_class not in holdings_by_class:
            holdings_by_class[holding.asset_class] = []

        holdings_by_class[holding.asset_class].append({
            'ticker': holding.ticker,
            'name': holding.name,
            'quantity': holding.quantity,
            'current_price': holding.current_price,
            'value': holding.quantity * holding.current_price,
            'account_type': holding.account_type
        })

    return {
        'portfolio_value': round(portfolio_value, 2),
        'current_allocation': {k: round(v, 2) for k, v in current_allocation.items()},
        'holdings_by_class': holdings_by_class,
        'total_holdings': len(holdings),
        'asset_classes': list(current_allocation.keys())
    }


@router.post("/calculate-drift", response_model=Dict[str, Any])
async def calculate_drift(
    request: DriftAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate portfolio drift from target allocation.

    Returns drift percentages for each asset class.
    """
    rebalancer = PortfolioRebalancer()

    # Convert request to objects
    holdings = [
        Holding(
            asset_class=h.asset_class,
            ticker=h.ticker,
            name=h.name,
            quantity=h.quantity,
            current_price=h.current_price,
            cost_basis=h.cost_basis,
            purchase_date=h.purchase_date,
            account_type=h.account_type
        )
        for h in request.holdings
    ]

    target_allocation = [
        TargetAllocation(
            asset_class=ta.asset_class,
            target_percentage=ta.target_percentage
        )
        for ta in request.target_allocation
    ]

    current_allocation = rebalancer.calculate_current_allocation(holdings)
    drift = rebalancer.calculate_drift(current_allocation, target_allocation)

    # Categorize drift
    overweight = {k: round(v, 2) for k, v in drift.items() if v > 0}
    underweight = {k: round(abs(v), 2) for k, v in drift.items() if v < 0}
    on_target = {k: round(v, 2) for k, v in drift.items() if abs(v) < 1.0}

    max_drift = max(abs(v) for v in drift.values()) if drift else 0

    return {
        'current_allocation': {k: round(v, 2) for k, v in current_allocation.items()},
        'target_allocation': {ta.asset_class: ta.target_percentage for ta in target_allocation},
        'drift': {k: round(v, 2) for k, v in drift.items()},
        'overweight': overweight,
        'underweight': underweight,
        'on_target': on_target,
        'max_drift': round(max_drift, 2),
        'needs_rebalancing': max_drift > 5.0,  # Default 5% threshold
        'drift_severity': 'High' if max_drift > 10 else 'Moderate' if max_drift > 5 else 'Low'
    }


@router.post("/generate-plan", response_model=Dict[str, Any])
async def generate_rebalancing_plan(
    request: RebalancingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive rebalancing plan with tax optimization.

    Analyzes portfolio drift and provides detailed buy/sell recommendations
    with CGT impact and cost-benefit analysis.
    """
    rebalancer = PortfolioRebalancer()

    # Convert request to objects
    holdings = [
        Holding(
            asset_class=h.asset_class,
            ticker=h.ticker,
            name=h.name,
            quantity=h.quantity,
            current_price=h.current_price,
            cost_basis=h.cost_basis,
            purchase_date=h.purchase_date,
            account_type=h.account_type
        )
        for h in request.holdings
    ]

    target_allocation = [
        TargetAllocation(
            asset_class=ta.asset_class,
            target_percentage=ta.target_percentage
        )
        for ta in request.target_allocation
    ]

    # Validate target allocation sums to 100%
    total_target = sum(ta.target_percentage for ta in target_allocation)
    if abs(total_target - 100) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Target allocation must sum to 100% (currently {total_target:.2f}%)"
        )

    # Generate rebalancing plan
    plan = rebalancer.generate_rebalancing_plan(
        holdings=holdings,
        target_allocation=target_allocation,
        tolerance=request.tolerance,
        tax_rate=request.tax_rate,
        annual_cgt_used=request.annual_cgt_used,
        min_trade_value=request.min_trade_value
    )

    # Add summary statistics
    sell_transactions = [tx for tx in plan['transactions'] if tx['action'] == 'SELL']
    buy_transactions = [tx for tx in plan['transactions'] if tx['action'] == 'BUY']

    plan['summary'] = {
        'total_transactions': len(plan['transactions']),
        'sell_transactions': len(sell_transactions),
        'buy_transactions': len(buy_transactions),
        'total_sell_value': sum(tx['estimated_value'] for tx in sell_transactions),
        'total_buy_value': sum(tx['estimated_value'] for tx in buy_transactions),
        'net_cash_flow': sum(tx['estimated_value'] for tx in sell_transactions) - sum(tx['estimated_value'] for tx in buy_transactions)
    }

    return plan


@router.post("/analyze-drift-history", response_model=Dict[str, Any])
async def analyze_drift_history(
    request: HistoricalDriftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze historical drift patterns.

    Provides insights into drift trends and recommended rebalancing frequency.
    """
    rebalancer = PortfolioRebalancer()

    target_allocation = [
        TargetAllocation(
            asset_class=ta.asset_class,
            target_percentage=ta.target_percentage
        )
        for ta in request.target_allocation
    ]

    analysis = rebalancer.analyze_drift_history(
        historical_allocations=request.historical_allocations,
        target_allocation=target_allocation
    )

    return analysis


@router.get("/tolerance-bands", response_model=Dict[str, Any])
async def get_tolerance_bands(
    current_user: User = Depends(get_current_user)
):
    """
    Get recommended tolerance bands for rebalancing.

    Returns common tolerance thresholds and when to use them.
    """
    return {
        'tolerance_bands': [
            {
                'threshold': 0.02,
                'percentage': '2%',
                'description': 'Very tight control',
                'rebalancing_frequency': 'Quarterly or more often',
                'suitable_for': 'Active investors, high volatility portfolios',
                'cost_consideration': 'High transaction costs'
            },
            {
                'threshold': 0.05,
                'percentage': '5%',
                'description': 'Standard tolerance (recommended)',
                'rebalancing_frequency': 'Semi-annually',
                'suitable_for': 'Most investors, balanced portfolios',
                'cost_consideration': 'Moderate transaction costs'
            },
            {
                'threshold': 0.10,
                'percentage': '10%',
                'description': 'Relaxed tolerance',
                'rebalancing_frequency': 'Annually',
                'suitable_for': 'Long-term investors, low volatility portfolios',
                'cost_consideration': 'Low transaction costs'
            },
            {
                'threshold': 0.15,
                'percentage': '15%',
                'description': 'Very relaxed tolerance',
                'rebalancing_frequency': 'Bi-annually or less',
                'suitable_for': 'Buy-and-hold investors',
                'cost_consideration': 'Minimal transaction costs'
            }
        ],
        'factors_to_consider': [
            'Portfolio size (larger portfolios can tolerate wider bands)',
            'Transaction costs (higher costs suggest wider bands)',
            'Tax implications (taxable accounts may need wider bands)',
            'Time horizon (longer horizons can tolerate more drift)',
            'Volatility (higher volatility needs tighter control)'
        ]
    }


@router.get("/tax-efficient-strategies", response_model=Dict[str, Any])
async def get_tax_efficient_strategies(
    current_user: User = Depends(get_current_user)
):
    """
    Get tax-efficient rebalancing strategies for UK investors.

    Returns best practices for minimizing tax impact during rebalancing.
    """
    return {
        'strategies': [
            {
                'name': 'ISA Rebalancing',
                'description': 'Rebalance within ISA first',
                'benefit': 'Tax-free trading',
                'implementation': 'Sell overweight positions and buy underweight positions within ISA wrapper',
                'priority': 1
            },
            {
                'name': 'SIPP Rebalancing',
                'description': 'Rebalance within pension next',
                'benefit': 'Tax-free trading',
                'implementation': 'Use SIPP for tax-free rebalancing, especially for large adjustments',
                'priority': 2
            },
            {
                'name': 'Tax-Loss Harvesting',
                'description': 'Sell positions with losses first',
                'benefit': 'Offset capital gains with losses',
                'implementation': 'In taxable accounts, sell losing positions to realize losses for tax purposes',
                'priority': 3
            },
            {
                'name': 'CGT Allowance Utilization',
                'description': 'Use annual CGT allowance (£3,000)',
                'benefit': 'Tax-free gains up to allowance',
                'implementation': 'Realize gains up to CGT allowance each year, especially late in tax year',
                'priority': 4
            },
            {
                'name': 'New Money Rebalancing',
                'description': 'Use new contributions to rebalance',
                'benefit': 'No selling required',
                'implementation': 'Direct new investments to underweight asset classes',
                'priority': 5
            },
            {
                'name': 'Dividend Reinvestment',
                'description': 'Reinvest dividends into underweight classes',
                'benefit': 'Passive rebalancing',
                'implementation': 'Change dividend reinvestment settings to favor underweight positions',
                'priority': 6
            }
        ],
        'timing_considerations': [
            'End of tax year (April 5th) - utilize CGT allowance',
            'After receiving bonuses or large income - add new money',
            'Market volatility - rebalance after significant moves',
            'ISA allowance - use annual £20,000 allowance strategically'
        ],
        'accounts_priority': [
            '1. ISA - Tax-free, rebalance here first',
            '2. SIPP - Tax-free, rebalance pensions next',
            '3. GIA - Taxable, minimize trading here, use tax-loss harvesting'
        ]
    }