"""Tax Profile Model

Tracks user's tax status across UK and South Africa including:
- Domicile status and history
- Tax residency status in each jurisdiction
- Years of residency tracking
- Remittance basis elections
- Split year treatment
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class TaxProfile(Base):
    """Tax profile for dual-country (UK/SA) tax planning."""

    __tablename__ = "tax_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Domicile Information
    domicile = Column(String, nullable=False)  # UK, SA, deemed_domicile_uk, other
    domicile_of_origin = Column(String)  # Birth domicile: UK, SA, other
    domicile_acquired_date = Column(Date)  # When current domicile was acquired

    # Deemed Domicile Tracking (UK specific)
    # UK rule: Resident in UK for 15 of the last 20 tax years
    uk_resident_years_count = Column(Integer, default=0)  # Count of UK resident years
    uk_deemed_domicile_date = Column(Date)  # Date when deemed domicile status acquired

    # Tax Residency Status
    tax_residency = Column(String, nullable=False)  # UK, SA, dual_resident, neither
    uk_tax_resident = Column(Boolean, default=False)
    sa_tax_resident = Column(Boolean, default=False)

    # Residency Tracking
    uk_years_of_residency = Column(Integer, default=0)  # Total years resident in UK
    sa_years_of_residency = Column(Integer, default=0)  # Total years resident in SA

    # Current Tax Year Residency (updated annually)
    current_tax_year_uk_resident = Column(Boolean, default=False)
    current_tax_year_sa_resident = Column(Boolean, default=False)

    # UK Specific Tax Status
    uk_remittance_basis_user = Column(Boolean, default=False)  # Using remittance basis (non-dom)
    uk_remittance_basis_charge_paid = Column(Boolean, default=False)  # £30k/£60k charge paid
    uk_split_year_treatment = Column(Boolean, default=False)  # Split year applies
    uk_split_year_uk_part_start = Column(Date)  # When UK part of split year starts
    uk_split_year_uk_part_end = Column(Date)  # When UK part of split year ends

    # SA Specific Tax Status
    sa_ordinarily_resident = Column(Boolean, default=False)  # SA ordinarily resident status
    sa_year_of_assessment = Column(String)  # Current SA tax year (March-February)

    # Days Tracking (for residency tests)
    # Stored as JSON: {tax_year: days_in_country}
    uk_days_by_tax_year = Column(JSON)  # {"2023/24": 150, "2024/25": 180}
    sa_days_by_tax_year = Column(JSON)  # {"2023/24": 120, "2024/25": 100}

    # Statutory Residence Test (SRT) - UK
    # Stored as JSON with SRT test results
    uk_srt_automatic_uk_resident = Column(Boolean, default=False)
    uk_srt_automatic_non_resident = Column(Boolean, default=False)
    uk_srt_sufficient_ties = Column(JSON)  # Store ties met in current year

    # SA Physical Presence Test
    sa_physical_presence_test_met = Column(Boolean, default=False)
    sa_days_current_year = Column(Integer, default=0)
    sa_days_last_5_years_total = Column(Integer, default=0)

    # Treaty Tie-Breaker (for dual residents)
    treaty_tie_breaker_country = Column(String)  # UK, SA (which country wins under treaty)
    treaty_tie_breaker_reason = Column(String)  # permanent_home, vital_interests, habitual_abode, nationality

    # Migration History
    # Stored as JSON: [{"from_country": "SA", "to_country": "UK", "date": "2020-04-06", "reason": "work"}]
    migration_history = Column(JSON)

    # Future Migration Plans
    planning_to_relocate = Column(Boolean, default=False)
    planned_relocation_country = Column(String)  # UK, SA
    planned_relocation_date = Column(Date)
    planned_relocation_reason = Column(String)  # work, retirement, family

    # Last Updated
    last_residency_review_date = Column(Date)  # When residency was last reviewed
    next_review_due_date = Column(Date)  # When next review is recommended

    # Metadata
    notes = Column(String)  # Free-text notes about tax situation
    professional_advice_received = Column(Boolean, default=False)
    advisor_name = Column(String)
    advisor_contact = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="tax_profile")

    def __repr__(self):
        return f"<TaxProfile(user_id={self.user_id}, domicile={self.domicile}, residency={self.tax_residency})>"

    @property
    def is_uk_domiciled(self) -> bool:
        """Check if user is UK domiciled (including deemed domicile)."""
        return self.domicile in ["UK", "deemed_domicile_uk"]

    @property
    def is_sa_domiciled(self) -> bool:
        """Check if user is SA domiciled."""
        return self.domicile == "SA"

    @property
    def is_dual_resident(self) -> bool:
        """Check if user is tax resident in both UK and SA."""
        return self.uk_tax_resident and self.sa_tax_resident

    @property
    def effective_tax_country(self) -> str:
        """
        Determine effective tax country based on residency and treaty tie-breaker.

        Returns:
            str: UK, SA, both, or neither
        """
        if self.is_dual_resident:
            # If dual resident, check treaty tie-breaker
            if self.treaty_tie_breaker_country:
                return self.treaty_tie_breaker_country
            return "both"  # Tie-breaker not determined
        elif self.uk_tax_resident:
            return "UK"
        elif self.sa_tax_resident:
            return "SA"
        else:
            return "neither"
