"""
Portfolio Rebalancing Service

Provides portfolio drift analysis, rebalancing recommendations,
and tax-efficient rebalancing strategies.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass


@dataclass
class Holding:
    """Represents a single investment holding."""
    asset_class: str
    ticker: str
    name: str
    quantity: float
    current_price: float
    cost_basis: float
    purchase_date: date
    account_type: str  # 'ISA', 'SIPP', 'GIA' (General Investment Account)


@dataclass
class TargetAllocation:
    """Target allocation for an asset class."""
    asset_class: str
    target_percentage: float


@dataclass
class RebalancingTransaction:
    """Recommended transaction for rebalancing."""
    action: str  # 'BUY', 'SELL', 'HOLD'
    asset_class: str
    ticker: str
    name: str
    quantity: float
    estimated_value: float
    current_price: float
    account_type: str
    reason: str
    cgt_impact: float  # Capital gains tax impact if selling


class PortfolioRebalancer:
    """
    Portfolio rebalancing engine with drift analysis and tax optimization.

    Features:
    - Portfolio drift calculation
    - Tax-efficient rebalancing (minimize CGT)
    - Transaction cost analysis
    - Tolerance band support
    - Multi-account rebalancing
    """

    def __init__(self):
        # UK Capital Gains Tax rates for 2024/25
        self.cgt_allowance = 3000  # Annual CGT allowance
        self.cgt_basic_rate = 0.10  # 10% for basic rate taxpayers
        self.cgt_higher_rate = 0.20  # 20% for higher rate taxpayers

        # Transaction costs
        self.transaction_cost_percentage = 0.0025  # 0.25% typical platform fee
        self.min_transaction_cost = 5.0  # Minimum £5 per trade

        # Default tolerance bands
        self.default_tolerance = 0.05  # 5% drift tolerance

    def calculate_portfolio_value(self, holdings: List[Holding]) -> float:
        """Calculate total portfolio value."""
        return sum(h.quantity * h.current_price for h in holdings)

    def calculate_current_allocation(self, holdings: List[Holding]) -> Dict[str, float]:
        """
        Calculate current asset allocation as percentages.

        Returns:
            Dict mapping asset_class to percentage of portfolio
        """
        total_value = self.calculate_portfolio_value(holdings)

        if total_value == 0:
            return {}

        allocation = {}
        for holding in holdings:
            asset_class = holding.asset_class
            holding_value = holding.quantity * holding.current_price

            if asset_class in allocation:
                allocation[asset_class] += holding_value
            else:
                allocation[asset_class] = holding_value

        # Convert to percentages
        return {
            asset_class: (value / total_value * 100)
            for asset_class, value in allocation.items()
        }

    def calculate_drift(
        self,
        current_allocation: Dict[str, float],
        target_allocation: List[TargetAllocation]
    ) -> Dict[str, float]:
        """
        Calculate drift from target allocation.

        Returns:
            Dict mapping asset_class to drift percentage (positive = overweight)
        """
        target_dict = {ta.asset_class: ta.target_percentage for ta in target_allocation}
        drift = {}

        # Calculate drift for each asset class
        all_asset_classes = set(current_allocation.keys()) | set(target_dict.keys())

        for asset_class in all_asset_classes:
            current = current_allocation.get(asset_class, 0.0)
            target = target_dict.get(asset_class, 0.0)
            drift[asset_class] = current - target

        return drift

    def calculate_cgt_on_sale(
        self,
        holding: Holding,
        quantity_to_sell: float,
        annual_cgt_used: float = 0.0,
        tax_rate: str = 'higher'
    ) -> float:
        """
        Calculate CGT liability on selling a position.

        Args:
            holding: The holding to sell
            quantity_to_sell: Number of shares/units to sell
            annual_cgt_used: Amount of annual CGT allowance already used
            tax_rate: 'basic' or 'higher' rate taxpayer

        Returns:
            CGT liability in GBP
        """
        # Calculate gain on sale
        cost_basis = holding.cost_basis * quantity_to_sell
        sale_proceeds = holding.current_price * quantity_to_sell
        gross_gain = sale_proceeds - cost_basis

        if gross_gain <= 0:
            return 0.0  # No CGT on losses

        # ISAs and SIPPs are tax-free
        if holding.account_type in ['ISA', 'SIPP']:
            return 0.0

        # Apply CGT allowance
        remaining_allowance = max(0, self.cgt_allowance - annual_cgt_used)
        taxable_gain = max(0, gross_gain - remaining_allowance)

        # Apply appropriate tax rate
        rate = self.cgt_higher_rate if tax_rate == 'higher' else self.cgt_basic_rate

        return taxable_gain * rate

    def calculate_transaction_cost(self, transaction_value: float) -> float:
        """Calculate transaction cost for a trade."""
        percentage_cost = transaction_value * self.transaction_cost_percentage
        return max(percentage_cost, self.min_transaction_cost)

    def generate_rebalancing_plan(
        self,
        holdings: List[Holding],
        target_allocation: List[TargetAllocation],
        tolerance: float = None,
        tax_rate: str = 'higher',
        annual_cgt_used: float = 0.0,
        min_trade_value: float = 100.0
    ) -> Dict[str, Any]:
        """
        Generate comprehensive rebalancing plan.

        Args:
            holdings: Current portfolio holdings
            target_allocation: Target allocation
            tolerance: Drift tolerance (default 5%)
            tax_rate: Tax rate for CGT calculations
            annual_cgt_used: CGT allowance already used this year
            min_trade_value: Minimum trade value to avoid small transactions

        Returns:
            Dict with analysis and recommendations
        """
        if tolerance is None:
            tolerance = self.default_tolerance

        total_value = self.calculate_portfolio_value(holdings)
        current_allocation = self.calculate_current_allocation(holdings)
        drift = self.calculate_drift(current_allocation, target_allocation)

        # Identify asset classes needing rebalancing
        needs_rebalancing = {
            asset_class: drift_pct
            for asset_class, drift_pct in drift.items()
            if abs(drift_pct) > (tolerance * 100)
        }

        # Generate transactions
        transactions = []
        total_cgt = 0.0
        total_transaction_costs = 0.0
        cgt_running_total = annual_cgt_used

        # First pass: Identify sells (overweight positions)
        for asset_class, drift_pct in needs_rebalancing.items():
            if drift_pct > 0:  # Overweight - need to sell
                # Find holdings in this asset class
                class_holdings = [h for h in holdings if h.asset_class == asset_class]

                # Calculate amount to sell
                sell_value = (drift_pct / 100) * total_value

                if sell_value < min_trade_value:
                    continue

                # Prioritize selling from taxable accounts first (tax-loss harvesting opportunity)
                # Then sell from most profitable holdings in taxable accounts (use CGT allowance)
                taxable_holdings = [h for h in class_holdings if h.account_type == 'GIA']
                tax_free_holdings = [h for h in class_holdings if h.account_type in ['ISA', 'SIPP']]

                # Sort taxable by gain/loss (sell losses first for tax-loss harvesting)
                taxable_holdings.sort(
                    key=lambda h: (h.current_price - h.cost_basis) * h.quantity
                )

                remaining_to_sell = sell_value

                for holding in taxable_holdings + tax_free_holdings:
                    if remaining_to_sell <= 0:
                        break

                    holding_value = holding.quantity * holding.current_price
                    sell_this = min(holding_value, remaining_to_sell)
                    quantity = sell_this / holding.current_price

                    # Calculate CGT
                    cgt = self.calculate_cgt_on_sale(
                        holding, quantity, cgt_running_total, tax_rate
                    )
                    cgt_running_total += cgt
                    total_cgt += cgt

                    # Calculate transaction cost
                    tx_cost = self.calculate_transaction_cost(sell_this)
                    total_transaction_costs += tx_cost

                    transactions.append(RebalancingTransaction(
                        action='SELL',
                        asset_class=asset_class,
                        ticker=holding.ticker,
                        name=holding.name,
                        quantity=quantity,
                        estimated_value=sell_this,
                        current_price=holding.current_price,
                        account_type=holding.account_type,
                        reason=f'Overweight by {drift_pct:.1f}% (target {[ta.target_percentage for ta in target_allocation if ta.asset_class == asset_class][0]:.1f}%)',
                        cgt_impact=cgt
                    ))

                    remaining_to_sell -= sell_this

        # Second pass: Identify buys (underweight positions)
        for asset_class, drift_pct in needs_rebalancing.items():
            if drift_pct < 0:  # Underweight - need to buy
                buy_value = abs(drift_pct / 100) * total_value

                if buy_value < min_trade_value:
                    continue

                # For buys, recommend a representative ticker (user can choose specific investment)
                # In real implementation, would suggest specific holdings
                tx_cost = self.calculate_transaction_cost(buy_value)
                total_transaction_costs += tx_cost

                # Recommend buying in tax-advantaged accounts first
                account_recommendation = 'ISA' if buy_value <= 20000 else 'GIA'

                transactions.append(RebalancingTransaction(
                    action='BUY',
                    asset_class=asset_class,
                    ticker=f'{asset_class}_ETF',  # Placeholder
                    name=f'{asset_class} (Select Investment)',
                    quantity=0,  # To be determined
                    estimated_value=buy_value,
                    current_price=0,
                    account_type=account_recommendation,
                    reason=f'Underweight by {abs(drift_pct):.1f}% (target {[ta.target_percentage for ta in target_allocation if ta.asset_class == asset_class][0]:.1f}%)',
                    cgt_impact=0.0
                ))

        # Calculate total costs and benefits
        total_costs = total_cgt + total_transaction_costs

        # Estimate benefit (reduced from perfect rebalancing, simplified)
        estimated_annual_benefit = total_value * 0.005  # Assume 0.5% annual benefit
        payback_period_years = total_costs / estimated_annual_benefit if estimated_annual_benefit > 0 else 0

        return {
            'portfolio_value': total_value,
            'current_allocation': current_allocation,
            'target_allocation': {ta.asset_class: ta.target_percentage for ta in target_allocation},
            'drift': drift,
            'needs_rebalancing': needs_rebalancing,
            'rebalancing_required': len(needs_rebalancing) > 0,
            'transactions': [
                {
                    'action': tx.action,
                    'asset_class': tx.asset_class,
                    'ticker': tx.ticker,
                    'name': tx.name,
                    'quantity': round(tx.quantity, 4),
                    'estimated_value': round(tx.estimated_value, 2),
                    'current_price': round(tx.current_price, 2),
                    'account_type': tx.account_type,
                    'reason': tx.reason,
                    'cgt_impact': round(tx.cgt_impact, 2)
                }
                for tx in transactions
            ],
            'cost_analysis': {
                'total_cgt': round(total_cgt, 2),
                'total_transaction_costs': round(total_transaction_costs, 2),
                'total_costs': round(total_costs, 2),
                'estimated_annual_benefit': round(estimated_annual_benefit, 2),
                'payback_period_years': round(payback_period_years, 2),
                'cost_benefit_ratio': round(total_costs / total_value * 100, 4) if total_value > 0 else 0,
                'recommendation': 'Proceed with rebalancing' if total_costs < estimated_annual_benefit * 2 else 'Consider delaying rebalancing due to high costs'
            },
            'tax_analysis': {
                'cgt_allowance_available': self.cgt_allowance,
                'cgt_allowance_used_before': annual_cgt_used,
                'cgt_allowance_used_by_rebalancing': round(cgt_running_total - annual_cgt_used, 2),
                'cgt_allowance_remaining': round(max(0, self.cgt_allowance - cgt_running_total), 2),
                'tax_rate_used': tax_rate
            }
        }

    def analyze_drift_history(
        self,
        historical_allocations: List[Dict[str, Any]],
        target_allocation: List[TargetAllocation]
    ) -> Dict[str, Any]:
        """
        Analyze historical drift patterns.

        Args:
            historical_allocations: List of {date, allocation} dicts
            target_allocation: Target allocation

        Returns:
            Drift analysis with trends
        """
        drift_history = []

        for hist in historical_allocations:
            drift = self.calculate_drift(hist['allocation'], target_allocation)
            drift_history.append({
                'date': hist['date'],
                'drift': drift,
                'max_drift': max(abs(d) for d in drift.values()) if drift else 0
            })

        # Calculate statistics
        if drift_history:
            max_drifts = [d['max_drift'] for d in drift_history]
            avg_max_drift = sum(max_drifts) / len(max_drifts)

            return {
                'drift_history': drift_history,
                'average_max_drift': round(avg_max_drift, 2),
                'current_max_drift': max_drifts[-1] if max_drifts else 0,
                'drift_increasing': max_drifts[-1] > avg_max_drift if max_drifts else False,
                'rebalancing_frequency_recommendation': self._recommend_rebalancing_frequency(avg_max_drift)
            }

        return {'drift_history': [], 'average_max_drift': 0, 'current_max_drift': 0}

    def _recommend_rebalancing_frequency(self, avg_max_drift: float) -> str:
        """Recommend rebalancing frequency based on drift patterns."""
        if avg_max_drift > 10:
            return 'Quarterly (high drift)'
        elif avg_max_drift > 5:
            return 'Semi-annually (moderate drift)'
        else:
            return 'Annually (low drift)'