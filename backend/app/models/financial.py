from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class BalanceSheet(Base):
    __tablename__ = "balance_sheets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Assets
    cash_and_equivalents = Column(Float, default=0.0)
    investments = Column(Float, default=0.0)
    property = Column(Float, default=0.0)
    other_assets = Column(Float, default=0.0)
    total_assets = Column(Float, default=0.0)

    # Liabilities
    current_liabilities = Column(Float, default=0.0)
    long_term_debt = Column(Float, default=0.0)
    other_liabilities = Column(Float, default=0.0)
    total_liabilities = Column(Float, default=0.0)

    # Net Worth
    net_worth = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class ProfitLoss(Base):
    __tablename__ = "profit_loss"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Income
    salary_income = Column(Float, default=0.0)
    business_income = Column(Float, default=0.0)
    investment_income = Column(Float, default=0.0)
    rental_income = Column(Float, default=0.0)
    other_income = Column(Float, default=0.0)
    total_income = Column(Float, default=0.0)

    # Expenses
    housing_expenses = Column(Float, default=0.0)
    transport_expenses = Column(Float, default=0.0)
    food_expenses = Column(Float, default=0.0)
    utilities_expenses = Column(Float, default=0.0)
    insurance_expenses = Column(Float, default=0.0)
    entertainment_expenses = Column(Float, default=0.0)
    other_expenses = Column(Float, default=0.0)
    taxes = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)

    # Net
    net_income = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class CashFlow(Base):
    __tablename__ = "cash_flows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    opening_balance = Column(Float, default=0.0)

    # Operating Activities
    income_received = Column(Float, default=0.0)
    operating_expenses_paid = Column(Float, default=0.0)

    # Investing Activities
    investments_made = Column(Float, default=0.0)
    investments_sold = Column(Float, default=0.0)

    # Financing Activities
    loans_received = Column(Float, default=0.0)
    loans_repaid = Column(Float, default=0.0)

    # Other
    other_inflows = Column(Float, default=0.0)
    other_outflows = Column(Float, default=0.0)

    net_cash_flow = Column(Float, default=0.0)
    closing_balance = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    statement_type = Column(String, nullable=False)  # balance_sheet, income_statement, cash_flow, pnl
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Balance Sheet items
    total_assets = Column(Float, default=0.0)
    current_assets = Column(Float, default=0.0)
    fixed_assets = Column(Float, default=0.0)
    total_liabilities = Column(Float, default=0.0)
    current_liabilities = Column(Float, default=0.0)
    long_term_liabilities = Column(Float, default=0.0)
    net_worth = Column(Float, default=0.0)

    # Income Statement items
    total_income = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    net_income = Column(Float, default=0.0)

    # Cash Flow items
    operating_cash_flow = Column(Float, default=0.0)
    investing_cash_flow = Column(Float, default=0.0)
    financing_cash_flow = Column(Float, default=0.0)
    net_cash_flow = Column(Float, default=0.0)

    # Detailed breakdown (JSON)
    detailed_items = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="financial_statements")


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    account_name = Column(String, nullable=False)
    account_type = Column(String)  # current, savings, credit
    bank_name = Column(String)  # Updated field name to match API
    account_number = Column(String)  # Can store last 4 digits or masked number
    currency = Column(String, default="GBP")

    current_balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    credit_limit = Column(Float)  # For credit cards
    interest_rate = Column(Float)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="bank_accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True)

    date = Column(Date, nullable=False)  # Changed from transaction_date to match API
    description = Column(String)
    transaction_type = Column(String)  # income, expense
    category = Column(String)  # salary, rent, groceries, etc.
    subcategory = Column(String)  # optional subcategory

    amount = Column(Float, nullable=False)
    balance_after = Column(Float)

    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String)  # monthly, weekly, etc.

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    account = relationship("BankAccount", back_populates="transactions")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String, nullable=False)
    period = Column(String)  # monthly, quarterly, annual
    start_date = Column(Date)
    end_date = Column(Date)

    # Budget categories (JSON)
    categories = Column(JSON)  # {category: {planned: 0, actual: 0}}

    total_income_planned = Column(Float, default=0.0)
    total_expenses_planned = Column(Float, default=0.0)
    total_income_actual = Column(Float, default=0.0)
    total_expenses_actual = Column(Float, default=0.0)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")