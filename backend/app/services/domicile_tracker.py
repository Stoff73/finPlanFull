"""Domicile Tracker Service

Tracks domicile status and forecasts deemed domicile for UK IHT purposes.

UK Deemed Domicile Rules (IHT):
- Resident in UK for 15 of past 20 tax years → Deemed domiciled for IHT
- Once deemed domiciled, status continues until non-resident for 4 complete tax years
- Different from income tax domicile rules

SA Domicile:
- Based on country of origin and intention to remain permanently
- Can change by domicile of choice (requires physical presence + intention)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import date, datetime
from enum import Enum


class DomicileStatus(str, Enum):
    """Domicile status."""
    UK_DOMICILED = "uk_domiciled"
    SA_DOMICILED = "sa_domiciled"
    OTHER_DOMICILED = "other_domiciled"
    DEEMED_UK_DOMICILED = "deemed_uk_domiciled"
    NOT_DEEMED_UK_DOMICILED = "not_deemed_uk_domiciled"


@dataclass
class DomicileTrackerInput:
    """Input for domicile tracker."""
    domicile_of_origin: str  # UK, SA, other
    current_domicile: str  # UK, SA, other, deemed_uk

    # UK residency history (dict of tax year → resident status)
    uk_residency_by_tax_year: Dict[str, bool]  # e.g., {"2023/24": True, "2022/23": False}

    # SA residency history
    sa_residency_by_tax_year: Dict[str, bool]

    # Current tax year
    current_tax_year: str  # e.g., "2024/25"

    # Domicile of choice intentions
    intends_permanent_uk: bool = False
    intends_permanent_sa: bool = False
    intends_leave_uk: bool = False
    planned_departure_year: Optional[str] = None


@dataclass
class DomicileTrackerResult:
    """Result of domicile tracking."""
    # Current status
    current_domicile: str
    domicile_of_origin: str
    is_deemed_uk_domiciled_iht: bool
    is_deemed_uk_domiciled_income_tax: bool

    # UK deemed domicile for IHT
    years_uk_resident_in_past_20: int
    uk_deemed_domicile_iht_date: Optional[str]  # Tax year when deemed domicile started
    years_until_deemed_domiciled: Optional[int]  # Years until deemed domicile (if not yet)
    years_non_resident_to_lose_deemed_status: int  # Years needed to lose deemed status

    # History
    uk_resident_years: List[str]  # List of tax years when UK resident
    sa_resident_years: List[str]  # List of tax years when SA resident

    # Forecasting
    forecast: Dict[str, any]
    recommendations: List[str]


class DomicileTracker:
    """Domicile tracking and forecasting service."""

    def track_domicile(self, input_data: DomicileTrackerInput) -> DomicileTrackerResult:
        """
        Track current domicile status and forecast future changes.
        """
        # Extract UK resident years from history
        uk_resident_years = [
            year for year, resident in input_data.uk_residency_by_tax_year.items()
            if resident
        ]

        sa_resident_years = [
            year for year, resident in input_data.sa_residency_by_tax_year.items()
            if resident
        ]

        # Calculate UK deemed domicile for IHT
        iht_deemed_result = self._check_uk_deemed_domicile_iht(
            input_data.uk_residency_by_tax_year,
            input_data.current_tax_year
        )

        # Calculate income tax deemed domicile (different rules)
        income_tax_deemed_result = self._check_uk_deemed_domicile_income_tax(
            input_data.uk_residency_by_tax_year,
            input_data.current_tax_year
        )

        # Generate forecast
        forecast = self._generate_forecast(
            input_data,
            iht_deemed_result,
            uk_resident_years
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            input_data,
            iht_deemed_result,
            forecast
        )

        return DomicileTrackerResult(
            current_domicile=input_data.current_domicile,
            domicile_of_origin=input_data.domicile_of_origin,
            is_deemed_uk_domiciled_iht=iht_deemed_result["is_deemed"],
            is_deemed_uk_domiciled_income_tax=income_tax_deemed_result["is_deemed"],
            years_uk_resident_in_past_20=iht_deemed_result["years_in_past_20"],
            uk_deemed_domicile_iht_date=iht_deemed_result["deemed_date"],
            years_until_deemed_domiciled=iht_deemed_result["years_until_deemed"],
            years_non_resident_to_lose_deemed_status=iht_deemed_result["years_to_lose"],
            uk_resident_years=uk_resident_years,
            sa_resident_years=sa_resident_years,
            forecast=forecast,
            recommendations=recommendations
        )

    def _check_uk_deemed_domicile_iht(
        self,
        uk_residency_by_tax_year: Dict[str, bool],
        current_tax_year: str
    ) -> Dict:
        """
        Check UK deemed domicile for IHT purposes.

        Rules:
        - Resident for 15 of past 20 tax years → Deemed domiciled
        - Continues until non-resident for 4 complete tax years
        """
        # Get past 20 tax years
        past_20_years = self._get_past_n_tax_years(current_tax_year, 20)

        # Count how many of past 20 years were UK resident
        uk_resident_count = sum(
            1 for year in past_20_years
            if uk_residency_by_tax_year.get(year, False)
        )

        is_deemed = uk_resident_count >= 15

        # Find when deemed domicile started (if applicable)
        deemed_date = None
        if is_deemed:
            # Find the first year where 15-of-20 was met
            for i, year in enumerate(past_20_years):
                years_to_check = past_20_years[max(0, i-19):i+1]
                count = sum(
                    1 for y in years_to_check
                    if uk_residency_by_tax_year.get(y, False)
                )
                if count >= 15:
                    deemed_date = year
                    break

        # Calculate years until deemed (if not yet)
        years_until_deemed = None
        if not is_deemed:
            years_until_deemed = 15 - uk_resident_count

        # Calculate years needed to lose deemed status
        # Need to be non-resident for 4 complete tax years
        years_to_lose = 0
        if is_deemed:
            # Check recent years for consecutive non-residence (from current backwards)
            recent_years = self._get_past_n_tax_years(current_tax_year, 5)
            consecutive_non_resident = 0
            for year in recent_years:  # Don't reverse - already in correct order (current first)
                if not uk_residency_by_tax_year.get(year, False):
                    consecutive_non_resident += 1
                else:
                    break
            years_to_lose = max(0, 4 - consecutive_non_resident)

        return {
            "is_deemed": is_deemed,
            "years_in_past_20": uk_resident_count,
            "deemed_date": deemed_date,
            "years_until_deemed": years_until_deemed,
            "years_to_lose": years_to_lose
        }

    def _check_uk_deemed_domicile_income_tax(
        self,
        uk_residency_by_tax_year: Dict[str, bool],
        current_tax_year: str
    ) -> Dict:
        """
        Check UK deemed domicile for income tax purposes.

        Rules:
        - Born in UK with UK domicile of origin: Deemed domiciled if UK resident in that year
        - Non-UK domicile: Deemed domiciled if resident in 15 of past 20 years
        """
        # For simplicity, using same 15-of-20 rule
        # In practice, this would check domicile of origin
        past_20_years = self._get_past_n_tax_years(current_tax_year, 20)
        uk_resident_count = sum(
            1 for year in past_20_years
            if uk_residency_by_tax_year.get(year, False)
        )

        return {
            "is_deemed": uk_resident_count >= 15,
            "years_in_past_20": uk_resident_count
        }

    def _generate_forecast(
        self,
        input_data: DomicileTrackerInput,
        iht_deemed_result: Dict,
        uk_resident_years: List[str]
    ) -> Dict:
        """
        Generate forecast of future domicile status.
        """
        forecast_scenarios = []

        # Scenario 1: Continue UK residence
        if not iht_deemed_result["is_deemed"] and iht_deemed_result["years_until_deemed"] is not None:
            years_until = iht_deemed_result["years_until_deemed"]
            forecast_year = self._add_tax_years(input_data.current_tax_year, years_until)
            forecast_scenarios.append({
                "scenario": "Continue UK residence",
                "outcome": "Deemed UK domiciled for IHT",
                "year": forecast_year,
                "years_from_now": years_until
            })

        # Scenario 2: Leave UK now
        if input_data.planned_departure_year:
            if iht_deemed_result["is_deemed"]:
                # Already deemed - need 4 years non-resident
                lose_deemed_year = self._add_tax_years(input_data.planned_departure_year, 4)
                forecast_scenarios.append({
                    "scenario": "Leave UK as planned",
                    "outcome": "Lose deemed domicile status",
                    "year": lose_deemed_year,
                    "years_from_now": self._years_between(input_data.current_tax_year, lose_deemed_year)
                })

        # Scenario 3: Become permanently resident in SA
        if input_data.intends_permanent_sa:
            forecast_scenarios.append({
                "scenario": "Acquire SA domicile of choice",
                "outcome": "SA domiciled (requires physical presence + clear intention)",
                "year": "Variable (depends on facts)",
                "years_from_now": None
            })

        return {
            "scenarios": forecast_scenarios,
            "current_trajectory": "Deemed UK domiciled" if iht_deemed_result["is_deemed"] else "Not deemed domiciled",
            "key_dates": {
                "current_tax_year": input_data.current_tax_year,
                "deemed_domicile_date": iht_deemed_result["deemed_date"],
                "planned_departure": input_data.planned_departure_year
            }
        }

    def _generate_recommendations(
        self,
        input_data: DomicileTrackerInput,
        iht_deemed_result: Dict,
        forecast: Dict
    ) -> List[str]:
        """
        Generate recommendations for domicile planning.
        """
        recommendations = []

        if iht_deemed_result["is_deemed"]:
            recommendations.append(
                "You are currently deemed UK domiciled for IHT purposes. "
                "To lose this status, you must be non-UK resident for 4 complete tax years."
            )
            if iht_deemed_result["years_to_lose"] > 0:
                recommendations.append(
                    f"You need {iht_deemed_result['years_to_lose']} more years of non-residence "
                    "to lose deemed domicile status."
                )
        else:
            if iht_deemed_result["years_until_deemed"] is not None:
                recommendations.append(
                    f"You will become deemed UK domiciled for IHT in "
                    f"{iht_deemed_result['years_until_deemed']} years if you remain UK resident."
                )

        # IHT planning
        if input_data.domicile_of_origin != "UK" and not iht_deemed_result["is_deemed"]:
            recommendations.append(
                "Consider excluded property trusts for non-UK assets before becoming deemed domiciled."
            )

        # Remittance basis
        if iht_deemed_result["years_in_past_20"] >= 7 and iht_deemed_result["years_in_past_20"] < 12:
            recommendations.append(
                "You may need to pay the £30,000 remittance basis charge if you want to use the remittance basis."
            )
        elif iht_deemed_result["years_in_past_20"] >= 12:
            recommendations.append(
                "You may need to pay the £60,000 remittance basis charge (or higher) if you want to use the remittance basis."
            )

        # Departure planning
        if input_data.intends_leave_uk and iht_deemed_result["is_deemed"]:
            recommendations.append(
                "If planning to leave the UK, ensure you meet the Statutory Residence Test requirements "
                "to become non-resident. Consider the 4-year wait to lose deemed domicile status."
            )

        return recommendations

    def _get_past_n_tax_years(self, current_tax_year: str, n: int) -> List[str]:
        """
        Get past N tax years including current.

        Example: current_tax_year="2024/25", n=3 → ["2024/25", "2023/24", "2022/23"]
        """
        years = []
        year = current_tax_year
        for _ in range(n):
            years.append(year)
            year = self._previous_tax_year(year)
        return years

    def _previous_tax_year(self, tax_year: str) -> str:
        """Get previous tax year. E.g., "2024/25" → "2023/24" """
        start_year = int(tax_year.split("/")[0])
        prev_start = start_year - 1
        prev_end = (prev_start + 1) % 100
        return f"{prev_start}/{prev_end:02d}"

    def _add_tax_years(self, tax_year: str, years_to_add: int) -> str:
        """Add years to a tax year. E.g., "2024/25" + 3 → "2027/28" """
        start_year = int(tax_year.split("/")[0])
        new_start = start_year + years_to_add
        new_end = (new_start + 1) % 100
        return f"{new_start}/{new_end:02d}"

    def _years_between(self, from_year: str, to_year: str) -> int:
        """Calculate years between two tax years."""
        from_start = int(from_year.split("/")[0])
        to_start = int(to_year.split("/")[0])
        return to_start - from_start


# Convenience function
def track_domicile(
    domicile_of_origin: str,
    current_domicile: str,
    uk_resident_years: List[str],
    current_tax_year: str = "2024/25",
    intends_permanent_uk: bool = False,
    planned_departure_year: Optional[str] = None
) -> DomicileTrackerResult:
    """
    Convenience function to track domicile.

    Example:
        result = track_domicile(
            domicile_of_origin="SA",
            current_domicile="SA",
            uk_resident_years=["2023/24", "2022/23", "2021/22", "2020/21"],
            current_tax_year="2024/25"
        )
        print(result.is_deemed_uk_domiciled_iht)
        print(result.years_until_deemed_domiciled)
    """
    tracker = DomicileTracker()

    # Build residency dictionary
    uk_residency_by_tax_year = {}
    for year in uk_resident_years:
        uk_residency_by_tax_year[year] = True

    input_data = DomicileTrackerInput(
        domicile_of_origin=domicile_of_origin,
        current_domicile=current_domicile,
        uk_residency_by_tax_year=uk_residency_by_tax_year,
        sa_residency_by_tax_year={},
        current_tax_year=current_tax_year,
        intends_permanent_uk=intends_permanent_uk,
        planned_departure_year=planned_departure_year
    )

    return tracker.track_domicile(input_data)
