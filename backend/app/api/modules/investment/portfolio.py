"""
Investment Portfolio Management Endpoints

CRUD operations for investment products within the Investment module.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


# Pydantic schemas
class InvestmentProductCreate(BaseModel):
    name: str = Field(..., description="Investment name")
    product_type: str = Field(..., description="Investment type: stocks_shares_isa, gia, bonds, funds, etf, stocks")
    provider: Optional[str] = Field(None, description="Provider/platform name")
    value: float = Field(..., description="Current market value")
    total_contributions: Optional[float] = Field(0, description="Total amount contributed")
    annual_dividend: Optional[float] = Field(0, description="Annual dividend income")
    asset_allocation: Optional[Dict[str, float]] = Field(None, description="Asset allocation breakdown")
    notes: Optional[str] = Field(None, description="Additional notes")


class InvestmentProductUpdate(BaseModel):
    name: Optional[str] = None
    product_type: Optional[str] = None
    provider: Optional[str] = None
    value: Optional[float] = None
    total_contributions: Optional[float] = None
    annual_dividend: Optional[float] = None
    asset_allocation: Optional[Dict[str, float]] = None
    notes: Optional[str] = None


@router.get("", response_model=List[Dict[str, Any]])
def get_investment_products(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all investment products for the current user.

    Supports pagination via skip/limit parameters.
    """
    investments = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == 'investment',
        Product.status == 'active'
    ).order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": inv.id,
            "name": inv.name,
            "product_type": inv.product_type,
            "provider": inv.provider,
            "value": inv.value,
            "total_contributions": inv.extra_metadata.get('total_contributions', 0) if inv.extra_metadata else 0,
            "annual_dividend": inv.extra_metadata.get('annual_dividend', 0) if inv.extra_metadata else 0,
            "asset_allocation": inv.extra_metadata.get('asset_allocation') if inv.extra_metadata else None,
            "notes": inv.extra_metadata.get('notes') if inv.extra_metadata else None,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "updated_at": inv.updated_at.isoformat() if inv.updated_at else None
        }
        for inv in investments
    ]


@router.post("", response_model=Dict[str, Any])
def create_investment_product(
    product_data: InvestmentProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new investment product.

    Sets module='investment' automatically.
    """

    # Build metadata
    metadata = {
        "total_contributions": product_data.total_contributions or 0,
        "annual_dividend": product_data.annual_dividend or 0,
    }

    if product_data.asset_allocation:
        metadata["asset_allocation"] = product_data.asset_allocation

    if product_data.notes:
        metadata["notes"] = product_data.notes

    # Create product
    new_product = Product(
        user_id=current_user.id,
        module='investment',
        name=product_data.name,
        product_type=product_data.product_type,
        provider=product_data.provider,
        value=product_data.value,
        status='active',
        extra_metadata=metadata
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "id": new_product.id,
        "name": new_product.name,
        "product_type": new_product.product_type,
        "provider": new_product.provider,
        "value": new_product.value,
        "total_contributions": metadata.get('total_contributions', 0),
        "annual_dividend": metadata.get('annual_dividend', 0),
        "asset_allocation": metadata.get('asset_allocation'),
        "notes": metadata.get('notes'),
        "created_at": new_product.created_at.isoformat() if new_product.created_at else None
    }


@router.get("/{product_id}", response_model=Dict[str, Any])
def get_investment_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific investment product by ID.

    Verifies user ownership.
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
        Product.module == 'investment'
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Investment product not found")

    return {
        "id": product.id,
        "name": product.name,
        "product_type": product.product_type,
        "provider": product.provider,
        "value": product.value,
        "total_contributions": product.extra_metadata.get('total_contributions', 0) if product.extra_metadata else 0,
        "annual_dividend": product.extra_metadata.get('annual_dividend', 0) if product.extra_metadata else 0,
        "asset_allocation": product.extra_metadata.get('asset_allocation') if product.extra_metadata else None,
        "notes": product.extra_metadata.get('notes') if product.extra_metadata else None,
        "status": product.status,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None
    }


@router.put("/{product_id}", response_model=Dict[str, Any])
def update_investment_product(
    product_id: int,
    product_data: InvestmentProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing investment product.

    Verifies user ownership before updating.
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
        Product.module == 'investment'
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Investment product not found")

    # Update fields if provided
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.product_type is not None:
        product.product_type = product_data.product_type
    if product_data.provider is not None:
        product.provider = product_data.provider
    if product_data.value is not None:
        product.value = product_data.value

    # Update metadata
    metadata = product.extra_metadata or {}

    if product_data.total_contributions is not None:
        metadata['total_contributions'] = product_data.total_contributions
    if product_data.annual_dividend is not None:
        metadata['annual_dividend'] = product_data.annual_dividend
    if product_data.asset_allocation is not None:
        metadata['asset_allocation'] = product_data.asset_allocation
    if product_data.notes is not None:
        metadata['notes'] = product_data.notes

    product.extra_metadata = metadata
    product.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(product)

    return {
        "id": product.id,
        "name": product.name,
        "product_type": product.product_type,
        "provider": product.provider,
        "value": product.value,
        "total_contributions": metadata.get('total_contributions', 0),
        "annual_dividend": metadata.get('annual_dividend', 0),
        "asset_allocation": metadata.get('asset_allocation'),
        "notes": metadata.get('notes'),
        "updated_at": product.updated_at.isoformat() if product.updated_at else None
    }


@router.delete("/{product_id}", response_model=Dict[str, str])
def delete_investment_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete an investment product (set status to archived).

    Preserves data for historical analysis.
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
        Product.module == 'investment'
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Investment product not found")

    # Soft delete
    product.status = 'archived'
    product.updated_at = datetime.utcnow()

    db.commit()

    return {"message": f"Investment product '{product.name}' archived successfully"}