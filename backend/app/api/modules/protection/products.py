"""Protection Products CRUD API

Handles creation, retrieval, update, and deletion of protection products
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models.product import Product

router = APIRouter()


# Pydantic schemas for validation
class ProtectionProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    product_type: str = Field(..., description="life_insurance, critical_illness, income_protection, etc.")
    provider: Optional[str] = Field(None, max_length=255)
    value: float = Field(..., gt=0, description="Coverage amount")
    monthly_premium: Optional[float] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    beneficiaries: Optional[str] = None
    notes: Optional[str] = None


class ProtectionProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    product_type: Optional[str] = None
    provider: Optional[str] = Field(None, max_length=255)
    value: Optional[float] = Field(None, gt=0)
    monthly_premium: Optional[float] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    beneficiaries: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|archived)$")


@router.get("")
async def list_protection_products(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all protection products for the current user

    Query params:
        - skip: Pagination offset
        - limit: Maximum number of results
    """
    products = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.module == "protection"
    ).order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": db.query(Product).filter(
            Product.user_id == current_user.id,
            Product.module == "protection"
        ).count(),
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "product_type": p.product_type,
                "provider": p.provider,
                "value": float(p.value or 0),
                "monthly_premium": p.extra_metadata.get("monthly_premium", 0) if p.extra_metadata else 0,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "end_date": p.end_date.isoformat() if p.end_date else None,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in products
        ]
    }


@router.post("")
async def create_protection_product(
    product_data: ProtectionProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new protection product

    Body:
        - name: Product name (required)
        - product_type: Type of protection (required)
        - value: Coverage amount (required)
        - monthly_premium: Premium amount
        - provider: Insurance provider
        - start_date: Policy start date
        - end_date: Policy end date
        - beneficiaries: Named beneficiaries
        - notes: Additional notes
    """
    # Create product with module='protection'
    new_product = Product(
        user_id=current_user.id,
        name=product_data.name,
        product_type=product_data.product_type,
        provider=product_data.provider,
        value=product_data.value,
        start_date=product_data.start_date,
        end_date=product_data.end_date,
        status="active",
        module="protection",  # Set module
        extra_metadata={
            "monthly_premium": product_data.monthly_premium,
            "beneficiaries": product_data.beneficiaries,
            "notes": product_data.notes
        }
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "id": new_product.id,
        "name": new_product.name,
        "product_type": new_product.product_type,
        "value": float(new_product.value or 0),
        "message": "Protection product created successfully"
    }


@router.get("/{product_id}")
async def get_protection_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific protection product by ID"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
        Product.module == "protection"
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Protection product not found")

    return {
        "id": product.id,
        "name": product.name,
        "product_type": product.product_type,
        "provider": product.provider,
        "value": float(product.value or 0),
        "monthly_premium": product.extra_metadata.get("monthly_premium", 0) if product.extra_metadata else 0,
        "beneficiaries": product.extra_metadata.get("beneficiaries") if product.extra_metadata else None,
        "notes": product.extra_metadata.get("notes") if product.extra_metadata else None,
        "start_date": product.start_date.isoformat() if product.start_date else None,
        "end_date": product.end_date.isoformat() if product.end_date else None,
        "status": product.status,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None
    }


@router.put("/{product_id}")
async def update_protection_product(
    product_id: int,
    product_data: ProtectionProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a protection product

    Only fields provided in the request body will be updated
    """
    # Verify ownership
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
        Product.module == "protection"
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Protection product not found")

    # Update fields
    update_data = product_data.dict(exclude_unset=True)

    # Handle metadata fields separately
    metadata_fields = ["monthly_premium", "beneficiaries", "notes"]
    metadata_updates = {}

    for field in metadata_fields:
        if field in update_data:
            metadata_updates[field] = update_data.pop(field)

    # Update direct fields
    for field, value in update_data.items():
        setattr(product, field, value)

    # Update metadata
    if metadata_updates:
        if not product.extra_metadata:
            product.extra_metadata = {}
        product.extra_metadata.update(metadata_updates)

    product.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(product)

    return {
        "id": product.id,
        "name": product.name,
        "value": float(product.value or 0),
        "message": "Protection product updated successfully"
    }


@router.delete("/{product_id}")
async def delete_protection_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete (archive) a protection product

    Sets status to 'archived' rather than hard deleting
    """
    # Verify ownership
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id,
        Product.module == "protection"
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Protection product not found")

    # Soft delete by setting status to archived
    product.status = "archived"
    product.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Protection product archived successfully",
        "id": product_id
    }