from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    product_type = Column(String, nullable=False)  # pension, investment, savings, protection
    module = Column(String(50), nullable=True, index=True)  # Module: protection, savings, investment, retirement
    product_name = Column(String, nullable=False)
    provider = Column(String)
    reference_number = Column(String)

    # Multi-jurisdiction fields
    currency = Column(String, default="GBP")  # GBP, ZAR, EUR, USD
    jurisdiction = Column(String, default="UK")  # UK, SA, offshore, international

    # Common fields
    current_value = Column(Float, default=0.0)
    initial_investment = Column(Float, default=0.0)
    start_date = Column(Date)
    maturity_date = Column(Date)
    status = Column(String, default="active")  # active, closed, pending

    # Performance
    performance_ytd = Column(Float)
    performance_1yr = Column(Float)
    performance_3yr = Column(Float)
    performance_5yr = Column(Float)

    # Fees
    annual_charge = Column(Float)  # Percentage
    platform_fee = Column(Float)  # Percentage
    other_fees = Column(JSON)

    # Additional fields
    notes = Column(Text)
    extra_metadata = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="products")
    documents = relationship("Document", back_populates="product", cascade="all, delete-orphan")

    # Type-specific relationships
    pension_details = relationship("PensionDetail", back_populates="product", uselist=False, cascade="all, delete-orphan")
    investment_details = relationship("InvestmentDetail", back_populates="product", uselist=False, cascade="all, delete-orphan")
    protection_details = relationship("ProtectionDetail", back_populates="product", uselist=False, cascade="all, delete-orphan")

    # Property aliases for module API compatibility
    @property
    def name(self):
        """Alias for product_name to support module APIs."""
        return self.product_name

    @name.setter
    def name(self, value):
        self.product_name = value

    @property
    def value(self):
        """Alias for current_value to support module APIs."""
        return self.current_value

    @value.setter
    def value(self, val):
        self.current_value = val


class PensionDetail(Base):
    __tablename__ = "pension_details"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)

    pension_type = Column(String)  # workplace, personal, SIPP
    retirement_age = Column(Integer)
    projected_value_at_retirement = Column(Float)

    # Contributions
    employee_contribution = Column(Float)
    employer_contribution = Column(Float)
    contribution_frequency = Column(String)  # monthly, annual

    # Benefits
    death_benefit = Column(Float)
    guaranteed_period = Column(Integer)  # Years
    tax_free_cash_percentage = Column(Float, default=25.0)

    # Annuity options
    annuity_rate = Column(Float)
    includes_spouse_benefit = Column(Boolean, default=False)
    spouse_benefit_percentage = Column(Float)

    # Relationships
    product = relationship("Product", back_populates="pension_details")


class InvestmentDetail(Base):
    __tablename__ = "investment_details"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)

    investment_type = Column(String)  # ISA, GIA, JISA
    risk_rating = Column(Integer)  # 1-10
    asset_allocation = Column(JSON)  # {equities: %, bonds: %, etc}

    # ISA specific
    isa_type = Column(String)  # stocks_shares, cash, innovative_finance
    current_year_contribution = Column(Float)
    isa_allowance_used = Column(Float)

    # Investment strategy
    investment_strategy = Column(String)
    benchmark = Column(String)
    fund_codes = Column(JSON)  # List of fund ISINs/codes

    # Regular investing
    regular_investment_amount = Column(Float)
    regular_investment_frequency = Column(String)

    # Relationships
    product = relationship("Product", back_populates="investment_details")


class ProtectionDetail(Base):
    __tablename__ = "protection_details"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)

    protection_type = Column(String)  # life, critical_illness, income_protection
    sum_assured = Column(Float)
    premium = Column(Float)
    premium_frequency = Column(String)  # monthly, annual

    # Life insurance specific
    term_years = Column(Integer)
    is_joint_policy = Column(Boolean, default=False)
    includes_critical_illness = Column(Boolean, default=False)
    includes_waiver_of_premium = Column(Boolean, default=False)

    # Trust status (for IHT purposes)
    in_trust = Column(Boolean, default=False)
    trust_details = Column(String)

    # Beneficiaries
    beneficiaries = Column(JSON)

    # Medical
    smoker_status = Column(String)  # non_smoker, smoker, ex_smoker
    medical_conditions = Column(JSON)

    # Relationships
    product = relationship("Product", back_populates="protection_details")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))

    document_type = Column(String)  # statement, policy_doc, valuation, etc.
    document_name = Column(String, nullable=False)
    file_path = Column(String)  # Store path to file
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="documents")


# Convenience subclasses for specific product types
class Pension(Product):
    __mapper_args__ = {
        'polymorphic_identity': 'pension',
    }

    @property
    def details(self):
        return self.pension_details


class Investment(Product):
    __mapper_args__ = {
        'polymorphic_identity': 'investment',
    }

    @property
    def details(self):
        return self.investment_details


class Savings(Product):
    __mapper_args__ = {
        'polymorphic_identity': 'savings',
    }


class Protection(Product):
    __mapper_args__ = {
        'polymorphic_identity': 'protection',
    }

    @property
    def details(self):
        return self.protection_details