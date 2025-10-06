from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.product import Product, Pension, Investment, Savings, Protection
from app.models.user import User
from app.api.auth.auth import get_current_user
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
import json

router = APIRouter(prefix="/products", tags=["Products"])


class ProductBase(BaseModel):
    product_type: str  # pension, investment, savings, protection
    provider: str
    product_name: str
    status: str = "active"  # active, closed, pending
    notes: Optional[str] = None


class PensionCreate(ProductBase):
    pension_type: str  # workplace, SIPP, personal
    current_value: float
    monthly_contribution: float = 0.0
    employer_contribution: float = 0.0
    tax_relief_percentage: float = 20.0
    annual_charges: float = 0.0
    projected_retirement_date: Optional[date] = None
    projected_value: Optional[float] = None


class InvestmentCreate(ProductBase):
    investment_type: str  # ISA, GIA, JISA, LISA
    current_value: float
    monthly_contribution: float = 0.0
    annual_allowance: Optional[float] = None
    risk_level: str = "medium"  # low, medium, high
    platform_fees: float = 0.0
    fund_fees: float = 0.0


class SavingsCreate(ProductBase):
    savings_type: str  # instant_access, fixed_term, regular_saver
    current_balance: float
    interest_rate: float
    monthly_deposit: float = 0.0
    maturity_date: Optional[date] = None
    notice_period_days: Optional[int] = None
    minimum_balance: float = 0.0


class ProtectionCreate(ProductBase):
    protection_type: str  # life, critical_illness, income_protection, health
    sum_assured: float
    monthly_premium: float
    start_date: date
    end_date: Optional[date] = None
    beneficiaries: Optional[str] = None
    cover_details: Optional[str] = None
    includes_critical_illness: bool = False
    includes_waiver_of_premium: bool = False


class ProductResponse(ProductBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    extra_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ProductSummary(BaseModel):
    total_pension_value: float
    total_investment_value: float
    total_savings_value: float
    total_protection_cover: float
    monthly_pension_contributions: float
    monthly_investment_contributions: float
    monthly_savings_deposits: float
    monthly_protection_premiums: float
    total_portfolio_value: float
    product_count_by_type: Dict[str, int]


@router.post("/pension", response_model=ProductResponse)
async def create_pension(
    pension: PensionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pension_data = pension.dict()
    base_data = {
        "product_type": "pension",
        "provider": pension_data.pop("provider"),
        "product_name": pension_data.pop("product_name"),
        "status": pension_data.pop("status"),
        "notes": pension_data.pop("notes"),
        "user_id": current_user.id
    }

    pension_data.pop("product_type", None)
    pension_data = {k: str(v) if isinstance(v, date) else v for k, v in pension_data.items()}
    base_data["extra_metadata"] = json.dumps(pension_data)

    db_pension = Pension(**base_data)
    db.add(db_pension)
    db.commit()
    db.refresh(db_pension)

    if db_pension.extra_metadata:
        db_pension.extra_metadata = json.loads(db_pension.extra_metadata)

    return db_pension


@router.post("/investment", response_model=ProductResponse)
async def create_investment(
    investment: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    investment_data = investment.dict()
    base_data = {
        "product_type": "investment",
        "provider": investment_data.pop("provider"),
        "product_name": investment_data.pop("product_name"),
        "status": investment_data.pop("status"),
        "notes": investment_data.pop("notes"),
        "user_id": current_user.id
    }

    investment_data.pop("product_type", None)
    base_data["extra_metadata"] = json.dumps(investment_data)

    db_investment = Investment(**base_data)
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)

    if db_investment.extra_metadata:
        db_investment.extra_metadata = json.loads(db_investment.extra_metadata)

    return db_investment


@router.post("/savings", response_model=ProductResponse)
async def create_savings(
    savings: SavingsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    savings_data = savings.dict()
    base_data = {
        "product_type": "savings",
        "provider": savings_data.pop("provider"),
        "product_name": savings_data.pop("product_name"),
        "status": savings_data.pop("status"),
        "notes": savings_data.pop("notes"),
        "user_id": current_user.id
    }

    savings_data.pop("product_type", None)
    savings_data = {k: str(v) if isinstance(v, date) else v for k, v in savings_data.items()}
    base_data["extra_metadata"] = json.dumps(savings_data)

    db_savings = Savings(**base_data)
    db.add(db_savings)
    db.commit()
    db.refresh(db_savings)

    if db_savings.extra_metadata:
        db_savings.extra_metadata = json.loads(db_savings.extra_metadata)

    return db_savings


@router.post("/protection", response_model=ProductResponse)
async def create_protection(
    protection: ProtectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    protection_data = protection.dict()
    base_data = {
        "product_type": "protection",
        "provider": protection_data.pop("provider"),
        "product_name": protection_data.pop("product_name"),
        "status": protection_data.pop("status"),
        "notes": protection_data.pop("notes"),
        "user_id": current_user.id
    }

    protection_data.pop("product_type", None)
    protection_data = {k: str(v) if isinstance(v, date) else v for k, v in protection_data.items()}
    base_data["extra_metadata"] = json.dumps(protection_data)

    db_protection = Protection(**base_data)
    db.add(db_protection)
    db.commit()
    db.refresh(db_protection)

    if db_protection.extra_metadata:
        db_protection.extra_metadata = json.loads(db_protection.extra_metadata)

    return db_protection


@router.get("/", response_model=List[ProductResponse])
async def get_all_products(
    product_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.user_id == current_user.id)

    if product_type:
        query = query.filter(Product.product_type == product_type)
    if status:
        query = query.filter(Product.status == status)

    products = query.all()

    for product in products:
        if product.extra_metadata:
            try:
                product.extra_metadata = json.loads(product.extra_metadata)
            except:
                product.extra_metadata = {}

    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if product.extra_metadata:
        try:
            product.extra_metadata = json.loads(product.extra_metadata)
        except:
            product.extra_metadata = {}

    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    updates: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    base_fields = ["provider", "product_name", "status", "notes"]
    metadata_updates = {}

    for key, value in updates.items():
        if key in base_fields:
            setattr(product, key, value)
        else:
            metadata_updates[key] = value

    if metadata_updates:
        current_metadata = json.loads(product.extra_metadata) if product.extra_metadata else {}
        current_metadata.update(metadata_updates)
        product.extra_metadata = json.dumps(current_metadata)

    db.commit()
    db.refresh(product)

    if product.extra_metadata:
        product.extra_metadata = json.loads(product.extra_metadata)

    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


@router.get("/summary/all", response_model=ProductSummary)
async def get_products_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.status == "active"
    ).all()

    summary = {
        "total_pension_value": 0.0,
        "total_investment_value": 0.0,
        "total_savings_value": 0.0,
        "total_protection_cover": 0.0,
        "monthly_pension_contributions": 0.0,
        "monthly_investment_contributions": 0.0,
        "monthly_savings_deposits": 0.0,
        "monthly_protection_premiums": 0.0,
        "product_count_by_type": {}
    }

    for product in products:
        product_type = product.product_type
        summary["product_count_by_type"][product_type] = summary["product_count_by_type"].get(product_type, 0) + 1

        if product.extra_metadata:
            try:
                metadata = json.loads(product.extra_metadata)
            except:
                continue

            if product_type == "pension":
                summary["total_pension_value"] += float(metadata.get("current_value", 0))
                summary["monthly_pension_contributions"] += float(metadata.get("monthly_contribution", 0))
                summary["monthly_pension_contributions"] += float(metadata.get("employer_contribution", 0))

            elif product_type == "investment":
                summary["total_investment_value"] += float(metadata.get("current_value", 0))
                summary["monthly_investment_contributions"] += float(metadata.get("monthly_contribution", 0))

            elif product_type == "savings":
                summary["total_savings_value"] += float(metadata.get("current_balance", 0))
                summary["monthly_savings_deposits"] += float(metadata.get("monthly_deposit", 0))

            elif product_type == "protection":
                summary["total_protection_cover"] += float(metadata.get("sum_assured", 0))
                summary["monthly_protection_premiums"] += float(metadata.get("monthly_premium", 0))

    summary["total_portfolio_value"] = (
        summary["total_pension_value"] +
        summary["total_investment_value"] +
        summary["total_savings_value"]
    )

    return ProductSummary(**summary)