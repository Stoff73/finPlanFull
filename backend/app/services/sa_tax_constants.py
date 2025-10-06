"""South African Tax Constants and Rates

Tax rates, brackets, and constants for South African tax calculations.
Tax year: 2024/25 (1 March 2024 - 28 February 2025)

Sources:
- SARS (South African Revenue Service)
- 2024 Budget Speech
- Income Tax Act, 1962
"""

from dataclasses import dataclass
from enum import Enum
from datetime import date


class TaxYear(str, Enum):
    """South African tax years (March to February)."""
    CURRENT_2024_25 = "2024/25"
    PREVIOUS_2023_24 = "2023/24"
    NEXT_2025_26 = "2025/26"


class AgeCategory(str, Enum):
    """Age categories for tax calculations."""
    UNDER_65 = "under_65"
    AGE_65_TO_74 = "65_to_74"
    AGE_75_PLUS = "75_plus"


@dataclass
class IncomeTaxBracket:
    """Income tax bracket definition."""
    min_income: float
    max_income: float
    rate: float
    base_tax: float  # Tax on lower threshold

    def __repr__(self):
        return f"R{self.min_income:,.0f} - R{self.max_income:,.0f} @ {self.rate*100}%"


@dataclass
class SATaxRates:
    """South African Tax Rates for 2024/25 tax year."""

    # Income Tax Brackets (2024/25)
    # Source: SARS
    income_tax_brackets: list[IncomeTaxBracket] = None

    # Tax Rebates (2024/25)
    primary_rebate: float = 17235  # All taxpayers
    secondary_rebate: float = 9444  # Age 65-74
    tertiary_rebate: float = 3145   # Age 75+

    # Tax Thresholds (income below which no tax is payable)
    # Calculated as: rebate / marginal_rate
    tax_threshold_under_65: float = 95750
    tax_threshold_65_to_74: float = 148217
    tax_threshold_75_plus: float = 165689

    # Medical Tax Credits (2024/25)
    medical_aid_credit_main_member: float = 364  # Per month
    medical_aid_credit_first_dependent: float = 364  # Per month
    medical_aid_credit_additional_dependents: float = 246  # Per month, per dependent

    # Capital Gains Tax (2024/25)
    cgt_annual_exclusion: float = 40000  # Annual exclusion
    cgt_inclusion_rate_individuals: float = 0.40  # 40% inclusion rate
    cgt_inclusion_rate_companies: float = 0.80  # 80% inclusion rate
    cgt_inclusion_rate_trusts: float = 0.80  # 80% inclusion rate

    # Primary residence exclusion for CGT
    primary_residence_exclusion: float = 2000000  # R2m

    # Estate Duty (2024/25)
    estate_duty_abatement: float = 3500000  # R3.5m
    estate_duty_rate_standard: float = 0.20  # 20%
    estate_duty_rate_over_30m: float = 0.25  # 25% (proposed, check if enacted)
    estate_duty_threshold_higher_rate: float = 30000000  # R30m

    # Donations Tax (2024/25)
    donations_tax_annual_exemption: float = 100000  # R100k per tax year
    donations_tax_rate: float = 0.20  # 20%

    # Transfer Duty (Property) (2024/25)
    # Progressive rates on property transfers
    transfer_duty_threshold: float = 1100000  # No duty below R1.1m
    transfer_duty_brackets: list = None  # Defined below

    # Securities Transfer Tax
    securities_transfer_tax_rate: float = 0.0025  # 0.25%

    # Dividends Tax
    dividends_tax_rate: float = 0.20  # 20% withholding tax

    # Interest Exemption (2024/25)
    interest_exemption_under_65: float = 23800  # Annual
    interest_exemption_65_plus: float = 34500  # Annual

    # Tax-Free Savings Account (TFSA) Limits (2024/25)
    tfsa_annual_limit: float = 36000  # Per tax year
    tfsa_lifetime_limit: float = 500000  # Lifetime

    # Retirement Fund Contributions (Section 10C)
    # Deduction: 27.5% of the greater of remuneration or taxable income
    # Capped at R350,000 per tax year
    retirement_contribution_percentage: float = 0.275  # 27.5%
    retirement_contribution_cap: float = 350000  # R350k

    # Unemployment Insurance Fund (UIF)
    uif_employee_rate: float = 0.01  # 1% of remuneration
    uif_employer_rate: float = 0.01  # 1% of remuneration
    uif_max_monthly_earnings: float = 17712  # Maximum earnings subject to UIF

    # Skills Development Levy (SDL)
    sdl_rate: float = 0.01  # 1% of payroll (employer only)

    def __post_init__(self):
        """Initialize bracket data."""
        if self.income_tax_brackets is None:
            self.income_tax_brackets = [
                IncomeTaxBracket(
                    min_income=0,
                    max_income=237100,
                    rate=0.18,
                    base_tax=0
                ),
                IncomeTaxBracket(
                    min_income=237101,
                    max_income=370500,
                    rate=0.26,
                    base_tax=42678  # 237100 * 0.18
                ),
                IncomeTaxBracket(
                    min_income=370501,
                    max_income=512800,
                    rate=0.31,
                    base_tax=77362  # 42678 + (370500-237100)*0.26
                ),
                IncomeTaxBracket(
                    min_income=512801,
                    max_income=673000,
                    rate=0.36,
                    base_tax=121475  # 77362 + (512800-370500)*0.31
                ),
                IncomeTaxBracket(
                    min_income=673001,
                    max_income=857900,
                    rate=0.39,
                    base_tax=179147  # 121475 + (673000-512800)*0.36
                ),
                IncomeTaxBracket(
                    min_income=857901,
                    max_income=1817000,
                    rate=0.41,
                    base_tax=251258  # 179147 + (857900-673000)*0.39
                ),
                IncomeTaxBracket(
                    min_income=1817001,
                    max_income=float('inf'),
                    rate=0.45,
                    base_tax=644489  # 251258 + (1817000-857900)*0.41
                )
            ]

        if self.transfer_duty_brackets is None:
            self.transfer_duty_brackets = [
                {
                    "min_value": 0,
                    "max_value": 1100000,
                    "rate": 0.0,
                    "base_duty": 0
                },
                {
                    "min_value": 1100001,
                    "max_value": 1512500,
                    "rate": 0.03,
                    "base_duty": 0
                },
                {
                    "min_value": 1512501,
                    "max_value": 2117500,
                    "rate": 0.06,
                    "base_duty": 12375  # (1512500-1100000)*0.03
                },
                {
                    "min_value": 2117501,
                    "max_value": 2722500,
                    "rate": 0.08,
                    "base_duty": 48675  # 12375 + (2117500-1512500)*0.06
                },
                {
                    "min_value": 2722501,
                    "max_value": 12100000,
                    "rate": 0.11,
                    "base_duty": 97075  # 48675 + (2722500-2117500)*0.08
                },
                {
                    "min_value": 12100001,
                    "max_value": float('inf'),
                    "rate": 0.13,
                    "base_duty": 1128600  # 97075 + (12100000-2722500)*0.11
                }
            ]


# Global instance for tax year 2024/25
sa_tax_rates_2024_25 = SATaxRates()


def get_sa_tax_rates(tax_year: str = TaxYear.CURRENT_2024_25) -> SATaxRates:
    """
    Get SA tax rates for a specific tax year.

    Args:
        tax_year: Tax year (default: 2024/25)

    Returns:
        SATaxRates instance
    """
    # For now, only 2024/25 is implemented
    # TODO: Add historical rates and future projections
    if tax_year == TaxYear.CURRENT_2024_25:
        return sa_tax_rates_2024_25
    else:
        # Default to current year
        return sa_tax_rates_2024_25


def get_age_category(date_of_birth: date, as_of_date: date = None) -> AgeCategory:
    """
    Determine age category for tax calculations.

    Args:
        date_of_birth: Date of birth
        as_of_date: Date to calculate age as of (default: today)

    Returns:
        AgeCategory: under_65, 65_to_74, or 75_plus
    """
    if as_of_date is None:
        as_of_date = date.today()

    age = as_of_date.year - date_of_birth.year
    if (as_of_date.month, as_of_date.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1

    if age < 65:
        return AgeCategory.UNDER_65
    elif age < 75:
        return AgeCategory.AGE_65_TO_74
    else:
        return AgeCategory.AGE_75_PLUS


def get_tax_rebate(age_category: AgeCategory) -> float:
    """
    Get total tax rebate for age category.

    Args:
        age_category: Age category

    Returns:
        float: Total rebate amount
    """
    rates = sa_tax_rates_2024_25

    if age_category == AgeCategory.UNDER_65:
        return rates.primary_rebate
    elif age_category == AgeCategory.AGE_65_TO_74:
        return rates.primary_rebate + rates.secondary_rebate
    else:  # AGE_75_PLUS
        return rates.primary_rebate + rates.secondary_rebate + rates.tertiary_rebate


def get_tax_threshold(age_category: AgeCategory) -> float:
    """
    Get tax-free threshold for age category.

    Args:
        age_category: Age category

    Returns:
        float: Tax threshold (income below which no tax is due)
    """
    rates = sa_tax_rates_2024_25

    if age_category == AgeCategory.UNDER_65:
        return rates.tax_threshold_under_65
    elif age_category == AgeCategory.AGE_65_TO_74:
        return rates.tax_threshold_65_to_74
    else:  # AGE_75_PLUS
        return rates.tax_threshold_75_plus
