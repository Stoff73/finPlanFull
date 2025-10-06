from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class IHTProfile(Base):
    __tablename__ = "iht_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Estate values
    estate_value = Column(Float, default=0.0)
    liabilities = Column(Float, default=0.0)
    net_estate = Column(Float, default=0.0)

    # UK-specific bands
    nil_rate_band_used = Column(Float, default=0.0)  # Max £325,000
    residence_nil_rate_band_used = Column(Float, default=0.0)  # Max £175,000
    transferable_nil_rate_band = Column(Float, default=0.0)  # From deceased spouse
    transferable_residence_band = Column(Float, default=0.0)  # From deceased spouse

    # Tax calculations
    taxable_estate = Column(Float, default=0.0)
    tax_due = Column(Float, default=0.0)
    effective_rate = Column(Float, default=0.0)

    # Charitable giving
    charitable_gifts = Column(Float, default=0.0)
    qualifies_for_reduced_rate = Column(Boolean, default=False)  # 36% if 10%+ to charity

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="iht_profile")
    gifts = relationship("Gift", back_populates="iht_profile", cascade="all, delete-orphan")
    trusts = relationship("Trust", back_populates="iht_profile", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="iht_profile", cascade="all, delete-orphan")
    gift_exemptions = relationship("GiftExemptionTracking", back_populates="iht_profile", cascade="all, delete-orphan")
    marriages = relationship("MarriageHistory", back_populates="iht_profile", cascade="all, delete-orphan")
    gwr_items = relationship("GiftWithReservation", back_populates="iht_profile", cascade="all, delete-orphan")


class Gift(Base):
    __tablename__ = "gifts"

    id = Column(Integer, primary_key=True, index=True)
    iht_profile_id = Column(Integer, ForeignKey("iht_profiles.id"))

    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    recipient = Column(String)
    recipient_relationship = Column(String)  # spouse, child, grandchild, charity, other
    gift_type = Column(String)  # cash, property, shares, other

    # UK Seven-year rule
    is_pet = Column(Boolean, default=True)  # Potentially Exempt Transfer
    years_survived = Column(Float)  # Calculated field
    taper_relief_rate = Column(Float, default=0.0)  # 0%, 20%, 40%, 60%, 80%

    # Exemptions
    exempt_amount = Column(Float, default=0.0)
    exemption_type = Column(String)  # annual, small_gift, wedding, normal_expenditure

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    iht_profile = relationship("IHTProfile", back_populates="gifts")


class Trust(Base):
    __tablename__ = "trusts"

    id = Column(Integer, primary_key=True, index=True)
    iht_profile_id = Column(Integer, ForeignKey("iht_profiles.id"))

    trust_name = Column(String, nullable=False)
    trust_type = Column(String)  # discretionary, interest_in_possession, bare, charitable
    creation_date = Column(Date)
    value = Column(Float, default=0.0)

    # UK-specific
    is_relevant_property = Column(Boolean, default=False)
    ten_year_charge_rate = Column(Float, default=0.0)
    exit_charge_applicable = Column(Boolean, default=False)

    # Beneficiaries
    beneficiaries = Column(String)  # JSON string for now

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    iht_profile = relationship("IHTProfile", back_populates="trusts")
    trust_charges = relationship("TrustChargeHistory", back_populates="trust", cascade="all, delete-orphan")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    iht_profile_id = Column(Integer, ForeignKey("iht_profiles.id"))

    asset_type = Column(String, nullable=False)  # property, investment, business, personal
    description = Column(String)
    value = Column(Float, default=0.0)
    ownership_percentage = Column(Float, default=100.0)

    # Property specific
    is_main_residence = Column(Boolean, default=False)
    property_address = Column(String)

    # Business/Agricultural Relief
    qualifies_for_bpr = Column(Boolean, default=False)  # Business Property Relief
    bpr_rate = Column(Float, default=0.0)  # 50% or 100%
    qualifies_for_apr = Column(Boolean, default=False)  # Agricultural Property Relief
    apr_rate = Column(Float, default=0.0)  # 50% or 100%

    # Joint ownership
    is_jointly_owned = Column(Boolean, default=False)
    joint_owner_type = Column(String)  # spouse, civil_partner, other

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    iht_profile = relationship("IHTProfile", back_populates="assets")


class GiftExemptionTracking(Base):
    __tablename__ = "gift_exemption_tracking"

    id = Column(Integer, primary_key=True, index=True)
    iht_profile_id = Column(Integer, ForeignKey("iht_profiles.id"))

    tax_year = Column(String(10), nullable=False)  # e.g., "2024/25"
    annual_exemption_used = Column(Float, default=0.0)  # Max £3,000
    annual_exemption_brought_forward = Column(Float, default=0.0)  # Unused from previous year

    # Small gifts tracking (JSON array of recipients and amounts)
    small_gifts = Column(JSON, default=list)  # [{"recipient": "Name", "amount": 250, "date": "2024-01-01"}]

    # Wedding gifts tracking (JSON array)
    wedding_gifts = Column(JSON, default=list)  # [{"recipient": "Name", "relationship": "child", "amount": 5000}]

    # Normal expenditure out of income
    normal_expenditure_gifts = Column(JSON, default=list)
    normal_expenditure_total = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    iht_profile = relationship("IHTProfile", back_populates="gift_exemptions")


class TrustChargeHistory(Base):
    __tablename__ = "trust_charge_history"

    id = Column(Integer, primary_key=True, index=True)
    trust_id = Column(Integer, ForeignKey("trusts.id"))

    charge_type = Column(String(20), nullable=False)  # "periodic", "exit", "creation"
    charge_date = Column(Date, nullable=False)

    # Trust value at charge date
    trust_value = Column(Float, default=0.0)
    chargeable_value = Column(Float, default=0.0)  # After exemptions

    # Charge calculation
    charge_rate = Column(Float, default=0.0)  # Percentage rate (0-6%)
    tax_due = Column(Float, default=0.0)

    # Additional details
    nil_rate_band_at_date = Column(Float, default=325000.0)
    cumulative_total = Column(Float, default=0.0)  # For periodic charges

    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trust = relationship("Trust", back_populates="trust_charges")


class MarriageHistory(Base):
    __tablename__ = "marriage_history"

    id = Column(Integer, primary_key=True, index=True)
    iht_profile_id = Column(Integer, ForeignKey("iht_profiles.id"))

    spouse_name = Column(String, nullable=False)
    marriage_date = Column(Date)
    death_date = Column(Date, nullable=False)

    # Estate details at death
    estate_value = Column(Float, default=0.0)
    iht_paid = Column(Float, default=0.0)

    # Nil-rate band usage
    nil_rate_band_at_death = Column(Float, default=325000.0)
    unused_nrb = Column(Float, default=0.0)
    tnrb_percentage = Column(Float, default=0.0)  # Calculated percentage for transfer

    # Residence nil-rate band (from April 2017)
    residence_nil_rate_band_at_death = Column(Float, default=0.0)
    unused_rnrb = Column(Float, default=0.0)
    trnrb_percentage = Column(Float, default=0.0)

    # Claim status
    has_claimed_tnrb = Column(Boolean, default=False)
    has_claimed_trnrb = Column(Boolean, default=False)
    claim_date = Column(Date)

    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    iht_profile = relationship("IHTProfile", back_populates="marriages")


class GiftWithReservation(Base):
    __tablename__ = "gift_with_reservation"

    id = Column(Integer, primary_key=True, index=True)
    iht_profile_id = Column(Integer, ForeignKey("iht_profiles.id"))

    asset_description = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)  # "property", "chattels", "investments", "other"

    # Gift details
    original_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    gift_date = Column(Date, nullable=False)
    recipient = Column(String)

    # Benefit retained
    benefit_retained = Column(Text)
    is_occupation = Column(Boolean, default=False)  # Living in property
    is_possession = Column(Boolean, default=False)  # Using chattels
    is_income = Column(Boolean, default=False)     # Receiving income

    # Annual benefit value
    annual_benefit = Column(Float, default=0.0)

    # Pre-Owned Assets Tax (POAT)
    poat_applies = Column(Boolean, default=False)
    poat_annual_charge = Column(Float, default=0.0)
    poat_rate = Column(Float, default=0.0)  # 5% for land, official rate for others

    # Market rent paid (if any) - can reduce GWR treatment
    market_rent_paid = Column(Float, default=0.0)

    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    iht_profile = relationship("IHTProfile", back_populates="gwr_items")


class AssetOwnershipPeriod(Base):
    __tablename__ = "asset_ownership_periods"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))

    # Ownership tracking for relief qualification
    acquisition_date = Column(Date)
    disposal_date = Column(Date)  # NULL if still owned

    # Business relief tracking (2-year ownership requirement)
    business_use_start = Column(Date)
    business_use_end = Column(Date)

    # Agricultural relief tracking
    agricultural_use_start = Column(Date)
    agricultural_use_end = Column(Date)
    occupation_requirement_met = Column(Boolean, default=False)

    # Relief qualification status
    qualifies_for_bpr = Column(Boolean, default=False)
    qualifies_for_apr = Column(Boolean, default=False)

    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    asset = relationship("Asset")