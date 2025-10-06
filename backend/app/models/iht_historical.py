"""
Historical IHT Rates and Thresholds Model
Stores historical tax rates, nil-rate bands, and thresholds for reference and calculations
"""

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class IHTHistoricalRates(Base):
    """
    Historical IHT rates and thresholds by tax year
    Reference data for calculations and historical comparisons
    """
    __tablename__ = "iht_historical_rates"

    id = Column(Integer, primary_key=True, index=True)

    # Tax year
    tax_year = Column(String(10), nullable=False, unique=True, index=True)  # e.g., "2024/25"
    start_date = Column(Date, nullable=False)  # 6 April
    end_date = Column(Date, nullable=False)    # 5 April

    # Nil-Rate Bands
    nil_rate_band = Column(Float, nullable=False)  # £325,000
    residence_nil_rate_band = Column(Float)        # £175,000 (from 2017/18)
    rnrb_taper_threshold = Column(Float)           # £2,000,000

    # Tax Rates
    standard_rate = Column(Float, nullable=False)  # 0.40 (40%)
    reduced_charity_rate = Column(Float)           # 0.36 (36%)
    lifetime_rate = Column(Float, nullable=False)  # 0.20 (20%)

    # Trust Rates
    trust_entry_rate = Column(Float)                  # 0.20
    trust_ten_year_rate_max = Column(Float)          # 0.06 (6%)
    trust_effective_rate_multiplier = Column(Float)  # 0.30 (30%)

    # Gift Exemptions
    annual_exemption = Column(Float)          # £3,000
    small_gift_exemption = Column(Float)      # £250
    wedding_gift_child = Column(Float)        # £5,000
    wedding_gift_grandchild = Column(Float)   # £2,500
    wedding_gift_other = Column(Float)        # £1,000

    # Business/Agricultural Relief
    bpr_unquoted_rate = Column(Float)         # 1.00 (100%)
    bpr_quoted_rate = Column(Float)           # 0.50 (50%)
    apr_owner_occupied_rate = Column(Float)   # 1.00 (100%)
    apr_let_rate = Column(Float)              # 1.00 or 0.50

    # Special Rules
    br_apr_cap_amount = Column(Float)         # £1,000,000 (from 2026)
    br_apr_cap_applies = Column(Boolean, default=False)

    pension_iht_inclusion = Column(Boolean, default=False)  # From 2027

    # Domicile/Residence Rules
    domicile_based_scope = Column(Boolean, default=True)   # Until 2025
    residence_based_scope = Column(Boolean, default=False)  # From 2025

    deemed_domicile_years = Column(Integer)  # 15 out of 20 years (current)
    residence_years_threshold = Column(Integer)  # 10 years (from 2025)

    # Notes
    notes = Column(Text)
    legislation_reference = Column(Text)  # e.g., "Finance Act 2024"

    def __repr__(self):
        return f"<IHTHistoricalRates {self.tax_year}: NRB £{self.nil_rate_band:,.0f}, RNRB £{self.residence_nil_rate_band:,.0f if self.residence_nil_rate_band else 0}>"


class TaperReliefSchedule(Base):
    """
    Taper relief percentages by years since gift
    Reference table for consistent calculations
    """
    __tablename__ = "taper_relief_schedule"

    id = Column(Integer, primary_key=True, index=True)

    years_min = Column(Float, nullable=False)  # 0, 3, 4, 5, 6, 7
    years_max = Column(Float, nullable=False)  # 3, 4, 5, 6, 7, infinity
    relief_percentage = Column(Float, nullable=False)  # 0, 20, 40, 60, 80, 100

    description = Column(String)

    def __repr__(self):
        return f"<TaperRelief {self.years_min}-{self.years_max} years: {self.relief_percentage}% relief>"


class QuickSuccessionReliefSchedule(Base):
    """
    Quick Succession Relief percentages by years between deaths
    """
    __tablename__ = "quick_succession_relief_schedule"

    id = Column(Integer, primary_key=True, index=True)

    years_min = Column(Float, nullable=False)  # 0, 1, 2, 3, 4, 5
    years_max = Column(Float, nullable=False)  # 1, 2, 3, 4, 5, infinity
    relief_percentage = Column(Float, nullable=False)  # 100, 80, 60, 40, 20, 0

    description = Column(String)

    def __repr__(self):
        return f"<QSR {self.years_min}-{self.years_max} years: {self.relief_percentage}% relief>"


def get_rates_for_tax_year(session, tax_year: str):
    """
    Helper function to get IHT rates for a specific tax year

    Args:
        session: SQLAlchemy session
        tax_year: Tax year string (e.g., "2024/25")

    Returns:
        IHTHistoricalRates object or None
    """
    return session.query(IHTHistoricalRates).filter(
        IHTHistoricalRates.tax_year == tax_year
    ).first()


def get_current_rates(session):
    """
    Get IHT rates for current tax year

    Args:
        session: SQLAlchemy session

    Returns:
        IHTHistoricalRates object for current tax year
    """
    from datetime import date
    today = date.today()

    # Find tax year containing today's date
    rates = session.query(IHTHistoricalRates).filter(
        IHTHistoricalRates.start_date <= today,
        IHTHistoricalRates.end_date >= today
    ).first()

    if not rates:
        # Fallback to latest available
        rates = session.query(IHTHistoricalRates).order_by(
            IHTHistoricalRates.start_date.desc()
        ).first()

    return rates


def get_taper_relief_percentage(years_since_gift: float):
    """
    Get taper relief percentage for given years since gift

    Args:
        years_since_gift: Number of years (can be decimal)

    Returns:
        Relief percentage (0-100)
    """
    if years_since_gift < 3:
        return 0
    elif years_since_gift < 4:
        return 20
    elif years_since_gift < 5:
        return 40
    elif years_since_gift < 6:
        return 60
    elif years_since_gift < 7:
        return 80
    else:
        return 100


def get_qsr_percentage(years_between_deaths: float):
    """
    Get Quick Succession Relief percentage

    Args:
        years_between_deaths: Number of years between deaths

    Returns:
        Relief percentage (0-100)
    """
    if years_between_deaths < 1:
        return 100
    elif years_between_deaths < 2:
        return 80
    elif years_between_deaths < 3:
        return 60
    elif years_between_deaths < 4:
        return 40
    elif years_between_deaths < 5:
        return 20
    else:
        return 0