from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.db.base import Base
import enum


class SchemeType(str, enum.Enum):
    DC = "DC"
    DB = "DB"
    HYBRID = "Hybrid"


class ReliefMethod(str, enum.Enum):
    RELIEF_AT_SOURCE = "relief_at_source"
    NET_PAY = "net_pay"
    SALARY_SACRIFICE = "salary_sacrifice"


class PensionType(str, enum.Enum):
    WORKPLACE = "workplace"
    PERSONAL = "personal"
    SIPP = "SIPP"
    STAKEHOLDER = "stakeholder"
    GROUP_PERSONAL = "group_personal"
    SSAS = "SSAS"


class MPAATriggerType(str, enum.Enum):
    UFPLS = "UFPLS"
    FLEXI_DRAWDOWN = "flexi_drawdown"
    FLEXIBLE_ANNUITY = "flexible_annuity"
    SCHEME_PENSION = "scheme_pension"
    NONE = "none"


class EnhancedPension(Base):
    """Enhanced pension model with UK-specific features"""
    __tablename__ = "enhanced_pensions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Basic information
    scheme_name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    scheme_type = Column(Enum(SchemeType), nullable=False)
    pension_type = Column(Enum(PensionType), nullable=False)
    relief_method = Column(Enum(ReliefMethod), nullable=False)

    # Values and contributions
    current_value = Column(Float, default=0)
    transfer_value = Column(Float, default=0)
    monthly_member_contribution = Column(Float, default=0)
    monthly_employer_contribution = Column(Float, default=0)
    employer_match_percentage = Column(Float, default=0)
    employer_match_cap = Column(Float, nullable=True)

    # Annual Allowance tracking
    annual_allowance_used = Column(Float, default=0)
    salary_sacrifice_active = Column(Boolean, default=False)

    # MPAA tracking
    mpaa_triggered = Column(Boolean, default=False)
    mpaa_trigger_date = Column(Date, nullable=True)
    mpaa_trigger_type = Column(Enum(MPAATriggerType), default=MPAATriggerType.NONE)

    # Protection and allowances
    protected_pension_age = Column(Integer, nullable=True)
    lifetime_allowance_protection = Column(String, nullable=True)  # FP2016, IP2016, etc.
    lump_sum_protection = Column(Float, nullable=True)

    # Performance and charges
    annual_growth_rate = Column(Float, default=5.0)
    annual_management_charge = Column(Float, default=0.75)
    platform_charge = Column(Float, default=0)

    # DB specific fields
    db_accrual_rate = Column(String, nullable=True)  # e.g., "1/60th"
    db_pensionable_salary = Column(Float, nullable=True)
    db_years_service = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    notes = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="enhanced_pensions")
    input_periods = relationship("PensionInputPeriod", back_populates="pension", cascade="all, delete-orphan")


class PensionInputPeriod(Base):
    """Track pension inputs for each tax year"""
    __tablename__ = "pension_input_periods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pension_id = Column(Integer, ForeignKey("enhanced_pensions.id"), nullable=False)

    tax_year = Column(String, nullable=False)  # e.g., "2025/26"

    # Contribution amounts
    member_contribution = Column(Float, default=0)
    employer_contribution = Column(Float, default=0)
    total_input_amount = Column(Float, default=0)

    # Tax relief
    tax_relief_claimed = Column(Float, default=0)
    relief_at_source_amount = Column(Float, default=0)
    salary_sacrifice_amount = Column(Float, default=0)

    # Annual Allowance
    annual_allowance_used = Column(Float, default=0)
    carry_forward_used = Column(Float, default=0)
    aa_charge = Column(Float, default=0)

    # DB accrual (if applicable)
    db_opening_value = Column(Float, nullable=True)
    db_closing_value = Column(Float, nullable=True)
    db_input_amount = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="pension_input_periods")
    pension = relationship("EnhancedPension", back_populates="input_periods")


class CarryForward(Base):
    """Track unused Annual Allowance for carry forward"""
    __tablename__ = "carry_forward"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tax_year = Column(String, nullable=False)  # e.g., "2024/25"
    annual_allowance = Column(Float, nullable=False)  # Standard or tapered AA for that year
    amount_used = Column(Float, default=0)
    amount_available = Column(Float, default=0)

    # Expiry tracking
    expires_tax_year = Column(String, nullable=False)  # e.g., "2028/29"

    # MPAA restriction
    mpaa_restricted = Column(Boolean, default=False)

    # Taper details
    was_tapered = Column(Boolean, default=False)
    tapered_amount = Column(Float, nullable=True)
    threshold_income = Column(Float, nullable=True)
    adjusted_income = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="carry_forward_records")


class PensionProjection(Base):
    """Store pension projection scenarios"""
    __tablename__ = "pension_projections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pension_id = Column(Integer, ForeignKey("enhanced_pensions.id"), nullable=True)

    scenario_name = Column(String, nullable=False)

    # Projection parameters
    retirement_age = Column(Integer, default=65)
    current_age = Column(Integer, nullable=False)
    projection_years = Column(Integer, nullable=False)

    # Growth assumptions
    annual_growth_rate = Column(Float, default=5.0)
    inflation_rate = Column(Float, default=2.5)
    charges_percentage = Column(Float, default=0.75)

    # Contribution assumptions
    monthly_contribution = Column(Float, default=0)
    contribution_increase_rate = Column(Float, default=3.0)  # Annual increase

    # Results
    projected_value = Column(Float, nullable=False)
    projected_tax_free_cash = Column(Float, nullable=False)
    projected_annual_income = Column(Float, nullable=False)

    # Probability metrics (for Monte Carlo)
    success_probability = Column(Float, nullable=True)
    percentile_10 = Column(Float, nullable=True)
    percentile_50 = Column(Float, nullable=True)
    percentile_90 = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    projection_data = Column(JSON, nullable=True)  # Store detailed year-by-year projection

    # Relationships
    user = relationship("User", back_populates="pension_projections")


class LifetimeAllowanceTracking(Base):
    """Track lifetime allowance and lump sum allowances (post-LTA)"""
    __tablename__ = "lifetime_allowance_tracking"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Lump Sum Allowances (post April 2024)
    lsa_available = Column(Float, default=268275)  # Standard LSA
    lsa_used = Column(Float, default=0)
    lsdba_available = Column(Float, default=1073100)  # Standard LSDBA
    lsdba_used = Column(Float, default=0)
    ota_available = Column(Float, default=1073100)  # Overseas Transfer Allowance
    ota_used = Column(Float, default=0)

    # Protection details
    protection_type = Column(String, nullable=True)  # FP2016, IP2016, etc.
    protection_reference = Column(String, nullable=True)
    protected_amount = Column(Float, nullable=True)

    # Transitional protections
    has_enhanced_protection = Column(Boolean, default=False)
    has_primary_protection = Column(Boolean, default=False)
    has_fixed_protection = Column(Boolean, default=False)
    has_individual_protection = Column(Boolean, default=False)

    # Benefits taken
    benefits_crystallised_date = Column(Date, nullable=True)
    tax_free_cash_taken = Column(Float, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="lifetime_allowance_tracking")


class AutoEnrolmentTracking(Base):
    """Track auto-enrolment status and compliance"""
    __tablename__ = "auto_enrolment_tracking"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employer_id = Column(String, nullable=True)

    # Eligibility
    is_eligible = Column(Boolean, default=False)
    earnings = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)

    # Enrolment status
    enrolment_date = Column(Date, nullable=True)
    opt_out_date = Column(Date, nullable=True)
    opt_in_date = Column(Date, nullable=True)
    cessation_date = Column(Date, nullable=True)

    # Contribution rates
    qualifying_earnings = Column(Float, default=0)
    employee_contribution_rate = Column(Float, default=5.0)
    employer_contribution_rate = Column(Float, default=3.0)
    total_contribution_rate = Column(Float, default=8.0)

    # Re-enrolment
    re_enrolment_date = Column(Date, nullable=True)
    postponement_date = Column(Date, nullable=True)

    # Compliance
    meets_minimum_requirements = Column(Boolean, default=False)
    last_review_date = Column(Date, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="auto_enrolment_tracking")