from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.base import Base, engine
from app.api.auth.auth import router as auth_router
from app.api.iht import router as iht_router
from app.api.iht_refactored import router as iht_enhanced_router
from app.api.financial_statements import router as financial_router
from app.api.products import router as products_router
from app.api.chat import router as chat_router
from app.api.banking.banking import router as banking_router
from app.api.export import router as export_router
from app.api.simulations import router as simulations_router
from app.api.projections import router as projections_router
from app.api.tax_optimization import router as tax_optimization_router
from app.api.rebalancing import router as rebalancing_router
from app.api.pension.pension_uk import router as pension_uk_router
from app.api.pension.pension_schemes import router as pension_schemes_router
from app.api.pension.pension_optimization import router as pension_optimization_router
from app.api.docs import router as docs_router
from app.api.dashboard import router as dashboard_router
from app.api.tax_profile import router as tax_profile_router
from app.api.income_sources import router as income_sources_router

# Module routers - Protection
from app.api.modules.protection.protection import router as protection_main_router
from app.api.modules.protection.products import router as protection_products_router
from app.api.modules.protection.analytics import router as protection_analytics_router
from app.api.modules.protection.needs_analysis import router as protection_needs_router

# Module routers - Savings
from app.api.modules.savings.savings import router as savings_main_router
from app.api.modules.savings.accounts import router as savings_accounts_router
from app.api.modules.savings.goals import router as savings_goals_router
from app.api.modules.savings.analytics import router as savings_analytics_router

# Module routers - Investment
from app.api.modules.investment.investment import router as investment_main_router
from app.api.modules.investment.portfolio import router as investment_portfolio_router
from app.api.modules.investment.analytics import router as investment_analytics_router
from app.api.modules.investment.rebalancing import router as investment_rebalancing_router

# Module routers - Retirement
from app.api.modules.retirement.retirement import router as retirement_main_router
from app.api.modules.retirement.pensions import router as retirement_pensions_router
from app.api.modules.retirement.projections import router as retirement_projections_router
from app.api.modules.retirement.monte_carlo import router as retirement_monte_carlo_router

# Module routers - IHT Planning
from app.api.modules.iht.iht import router as iht_main_router
from app.api.modules.iht.calculator import router as iht_calculator_router
from app.api.modules.iht.gifts import router as iht_gifts_router
from app.api.modules.iht.trusts import router as iht_trusts_router

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(iht_router, prefix="/api/iht", tags=["IHT"])
app.include_router(iht_enhanced_router, prefix="/api/iht-enhanced", tags=["IHT Enhanced"])
app.include_router(financial_router, prefix="/api/financial", tags=["Financial Statements"])
app.include_router(products_router, prefix="/api/products", tags=["Products"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(banking_router, prefix="/api/banking", tags=["Banking"])
app.include_router(export_router, tags=["Export"])
app.include_router(simulations_router, tags=["Simulations"])
app.include_router(projections_router, tags=["Projections"])
app.include_router(tax_optimization_router, tags=["Tax Optimization"])
app.include_router(rebalancing_router, tags=["Rebalancing"])
app.include_router(pension_uk_router, prefix="/api", tags=["UK Pension"])
app.include_router(pension_schemes_router, prefix="/api", tags=["Pension Schemes"])
app.include_router(pension_optimization_router, prefix="/api", tags=["Pension Optimization"])
app.include_router(docs_router, prefix="/api/docs", tags=["Documentation"])
app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(tax_profile_router, prefix="/api/tax-profile", tags=["Tax Profile"])
app.include_router(income_sources_router, prefix="/api/income-sources", tags=["Income Sources"])

# Module routers
app.include_router(protection_main_router, prefix="/api/modules/protection", tags=["Protection Module"])
app.include_router(protection_products_router, prefix="/api/modules/protection/products", tags=["Protection Module - Products"])
app.include_router(protection_analytics_router, prefix="/api/modules/protection/analytics", tags=["Protection Module - Analytics"])
app.include_router(protection_needs_router, prefix="/api/modules/protection/needs-analysis", tags=["Protection Module - Needs Analysis"])

app.include_router(savings_main_router, prefix="/api/modules/savings", tags=["Savings Module"])
app.include_router(savings_accounts_router, prefix="/api/modules/savings/accounts", tags=["Savings Module - Accounts"])
app.include_router(savings_goals_router, prefix="/api/modules/savings/goals", tags=["Savings Module - Goals"])
app.include_router(savings_analytics_router, prefix="/api/modules/savings/analytics", tags=["Savings Module - Analytics"])

app.include_router(investment_main_router, prefix="/api/modules/investment", tags=["Investment Module"])
app.include_router(investment_portfolio_router, prefix="/api/modules/investment/portfolio", tags=["Investment Module - Portfolio"])
app.include_router(investment_analytics_router, prefix="/api/modules/investment/analytics", tags=["Investment Module - Analytics"])
app.include_router(investment_rebalancing_router, prefix="/api/modules/investment/rebalancing", tags=["Investment Module - Rebalancing"])

app.include_router(retirement_main_router, prefix="/api/modules/retirement", tags=["Retirement Module"])
app.include_router(retirement_pensions_router, prefix="/api/modules/retirement/pensions", tags=["Retirement Module - Pensions"])
app.include_router(retirement_projections_router, prefix="/api/modules/retirement/projections", tags=["Retirement Module - Projections"])
app.include_router(retirement_monte_carlo_router, prefix="/api/modules/retirement/monte-carlo", tags=["Retirement Module - Monte Carlo"])

app.include_router(iht_main_router, prefix="/api/modules/iht", tags=["IHT Planning Module"])
app.include_router(iht_calculator_router, prefix="/api/modules/iht/calculator", tags=["IHT Planning Module - Calculator"])
app.include_router(iht_gifts_router, prefix="/api/modules/iht/gifts", tags=["IHT Planning Module - Gifts"])
app.include_router(iht_trusts_router, prefix="/api/modules/iht/trusts", tags=["IHT Planning Module - Trusts"])


@app.get("/")
async def root():
    return {"message": "Financial Planning API", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}