"""Income Sources API Router

Handles income tracking by country for dual-country tax planning.

Endpoints:
- GET /api/income-sources - List all user's income sources
- POST /api/income-sources - Create new income source
- GET /api/income-sources/{id} - Get specific income source
- PUT /api/income-sources/{id} - Update income source
- DELETE /api/income-sources/{id} - Delete income source
- GET /api/income-sources/summary - Summary by country and type
- GET /api/income-sources/tax-year/{year} - Filter by tax year
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.income_source import IncomeSource


router = APIRouter()


# Pydantic Schemas

class IncomeSourceCreate(BaseModel):
    """Schema for creating an income source."""
    name: str = Field(..., description="Name of income source")
    income_type: str = Field(..., description="salary, dividend, rental, interest, pension, business, capital_gains, other")
    amount: float = Field(..., ge=0)
    currency: str = Field(default="GBP", description="GBP, ZAR, EUR, USD")
    frequency: str = Field(default="annual", description="annual, monthly, quarterly")

    source_country: str = Field(..., description="UK, SA, other")
    paid_in_country: Optional[str] = None
    taxed_at_source: bool = False
    tax_withheld: float = Field(default=0.0, ge=0)

    uk_taxable: bool = True
    sa_taxable: bool = True
    treaty_relief_applicable: bool = False
    treaty_relief_percentage: float = Field(default=0.0, ge=0, le=100)

    uk_tax_deducted: float = Field(default=0.0, ge=0)
    uk_remittance_basis: bool = False

    sa_tax_deducted: float = Field(default=0.0, ge=0)
    sa_exempt_income: bool = False

    tax_year: str = Field(..., description="e.g., '2024/25'")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True
    is_recurring: bool = True

    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class IncomeSourceUpdate(BaseModel):
    """Schema for updating an income source."""
    name: Optional[str] = None
    income_type: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    frequency: Optional[str] = None

    source_country: Optional[str] = None
    paid_in_country: Optional[str] = None
    taxed_at_source: Optional[bool] = None
    tax_withheld: Optional[float] = Field(None, ge=0)

    uk_taxable: Optional[bool] = None
    sa_taxable: Optional[bool] = None
    treaty_relief_applicable: Optional[bool] = None
    treaty_relief_percentage: Optional[float] = Field(None, ge=0, le=100)

    uk_tax_deducted: Optional[float] = Field(None, ge=0)
    uk_remittance_basis: Optional[bool] = None

    sa_tax_deducted: Optional[float] = Field(None, ge=0)
    sa_exempt_income: Optional[bool] = None

    tax_year: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_recurring: Optional[bool] = None

    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class IncomeSourceResponse(BaseModel):
    """Schema for income source response."""
    id: int
    user_id: int
    name: str
    income_type: str
    amount: float
    currency: str
    frequency: str

    source_country: str
    paid_in_country: Optional[str]
    taxed_at_source: bool
    tax_withheld: float

    uk_taxable: bool
    sa_taxable: bool
    treaty_relief_applicable: bool
    treaty_relief_percentage: float

    uk_tax_deducted: float
    uk_remittance_basis: bool

    sa_tax_deducted: float
    sa_exempt_income: bool

    tax_year: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: bool
    is_recurring: bool

    notes: Optional[str]
    extra_data: Optional[Dict[str, Any]]

    created_at: datetime
    updated_at: Optional[datetime]

    # Computed properties
    effective_uk_tax: float
    effective_sa_tax: float
    net_amount: float
    total_tax_burden: float
    effective_tax_rate: float

    class Config:
        from_attributes = True


# API Endpoints

@router.get("", response_model=List[IncomeSourceResponse])
async def get_income_sources(
    tax_year: Optional[str] = None,
    source_country: Optional[str] = None,
    income_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all income sources for the current user.

    Optional filters: tax_year, source_country, income_type, is_active
    """
    query = db.query(IncomeSource).filter(IncomeSource.user_id == current_user.id)

    if tax_year:
        query = query.filter(IncomeSource.tax_year == tax_year)
    if source_country:
        query = query.filter(IncomeSource.source_country == source_country)
    if income_type:
        query = query.filter(IncomeSource.income_type == income_type)
    if is_active is not None:
        query = query.filter(IncomeSource.is_active == is_active)

    income_sources = query.all()

    # Add computed properties
    result = []
    for source in income_sources:
        source_dict = IncomeSourceResponse.from_orm(source)
        source_dict.effective_uk_tax = source.effective_uk_tax
        source_dict.effective_sa_tax = source.effective_sa_tax
        source_dict.net_amount = source.net_amount
        source_dict.total_tax_burden = source.total_tax_burden
        source_dict.effective_tax_rate = source.effective_tax_rate
        result.append(source_dict)

    return result


@router.post("", response_model=IncomeSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_income_source(
    source_data: IncomeSourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new income source for the current user.
    """
    income_source = IncomeSource(
        user_id=current_user.id,
        **source_data.dict()
    )

    db.add(income_source)
    db.commit()
    db.refresh(income_source)

    # Add computed properties
    response_data = IncomeSourceResponse.from_orm(income_source)
    response_data.effective_uk_tax = income_source.effective_uk_tax
    response_data.effective_sa_tax = income_source.effective_sa_tax
    response_data.net_amount = income_source.net_amount
    response_data.total_tax_burden = income_source.total_tax_burden
    response_data.effective_tax_rate = income_source.effective_tax_rate

    return response_data


@router.get("/summary")
async def get_income_summary(
    tax_year: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get income summary by country and type.

    Returns aggregated data for dashboard widgets.
    """
    query = db.query(IncomeSource).filter(
        IncomeSource.user_id == current_user.id,
        IncomeSource.is_active == True
    )

    if tax_year:
        query = query.filter(IncomeSource.tax_year == tax_year)

    income_sources = query.all()

    # Aggregate by country
    by_country = {}
    by_type = {}
    total_income = 0.0
    total_uk_tax = 0.0
    total_sa_tax = 0.0

    for source in income_sources:
        # By country
        country = source.source_country
        if country not in by_country:
            by_country[country] = {
                "total_income": 0.0,
                "uk_tax": 0.0,
                "sa_tax": 0.0,
                "count": 0
            }
        by_country[country]["total_income"] += source.amount
        by_country[country]["uk_tax"] += source.effective_uk_tax
        by_country[country]["sa_tax"] += source.effective_sa_tax
        by_country[country]["count"] += 1

        # By type
        income_type = source.income_type
        if income_type not in by_type:
            by_type[income_type] = {
                "total_income": 0.0,
                "count": 0
            }
        by_type[income_type]["total_income"] += source.amount
        by_type[income_type]["count"] += 1

        # Totals
        total_income += source.amount
        total_uk_tax += source.effective_uk_tax
        total_sa_tax += source.effective_sa_tax

    return {
        "by_country": by_country,
        "by_type": by_type,
        "totals": {
            "total_income": total_income,
            "total_uk_tax": total_uk_tax,
            "total_sa_tax": total_sa_tax,
            "total_tax": total_uk_tax + total_sa_tax,
            "net_income": total_income - total_uk_tax - total_sa_tax,
            "effective_tax_rate": (total_uk_tax + total_sa_tax) / total_income * 100 if total_income > 0 else 0
        },
        "tax_year": tax_year or "All years"
    }


@router.get("/{income_id}", response_model=IncomeSourceResponse)
async def get_income_source(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific income source.
    """
    income_source = db.query(IncomeSource).filter(
        IncomeSource.id == income_id,
        IncomeSource.user_id == current_user.id
    ).first()

    if not income_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income source not found"
        )

    # Add computed properties
    response_data = IncomeSourceResponse.from_orm(income_source)
    response_data.effective_uk_tax = income_source.effective_uk_tax
    response_data.effective_sa_tax = income_source.effective_sa_tax
    response_data.net_amount = income_source.net_amount
    response_data.total_tax_burden = income_source.total_tax_burden
    response_data.effective_tax_rate = income_source.effective_tax_rate

    return response_data


@router.put("/{income_id}", response_model=IncomeSourceResponse)
async def update_income_source(
    income_id: int,
    source_update: IncomeSourceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an income source.
    """
    income_source = db.query(IncomeSource).filter(
        IncomeSource.id == income_id,
        IncomeSource.user_id == current_user.id
    ).first()

    if not income_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income source not found"
        )

    # Update fields
    update_data = source_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(income_source, field, value)

    db.commit()
    db.refresh(income_source)

    # Add computed properties
    response_data = IncomeSourceResponse.from_orm(income_source)
    response_data.effective_uk_tax = income_source.effective_uk_tax
    response_data.effective_sa_tax = income_source.effective_sa_tax
    response_data.net_amount = income_source.net_amount
    response_data.total_tax_burden = income_source.total_tax_burden
    response_data.effective_tax_rate = income_source.effective_tax_rate

    return response_data


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income_source(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an income source.
    """
    income_source = db.query(IncomeSource).filter(
        IncomeSource.id == income_id,
        IncomeSource.user_id == current_user.id
    ).first()

    if not income_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income source not found"
        )

    db.delete(income_source)
    db.commit()

    return None


@router.get("/tax-year/{year}")
async def get_income_by_tax_year(
    year: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all income sources for a specific tax year with summary.
    """
    income_sources = db.query(IncomeSource).filter(
        IncomeSource.user_id == current_user.id,
        IncomeSource.tax_year == year
    ).all()

    # Calculate summary
    total_income = sum(source.amount for source in income_sources)
    total_uk_tax = sum(source.effective_uk_tax for source in income_sources)
    total_sa_tax = sum(source.effective_sa_tax for source in income_sources)

    return {
        "tax_year": year,
        "income_sources": [
            {
                "id": source.id,
                "name": source.name,
                "income_type": source.income_type,
                "source_country": source.source_country,
                "amount": source.amount,
                "currency": source.currency,
                "uk_tax": source.effective_uk_tax,
                "sa_tax": source.effective_sa_tax,
                "net_amount": source.net_amount
            }
            for source in income_sources
        ],
        "summary": {
            "total_income": total_income,
            "total_uk_tax": total_uk_tax,
            "total_sa_tax": total_sa_tax,
            "total_tax": total_uk_tax + total_sa_tax,
            "net_income": total_income - total_uk_tax - total_sa_tax,
            "effective_tax_rate": (total_uk_tax + total_sa_tax) / total_income * 100 if total_income > 0 else 0,
            "count": len(income_sources)
        }
    }
