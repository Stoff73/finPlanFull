"""Income Source Model

Tracks income sources by country for dual-country tax planning.
Essential for determining tax liability in each jurisdiction.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class IncomeSource(Base):
    """Income source model for tracking income by country."""

    __tablename__ = "income_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Income details
    name = Column(String, nullable=False)  # e.g., "Software Engineering Salary"
    income_type = Column(String, nullable=False)  # salary, dividend, rental, interest, pension, business, capital_gains, other
    amount = Column(Float, nullable=False)  # Annual amount
    currency = Column(String, default="GBP")  # GBP, ZAR, EUR, USD
    frequency = Column(String, default="annual")  # annual, monthly, quarterly

    # Source country tracking
    source_country = Column(String, nullable=False)  # UK, SA, other
    paid_in_country = Column(String)  # Country where payment is made
    taxed_at_source = Column(Boolean, default=False)  # Tax deducted at source?
    tax_withheld = Column(Float, default=0.0)  # Amount of tax withheld

    # Tax treatment
    uk_taxable = Column(Boolean, default=True)  # Subject to UK tax?
    sa_taxable = Column(Boolean, default=True)  # Subject to SA tax?
    treaty_relief_applicable = Column(Boolean, default=False)  # DTA relief applies?
    treaty_relief_percentage = Column(Float, default=0.0)  # e.g., 0.0 - 100.0

    # UK-specific
    uk_tax_deducted = Column(Float, default=0.0)  # UK PAYE or withholding
    uk_remittance_basis = Column(Boolean, default=False)  # Remitted to UK?

    # SA-specific
    sa_tax_deducted = Column(Float, default=0.0)  # SA PAYE or withholding
    sa_exempt_income = Column(Boolean, default=False)  # SA tax exempt?

    # Additional details
    tax_year = Column(String, nullable=False)  # e.g., "2024/25"
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_recurring = Column(Boolean, default=True)  # Recurring income?

    # Notes and documentation
    notes = Column(String)
    extra_data = Column(JSON)  # Flexible field for additional data

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="income_sources")

    def __repr__(self):
        return f"<IncomeSource {self.name} - {self.source_country} - {self.currency}{self.amount}>"

    @property
    def effective_uk_tax(self) -> float:
        """Calculate effective UK tax after treaty relief."""
        if not self.uk_taxable:
            return 0.0

        if self.treaty_relief_applicable and self.treaty_relief_percentage > 0:
            relief = self.uk_tax_deducted * (self.treaty_relief_percentage / 100)
            return max(0.0, self.uk_tax_deducted - relief)

        return self.uk_tax_deducted

    @property
    def effective_sa_tax(self) -> float:
        """Calculate effective SA tax after treaty relief."""
        if not self.sa_taxable or self.sa_exempt_income:
            return 0.0

        if self.treaty_relief_applicable and self.treaty_relief_percentage > 0:
            relief = self.sa_tax_deducted * (self.treaty_relief_percentage / 100)
            return max(0.0, self.sa_tax_deducted - relief)

        return self.sa_tax_deducted

    @property
    def net_amount(self) -> float:
        """Calculate net amount after all taxes."""
        return self.amount - self.effective_uk_tax - self.effective_sa_tax - self.tax_withheld

    @property
    def total_tax_burden(self) -> float:
        """Calculate total tax burden across all jurisdictions."""
        return self.effective_uk_tax + self.effective_sa_tax + self.tax_withheld

    @property
    def effective_tax_rate(self) -> float:
        """Calculate effective tax rate as percentage."""
        if self.amount == 0:
            return 0.0
        return (self.total_tax_burden / self.amount) * 100
