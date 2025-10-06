"""UK Statutory Residence Test (SRT) Calculator

Determines UK tax residency status based on the Statutory Residence Test.

The SRT has three parts:
1. Automatic Overseas Tests (conclusively NOT UK resident)
2. Automatic UK Tests (conclusively UK resident)
3. Sufficient Ties Test (if not determined by automatic tests)

References:
- HMRC Guidance RDR3
- Finance Act 2013 Schedule 45
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import date, datetime
from enum import Enum


class ResidencyStatus(str, Enum):
    """UK residency status."""
    UK_RESIDENT = "uk_resident"
    NON_RESIDENT = "non_resident"
    UNDETERMINED = "undetermined"


class TieType(str, Enum):
    """Types of ties to the UK."""
    FAMILY = "family"
    ACCOMMODATION = "accommodation"
    WORK = "work"
    UK_DAYS_90 = "uk_days_90"  # 90+ days in UK in either of previous 2 years
    COUNTRY = "country"  # More time in UK than any other country


@dataclass
class SRTInput:
    """Input data for SRT calculation."""
    tax_year: str  # e.g., "2024/25"
    days_in_uk: int  # Days in UK during tax year

    # Previous years (for ties)
    days_in_uk_previous_year_1: int = 0  # Previous year
    days_in_uk_previous_year_2: int = 0  # 2 years ago

    # UK ties
    has_family_tie: bool = False  # Spouse/partner or minor children in UK
    has_accommodation_tie: bool = False  # Available accommodation in UK (used)
    has_work_tie: bool = False  # 40+ days work in UK
    has_country_tie: bool = False  # More days in UK than any other country

    # Work details (for automatic tests)
    full_time_work_abroad: bool = False  # Working full-time abroad
    full_time_work_uk: bool = False  # Working full-time in UK
    uk_work_days: int = 0  # Days worked in UK

    # Previous residency
    was_uk_resident_in_one_of_previous_3_years: bool = False

    # Split year treatment
    split_year_applicable: bool = False


@dataclass
class SRTResult:
    """Result of SRT calculation."""
    status: ResidencyStatus
    reason: str
    days_in_uk: int
    ties_count: int
    ties_present: List[TieType]
    sufficient_ties_threshold: int
    test_applied: str  # "automatic_overseas", "automatic_uk", "sufficient_ties"
    split_year_treatment: bool = False


class UKResidencyCalculator:
    """UK Statutory Residence Test calculator."""

    def __init__(self):
        # Sufficient ties thresholds
        # Key: (was_resident_in_prev_3_years, days_in_uk_range) → required_ties
        self.ties_thresholds = {
            # Previously resident (leaver)
            (True, "16-45"): 4,
            (True, "46-90"): 3,
            (True, "91-120"): 2,
            (True, "121-182"): 1,

            # Not previously resident (arriver)
            (False, "46-90"): 4,
            (False, "91-120"): 3,
            (False, "121-182"): 2,
        }

    def calculate_srt(self, input_data: SRTInput) -> SRTResult:
        """
        Calculate UK residency status using the Statutory Residence Test.

        Process:
        1. Check Automatic Overseas Tests
        2. Check Automatic UK Tests
        3. Apply Sufficient Ties Test
        """
        days = input_data.days_in_uk

        # Step 1: Automatic Overseas Tests (conclusively NOT UK resident)
        automatic_overseas = self._check_automatic_overseas_tests(input_data)
        if automatic_overseas:
            return SRTResult(
                status=ResidencyStatus.NON_RESIDENT,
                reason=automatic_overseas,
                days_in_uk=days,
                ties_count=0,
                ties_present=[],
                sufficient_ties_threshold=0,
                test_applied="automatic_overseas"
            )

        # Step 2: Automatic UK Tests (conclusively UK resident)
        automatic_uk = self._check_automatic_uk_tests(input_data)
        if automatic_uk:
            ties = self._count_ties(input_data)
            return SRTResult(
                status=ResidencyStatus.UK_RESIDENT,
                reason=automatic_uk,
                days_in_uk=days,
                ties_count=len(ties),
                ties_present=ties,
                sufficient_ties_threshold=0,
                test_applied="automatic_uk"
            )

        # Step 3: Sufficient Ties Test
        return self._apply_sufficient_ties_test(input_data)

    def _check_automatic_overseas_tests(self, input_data: SRTInput) -> Optional[str]:
        """
        Check Automatic Overseas Tests.

        Returns reason if test passes (NOT UK resident).
        """
        days = input_data.days_in_uk

        # Test 1: Fewer than 16 days in UK
        if days < 16:
            return "Automatic Overseas Test 1: Fewer than 16 days in UK"

        # Test 2: Fewer than 46 days AND not UK resident in any of previous 3 years
        if days < 46 and not input_data.was_uk_resident_in_one_of_previous_3_years:
            return "Automatic Overseas Test 2: Fewer than 46 days in UK and not UK resident in previous 3 years"

        # Test 3: Full-time work abroad (and fewer than 91 days in UK, fewer than 31 days working in UK)
        if (input_data.full_time_work_abroad and
            days < 91 and
            input_data.uk_work_days < 31):
            return "Automatic Overseas Test 3: Full-time work abroad (fewer than 91 days in UK, fewer than 31 work days in UK)"

        return None

    def _check_automatic_uk_tests(self, input_data: SRTInput) -> Optional[str]:
        """
        Check Automatic UK Tests.

        Returns reason if test passes (UK resident).
        """
        days = input_data.days_in_uk

        # Test 1: 183+ days in UK
        if days >= 183:
            return "Automatic UK Test 1: 183 or more days in UK"

        # Test 2: Only home in UK (available for at least 91 days, used for at least 30 days)
        # Note: This test requires additional data not in our input, simplified

        # Test 3: Full-time work in UK (and not full-time work abroad)
        if input_data.full_time_work_uk and not input_data.full_time_work_abroad:
            return "Automatic UK Test 3: Full-time work in UK"

        # Test 4: Died in tax year, UK resident in previous year, and accommodation tie in year of death
        # Note: Requires death date, not implemented

        return None

    def _apply_sufficient_ties_test(self, input_data: SRTInput) -> SRTResult:
        """
        Apply Sufficient Ties Test.

        Determine residency based on number of days and ties to UK.
        """
        days = input_data.days_in_uk
        was_resident = input_data.was_uk_resident_in_one_of_previous_3_years

        # Count ties
        ties = self._count_ties(input_data)
        ties_count = len(ties)

        # Determine required ties based on days and previous residency
        required_ties = self._get_required_ties(days, was_resident)

        if required_ties is None:
            # Days < 16: Already caught by automatic overseas
            # Days > 182: Already caught by automatic UK
            # Days 16-45 and not previously resident: Non-resident
            if days >= 16 and days <= 45 and not was_resident:
                return SRTResult(
                    status=ResidencyStatus.NON_RESIDENT,
                    reason="Sufficient Ties Test: 16-45 days and not previously UK resident",
                    days_in_uk=days,
                    ties_count=ties_count,
                    ties_present=ties,
                    sufficient_ties_threshold=0,
                    test_applied="sufficient_ties"
                )
            else:
                return SRTResult(
                    status=ResidencyStatus.UNDETERMINED,
                    reason="Sufficient Ties Test: Insufficient data",
                    days_in_uk=days,
                    ties_count=ties_count,
                    ties_present=ties,
                    sufficient_ties_threshold=0,
                    test_applied="sufficient_ties"
                )

        # Compare ties to threshold
        if ties_count >= required_ties:
            status = ResidencyStatus.UK_RESIDENT
            reason = f"Sufficient Ties Test: {ties_count} ties (threshold: {required_ties}) with {days} days in UK"
        else:
            status = ResidencyStatus.NON_RESIDENT
            reason = f"Sufficient Ties Test: Only {ties_count} ties (threshold: {required_ties}) with {days} days in UK"

        return SRTResult(
            status=status,
            reason=reason,
            days_in_uk=days,
            ties_count=ties_count,
            ties_present=ties,
            sufficient_ties_threshold=required_ties,
            test_applied="sufficient_ties"
        )

    def _count_ties(self, input_data: SRTInput) -> List[TieType]:
        """Count UK ties present."""
        ties = []

        if input_data.has_family_tie:
            ties.append(TieType.FAMILY)

        if input_data.has_accommodation_tie:
            ties.append(TieType.ACCOMMODATION)

        if input_data.has_work_tie:
            ties.append(TieType.WORK)

        # 90-day tie: 90+ days in UK in either of previous 2 years
        if (input_data.days_in_uk_previous_year_1 >= 90 or
            input_data.days_in_uk_previous_year_2 >= 90):
            ties.append(TieType.UK_DAYS_90)

        if input_data.has_country_tie:
            ties.append(TieType.COUNTRY)

        return ties

    def _get_required_ties(self, days: int, was_resident: bool) -> Optional[int]:
        """
        Get required number of ties for sufficient ties test.

        Returns None if outside sufficient ties test range.
        """
        # Determine day range
        if was_resident:
            # Previously resident (leaver)
            if days < 16:
                return None
            elif days <= 45:
                return 4
            elif days <= 90:
                return 3
            elif days <= 120:
                return 2
            elif days <= 182:
                return 1
            else:
                return None  # 183+ covered by automatic UK test
        else:
            # Not previously resident (arriver)
            if days < 46:
                return None  # < 46 covered by automatic overseas
            elif days <= 90:
                return 4
            elif days <= 120:
                return 3
            elif days <= 182:
                return 2
            else:
                return None  # 183+ covered by automatic UK test

    def determine_split_year_treatment(
        self,
        arrival_date: Optional[date] = None,
        departure_date: Optional[date] = None,
        reason: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Determine if split year treatment applies.

        Split year treatment can apply in specific circumstances:
        - Starting full-time work abroad
        - Starting to have only home abroad
        - Ceasing to have only home in UK
        - Starting full-time work in UK
        - Ceasing full-time work abroad
        - Starting to have home in UK

        Note: Simplified implementation - full rules are complex.
        """
        # This would require detailed case analysis
        # Placeholder for now
        return {
            "applies": False,
            "uk_part_start": None,
            "uk_part_end": None,
            "reason": "Split year determination requires detailed case analysis"
        }


# Convenience function
def calculate_uk_residency(
    days_in_uk: int,
    days_previous_year: int = 0,
    has_family_tie: bool = False,
    has_accommodation_tie: bool = False,
    has_work_tie: bool = False,
    has_country_tie: bool = False,
    was_previously_resident: bool = False,
    tax_year: str = "2024/25"
) -> SRTResult:
    """
    Convenience function to calculate UK residency.

    Example:
        result = calculate_uk_residency(
            days_in_uk=120,
            days_previous_year=150,
            has_family_tie=True,
            has_accommodation_tie=True,
            was_previously_resident=True
        )
        print(result.status)  # "uk_resident" or "non_resident"
        print(result.reason)
    """
    calculator = UKResidencyCalculator()

    input_data = SRTInput(
        tax_year=tax_year,
        days_in_uk=days_in_uk,
        days_in_uk_previous_year_1=days_previous_year,
        has_family_tie=has_family_tie,
        has_accommodation_tie=has_accommodation_tie,
        has_work_tie=has_work_tie,
        has_country_tie=has_country_tie,
        was_uk_resident_in_one_of_previous_3_years=was_previously_resident
    )

    return calculator.calculate_srt(input_data)
