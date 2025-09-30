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

# Module routers
from app.api.modules.protection.protection import router as protection_main_router
from app.api.modules.protection.products import router as protection_products_router
from app.api.modules.protection.analytics import router as protection_analytics_router
from app.api.modules.protection.needs_analysis import router as protection_needs_router

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

# Module routers
app.include_router(protection_main_router, prefix="/api/modules/protection", tags=["Protection Module"])
app.include_router(protection_products_router, prefix="/api/modules/protection/products", tags=["Protection Module - Products"])
app.include_router(protection_analytics_router, prefix="/api/modules/protection/analytics", tags=["Protection Module - Analytics"])
app.include_router(protection_needs_router, prefix="/api/modules/protection/needs-analysis", tags=["Protection Module - Needs Analysis"])


@app.get("/")
async def root():
    return {"message": "Financial Planning API", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}