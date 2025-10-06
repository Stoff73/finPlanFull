from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from typing import List, Optional
from datetime import datetime, date, timedelta
import csv
import io
import json
from pydantic import BaseModel, Field

from app.db.base import get_db
from app.api.auth.auth import get_current_user
from app.models import User, BankAccount, Transaction

router = APIRouter()


# Pydantic models for request/response
class BankAccountCreate(BaseModel):
    account_name: str
    account_type: str = Field(..., description="current, savings, credit")
    bank_name: str
    account_number: Optional[str] = None
    currency: str = "GBP"
    current_balance: float = 0.0
    available_balance: Optional[float] = None
    credit_limit: Optional[float] = None
    interest_rate: Optional[float] = None


class BankAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    current_balance: Optional[float] = None
    available_balance: Optional[float] = None
    credit_limit: Optional[float] = None
    interest_rate: Optional[float] = None
    is_active: Optional[bool] = None


class BankAccountResponse(BaseModel):
    id: int
    user_id: int
    account_name: str
    account_type: Optional[str]
    bank_name: Optional[str]
    account_number: Optional[str]
    currency: str
    current_balance: float
    available_balance: float
    credit_limit: Optional[float]
    interest_rate: Optional[float]
    is_active: bool
    transaction_count: Optional[int] = 0
    last_transaction_date: Optional[date] = None

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    account_id: Optional[int] = None
    date: date
    description: str
    transaction_type: str = Field(..., description="income or expense")
    category: str
    subcategory: Optional[str] = None
    amount: float
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None


class TransactionUpdate(BaseModel):
    account_id: Optional[int] = None
    date: Optional[date] = None
    description: Optional[str] = None
    transaction_type: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    amount: Optional[float] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: Optional[int]
    account_name: Optional[str] = None
    date: date
    description: Optional[str]
    transaction_type: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    amount: float
    balance_after: Optional[float]
    is_recurring: bool
    recurrence_pattern: Optional[str]

    class Config:
        from_attributes = True


class TransactionFilter(BaseModel):
    account_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    transaction_type: Optional[str] = None
    category: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    search: Optional[str] = None


class CategorySummary(BaseModel):
    category: str
    transaction_type: str
    count: int
    total_amount: float
    average_amount: float
    percentage: float


class AccountSummary(BaseModel):
    total_accounts: int
    active_accounts: int
    total_balance: float
    total_credit_available: float
    accounts_by_type: dict
    recent_transactions: List[TransactionResponse]


# Transaction categories
TRANSACTION_CATEGORIES = {
    "income": [
        "Salary",
        "Freelance",
        "Investment Income",
        "Rental Income",
        "Business Income",
        "Pension",
        "Benefits",
        "Gifts Received",
        "Refunds",
        "Other Income"
    ],
    "expense": [
        "Housing",
        "Transportation",
        "Food & Dining",
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Healthcare",
        "Education",
        "Travel",
        "Insurance",
        "Savings & Investments",
        "Debt Payments",
        "Gifts & Donations",
        "Business Expenses",
        "Taxes",
        "Other Expenses"
    ]
}


# Bank Account Endpoints
@router.get("/accounts", response_model=List[BankAccountResponse])
async def get_bank_accounts(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bank accounts for the current user"""
    query = db.query(BankAccount).filter(BankAccount.user_id == current_user.id)

    if not include_inactive:
        query = query.filter(BankAccount.is_active == True)

    accounts = query.all()

    # Add transaction statistics
    response = []
    for account in accounts:
        account_dict = {
            "id": account.id,
            "user_id": account.user_id,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "bank_name": account.bank_name,
            "account_number": account.account_number,
            "currency": account.currency,
            "current_balance": account.current_balance,
            "available_balance": account.available_balance or account.current_balance,
            "credit_limit": account.credit_limit,
            "interest_rate": account.interest_rate,
            "is_active": account.is_active
        }

        # Get transaction stats
        transactions = db.query(Transaction).filter(
            Transaction.account_id == account.id
        ).all()

        account_dict["transaction_count"] = len(transactions)
        if transactions:
            account_dict["last_transaction_date"] = max(t.date for t in transactions)

        response.append(BankAccountResponse(**account_dict))

    return response


@router.get("/accounts/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific bank account"""
    account = db.query(BankAccount).filter(
        and_(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Add transaction statistics
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account.id
    ).all()

    response = BankAccountResponse(
        id=account.id,
        user_id=account.user_id,
        account_name=account.account_name,
        account_type=account.account_type,
        bank_name=account.bank_name,
        account_number=account.account_number,
        currency=account.currency,
        current_balance=account.current_balance,
        available_balance=account.available_balance or account.current_balance,
        credit_limit=account.credit_limit,
        interest_rate=account.interest_rate,
        is_active=account.is_active,
        transaction_count=len(transactions),
        last_transaction_date=max(t.date for t in transactions) if transactions else None
    )

    return response


@router.post("/accounts", response_model=BankAccountResponse)
async def create_bank_account(
    account: BankAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new bank account"""
    db_account = BankAccount(
        user_id=current_user.id,
        account_name=account.account_name,
        account_type=account.account_type,
        bank_name=account.bank_name,
        account_number=account.account_number,
        currency=account.currency,
        current_balance=account.current_balance,
        available_balance=account.available_balance or account.current_balance,
        credit_limit=account.credit_limit,
        interest_rate=account.interest_rate,
        is_active=True
    )

    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    return BankAccountResponse(
        id=db_account.id,
        user_id=db_account.user_id,
        account_name=db_account.account_name,
        account_type=db_account.account_type,
        bank_name=db_account.bank_name,
        account_number=db_account.account_number,
        currency=db_account.currency,
        current_balance=db_account.current_balance,
        available_balance=db_account.available_balance,
        credit_limit=db_account.credit_limit,
        interest_rate=db_account.interest_rate,
        is_active=db_account.is_active,
        transaction_count=0,
        last_transaction_date=None
    )


@router.put("/accounts/{account_id}", response_model=BankAccountResponse)
async def update_bank_account(
    account_id: int,
    account_update: BankAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a bank account"""
    account = db.query(BankAccount).filter(
        and_(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Update fields if provided
    update_data = account_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    # Update available_balance if not provided but current_balance changed
    if "current_balance" in update_data and "available_balance" not in update_data:
        account.available_balance = account.current_balance

    db.commit()
    db.refresh(account)

    # Get transaction stats
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account.id
    ).all()

    return BankAccountResponse(
        id=account.id,
        user_id=account.user_id,
        account_name=account.account_name,
        account_type=account.account_type,
        bank_name=account.bank_name,
        account_number=account.account_number,
        currency=account.currency,
        current_balance=account.current_balance,
        available_balance=account.available_balance,
        credit_limit=account.credit_limit,
        interest_rate=account.interest_rate,
        is_active=account.is_active,
        transaction_count=len(transactions),
        last_transaction_date=max(t.date for t in transactions) if transactions else None
    )


@router.delete("/accounts/{account_id}")
async def delete_bank_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a bank account (soft delete by deactivating)"""
    account = db.query(BankAccount).filter(
        and_(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Soft delete - just deactivate
    account.is_active = False
    db.commit()

    return {"message": "Account deactivated successfully"}


# Transaction Endpoints
@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    account_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    transaction_type: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions with optional filters"""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)

    if category:
        query = query.filter(Transaction.category == category)

    # Order by date descending
    query = query.order_by(Transaction.date.desc())

    # Apply pagination
    transactions = query.offset(offset).limit(limit).all()

    # Add account names to response
    response = []
    for trans in transactions:
        trans_dict = {
            "id": trans.id,
            "user_id": trans.user_id,
            "account_id": trans.account_id,
            "date": trans.date,
            "description": trans.description,
            "transaction_type": trans.transaction_type,
            "category": trans.category,
            "subcategory": trans.subcategory,
            "amount": trans.amount,
            "balance_after": trans.balance_after,
            "is_recurring": trans.is_recurring,
            "recurrence_pattern": trans.recurrence_pattern
        }

        if trans.account:
            trans_dict["account_name"] = trans.account.account_name

        response.append(TransactionResponse(**trans_dict))

    return response


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction"""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    response = TransactionResponse(
        id=transaction.id,
        user_id=transaction.user_id,
        account_id=transaction.account_id,
        account_name=transaction.account.account_name if transaction.account else None,
        date=transaction.date,
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        subcategory=transaction.subcategory,
        amount=transaction.amount,
        balance_after=transaction.balance_after,
        is_recurring=transaction.is_recurring,
        recurrence_pattern=transaction.recurrence_pattern
    )

    return response


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    # Verify account belongs to user if account_id is provided
    if transaction.account_id:
        account = db.query(BankAccount).filter(
            and_(
                BankAccount.id == transaction.account_id,
                BankAccount.user_id == current_user.id
            )
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Update account balance
        if transaction.transaction_type == "income":
            account.current_balance += transaction.amount
        else:
            account.current_balance -= transaction.amount

        balance_after = account.current_balance
    else:
        balance_after = None

    db_transaction = Transaction(
        user_id=current_user.id,
        account_id=transaction.account_id,
        date=transaction.date,
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        subcategory=transaction.subcategory,
        amount=transaction.amount,
        balance_after=balance_after,
        is_recurring=transaction.is_recurring,
        recurrence_pattern=transaction.recurrence_pattern
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return TransactionResponse(
        id=db_transaction.id,
        user_id=db_transaction.user_id,
        account_id=db_transaction.account_id,
        account_name=db_transaction.account.account_name if db_transaction.account else None,
        date=db_transaction.date,
        description=db_transaction.description,
        transaction_type=db_transaction.transaction_type,
        category=db_transaction.category,
        subcategory=db_transaction.subcategory,
        amount=db_transaction.amount,
        balance_after=db_transaction.balance_after,
        is_recurring=db_transaction.is_recurring,
        recurrence_pattern=db_transaction.recurrence_pattern
    )


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Store old values for balance adjustment
    old_amount = transaction.amount
    old_type = transaction.transaction_type
    old_account_id = transaction.account_id

    # Update fields
    update_data = transaction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    # Adjust account balances if needed
    if old_account_id and (
        "amount" in update_data or
        "transaction_type" in update_data or
        "account_id" in update_data
    ):
        # Reverse old transaction from old account
        if old_account_id:
            old_account = db.query(BankAccount).filter(
                BankAccount.id == old_account_id
            ).first()
            if old_account:
                if old_type == "income":
                    old_account.current_balance -= old_amount
                else:
                    old_account.current_balance += old_amount

        # Apply new transaction to new/current account
        if transaction.account_id:
            new_account = db.query(BankAccount).filter(
                BankAccount.id == transaction.account_id
            ).first()
            if new_account:
                if transaction.transaction_type == "income":
                    new_account.current_balance += transaction.amount
                else:
                    new_account.current_balance -= transaction.amount

                transaction.balance_after = new_account.current_balance

    db.commit()
    db.refresh(transaction)

    return TransactionResponse(
        id=transaction.id,
        user_id=transaction.user_id,
        account_id=transaction.account_id,
        account_name=transaction.account.account_name if transaction.account else None,
        date=transaction.date,
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        subcategory=transaction.subcategory,
        amount=transaction.amount,
        balance_after=transaction.balance_after,
        is_recurring=transaction.is_recurring,
        recurrence_pattern=transaction.recurrence_pattern
    )


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Adjust account balance if linked to account
    if transaction.account_id:
        account = db.query(BankAccount).filter(
            BankAccount.id == transaction.account_id
        ).first()
        if account:
            if transaction.transaction_type == "income":
                account.current_balance -= transaction.amount
            else:
                account.current_balance += transaction.amount

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted successfully"}


# Analytics Endpoints
@router.get("/analytics/summary", response_model=AccountSummary)
async def get_account_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive account and transaction summary"""
    accounts = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id
    ).all()

    total_balance = sum(acc.current_balance for acc in accounts)
    total_credit = sum(acc.credit_limit or 0 for acc in accounts if acc.account_type == "credit")
    active_accounts = sum(1 for acc in accounts if acc.is_active)

    # Group accounts by type
    accounts_by_type = {}
    for acc in accounts:
        acc_type = acc.account_type or "Other"
        if acc_type not in accounts_by_type:
            accounts_by_type[acc_type] = {"count": 0, "total_balance": 0}
        accounts_by_type[acc_type]["count"] += 1
        accounts_by_type[acc_type]["total_balance"] += acc.current_balance

    # Get recent transactions
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.date.desc()).limit(10).all()

    recent_trans_response = []
    for trans in recent_transactions:
        trans_dict = {
            "id": trans.id,
            "user_id": trans.user_id,
            "account_id": trans.account_id,
            "date": trans.date,
            "description": trans.description,
            "transaction_type": trans.transaction_type,
            "category": trans.category,
            "subcategory": trans.subcategory,
            "amount": trans.amount,
            "balance_after": trans.balance_after,
            "is_recurring": trans.is_recurring,
            "recurrence_pattern": trans.recurrence_pattern
        }
        if trans.account:
            trans_dict["account_name"] = trans.account.account_name
        recent_trans_response.append(TransactionResponse(**trans_dict))

    return AccountSummary(
        total_accounts=len(accounts),
        active_accounts=active_accounts,
        total_balance=total_balance,
        total_credit_available=total_credit,
        accounts_by_type=accounts_by_type,
        recent_transactions=recent_trans_response
    )


@router.get("/analytics/categories", response_model=List[CategorySummary])
async def get_category_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction summary by category"""
    query = db.query(
        Transaction.category,
        Transaction.transaction_type,
        func.count(Transaction.id).label("count"),
        func.sum(Transaction.amount).label("total"),
        func.avg(Transaction.amount).label("average")
    ).filter(Transaction.user_id == current_user.id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    results = query.group_by(
        Transaction.category,
        Transaction.transaction_type
    ).all()

    # Calculate total for percentages
    total_amount = sum(r.total for r in results)

    response = []
    for r in results:
        response.append(CategorySummary(
            category=r.category,
            transaction_type=r.transaction_type,
            count=r.count,
            total_amount=r.total,
            average_amount=r.average,
            percentage=(r.total / total_amount * 100) if total_amount > 0 else 0
        ))

    return response


@router.get("/analytics/monthly-trend")
async def get_monthly_trend(
    year: int = datetime.now().year,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly income/expense trend for a year"""
    results = db.query(
        extract('month', Transaction.date).label('month'),
        Transaction.transaction_type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        and_(
            Transaction.user_id == current_user.id,
            extract('year', Transaction.date) == year
        )
    ).group_by(
        extract('month', Transaction.date),
        Transaction.transaction_type
    ).all()

    # Organize data by month
    monthly_data = {}
    for month in range(1, 13):
        monthly_data[month] = {"income": 0, "expense": 0, "net": 0}

    for r in results:
        month = int(r.month)
        if r.transaction_type == "income":
            monthly_data[month]["income"] = float(r.total)
        else:
            monthly_data[month]["expense"] = float(r.total)

    # Calculate net
    for month in monthly_data:
        monthly_data[month]["net"] = monthly_data[month]["income"] - monthly_data[month]["expense"]

    return monthly_data


# CSV Import/Export
@router.post("/transactions/import-csv")
async def import_transactions_csv(
    file: UploadFile = File(...),
    account_id: Optional[int] = Form(None),
    date_format: str = Form("%Y-%m-%d"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import transactions from CSV file

    Expected CSV format:
    Date,Description,Category,Type,Amount
    2024-01-01,Salary,Salary,income,3000
    2024-01-02,Groceries,Food & Dining,expense,50
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    # Verify account if provided
    if account_id:
        account = db.query(BankAccount).filter(
            and_(
                BankAccount.id == account_id,
                BankAccount.user_id == current_user.id
            )
        ).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

    contents = await file.read()
    csv_reader = csv.DictReader(io.StringIO(contents.decode('utf-8')))

    imported_count = 0
    errors = []

    for row_num, row in enumerate(csv_reader, start=2):
        try:
            # Parse date
            trans_date = datetime.strptime(row['Date'], date_format).date()

            # Determine transaction type if not provided
            trans_type = row.get('Type', '').lower()
            if trans_type not in ['income', 'expense']:
                # Try to guess from amount
                amount = float(row['Amount'])
                trans_type = 'expense' if amount < 0 else 'income'
                amount = abs(amount)
            else:
                amount = abs(float(row['Amount']))

            # Create transaction
            transaction = Transaction(
                user_id=current_user.id,
                account_id=account_id,
                date=trans_date,
                description=row.get('Description', ''),
                transaction_type=trans_type,
                category=row.get('Category', 'Other'),
                amount=amount,
                is_recurring=False
            )

            db.add(transaction)
            imported_count += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    if imported_count > 0:
        db.commit()

    return {
        "imported": imported_count,
        "errors": errors,
        "message": f"Successfully imported {imported_count} transactions"
    }


@router.get("/transactions/export-csv")
async def export_transactions_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions to CSV"""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.order_by(Transaction.date).all()

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Date', 'Description', 'Category', 'Subcategory',
        'Type', 'Amount', 'Account', 'Balance After'
    ])

    # Write data
    for trans in transactions:
        writer.writerow([
            trans.date.strftime('%Y-%m-%d'),
            trans.description or '',
            trans.category or '',
            trans.subcategory or '',
            trans.transaction_type,
            trans.amount,
            trans.account.account_name if trans.account else '',
            trans.balance_after or ''
        ])

    output.seek(0)

    from fastapi.responses import Response

    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=transactions_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    )


@router.get("/categories")
async def get_categories():
    """Get list of available transaction categories"""
    return TRANSACTION_CATEGORIES