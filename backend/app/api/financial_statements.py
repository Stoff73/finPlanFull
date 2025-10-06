from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models.financial import BalanceSheet, ProfitLoss, CashFlow
from app.api.auth.auth import get_current_user
from app.models.user import User

router = APIRouter()

# Pydantic models for requests/responses
class BalanceSheetCreate(BaseModel):
    period_start: date
    period_end: date
    cash_and_equivalents: float = 0
    investments: float = 0
    property: float = 0
    other_assets: float = 0
    current_liabilities: float = 0
    long_term_debt: float = 0
    other_liabilities: float = 0

class BalanceSheetResponse(BalanceSheetCreate):
    id: int
    user_id: int
    total_assets: float
    total_liabilities: float
    net_worth: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ProfitLossCreate(BaseModel):
    period_start: date
    period_end: date
    salary_income: float = 0
    business_income: float = 0
    investment_income: float = 0
    rental_income: float = 0
    other_income: float = 0
    housing_expenses: float = 0
    transport_expenses: float = 0
    food_expenses: float = 0
    healthcare_expenses: float = 0
    entertainment_expenses: float = 0
    other_expenses: float = 0

class ProfitLossResponse(ProfitLossCreate):
    id: int
    user_id: int
    total_income: float
    total_expenses: float
    net_income: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class CashFlowCreate(BaseModel):
    period_start: date
    period_end: date
    opening_balance: float = 0
    income_received: float = 0
    operating_expenses_paid: float = 0
    investment_purchases: float = 0
    investment_sales: float = 0
    loan_proceeds: float = 0
    loan_payments: float = 0
    other_inflows: float = 0
    other_outflows: float = 0

class CashFlowResponse(CashFlowCreate):
    id: int
    user_id: int
    net_cash_flow: float
    closing_balance: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class FinancialSummary(BaseModel):
    net_worth: float
    monthly_income: float
    monthly_expenses: float
    savings_rate: float
    debt_to_income_ratio: float
    emergency_fund_months: float
    investment_allocation: dict
    recent_trends: dict

# Balance Sheet endpoints
@router.get("/balance-sheet/latest", response_model=Optional[BalanceSheetResponse])
def get_latest_balance_sheet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the most recent balance sheet for the current user"""
    balance_sheet = db.query(BalanceSheet)\
        .filter(BalanceSheet.user_id == current_user.id)\
        .order_by(BalanceSheet.period_end.desc())\
        .first()

    if balance_sheet:
        # Calculate totals
        balance_sheet.total_assets = (
            balance_sheet.cash_and_equivalents +
            balance_sheet.investments +
            balance_sheet.property +
            balance_sheet.other_assets
        )
        balance_sheet.total_liabilities = (
            balance_sheet.current_liabilities +
            balance_sheet.long_term_debt +
            balance_sheet.other_liabilities
        )
        balance_sheet.net_worth = balance_sheet.total_assets - balance_sheet.total_liabilities

    return balance_sheet

@router.get("/balance-sheet", response_model=List[BalanceSheetResponse])
def get_balance_sheets(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get balance sheet history for the current user"""
    balance_sheets = db.query(BalanceSheet)\
        .filter(BalanceSheet.user_id == current_user.id)\
        .order_by(BalanceSheet.period_end.desc())\
        .limit(limit)\
        .all()

    for bs in balance_sheets:
        bs.total_assets = (
            bs.cash_and_equivalents +
            bs.investments +
            bs.property +
            bs.other_assets
        )
        bs.total_liabilities = (
            bs.current_liabilities +
            bs.long_term_debt +
            bs.other_liabilities
        )
        bs.net_worth = bs.total_assets - bs.total_liabilities

    return balance_sheets

@router.post("/balance-sheet", response_model=BalanceSheetResponse)
def create_balance_sheet(
    balance_sheet_data: BalanceSheetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new balance sheet entry"""

    # Check if entry already exists for this period
    existing = db.query(BalanceSheet).filter(
        BalanceSheet.user_id == current_user.id,
        BalanceSheet.period_end == balance_sheet_data.period_end
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Balance sheet already exists for this period")

    balance_sheet = BalanceSheet(
        user_id=current_user.id,
        **balance_sheet_data.dict()
    )

    # Calculate totals
    balance_sheet.total_assets = (
        balance_sheet.cash_and_equivalents +
        balance_sheet.investments +
        balance_sheet.property +
        balance_sheet.other_assets
    )
    balance_sheet.total_liabilities = (
        balance_sheet.current_liabilities +
        balance_sheet.long_term_debt +
        balance_sheet.other_liabilities
    )
    balance_sheet.net_worth = balance_sheet.total_assets - balance_sheet.total_liabilities

    db.add(balance_sheet)
    db.commit()
    db.refresh(balance_sheet)

    return balance_sheet

@router.put("/balance-sheet/{balance_sheet_id}", response_model=BalanceSheetResponse)
def update_balance_sheet(
    balance_sheet_id: int,
    balance_sheet_data: BalanceSheetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing balance sheet"""

    balance_sheet = db.query(BalanceSheet).filter(
        BalanceSheet.id == balance_sheet_id,
        BalanceSheet.user_id == current_user.id
    ).first()

    if not balance_sheet:
        raise HTTPException(status_code=404, detail="Balance sheet not found")

    for key, value in balance_sheet_data.dict().items():
        setattr(balance_sheet, key, value)

    # Recalculate totals
    balance_sheet.total_assets = (
        balance_sheet.cash_and_equivalents +
        balance_sheet.investments +
        balance_sheet.property +
        balance_sheet.other_assets
    )
    balance_sheet.total_liabilities = (
        balance_sheet.current_liabilities +
        balance_sheet.long_term_debt +
        balance_sheet.other_liabilities
    )
    balance_sheet.net_worth = balance_sheet.total_assets - balance_sheet.total_liabilities

    db.commit()
    db.refresh(balance_sheet)

    return balance_sheet

# Profit & Loss endpoints
@router.get("/profit-loss/latest", response_model=Optional[ProfitLossResponse])
def get_latest_profit_loss(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the most recent P&L statement for the current user"""
    profit_loss = db.query(ProfitLoss)\
        .filter(ProfitLoss.user_id == current_user.id)\
        .order_by(ProfitLoss.period_end.desc())\
        .first()

    if profit_loss:
        # Calculate totals
        profit_loss.total_income = (
            profit_loss.salary_income +
            profit_loss.business_income +
            profit_loss.investment_income +
            profit_loss.rental_income +
            profit_loss.other_income
        )
        profit_loss.total_expenses = (
            profit_loss.housing_expenses +
            profit_loss.transport_expenses +
            profit_loss.food_expenses +
            profit_loss.utilities_expenses +
            profit_loss.insurance_expenses +
            profit_loss.entertainment_expenses +
            profit_loss.other_expenses
        )
        profit_loss.net_income = profit_loss.total_income - profit_loss.total_expenses

    return profit_loss

@router.get("/profit-loss", response_model=List[ProfitLossResponse])
def get_profit_loss_statements(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get P&L statement history for the current user"""
    statements = db.query(ProfitLoss)\
        .filter(ProfitLoss.user_id == current_user.id)\
        .order_by(ProfitLoss.period_end.desc())\
        .limit(limit)\
        .all()

    for pl in statements:
        pl.total_income = (
            pl.salary_income +
            pl.business_income +
            pl.investment_income +
            pl.rental_income +
            pl.other_income
        )
        pl.total_expenses = (
            pl.housing_expenses +
            pl.transport_expenses +
            pl.food_expenses +
            pl.healthcare_expenses +
            pl.entertainment_expenses +
            pl.other_expenses
        )
        pl.net_income = pl.total_income - pl.total_expenses

    return statements

@router.post("/profit-loss", response_model=ProfitLossResponse)
def create_profit_loss(
    profit_loss_data: ProfitLossCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new P&L statement"""

    # Check if entry already exists for this period
    existing = db.query(ProfitLoss).filter(
        ProfitLoss.user_id == current_user.id,
        ProfitLoss.period_end == profit_loss_data.period_end
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="P&L statement already exists for this period")

    profit_loss = ProfitLoss(
        user_id=current_user.id,
        **profit_loss_data.dict()
    )

    # Calculate totals
    profit_loss.total_income = (
        profit_loss.salary_income +
        profit_loss.business_income +
        profit_loss.investment_income +
        profit_loss.rental_income +
        profit_loss.other_income
    )
    profit_loss.total_expenses = (
        profit_loss.housing_expenses +
        profit_loss.transport_expenses +
        profit_loss.food_expenses +
        profit_loss.healthcare_expenses +
        profit_loss.entertainment_expenses +
        profit_loss.other_expenses
    )
    profit_loss.net_income = profit_loss.total_income - profit_loss.total_expenses

    db.add(profit_loss)
    db.commit()
    db.refresh(profit_loss)

    return profit_loss

# Cash Flow endpoints
@router.get("/cash-flow/latest", response_model=Optional[CashFlowResponse])
def get_latest_cash_flow(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the most recent cash flow statement for the current user"""
    cash_flow = db.query(CashFlow)\
        .filter(CashFlow.user_id == current_user.id)\
        .order_by(CashFlow.period_end.desc())\
        .first()

    if cash_flow:
        # Calculate net cash flow and closing balance
        cash_flow.net_cash_flow = (
            cash_flow.income_received +
            cash_flow.investment_sales +
            cash_flow.loan_proceeds +
            cash_flow.other_inflows -
            cash_flow.operating_expenses_paid -
            cash_flow.investment_purchases -
            cash_flow.loan_payments -
            cash_flow.other_outflows
        )
        cash_flow.closing_balance = cash_flow.opening_balance + cash_flow.net_cash_flow

    return cash_flow

@router.post("/cash-flow", response_model=CashFlowResponse)
def create_cash_flow(
    cash_flow_data: CashFlowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new cash flow statement"""

    cash_flow = CashFlow(
        user_id=current_user.id,
        **cash_flow_data.dict()
    )

    # Calculate net cash flow and closing balance
    cash_flow.net_cash_flow = (
        cash_flow.income_received +
        cash_flow.investment_sales +
        cash_flow.loan_proceeds +
        cash_flow.other_inflows -
        cash_flow.operating_expenses_paid -
        cash_flow.investment_purchases -
        cash_flow.loan_payments -
        cash_flow.other_outflows
    )
    cash_flow.closing_balance = cash_flow.opening_balance + cash_flow.net_cash_flow

    db.add(cash_flow)
    db.commit()
    db.refresh(cash_flow)

    return cash_flow

# Financial Summary endpoint
@router.get("/summary", response_model=FinancialSummary)
def get_financial_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive financial summary for the current user"""

    # Get latest balance sheet
    balance_sheet = db.query(BalanceSheet)\
        .filter(BalanceSheet.user_id == current_user.id)\
        .order_by(BalanceSheet.period_end.desc())\
        .first()

    # Get latest P&L
    profit_loss = db.query(ProfitLoss)\
        .filter(ProfitLoss.user_id == current_user.id)\
        .order_by(ProfitLoss.period_end.desc())\
        .first()

    # Calculate summary metrics
    net_worth = 0
    monthly_income = 0
    monthly_expenses = 0
    investment_allocation = {}

    if balance_sheet:
        total_assets = (
            balance_sheet.cash_and_equivalents +
            balance_sheet.investments +
            balance_sheet.property +
            balance_sheet.other_assets
        )
        total_liabilities = (
            balance_sheet.current_liabilities +
            balance_sheet.long_term_debt +
            balance_sheet.other_liabilities
        )
        net_worth = total_assets - total_liabilities

        if total_assets > 0:
            investment_allocation = {
                "cash": round((balance_sheet.cash_and_equivalents / total_assets) * 100, 1),
                "investments": round((balance_sheet.investments / total_assets) * 100, 1),
                "property": round((balance_sheet.property / total_assets) * 100, 1),
                "other": round((balance_sheet.other_assets / total_assets) * 100, 1)
            }

    if profit_loss:
        # Assuming P&L is annual, convert to monthly
        period_months = 12  # Could calculate from period_start and period_end
        monthly_income = (
            profit_loss.salary_income +
            profit_loss.business_income +
            profit_loss.investment_income +
            profit_loss.rental_income +
            profit_loss.other_income
        ) / period_months

        monthly_expenses = (
            profit_loss.housing_expenses +
            profit_loss.transport_expenses +
            profit_loss.food_expenses +
            profit_loss.utilities_expenses +
            profit_loss.insurance_expenses +
            profit_loss.entertainment_expenses +
            profit_loss.other_expenses
        ) / period_months

    savings_rate = 0
    if monthly_income > 0:
        savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100

    debt_to_income_ratio = 0
    if balance_sheet and monthly_income > 0:
        monthly_debt_payments = (balance_sheet.long_term_debt / 12)  # Simplified
        debt_to_income_ratio = (monthly_debt_payments / monthly_income) * 100

    emergency_fund_months = 0
    if balance_sheet and monthly_expenses > 0:
        emergency_fund_months = balance_sheet.cash_and_equivalents / monthly_expenses

    # Get trends (last 3 periods)
    recent_balances = db.query(BalanceSheet)\
        .filter(BalanceSheet.user_id == current_user.id)\
        .order_by(BalanceSheet.period_end.desc())\
        .limit(3)\
        .all()

    net_worth_trend = []
    for bs in recent_balances:
        total_assets = bs.cash_and_equivalents + bs.investments + bs.property + bs.other_assets
        total_liabilities = bs.current_liabilities + bs.long_term_debt + bs.other_liabilities
        net_worth_trend.append({
            "period": bs.period_end.isoformat(),
            "value": total_assets - total_liabilities
        })

    return FinancialSummary(
        net_worth=net_worth,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        savings_rate=savings_rate,
        debt_to_income_ratio=debt_to_income_ratio,
        emergency_fund_months=emergency_fund_months,
        investment_allocation=investment_allocation,
        recent_trends={"net_worth": net_worth_trend}
    )