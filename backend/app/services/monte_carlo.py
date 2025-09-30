"""Monte Carlo simulation service for financial projections and IHT calculations."""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class MonteCarloParams:
    """Parameters for Monte Carlo simulation."""
    initial_value: float
    expected_return: float
    volatility: float
    years: int
    simulations: int = 1000
    confidence_levels: List[float] = None

    def __post_init__(self):
        if self.confidence_levels is None:
            self.confidence_levels = [0.05, 0.25, 0.50, 0.75, 0.95]

@dataclass
class IHTMonteCarloParams:
    """Parameters specific to IHT Monte Carlo simulations."""
    current_estate_value: float
    annual_growth_rate_mean: float
    annual_growth_rate_std: float
    years_to_project: int
    life_expectancy_years: float
    life_expectancy_std: float
    annual_gift_allowance: float
    planned_gifts: List[Dict[str, float]]
    simulations: int = 1000
    nil_rate_band: float = 325000
    residence_nil_rate_band: float = 175000
    iht_rate: float = 0.40

class MonteCarloSimulator:
    """Monte Carlo simulation engine for financial projections."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize the simulator with optional random seed for reproducibility."""
        if seed:
            np.random.seed(seed)

    def simulate_asset_growth(self, params: MonteCarloParams) -> Dict:
        """
        Simulate asset growth using geometric Brownian motion.

        Returns:
            Dictionary containing simulation results and statistics
        """
        dt = 1 / 252  # Daily time steps (252 trading days per year)
        n_steps = int(params.years * 252)

        # Initialize arrays for all simulations
        simulations = np.zeros((params.simulations, n_steps + 1))
        simulations[:, 0] = params.initial_value

        # Generate random walks for all simulations at once
        drift = (params.expected_return - 0.5 * params.volatility ** 2) * dt
        diffusion = params.volatility * np.sqrt(dt)

        for t in range(1, n_steps + 1):
            z = np.random.standard_normal(params.simulations)
            simulations[:, t] = simulations[:, t-1] * np.exp(drift + diffusion * z)

        # Calculate statistics
        final_values = simulations[:, -1]
        percentiles = np.percentile(final_values, [p * 100 for p in params.confidence_levels])

        # Calculate value at risk (VaR) and conditional value at risk (CVaR)
        var_95 = np.percentile(final_values, 5)
        cvar_95 = np.mean(final_values[final_values <= var_95])

        # Time series statistics (sample every 21 days = monthly)
        monthly_indices = list(range(0, n_steps + 1, 21))
        monthly_percentiles = []
        for i in monthly_indices:
            monthly_percentiles.append({
                'month': i // 21,
                'percentiles': {
                    f'p{int(p*100)}': float(np.percentile(simulations[:, i], p * 100))
                    for p in params.confidence_levels
                }
            })

        return {
            'params': {
                'initial_value': params.initial_value,
                'expected_return': params.expected_return,
                'volatility': params.volatility,
                'years': params.years,
                'simulations': params.simulations
            },
            'final_values': {
                'mean': float(np.mean(final_values)),
                'std': float(np.std(final_values)),
                'min': float(np.min(final_values)),
                'max': float(np.max(final_values)),
                'percentiles': {
                    f'p{int(p*100)}': float(val)
                    for p, val in zip(params.confidence_levels, percentiles)
                }
            },
            'risk_metrics': {
                'var_95': float(var_95),
                'cvar_95': float(cvar_95),
                'probability_of_loss': float(np.mean(final_values < params.initial_value)),
                'expected_shortfall': float(cvar_95 - params.initial_value) if cvar_95 < params.initial_value else 0
            },
            'time_series': monthly_percentiles,
            'distribution': {
                'histogram': np.histogram(final_values, bins=50)[0].tolist(),
                'bin_edges': np.histogram(final_values, bins=50)[1].tolist()
            }
        }

    def simulate_iht_scenarios(self, params: IHTMonteCarloParams) -> Dict:
        """
        Simulate IHT liability under various scenarios.

        Considers:
        - Estate growth uncertainty
        - Life expectancy uncertainty
        - Gift strategies
        - Tax threshold changes
        """
        results = []

        for sim in range(params.simulations):
            # Simulate life expectancy
            years_of_life = max(1, np.random.normal(
                params.life_expectancy_years,
                params.life_expectancy_std
            ))

            # Simulate estate value growth
            estate_value = params.current_estate_value
            total_gifts_made = 0

            for year in range(int(min(years_of_life, params.years_to_project))):
                # Annual growth with uncertainty
                growth_rate = np.random.normal(
                    params.annual_growth_rate_mean,
                    params.annual_growth_rate_std
                )
                estate_value *= (1 + growth_rate)

                # Apply annual gift allowance
                estate_value -= params.annual_gift_allowance
                total_gifts_made += params.annual_gift_allowance

                # Apply planned gifts
                for gift in params.planned_gifts:
                    if gift['year'] == year:
                        estate_value -= gift['amount']
                        total_gifts_made += gift['amount']

                # Ensure estate value doesn't go negative
                estate_value = max(0, estate_value)

            # Calculate IHT liability
            taxable_estate = max(0, estate_value - params.nil_rate_band - params.residence_nil_rate_band)
            iht_liability = taxable_estate * params.iht_rate

            results.append({
                'final_estate_value': estate_value,
                'iht_liability': iht_liability,
                'effective_tax_rate': iht_liability / estate_value if estate_value > 0 else 0,
                'total_gifts': total_gifts_made,
                'years_lived': years_of_life
            })

        # Aggregate statistics
        iht_liabilities = [r['iht_liability'] for r in results]
        estate_values = [r['final_estate_value'] for r in results]
        effective_rates = [r['effective_tax_rate'] for r in results]

        return {
            'params': {
                'current_estate_value': params.current_estate_value,
                'years_to_project': params.years_to_project,
                'simulations': params.simulations
            },
            'iht_liability': {
                'mean': float(np.mean(iht_liabilities)),
                'std': float(np.std(iht_liabilities)),
                'min': float(np.min(iht_liabilities)),
                'max': float(np.max(iht_liabilities)),
                'percentiles': {
                    'p5': float(np.percentile(iht_liabilities, 5)),
                    'p25': float(np.percentile(iht_liabilities, 25)),
                    'p50': float(np.percentile(iht_liabilities, 50)),
                    'p75': float(np.percentile(iht_liabilities, 75)),
                    'p95': float(np.percentile(iht_liabilities, 95))
                }
            },
            'estate_value': {
                'mean': float(np.mean(estate_values)),
                'std': float(np.std(estate_values)),
                'percentiles': {
                    'p5': float(np.percentile(estate_values, 5)),
                    'p25': float(np.percentile(estate_values, 25)),
                    'p50': float(np.percentile(estate_values, 50)),
                    'p75': float(np.percentile(estate_values, 75)),
                    'p95': float(np.percentile(estate_values, 95))
                }
            },
            'effective_tax_rate': {
                'mean': float(np.mean(effective_rates)),
                'std': float(np.std(effective_rates)),
                'min': float(np.min(effective_rates)),
                'max': float(np.max(effective_rates))
            },
            'probability_thresholds': {
                'prob_no_iht': float(np.mean([r['iht_liability'] == 0 for r in results])),
                'prob_iht_over_100k': float(np.mean([r['iht_liability'] > 100000 for r in results])),
                'prob_iht_over_500k': float(np.mean([r['iht_liability'] > 500000 for r in results])),
                'prob_iht_over_1m': float(np.mean([r['iht_liability'] > 1000000 for r in results]))
            },
            'distribution': {
                'iht_histogram': np.histogram(iht_liabilities, bins=30)[0].tolist(),
                'iht_bin_edges': np.histogram(iht_liabilities, bins=30)[1].tolist(),
                'estate_histogram': np.histogram(estate_values, bins=30)[0].tolist(),
                'estate_bin_edges': np.histogram(estate_values, bins=30)[1].tolist()
            }
        }

    def optimize_gift_strategy(
        self,
        current_estate: float,
        target_iht: float,
        years_available: int,
        max_annual_gift: float
    ) -> Dict:
        """
        Use Monte Carlo to optimize gift strategy to achieve target IHT liability.
        """
        best_strategy = None
        best_score = float('inf')

        # Try different gift strategies
        strategies = []
        for annual_gift in np.linspace(0, max_annual_gift, 20):
            params = IHTMonteCarloParams(
                current_estate_value=current_estate,
                annual_growth_rate_mean=0.05,
                annual_growth_rate_std=0.10,
                years_to_project=years_available,
                life_expectancy_years=years_available,
                life_expectancy_std=5,
                annual_gift_allowance=annual_gift,
                planned_gifts=[],
                simulations=500
            )

            result = self.simulate_iht_scenarios(params)
            mean_iht = result['iht_liability']['mean']
            score = abs(mean_iht - target_iht)

            strategies.append({
                'annual_gift': annual_gift,
                'expected_iht': mean_iht,
                'score': score
            })

            if score < best_score:
                best_score = score
                best_strategy = {
                    'annual_gift': annual_gift,
                    'total_gifts': annual_gift * years_available,
                    'expected_iht': mean_iht,
                    'iht_reduction': current_estate * 0.4 - mean_iht
                }

        return {
            'optimal_strategy': best_strategy,
            'all_strategies': sorted(strategies, key=lambda x: x['score'])[:5]
        }

def run_portfolio_monte_carlo(
    portfolio_value: float,
    expected_return: float,
    volatility: float,
    years: int,
    simulations: int = 1000
) -> Dict:
    """Convenience function to run portfolio Monte Carlo simulation."""
    simulator = MonteCarloSimulator()
    params = MonteCarloParams(
        initial_value=portfolio_value,
        expected_return=expected_return,
        volatility=volatility,
        years=years,
        simulations=simulations
    )
    return simulator.simulate_asset_growth(params)

def run_iht_monte_carlo(
    estate_value: float,
    growth_rate: float,
    years: int,
    life_expectancy: float,
    annual_gifts: float = 3000,
    simulations: int = 1000
) -> Dict:
    """Convenience function to run IHT Monte Carlo simulation."""
    simulator = MonteCarloSimulator()
    params = IHTMonteCarloParams(
        current_estate_value=estate_value,
        annual_growth_rate_mean=growth_rate,
        annual_growth_rate_std=0.10,  # 10% standard deviation
        years_to_project=years,
        life_expectancy_years=life_expectancy,
        life_expectancy_std=5,  # 5 years standard deviation
        annual_gift_allowance=annual_gifts,
        planned_gifts=[],
        simulations=simulations
    )
    return simulator.simulate_iht_scenarios(params)