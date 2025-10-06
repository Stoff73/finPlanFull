from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Financial profile
    risk_tolerance = Column(String)  # conservative, moderate, aggressive
    financial_goals = Column(String)  # JSON string for now
    extra_metadata = Column(JSON)  # User profile metadata (age, retirement_age, etc.)

    # Currency and Tax Settings
    primary_currency = Column(String, default="GBP")  # GBP, ZAR, EUR, USD
    secondary_currency = Column(String)  # Optional secondary currency for dual-country users

    # Relationships
    iht_profile = relationship("IHTProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    financial_statements = relationship("FinancialStatement", back_populates="user", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="user", cascade="all, delete-orphan")
    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")

    # Pension relationships
    enhanced_pensions = relationship("EnhancedPension", back_populates="user", cascade="all, delete-orphan")
    pension_input_periods = relationship("PensionInputPeriod", back_populates="user", cascade="all, delete-orphan")
    carry_forward_records = relationship("CarryForward", back_populates="user", cascade="all, delete-orphan")
    pension_projections = relationship("PensionProjection", back_populates="user", cascade="all, delete-orphan")
    lifetime_allowance_tracking = relationship("LifetimeAllowanceTracking", back_populates="user", uselist=False, cascade="all, delete-orphan")
    auto_enrolment_tracking = relationship("AutoEnrolmentTracking", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # Module-based relationships
    module_goals = relationship("ModuleGoal", back_populates="user", cascade="all, delete-orphan")
    module_metrics = relationship("ModuleMetric", back_populates="user", cascade="all, delete-orphan")

    # Tax Profile (for dual-country tax planning)
    tax_profile = relationship("TaxProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")