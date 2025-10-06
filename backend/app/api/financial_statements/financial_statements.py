from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.financial import BalanceSheet, ProfitLoss, CashFlow, BankAccount, Transaction
from app.models.user import User
from app.api.auth.auth import get_current_user
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal

router = APIRouter(prefix="/financial-statements", tags=["Financial Statements"])


class TransactionCreate(BaseModel):
    description: str
    amount: float
    transaction_type: str  # income, expense
    category: str
    date: date
    bank_account_id: Optional[int] = None


class TransactionResponse(TransactionCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BankAccountCreate(BaseModel):
    account_name: str
    account_type: str  # current, savings, credit
    bank_name: str
    account_number: Optional[str] = None
    current_balance: float = 0.0
    currency: str = "GBP"


class BankAccountResponse(BankAccountCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BalanceSheetCreate(BaseModel):
    period_start: date
    period_end: date
    cash_and_equivalents: float = 0.0
    investments: float = 0.0
    property: float = 0.0
    other_assets: float = 0.0
    current_liabilities: float = 0.0
    long_term_debt: float = 0.0
    other_liabilities: float = 0.0


class BalanceSheetResponse(BalanceSheetCreate):
    id: int
    user_id: int
    total_assets: float
    total_liabilities: float
    net_worth: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfitLossCreate(BaseModel):
    period_start: date
    period_end: date
    salary_income: float = 0.0
    business_income: float = 0.0
    investment_income: float = 0.0
    rental_income: float = 0.0
    other_income: float = 0.0
    housing_expenses: float = 0.0
    transport_expenses: float = 0.0
    food_expenses: float = 0.0
    utilities_expenses: float = 0.0
    insurance_expenses: float = 0.0
    entertainment_expenses: float = 0.0
    other_expenses: float = 0.0
    taxes: float = 0.0


class ProfitLossResponse(ProfitLossCreate):
    id: int
    user_id: int
    total_income: float
    total_expenses: float
    net_income: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CashFlowCreate(BaseModel):
    period_start: date
    period_end: date
    opening_balance: float
    income_received: float = 0.0
    operating_expenses_paid: float = 0.0
    investments_made: float = 0.0
    investments_sold: float = 0.0
    loans_received: float = 0.0
    loans_repaid: float = 0.0
    other_inflows: float = 0.0
    other_outflows: float = 0.0


class CashFlowResponse(CashFlowCreate):
    id: int
    user_id: int
    net_cash_flow: float
    closing_balance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FinancialSummary(BaseModel):
    net_worth: float
    monthly_income: float
    monthly_expenses: float
    monthly_savings: float
    savings_rate: float
    total_assets: float
    total_liabilities: float
    debt_to_income_ratio: float
    emergency_fund_months: float


@router.post("/bank-accounts", response_model=BankAccountResponse)
async def create_bank_account(
    account: BankAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_account = BankAccount(
        **account.dict(),
        user_id=current_user.id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get("/bank-accounts", response_model=List[BankAccountResponse])
async def get_bank_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    accounts = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id
    ).all()
    return accounts


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_transaction = Transaction(
        **transaction.dict(),
        user_id=current_user.id
    )
    db.add(db_transaction)

    if transaction.bank_account_id:
        account = db.query(BankAccount).filter(
            BankAccount.id == transaction.bank_account_id,
            BankAccount.user_id == current_user.id
        ).first()

        if account:
            if transaction.transaction_type == "income":
                account.current_balance += transaction.amount
            else:
                account.current_balance -= transaction.amount

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if category:
        query = query.filter(Transaction.category == category)

    return query.all()


@router.post("/balance-sheet", response_model=BalanceSheetResponse)
async def create_balance_sheet(
    balance_sheet: BalanceSheetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(BalanceSheet).filter(
        BalanceSheet.user_id == current_user.id,
        BalanceSheet.period_end == balance_sheet.period_end
    ).first()

    if existing:
        for key, value in balance_sheet.dict().items():
            setattr(existing, key, value)
        db_balance_sheet = existing
    else:
        db_balance_sheet = BalanceSheet(
            **balance_sheet.dict(),
            user_id=current_user.id
        )
        db.add(db_balance_sheet)

    db_balance_sheet.total_assets = (
        db_balance_sheet.cash_and_equivalents +
        db_balance_sheet.investments +
        db_balance_sheet.property +
        db_balance_sheet.other_assets
    )
    db_balance_sheet.total_liabilities = (
        db_balance_sheet.current_liabilities +
        db_balance_sheet.long_term_debt +
        db_balance_sheet.other_liabilities
    )
    db_balance_sheet.net_worth = (
        db_balance_sheet.total_assets - db_balance_sheet.total_liabilities
    )

    db.commit()
    db.refresh(db_balance_sheet)
    return db_balance_sheet


@router.get("/balance-sheet", response_model=List[BalanceSheetResponse])
async def get_balance_sheets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sheets = db.query(BalanceSheet).filter(
        BalanceSheet.user_id == current_user.id
    ).order_by(BalanceSheet.period_end.desc()).all()
    return sheets


@router.post("/profit-loss", response_model=ProfitLossResponse)
async def create_profit_loss(
    profit_loss: ProfitLossCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(ProfitLoss).filter(
        ProfitLoss.user_id == current_user.id,
        ProfitLoss.period_end == profit_loss.period_end
    ).first()

    if existing:
        for key, value in profit_loss.dict().items():
            setattr(existing, key, value)
        db_profit_loss = existing
    else:
        db_profit_loss = ProfitLoss(
            **profit_loss.dict(),
            user_id=current_user.id
        )
        db.add(db_profit_loss)

    db_profit_loss.total_income = (
        db_profit_loss.salary_income +
        db_profit_loss.business_income +
        db_profit_loss.investment_income +
        db_profit_loss.rental_income +
        db_profit_loss.other_income
    )
    db_profit_loss.total_expenses = (
        db_profit_loss.housing_expenses +
        db_profit_loss.transport_expenses +
        db_profit_loss.food_expenses +
        db_profit_loss.utilities_expenses +
        db_profit_loss.insurance_expenses +
        db_profit_loss.entertainment_expenses +
        db_profit_loss.other_expenses +
        db_profit_loss.taxes
    )
    db_profit_loss.net_income = (
        db_profit_loss.total_income - db_profit_loss.total_expenses
    )

    db.commit()
    db.refresh(db_profit_loss)
    return db_profit_loss


@router.get("/profit-loss", response_model=List[ProfitLossResponse])
async def get_profit_loss_statements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    statements = db.query(ProfitLoss).filter(
        ProfitLoss.user_id == current_user.id
    ).order_by(ProfitLoss.period_end.desc()).all()
    return statements


@router.post("/cash-flow", response_model=CashFlowResponse)
async def create_cash_flow(
    cash_flow: CashFlowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(CashFlow).filter(
        CashFlow.user_id == current_user.id,
        CashFlow.period_end == cash_flow.period_end
    ).first()

    if existing:
        for key, value in cash_flow.dict().items():
            setattr(existing, key, value)
        db_cash_flow = existing
    else:
        db_cash_flow = CashFlow(
            **cash_flow.dict(),
            user_id=current_user.id
        )
        db.add(db_cash_flow)

    total_inflows = (
        db_cash_flow.income_received +
        db_cash_flow.investments_sold +
        db_cash_flow.loans_received +
        db_cash_flow.other_inflows
    )
    total_outflows = (
        db_cash_flow.operating_expenses_paid +
        db_cash_flow.investments_made +
        db_cash_flow.loans_repaid +
        db_cash_flow.other_outflows
    )

    db_cash_flow.net_cash_flow = total_inflows - total_outflows
    db_cash_flow.closing_balance = (
        db_cash_flow.opening_balance + db_cash_flow.net_cash_flow
    )

    db.commit()
    db.refresh(db_cash_flow)
    return db_cash_flow


@router.get("/cash-flow", response_model=List[CashFlowResponse])
async def get_cash_flow_statements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    statements = db.query(CashFlow).filter(
        CashFlow.user_id == current_user.id
    ).order_by(CashFlow.period_end.desc()).all()
    return statements


@router.get("/summary", response_model=FinancialSummary)
async def get_financial_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_balance_sheet = db.query(BalanceSheet).filter(
        BalanceSheet.user_id == current_user.id
    ).order_by(BalanceSheet.period_end.desc()).first()

    latest_profit_loss = db.query(ProfitLoss).filter(
        ProfitLoss.user_id == current_user.id
    ).order_by(ProfitLoss.period_end.desc()).first()

    if not latest_balance_sheet or not latest_profit_loss:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial statements not found. Please create them first."
        )

    monthly_income = latest_profit_loss.total_income / max(1, (latest_profit_loss.period_end - latest_profit_loss.period_start).days / 30)
    monthly_expenses = latest_profit_loss.total_expenses / max(1, (latest_profit_loss.period_end - latest_profit_loss.period_start).days / 30)
    monthly_savings = monthly_income - monthly_expenses
    savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
    debt_to_income = (latest_balance_sheet.total_liabilities / (monthly_income * 12) * 100) if monthly_income > 0 else 0
    emergency_fund_months = (latest_balance_sheet.cash_and_equivalents / monthly_expenses) if monthly_expenses > 0 else 0

    return FinancialSummary(
        net_worth=latest_balance_sheet.net_worth,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_savings=monthly_savings,
        savings_rate=savings_rate,
        total_assets=latest_balance_sheet.total_assets,
        total_liabilities=latest_balance_sheet.total_liabilities,
        debt_to_income_ratio=debt_to_income,
        emergency_fund_months=emergency_fund_months
    )