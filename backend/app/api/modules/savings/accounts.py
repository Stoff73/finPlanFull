"""Savings Accounts API (Bridge to Banking)

This module provides savings/banking account management.
Currently wraps existing Banking API for compatibility.

Future: Will fully migrate to Product model with module='savings'
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

from app.database import get_db
from app.api.auth.auth import get_current_user
from app.models.user import User
from app.models import BankAccount, Transaction

router = APIRouter()


# Pydantic models for request/response
class AccountCreate(BaseModel):
    account_name: str = Field(..., min_length=1)
    account_type: str = Field(..., description="current, savings, isa, notice")
    bank_name: str
    account_number: Optional[str] = None
    current_balance: float = Field(default=0.0, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    currency: str = "GBP"


class AccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1)
    account_type: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    current_balance: Optional[float] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class TransactionCreate(BaseModel):
    date: date
    description: str = Field(..., min_length=1)
    transaction_type: str = Field(..., description="income or expense")
    category: str
    amount: float = Field(..., description="Positive for income, positive for expense")
    notes: Optional[str] = None


@router.get("")
async def list_savings_accounts(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all savings/bank accounts for the current user

    Query params:
        - include_inactive: Include inactive accounts (default: false)
    """
    query = db.query(BankAccount).filter(BankAccount.user_id == current_user.id)

    if not include_inactive:
        query = query.filter(BankAccount.is_active == True)

    accounts = query.order_by(BankAccount.account_name).all()

    # Calculate total balance
    total_balance = sum(acc.current_balance for acc in accounts)

    return {
        "total_balance": total_balance,
        "account_count": len(accounts),
        "accounts": [
            {
                "id": acc.id,
                "account_name": acc.account_name,
                "account_type": acc.account_type,
                "bank_name": acc.bank_name,
                "account_number": acc.account_number,
                "current_balance": acc.current_balance,
                "interest_rate": acc.interest_rate,
                "is_active": acc.is_active,
                "currency": acc.currency
            }
            for acc in accounts
        ]
    }


@router.post("")
async def create_savings_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new savings/bank account

    Body:
        - account_name: Account name/nickname (required)
        - account_type: Type of account (required)
        - bank_name: Bank/provider name (required)
        - current_balance: Current balance (default: 0)
        - interest_rate: Interest rate percentage
        - account_number: Account number (optional)
    """
    new_account = BankAccount(
        user_id=current_user.id,
        account_name=account_data.account_name,
        account_type=account_data.account_type,
        bank_name=account_data.bank_name,
        account_number=account_data.account_number,
        current_balance=account_data.current_balance,
        available_balance=account_data.current_balance,  # Same as current for savings
        interest_rate=account_data.interest_rate,
        currency=account_data.currency,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return {
        "id": new_account.id,
        "account_name": new_account.account_name,
        "current_balance": new_account.current_balance,
        "message": "Savings account created successfully"
    }


@router.get("/{account_id}")
async def get_savings_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific savings account by ID"""
    account = db.query(BankAccount).filter(
        and_(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Savings account not found")

    # Get transaction count
    transaction_count = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).count()

    return {
        "id": account.id,
        "account_name": account.account_name,
        "account_type": account.account_type,
        "bank_name": account.bank_name,
        "account_number": account.account_number,
        "current_balance": account.current_balance,
        "interest_rate": account.interest_rate,
        "is_active": account.is_active,
        "currency": account.currency,
        "transaction_count": transaction_count,
        "created_at": account.created_at.isoformat() if account.created_at else None
    }


@router.put("/{account_id}")
async def update_savings_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a savings account

    Only fields provided in the request body will be updated
    """
    # Verify ownership
    account = db.query(BankAccount).filter(
        and_(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Savings account not found")

    # Update fields
    update_data = account_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(account, field, value)

    # Update available_balance if current_balance changed
    if "current_balance" in update_data:
        account.available_balance = update_data["current_balance"]

    account.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(account)

    return {
        "id": account.id,
        "account_name": account.account_name,
        "current_balance": account.current_balance,
        "message": "Savings account updated successfully"
    }


@router.delete("/{account_id}")
async def delete_savings_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a savings account

    Sets is_active to False rather than hard deleting
    """
    # Verify ownership
    account = db.query(BankAccount).filter(
        and_(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Savings account not found")

    # Soft delete by deactivating
    account.is_active = False
    account.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Savings account deactivated successfully",
        "id": account_id
    }


@router.get("/{account_id}/transactions")
async def get_account_transactions(
    account_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transactions for a specific account

    Query params:
        - limit: Maximum number of transactions (default: 50)
        - offset: Pagination offset (default: 0)
    """
    # Verify account ownership
    account = db.query(BankAccount).filter(
        and_(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Savings account not found")

    # Get transactions
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.date.desc()).offset(offset).limit(limit).all()

    total_count = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).count()

    return {
        "account_id": account_id,
        "account_name": account.account_name,
        "total_transactions": total_count,
        "transactions": [
            {
                "id": t.id,
                "date": t.date.isoformat(),
                "description": t.description,
                "transaction_type": t.transaction_type,
                "category": t.category,
                "amount": t.amount,
                "balance_after": t.balance_after
            }
            for t in transactions
        ]
    }


@router.post("/{account_id}/transactions")
async def add_account_transaction(
    account_id: int,
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a transaction to an account

    Body:
        - date: Transaction date (required)
        - description: Transaction description (required)
        - transaction_type: income or expense (required)
        - category: Transaction category (required)
        - amount: Transaction amount (required)
        - notes: Additional notes (optional)
    """
    # Verify account ownership
    account = db.query(BankAccount).filter(
        and_(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Savings account not found")

    # Create transaction
    new_transaction = Transaction(
        user_id=current_user.id,
        account_id=account_id,
        date=transaction_data.date,
        description=transaction_data.description,
        transaction_type=transaction_data.transaction_type,
        category=transaction_data.category,
        subcategory=transaction_data.notes,  # Use notes as subcategory
        amount=transaction_data.amount,
        is_recurring=False,
        created_at=datetime.utcnow()
    )

    # Update account balance
    if transaction_data.transaction_type == "income":
        account.current_balance += transaction_data.amount
        new_transaction.balance_after = account.current_balance
    else:  # expense
        account.current_balance -= transaction_data.amount
        new_transaction.balance_after = account.current_balance

    account.available_balance = account.current_balance
    account.updated_at = datetime.utcnow()

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return {
        "id": new_transaction.id,
        "account_balance": account.current_balance,
        "message": "Transaction added successfully"
    }