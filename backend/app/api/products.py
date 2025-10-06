from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from datetime import datetime, date
from pydantic import BaseModel

from app.database import get_db
from app.models.product import Product
from app.api.auth.auth import get_current_user
from app.models.user import User

router = APIRouter()

# Base product schema
class ProductBase(BaseModel):
    product_name: str
    provider: str
    product_type: str
    current_value: float
    start_date: Optional[date] = None
    extra_metadata: Optional[dict] = None

class ProductResponse(ProductBase):
    id: int
    user_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Pension schemas
class PensionCreate(ProductBase):
    product_type: str = "pension"
    pension_type: str  # defined_contribution, defined_benefit, sipp
    employer_contribution: Optional[float] = 0
    employee_contribution: Optional[float] = 0
    retirement_age: Optional[int] = 65
    projected_value: Optional[float] = None
    annual_management_charge: Optional[float] = None

class PensionResponse(PensionCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Investment schemas
class InvestmentCreate(ProductBase):
    product_type: str = "investment"
    investment_type: str  # isa, gia, junior_isa, sipp
    risk_level: str  # low, moderate, high
    annual_return: Optional[float] = None
    management_fee: Optional[float] = None
    platform_fee: Optional[float] = None

class InvestmentResponse(InvestmentCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Protection schemas
class ProtectionCreate(ProductBase):
    product_type: str = "protection"
    protection_type: str  # life, critical_illness, income_protection
    sum_assured: float
    premium_monthly: float
    term_years: Optional[int] = None
    beneficiaries: Optional[str] = None

class ProtectionResponse(ProtectionCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Portfolio summary
class PortfolioSummary(BaseModel):
    total_value: float
    total_pensions: float
    total_investments: float
    total_protection: float
    monthly_contributions: float
    annual_fees: float
    product_count: dict
    allocation_by_type: dict
    risk_distribution: dict

# Get all products
@router.get("/", response_model=List[ProductResponse])
def get_all_products(
    product_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products for the current user, optionally filtered by type"""
    query = db.query(Product).filter(Product.user_id == current_user.id)

    if product_type:
        query = query.filter(Product.product_type == product_type)

    products = query.order_by(Product.created_at.desc()).all()
    return products

# Get specific product with full details
@router.get("/{product_id}/details")
def get_product_details(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific product by ID with ALL details including type-specific information"""
    from app.models.product import PensionDetail, InvestmentDetail, ProtectionDetail, Document

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Build comprehensive response
    response = {
        # Core product fields
        "id": product.id,
        "product_name": product.product_name,
        "provider": product.provider,
        "reference_number": product.reference_number,
        "product_type": product.product_type,
        "module": product.module,

        # Multi-jurisdiction
        "currency": product.currency,
        "jurisdiction": product.jurisdiction,

        # Common fields
        "current_value": product.current_value,
        "initial_investment": product.initial_investment,
        "start_date": product.start_date.isoformat() if product.start_date else None,
        "maturity_date": product.maturity_date.isoformat() if product.maturity_date else None,
        "status": product.status,

        # Performance
        "performance_ytd": product.performance_ytd,
        "performance_1yr": product.performance_1yr,
        "performance_3yr": product.performance_3yr,
        "performance_5yr": product.performance_5yr,

        # Fees
        "annual_charge": product.annual_charge,
        "platform_fee": product.platform_fee,
        "other_fees": product.other_fees,

        # Additional
        "notes": product.notes,
        "extra_metadata": product.extra_metadata,

        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }

    # Add type-specific details
    if product.product_type == "pension" or product.module == "retirement":
        pension_detail = db.query(PensionDetail).filter(PensionDetail.product_id == product.id).first()
        if pension_detail:
            response["pension_details"] = {
                "pension_type": pension_detail.pension_type,
                "retirement_age": pension_detail.retirement_age,
                "projected_value_at_retirement": pension_detail.projected_value_at_retirement,
                "employee_contribution": pension_detail.employee_contribution,
                "employer_contribution": pension_detail.employer_contribution,
                "contribution_frequency": pension_detail.contribution_frequency,
                "death_benefit": pension_detail.death_benefit,
                "guaranteed_period": pension_detail.guaranteed_period,
                "tax_free_cash_percentage": pension_detail.tax_free_cash_percentage,
                "annuity_rate": pension_detail.annuity_rate,
                "includes_spouse_benefit": pension_detail.includes_spouse_benefit,
                "spouse_benefit_percentage": pension_detail.spouse_benefit_percentage,
            }

    elif product.product_type == "investment" or product.module == "investment":
        investment_detail = db.query(InvestmentDetail).filter(InvestmentDetail.product_id == product.id).first()
        if investment_detail:
            response["investment_details"] = {
                "investment_type": investment_detail.investment_type,
                "risk_rating": investment_detail.risk_rating,
                "asset_allocation": investment_detail.asset_allocation,
                "isa_type": investment_detail.isa_type,
                "current_year_contribution": investment_detail.current_year_contribution,
                "isa_allowance_used": investment_detail.isa_allowance_used,
                "investment_strategy": investment_detail.investment_strategy,
                "benchmark": investment_detail.benchmark,
                "fund_codes": investment_detail.fund_codes,
                "regular_investment_amount": investment_detail.regular_investment_amount,
                "regular_investment_frequency": investment_detail.regular_investment_frequency,
            }

    elif product.product_type == "protection" or product.module == "protection":
        protection_detail = db.query(ProtectionDetail).filter(ProtectionDetail.product_id == product.id).first()
        if protection_detail:
            response["protection_details"] = {
                "protection_type": protection_detail.protection_type,
                "sum_assured": protection_detail.sum_assured,
                "premium": protection_detail.premium,
                "premium_frequency": protection_detail.premium_frequency,
                "term_years": protection_detail.term_years,
                "is_joint_policy": protection_detail.is_joint_policy,
                "includes_critical_illness": protection_detail.includes_critical_illness,
                "includes_waiver_of_premium": protection_detail.includes_waiver_of_premium,
                "in_trust": protection_detail.in_trust,
                "trust_details": protection_detail.trust_details,
                "beneficiaries": protection_detail.beneficiaries,
                "smoker_status": protection_detail.smoker_status,
                "medical_conditions": protection_detail.medical_conditions,
            }

    # Add documents
    documents = db.query(Document).filter(Document.product_id == product.id).all()
    response["documents"] = [
        {
            "id": doc.id,
            "document_type": doc.document_type,
            "document_name": doc.document_name,
            "file_path": doc.file_path,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
        }
        for doc in documents
    ]

    return response

# Get product by module/provider/slug
@router.get("/lookup/{module}/{provider}/{slug}")
def get_product_by_slug(
    module: str,
    provider: str,
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a product by module, provider, and slug (product_type-reference_number)"""
    from app.models.product import PensionDetail, InvestmentDetail, ProtectionDetail, Document

    # Normalize module name (URL uses 'pension' but DB uses 'retirement')
    module_normalized = module
    if module.lower() == 'pension':
        module_normalized = 'retirement'

    # Parse slug to extract product_type and reference_number
    # Format: {product_type}-{reference_number}
    # e.g., "workplace-123456" or "isa-345678" or "QROPS-****2345"
    if '-' not in slug:
        raise HTTPException(status_code=400, detail="Invalid slug format. Expected: {product_type}-{reference_number}")

    parts = slug.split('-', 1)  # Split only on first dash
    product_type_from_slug = parts[0]
    reference_number = parts[1]

    # Lookup product
    product = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == module_normalized,
        Product.provider == provider,
        Product.reference_number == reference_number
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail=f"Product not found (module={module_normalized}, provider={provider}, ref={reference_number})")

    # Build comprehensive response (same as get_product_details)
    response = {
        # Core product fields (using frontend-expected field names)
        "id": product.id,
        "name": product.product_name,  # Frontend expects "name"
        "product_name": product.product_name,  # Keep for backwards compatibility
        "provider": product.provider,
        "reference_number": product.reference_number,
        "product_type": product.product_type,
        "module": product.module,

        # Multi-jurisdiction
        "currency": product.currency,
        "jurisdiction": product.jurisdiction,

        # Common fields
        "value": product.current_value,  # Frontend expects "value"
        "current_value": product.current_value,  # Keep for backwards compatibility
        "initial_investment": product.initial_investment,
        "start_date": product.start_date.isoformat() if product.start_date else None,
        "maturity_date": product.maturity_date.isoformat() if product.maturity_date else None,
        "status": product.status,

        # Performance
        "performance_ytd": product.performance_ytd,
        "performance_1yr": product.performance_1yr,
        "performance_3yr": product.performance_3yr,
        "performance_5yr": product.performance_5yr,

        # Fees
        "annual_charge": product.annual_charge,
        "platform_fee": product.platform_fee,
        "other_fees": product.other_fees,

        # Additional
        "notes": product.notes,
        "extra_metadata": product.extra_metadata,

        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }

    # Add type-specific details
    if product.product_type == "pension" or product.module == "retirement":
        pension_detail = db.query(PensionDetail).filter(PensionDetail.product_id == product.id).first()
        if pension_detail:
            response["pension_details"] = {
                "pension_type": pension_detail.pension_type,
                "retirement_age": pension_detail.retirement_age,
                "projected_value_at_retirement": pension_detail.projected_value_at_retirement,
                "employee_contribution": pension_detail.employee_contribution,
                "employer_contribution": pension_detail.employer_contribution,
                "contribution_frequency": pension_detail.contribution_frequency,
                "death_benefit": pension_detail.death_benefit,
                "guaranteed_period": pension_detail.guaranteed_period,
                "tax_free_cash_percentage": pension_detail.tax_free_cash_percentage,
                "annuity_rate": pension_detail.annuity_rate,
                "includes_spouse_benefit": pension_detail.includes_spouse_benefit,
                "spouse_benefit_percentage": pension_detail.spouse_benefit_percentage,
            }

    elif product.product_type == "investment" or product.module == "investment":
        investment_detail = db.query(InvestmentDetail).filter(InvestmentDetail.product_id == product.id).first()
        if investment_detail:
            response["investment_details"] = {
                "investment_type": investment_detail.investment_type,
                "risk_rating": investment_detail.risk_rating,
                "asset_allocation": investment_detail.asset_allocation,
                "isa_type": investment_detail.isa_type,
                "current_year_contribution": investment_detail.current_year_contribution,
                "isa_allowance_used": investment_detail.isa_allowance_used,
                "investment_strategy": investment_detail.investment_strategy,
                "benchmark": investment_detail.benchmark,
                "fund_codes": investment_detail.fund_codes,
                "regular_investment_amount": investment_detail.regular_investment_amount,
                "regular_investment_frequency": investment_detail.regular_investment_frequency,
            }

    elif product.product_type == "protection" or product.module == "protection":
        protection_detail = db.query(ProtectionDetail).filter(ProtectionDetail.product_id == product.id).first()
        if protection_detail:
            response["protection_details"] = {
                "protection_type": protection_detail.protection_type,
                "sum_assured": protection_detail.sum_assured,
                "premium": protection_detail.premium,
                "premium_frequency": protection_detail.premium_frequency,
                "term_years": protection_detail.term_years,
                "is_joint_policy": protection_detail.is_joint_policy,
                "includes_critical_illness": protection_detail.includes_critical_illness,
                "includes_waiver_of_premium": protection_detail.includes_waiver_of_premium,
                "in_trust": protection_detail.in_trust,
                "trust_details": protection_detail.trust_details,
                "beneficiaries": protection_detail.beneficiaries,
                "smoker_status": protection_detail.smoker_status,
                "medical_conditions": protection_detail.medical_conditions,
            }

    # Add documents
    documents = db.query(Document).filter(Document.product_id == product.id).all()
    response["documents"] = [
        {
            "id": doc.id,
            "document_type": doc.document_type,
            "document_name": doc.document_name,
            "file_path": doc.file_path,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
        }
        for doc in documents
    ]

    return response

# Get specific product (basic)
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific product by ID (basic info only)"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

# Pension endpoints
@router.get("/pensions/all", response_model=List[PensionResponse])
def get_pensions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pension products for the current user"""
    pensions = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.product_type == "pension"
    ).all()
    return pensions

@router.post("/pensions", response_model=PensionResponse)
def create_pension(
    pension_data: PensionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new pension product"""
    pension = Product(
        user_id=current_user.id,
        product_type="pension",
        **pension_data.dict(exclude={'product_type'})
    )

    db.add(pension)
    db.commit()
    db.refresh(pension)

    return pension

@router.put("/pensions/{pension_id}", response_model=PensionResponse)
def update_pension(
    pension_id: int,
    pension_data: PensionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing pension product"""
    pension = db.query(Product).filter(
        Product.id == pension_id,
        Product.user_id == current_user.id,
        Product.product_type == "pension"
    ).first()

    if not pension:
        raise HTTPException(status_code=404, detail="Pension not found")

    for key, value in pension_data.dict().items():
        setattr(pension, key, value)

    db.commit()
    db.refresh(pension)

    return pension

# Investment endpoints
@router.get("/investments/all", response_model=List[InvestmentResponse])
def get_investments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all investment products for the current user"""
    investments = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.product_type == "investment"
    ).all()
    return investments

@router.post("/investments", response_model=InvestmentResponse)
def create_investment(
    investment_data: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new investment product"""
    investment = Product(
        user_id=current_user.id,
        product_type="investment",
        **investment_data.dict(exclude={'product_type'})
    )

    db.add(investment)
    db.commit()
    db.refresh(investment)

    return investment

@router.put("/investments/{investment_id}", response_model=InvestmentResponse)
def update_investment(
    investment_id: int,
    investment_data: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing investment product"""
    investment = db.query(Product).filter(
        Product.id == investment_id,
        Product.user_id == current_user.id,
        Product.product_type == "investment"
    ).first()

    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    for key, value in investment_data.dict().items():
        setattr(investment, key, value)

    db.commit()
    db.refresh(investment)

    return investment

# Protection endpoints
@router.get("/protection/all", response_model=List[ProtectionResponse])
def get_protection_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all protection products for the current user"""
    protections = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.product_type == "protection"
    ).all()
    return protections

@router.post("/protection", response_model=ProtectionResponse)
def create_protection(
    protection_data: ProtectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new protection product"""
    protection = Product(
        user_id=current_user.id,
        product_type="protection",
        **protection_data.dict(exclude={'product_type'})
    )

    db.add(protection)
    db.commit()
    db.refresh(protection)

    return protection

# Delete product
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}

# Portfolio summary
@router.get("/portfolio/summary", response_model=PortfolioSummary)
def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive portfolio summary"""

    # Get all products
    all_products = db.query(Product).filter(Product.user_id == current_user.id).all()
    pensions = [p for p in all_products if p.product_type == "pension"]
    investments = [i for i in all_products if i.product_type == "investment"]
    protections = [pr for pr in all_products if pr.product_type == "protection"]

    # Calculate totals
    total_pensions = sum(p.current_value for p in pensions if p.current_value)
    total_investments = sum(i.current_value for i in investments if i.current_value)
    total_protection = sum(
        pr.extra_metadata.get('sum_assured', 0) if pr.extra_metadata else 0
        for pr in protections
    )
    total_value = total_pensions + total_investments

    # Calculate monthly contributions
    monthly_contributions = 0
    for p in pensions:
        if p.extra_metadata:
            monthly_contributions += (
                p.extra_metadata.get('employer_contribution', 0) +
                p.extra_metadata.get('employee_contribution', 0)
            )

    for pr in protections:
        if pr.extra_metadata:
            monthly_contributions += pr.extra_metadata.get('premium_monthly', 0)

    # Calculate annual fees
    annual_fees = 0
    for p in pensions:
        if p.extra_metadata and p.extra_metadata.get('annual_management_charge'):
            annual_fees += (
                (p.current_value or 0) *
                p.extra_metadata.get('annual_management_charge', 0) / 100
            )

    for i in investments:
        if i.extra_metadata:
            if i.extra_metadata.get('management_fee'):
                annual_fees += (
                    (i.current_value or 0) *
                    i.extra_metadata.get('management_fee', 0) / 100
                )
            if i.extra_metadata.get('platform_fee'):
                annual_fees += (
                    (i.current_value or 0) *
                    i.extra_metadata.get('platform_fee', 0) / 100
                )

    # Product count by type
    product_count = {
        "pensions": len(pensions),
        "investments": len(investments),
        "protection": len(protections)
    }

    # Allocation by type
    allocation_by_type = {}
    if total_value > 0:
        allocation_by_type = {
            "pensions": round((total_pensions / total_value) * 100, 1),
            "investments": round((total_investments / total_value) * 100, 1)
        }

    # Risk distribution (for investments)
    risk_distribution = {"low": 0, "moderate": 0, "high": 0}
    for inv in investments:
        if inv.extra_metadata:
            risk_level = inv.extra_metadata.get('risk_level', 'moderate')
            if risk_level in risk_distribution:
                risk_distribution[risk_level] += inv.current_value or 0

    # Convert to percentages
    total_inv = sum(risk_distribution.values())
    if total_inv > 0:
        risk_distribution = {
            k: round((v / total_inv) * 100, 1)
            for k, v in risk_distribution.items()
        }

    return PortfolioSummary(
        total_value=total_value,
        total_pensions=total_pensions,
        total_investments=total_investments,
        total_protection=total_protection,
        monthly_contributions=monthly_contributions,
        annual_fees=annual_fees,
        product_count=product_count,
        allocation_by_type=allocation_by_type,
        risk_distribution=risk_distribution
    )

# Retirement projection endpoint
@router.get("/retirement/projection")
def get_retirement_projection(
    retirement_age: int = 65,
    expected_return: float = 5.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate retirement projection based on current products"""

    # Get current age from user profile (assuming birth_date field exists)
    # For now, we'll use a placeholder
    current_age = 35  # This should come from user profile
    years_to_retirement = retirement_age - current_age

    if years_to_retirement <= 0:
        raise HTTPException(status_code=400, detail="Already past retirement age")

    # Get all pensions
    pensions = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.product_type == "pension"
    ).all()

    current_total = sum(p.current_value for p in pensions)
    annual_contributions = 0

    for p in pensions:
        if p.extra_metadata:
            annual_contributions += (
                (p.extra_metadata.get('employer_contribution', 0) +
                 p.extra_metadata.get('employee_contribution', 0)) * 12
            )

    # Calculate future value with compound interest
    future_value = current_total
    annual_return_rate = expected_return / 100

    for year in range(years_to_retirement):
        future_value = future_value * (1 + annual_return_rate) + annual_contributions

    # Calculate monthly retirement income (4% withdrawal rate)
    annual_retirement_income = future_value * 0.04
    monthly_retirement_income = annual_retirement_income / 12

    return {
        "current_pension_value": current_total,
        "annual_contributions": annual_contributions,
        "years_to_retirement": years_to_retirement,
        "expected_return": expected_return,
        "projected_value_at_retirement": round(future_value, 2),
        "estimated_annual_income": round(annual_retirement_income, 2),
        "estimated_monthly_income": round(monthly_retirement_income, 2)
    }