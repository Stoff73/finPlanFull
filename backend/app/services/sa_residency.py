"""South African Physical Presence Test Calculator

Determines SA tax residency status based on the Physical Presence Test.

The Physical Presence Test has two parts:
1. Physical Presence Test (days-based, objective)
2. Ordinarily Resident Test (subjective, based on real home)

References:
- SARS Interpretation Note 4 (Issue 4)
- Income Tax Act 1962 Section 1 (definition of "resident")
- South African Tax Administration Act
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import date
from enum import Enum


class SAResidencyStatus(str, Enum):
    """SA residency status."""
    RESIDENT = "resident"
    NON_RESIDENT = "non_resident"
    ORDINARILY_RESIDENT = "ordinarily_resident"
    UNDETERMINED = "undetermined"


@dataclass
class SAPhysicalPresenceInput:
    """Input data for SA Physical Presence Test."""
    tax_year: str  # e.g., "2024/25" (March to February)

    # Days in SA
    days_current_year: int
    days_year_1_prior: int = 0  # 1 year ago
    days_year_2_prior: int = 0  # 2 years ago
    days_year_3_prior: int = 0  # 3 years ago
    days_year_4_prior: int = 0  # 4 years ago
    days_year_5_prior: int = 0  # 5 years ago

    # Ordinarily resident indicators
    has_permanent_home_sa: bool = False
    has_permanent_home_abroad: bool = False
    has_family_sa: bool = False  # Spouse/children permanently in SA
    has_business_interests_sa: bool = False
    has_social_ties_sa: bool = False

    # Immigration status
    sa_citizen: bool = False
    sa_permanent_resident: bool = False
    has_work_permit: bool = False

    # Financial ties
    has_property_sa: bool = False
    has_bank_accounts_sa: bool = False
    has_investments_sa: bool = False


@dataclass
class SAPhysicalPresenceResult:
    """Result of SA Physical Presence Test."""
    status: SAResidencyStatus
    reason: str
    days_current_year: int
    days_prior_5_years_total: int
    days_prior_5_years_breakdown: Dict[str, int]

    # Physical presence test details
    physical_presence_test_met: bool
    days_test_91_in_current: bool
    days_test_91_each_of_5: bool
    days_test_915_total_in_5: bool

    # Ordinarily resident indicators
    ordinarily_resident_indicators: List[str]
    ordinarily_resident_score: int  # 0-10 scale

    test_applied: str  # "physical_presence", "ordinarily_resident", "both"


class SAResidencyCalculator:
    """SA Physical Presence Test calculator."""

    def calculate_residency(self, input_data: SAPhysicalPresenceInput) -> SAPhysicalPresenceResult:
        """
        Calculate SA residency status using the Physical Presence Test.

        Process:
        1. Check Physical Presence Test (objective, days-based)
        2. Assess Ordinarily Resident indicators (subjective)
        3. Determine overall status
        """
        # Calculate days breakdown
        days_breakdown = {
            "year_1_prior": input_data.days_year_1_prior,
            "year_2_prior": input_data.days_year_2_prior,
            "year_3_prior": input_data.days_year_3_prior,
            "year_4_prior": input_data.days_year_4_prior,
            "year_5_prior": input_data.days_year_5_prior,
        }

        total_prior_5_years = sum(days_breakdown.values())

        # Step 1: Physical Presence Test
        physical_test_result = self._check_physical_presence_test(
            input_data.days_current_year,
            days_breakdown
        )

        # Step 2: Ordinarily Resident Assessment
        ordinarily_resident_result = self._assess_ordinarily_resident(input_data)

        # Step 3: Determine overall status
        if physical_test_result["met"]:
            status = SAResidencyStatus.RESIDENT
            reason = physical_test_result["reason"]
            test_applied = "physical_presence"
        elif ordinarily_resident_result["score"] >= 7:
            # Strong indicators of ordinarily resident
            status = SAResidencyStatus.ORDINARILY_RESIDENT
            reason = f"Ordinarily Resident: Strong ties to SA (score: {ordinarily_resident_result['score']}/10)"
            test_applied = "ordinarily_resident"
        elif ordinarily_resident_result["score"] >= 5:
            # Moderate indicators - may be ordinarily resident
            status = SAResidencyStatus.ORDINARILY_RESIDENT
            reason = f"Ordinarily Resident: Moderate ties to SA (score: {ordinarily_resident_result['score']}/10)"
            test_applied = "ordinarily_resident"
        else:
            status = SAResidencyStatus.NON_RESIDENT
            reason = "Physical Presence Test not met and insufficient ties for Ordinarily Resident status"
            test_applied = "both"

        return SAPhysicalPresenceResult(
            status=status,
            reason=reason,
            days_current_year=input_data.days_current_year,
            days_prior_5_years_total=total_prior_5_years,
            days_prior_5_years_breakdown=days_breakdown,
            physical_presence_test_met=physical_test_result["met"],
            days_test_91_in_current=physical_test_result["91_in_current"],
            days_test_91_each_of_5=physical_test_result["91_each_of_5"],
            days_test_915_total_in_5=physical_test_result["915_total_in_5"],
            ordinarily_resident_indicators=ordinarily_resident_result["indicators"],
            ordinarily_resident_score=ordinarily_resident_result["score"],
            test_applied=test_applied
        )

    def _check_physical_presence_test(
        self,
        days_current: int,
        days_breakdown: Dict[str, int]
    ) -> Dict:
        """
        Check SA Physical Presence Test.

        Test is met if:
        - 91+ days in current year, AND
        - Either:
          a) 91+ days in each of the 5 preceding years, OR
          b) 915+ days in total during the 5 preceding years
        """
        # Requirement 1: 91+ days in current year
        test_91_in_current = days_current >= 91

        # Requirement 2a: 91+ days in each of the 5 preceding years
        test_91_each_of_5 = all(days >= 91 for days in days_breakdown.values())

        # Requirement 2b: 915+ days total in 5 preceding years
        total_prior_5 = sum(days_breakdown.values())
        test_915_total_in_5 = total_prior_5 >= 915

        # Test is met if current year AND (each of 5 OR total 915+)
        test_met = test_91_in_current and (test_91_each_of_5 or test_915_total_in_5)

        # Generate reason
        if not test_91_in_current:
            reason = f"Physical Presence Test not met: Only {days_current} days in current year (need 91+)"
        elif test_91_each_of_5:
            reason = f"Physical Presence Test met: {days_current} days in current year and 91+ days in each of the 5 preceding years"
        elif test_915_total_in_5:
            reason = f"Physical Presence Test met: {days_current} days in current year and {total_prior_5} total days in 5 preceding years (need 915+)"
        else:
            reason = f"Physical Presence Test not met: {days_current} days in current year but only {total_prior_5} total days in 5 preceding years (need 91 in each year OR 915+ total)"

        return {
            "met": test_met,
            "reason": reason,
            "91_in_current": test_91_in_current,
            "91_each_of_5": test_91_each_of_5,
            "915_total_in_5": test_915_total_in_5
        }

    def _assess_ordinarily_resident(self, input_data: SAPhysicalPresenceInput) -> Dict:
        """
        Assess Ordinarily Resident status.

        This is a subjective test based on where someone's "real home" is.
        We score various indicators on a 0-10 scale.
        """
        indicators = []
        score = 0

        # Home indicators (4 points max)
        if input_data.has_permanent_home_sa:
            indicators.append("Has permanent home in SA")
            score += 2
        if not input_data.has_permanent_home_abroad:
            indicators.append("No permanent home abroad")
            score += 1
        if input_data.has_property_sa:
            indicators.append("Owns property in SA")
            score += 1

        # Family indicators (2 points max)
        if input_data.has_family_sa:
            indicators.append("Immediate family resides in SA")
            score += 2

        # Economic indicators (2 points max)
        if input_data.has_business_interests_sa:
            indicators.append("Has business interests in SA")
            score += 1
        if input_data.has_investments_sa:
            indicators.append("Has investments in SA")
            score += 0.5
        if input_data.has_bank_accounts_sa:
            indicators.append("Has bank accounts in SA")
            score += 0.5

        # Social indicators (1 point max)
        if input_data.has_social_ties_sa:
            indicators.append("Has social ties in SA")
            score += 1

        # Immigration/citizenship (1 point max)
        if input_data.sa_citizen:
            indicators.append("SA citizen")
            score += 1
        elif input_data.sa_permanent_resident:
            indicators.append("SA permanent resident")
            score += 0.5

        # Cap at 10
        score = min(score, 10)

        return {
            "indicators": indicators,
            "score": int(score)
        }

    def determine_ceasing_ordinarily_resident(
        self,
        departure_date: date,
        years_abroad: int,
        severed_ties: List[str]
    ) -> Dict:
        """
        Determine when someone ceases to be ordinarily resident.

        Generally:
        - If you leave SA with intention not to return, you cease being ordinarily resident when you leave
        - If you leave SA but maintain ties, you may remain ordinarily resident for several years
        - 3+ years abroad with severed ties usually means you've ceased
        """
        strong_ties_severed = any([
            "sold_sa_home" in severed_ties,
            "moved_family_abroad" in severed_ties,
            "closed_business" in severed_ties,
            "relinquished_citizenship" in severed_ties
        ])

        if years_abroad >= 3 and strong_ties_severed:
            ceased = True
            reason = "Ceased being ordinarily resident: 3+ years abroad with strong ties severed"
        elif years_abroad >= 5:
            ceased = True
            reason = "Ceased being ordinarily resident: 5+ years abroad (presumption of ceasing)"
        else:
            ceased = False
            reason = f"Still ordinarily resident: Only {years_abroad} years abroad and/or ties not fully severed"

        return {
            "ceased": ceased,
            "reason": reason,
            "departure_date": departure_date,
            "years_abroad": years_abroad,
            "ties_severed": severed_ties
        }


# Convenience function
def calculate_sa_residency(
    days_current_year: int,
    days_prior_years: List[int] = None,
    has_permanent_home_sa: bool = False,
    has_family_sa: bool = False,
    sa_citizen: bool = False,
    tax_year: str = "2024/25"
) -> SAPhysicalPresenceResult:
    """
    Convenience function to calculate SA residency.

    Example:
        result = calculate_sa_residency(
            days_current_year=120,
            days_prior_years=[150, 140, 160, 155, 145],
            has_permanent_home_sa=True,
            has_family_sa=True,
            sa_citizen=True
        )
        print(result.status)  # "resident" or "non_resident" or "ordinarily_resident"
        print(result.reason)
    """
    calculator = SAResidencyCalculator()

    # Handle days_prior_years
    if days_prior_years is None:
        days_prior_years = [0, 0, 0, 0, 0]
    elif len(days_prior_years) < 5:
        # Pad with zeros
        days_prior_years = days_prior_years + [0] * (5 - len(days_prior_years))

    input_data = SAPhysicalPresenceInput(
        tax_year=tax_year,
        days_current_year=days_current_year,
        days_year_1_prior=days_prior_years[0],
        days_year_2_prior=days_prior_years[1],
        days_year_3_prior=days_prior_years[2],
        days_year_4_prior=days_prior_years[3],
        days_year_5_prior=days_prior_years[4],
        has_permanent_home_sa=has_permanent_home_sa,
        has_family_sa=has_family_sa,
        sa_citizen=sa_citizen
    )

    return calculator.calculate_residency(input_data)
