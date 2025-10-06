"""API endpoints for Monte Carlo simulations and advanced analytics."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

from app.api.auth.auth import get_current_user
from app.models.user import User
from app.services.monte_carlo import (
    MonteCarloSimulator,
    MonteCarloParams,
    IHTMonteCarloParams,
    run_portfolio_monte_carlo,
    run_iht_monte_carlo
)

router = APIRouter(prefix="/api/simulations", tags=["simulations"])

class PortfolioSimulationRequest(BaseModel):
    """Request model for portfolio Monte Carlo simulation."""
    portfolio_value: float = Field(..., gt=0, description="Current portfolio value")
    expected_return: float = Field(..., ge=-1, le=1, description="Expected annual return (as decimal)")
    volatility: float = Field(..., ge=0, le=1, description="Annual volatility (as decimal)")
    years: int = Field(..., ge=1, le=50, description="Years to project")
    simulations: int = Field(1000, ge=100, le=10000, description="Number of simulations")

class IHTSimulationRequest(BaseModel):
    """Request model for IHT Monte Carlo simulation."""
    estate_value: float = Field(..., gt=0, description="Current estate value")
    growth_rate: float = Field(..., ge=-0.2, le=0.5, description="Expected annual growth rate")
    years: int = Field(..., ge=1, le=50, description="Years to project")
    life_expectancy: float = Field(..., ge=1, le=100, description="Expected years of life")
    annual_gifts: float = Field(3000, ge=0, description="Annual gift allowance to use")
    planned_gifts: Optional[List[Dict[str, float]]] = Field(default_factory=list)
    simulations: int = Field(1000, ge=100, le=10000, description="Number of simulations")

class OptimizeGiftStrategyRequest(BaseModel):
    """Request model for gift strategy optimization."""
    current_estate: float = Field(..., gt=0, description="Current estate value")
    target_iht: float = Field(..., ge=0, description="Target IHT liability")
    years_available: int = Field(..., ge=1, le=50, description="Years available for gifting")
    max_annual_gift: float = Field(..., gt=0, description="Maximum annual gift amount")

class MultiAssetSimulationRequest(BaseModel):
    """Request model for multi-asset portfolio simulation."""
    assets: List[Dict[str, float]] = Field(..., description="List of assets with value, return, volatility")
    correlations: Optional[List[List[float]]] = None
    years: int = Field(..., ge=1, le=50)
    rebalancing_frequency: str = Field("quarterly", description="never, annual, quarterly, monthly")
    simulations: int = Field(1000, ge=100, le=10000)

@router.post("/portfolio")
async def simulate_portfolio(
    request: PortfolioSimulationRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Run Monte Carlo simulation for portfolio growth.

    Returns probability distributions and risk metrics.
    """
    try:
        result = run_portfolio_monte_carlo(
            portfolio_value=request.portfolio_value,
            expected_return=request.expected_return,
            volatility=request.volatility,
            years=request.years,
            simulations=request.simulations
        )

        # Add user-specific context
        result['user_id'] = current_user.id
        result['simulation_date'] = datetime.now().isoformat()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.post("/iht")
async def simulate_iht(
    request: IHTSimulationRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Run Monte Carlo simulation for IHT liability.

    Considers estate growth, life expectancy, and gift strategies.
    """
    try:
        simulator = MonteCarloSimulator()

        params = IHTMonteCarloParams(
            current_estate_value=request.estate_value,
            annual_growth_rate_mean=request.growth_rate,
            annual_growth_rate_std=0.10,  # 10% standard deviation
            years_to_project=request.years,
            life_expectancy_years=request.life_expectancy,
            life_expectancy_std=5,  # 5 years standard deviation
            annual_gift_allowance=request.annual_gifts,
            planned_gifts=request.planned_gifts or [],
            simulations=request.simulations
        )

        result = simulator.simulate_iht_scenarios(params)

        # Add user context and recommendations
        result['user_id'] = current_user.id
        result['simulation_date'] = datetime.now().isoformat()

        # Add recommendations based on results
        mean_iht = result['iht_liability']['mean']
        if mean_iht > 500000:
            result['recommendations'] = [
                "Consider increasing annual gifts to reduce estate value",
                "Explore trust structures for estate planning",
                "Review business property relief eligibility",
                "Consider charitable donations for tax relief"
            ]
        elif mean_iht > 100000:
            result['recommendations'] = [
                "Utilize annual gift exemptions fully",
                "Consider gifts to children or grandchildren",
                "Review life insurance for IHT coverage"
            ]
        else:
            result['recommendations'] = [
                "Current IHT exposure is relatively low",
                "Continue monitoring estate value growth",
                "Maintain current gift strategy"
            ]

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IHT simulation failed: {str(e)}")

@router.post("/optimize-gifts")
async def optimize_gift_strategy(
    request: OptimizeGiftStrategyRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Optimize gift strategy to achieve target IHT liability.

    Uses Monte Carlo to find optimal annual gift amounts.
    """
    try:
        simulator = MonteCarloSimulator()

        result = simulator.optimize_gift_strategy(
            current_estate=request.current_estate,
            target_iht=request.target_iht,
            years_available=request.years_available,
            max_annual_gift=request.max_annual_gift
        )

        result['user_id'] = current_user.id
        result['optimization_date'] = datetime.now().isoformat()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.post("/multi-asset")
async def simulate_multi_asset_portfolio(
    request: MultiAssetSimulationRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Run Monte Carlo simulation for multi-asset portfolio with correlations.

    Supports different rebalancing strategies.
    """
    try:
        simulator = MonteCarloSimulator()

        # Extract asset parameters
        n_assets = len(request.assets)
        initial_values = [a['value'] for a in request.assets]
        expected_returns = [a['return'] for a in request.assets]
        volatilities = [a['volatility'] for a in request.assets]

        # Use provided correlations or assume independence
        if request.correlations:
            correlation_matrix = request.correlations
        else:
            correlation_matrix = [[1 if i == j else 0 for j in range(n_assets)] for i in range(n_assets)]

        # Run simulation for each asset
        results = []
        total_portfolio_value = sum(initial_values)

        for i, asset in enumerate(request.assets):
            params = MonteCarloParams(
                initial_value=asset['value'],
                expected_return=asset['return'],
                volatility=asset['volatility'],
                years=request.years,
                simulations=request.simulations
            )
            asset_result = simulator.simulate_asset_growth(params)
            asset_result['asset_name'] = asset.get('name', f'Asset {i+1}')
            asset_result['initial_weight'] = asset['value'] / total_portfolio_value
            results.append(asset_result)

        # Aggregate portfolio results
        portfolio_final_values = sum([r['final_values']['mean'] for r in results])

        return {
            'user_id': current_user.id,
            'simulation_date': datetime.now().isoformat(),
            'assets': results,
            'portfolio_summary': {
                'initial_value': total_portfolio_value,
                'expected_final_value': portfolio_final_values,
                'years': request.years,
                'simulations': request.simulations,
                'rebalancing': request.rebalancing_frequency
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-asset simulation failed: {str(e)}")

@router.get("/scenarios")
async def get_predefined_scenarios(
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get predefined simulation scenarios for quick analysis.
    """
    return {
        'portfolio_scenarios': [
            {
                'name': 'Conservative Growth',
                'description': 'Low risk, steady returns',
                'expected_return': 0.05,
                'volatility': 0.08
            },
            {
                'name': 'Balanced Portfolio',
                'description': 'Moderate risk and return',
                'expected_return': 0.08,
                'volatility': 0.15
            },
            {
                'name': 'Aggressive Growth',
                'description': 'High risk, high potential return',
                'expected_return': 0.12,
                'volatility': 0.25
            }
        ],
        'iht_scenarios': [
            {
                'name': 'Standard Growth',
                'description': 'Average UK property and investment growth',
                'growth_rate': 0.05,
                'annual_gifts': 3000
            },
            {
                'name': 'Property Boom',
                'description': 'High property value growth scenario',
                'growth_rate': 0.08,
                'annual_gifts': 3000
            },
            {
                'name': 'Aggressive Gifting',
                'description': 'Maximum gift strategy',
                'growth_rate': 0.05,
                'annual_gifts': 20000
            }
        ]
    }