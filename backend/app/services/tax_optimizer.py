"""UK Tax Optimization Engine - Comprehensive tax efficiency analysis and recommendations."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import date
from enum import Enum


class TaxBand(str, Enum):
    """UK Income Tax Bands 2024/25."""
    PERSONAL_ALLOWANCE = "personal_allowance"
    BASIC_RATE = "basic_rate"
    HIGHER_RATE = "higher_rate"
    ADDITIONAL_RATE = "additional_rate"


class TaxYear(str, Enum):
    """Tax year periods."""
    CURRENT_2024_25 = "2024/25"
    NEXT_2025_26 = "2025/26"


@dataclass
class TaxThresholds:
    """UK Tax Thresholds for 2024/25."""
    personal_allowance: float = 12570
    personal_allowance_taper_start: float = 100000
    basic_rate_threshold: float = 50270
    higher_rate_threshold: float = 125140
    additional_rate_threshold: float = 125140

    # Rates
    basic_rate: float = 0.20
    higher_rate: float = 0.40
    additional_rate: float = 0.45

    # National Insurance (Employee)
    ni_primary_threshold: float = 12570
    ni_upper_earnings_limit: float = 50270
    ni_rate_below_uel: float = 0.08  # Changed from 12% to 8% (2024/25)
    ni_rate_above_uel: float = 0.02

    # Dividend Allowance & Rates
    dividend_allowance: float = 500  # Reduced from £1,000 (2024/25)
    dividend_basic_rate: float = 0.0875
    dividend_higher_rate: float = 0.3375
    dividend_additional_rate: float = 0.3935

    # Capital Gains
    cgt_allowance: float = 3000  # Reduced from £6,000 (2024/25)
    cgt_basic_rate: float = 0.10
    cgt_higher_rate: float = 0.20
    cgt_property_basic_rate: float = 0.18
    cgt_property_higher_rate: float = 0.24

    # ISA & Pension
    isa_allowance: float = 20000
    pension_annual_allowance: float = 60000
    pension_lifetime_allowance_abolished: bool = True  # Abolished April 2024
    lump_sum_allowance: float = 268275
    lump_sum_death_benefit_allowance: float = 1073100


class TaxOptimizer:
    """Comprehensive UK tax optimization engine."""

    def __init__(self, tax_year: str = TaxYear.CURRENT_2024_25):
        """Initialize with tax year thresholds."""
        self.thresholds = TaxThresholds()
        self.tax_year = tax_year

    def calculate_income_tax(
        self,
        total_income: float,
        pension_contributions: float = 0,
        gift_aid_donations: float = 0
    ) -> Dict[str, float]:
        """
        Calculate income tax with allowances and reliefs.

        Returns breakdown of tax by band and total tax due.
        """
        # Adjust income for pension contributions (gross up relief at source)
        adjusted_income = total_income - pension_contributions

        # Calculate personal allowance (tapered for high earners)
        personal_allowance = self._calculate_personal_allowance(adjusted_income)

        # Taxable income
        taxable_income = max(0, adjusted_income - personal_allowance)

        # Calculate tax by band
        tax_breakdown = {
            "personal_allowance_used": personal_allowance,
            "taxable_income": taxable_income,
            "basic_rate_tax": 0.0,
            "higher_rate_tax": 0.0,
            "additional_rate_tax": 0.0,
            "total_tax": 0.0
        }

        remaining = taxable_income

        # Basic rate (20%)
        basic_rate_band = self.thresholds.basic_rate_threshold - self.thresholds.personal_allowance
        if remaining > 0:
            basic_taxable = min(remaining, basic_rate_band)
            tax_breakdown["basic_rate_tax"] = basic_taxable * self.thresholds.basic_rate
            remaining -= basic_taxable

        # Higher rate (40%)
        if remaining > 0:
            higher_rate_band = self.thresholds.higher_rate_threshold - self.thresholds.basic_rate_threshold
            higher_taxable = min(remaining, higher_rate_band)
            tax_breakdown["higher_rate_tax"] = higher_taxable * self.thresholds.higher_rate
            remaining -= higher_taxable

        # Additional rate (45%)
        if remaining > 0:
            tax_breakdown["additional_rate_tax"] = remaining * self.thresholds.additional_rate

        tax_breakdown["total_tax"] = (
            tax_breakdown["basic_rate_tax"] +
            tax_breakdown["higher_rate_tax"] +
            tax_breakdown["additional_rate_tax"]
        )

        return tax_breakdown

    def calculate_national_insurance(
        self,
        employment_income: float,
        is_self_employed: bool = False
    ) -> Dict[str, float]:
        """Calculate National Insurance contributions."""
        if employment_income <= self.thresholds.ni_primary_threshold:
            return {
                "below_uel": 0.0,
                "above_uel": 0.0,
                "total_ni": 0.0
            }

        ni_breakdown = {
            "below_uel": 0.0,
            "above_uel": 0.0,
            "total_ni": 0.0
        }

        # NI on earnings between primary threshold and UEL
        earnings_below_uel = min(
            employment_income - self.thresholds.ni_primary_threshold,
            self.thresholds.ni_upper_earnings_limit - self.thresholds.ni_primary_threshold
        )
        ni_breakdown["below_uel"] = earnings_below_uel * self.thresholds.ni_rate_below_uel

        # NI on earnings above UEL (2%)
        if employment_income > self.thresholds.ni_upper_earnings_limit:
            earnings_above_uel = employment_income - self.thresholds.ni_upper_earnings_limit
            ni_breakdown["above_uel"] = earnings_above_uel * self.thresholds.ni_rate_above_uel

        ni_breakdown["total_ni"] = ni_breakdown["below_uel"] + ni_breakdown["above_uel"]

        return ni_breakdown

    def calculate_dividend_tax(
        self,
        dividend_income: float,
        other_income: float
    ) -> Dict[str, float]:
        """Calculate dividend tax based on other income."""
        # Dividend allowance
        taxable_dividends = max(0, dividend_income - self.thresholds.dividend_allowance)

        if taxable_dividends == 0:
            return {
                "dividend_allowance_used": min(dividend_income, self.thresholds.dividend_allowance),
                "basic_rate_dividends": 0.0,
                "higher_rate_dividends": 0.0,
                "additional_rate_dividends": 0.0,
                "total_dividend_tax": 0.0
            }

        # Determine which tax band dividends fall into
        personal_allowance = self._calculate_personal_allowance(other_income)
        taxable_other = max(0, other_income - personal_allowance)

        dividend_breakdown = {
            "dividend_allowance_used": self.thresholds.dividend_allowance,
            "basic_rate_dividends": 0.0,
            "higher_rate_dividends": 0.0,
            "additional_rate_dividends": 0.0,
            "total_dividend_tax": 0.0
        }

        remaining_dividends = taxable_dividends
        current_income = taxable_other

        # Basic rate band
        basic_rate_limit = self.thresholds.basic_rate_threshold - self.thresholds.personal_allowance
        if current_income < basic_rate_limit:
            basic_rate_dividends = min(remaining_dividends, basic_rate_limit - current_income)
            dividend_breakdown["basic_rate_dividends"] = basic_rate_dividends * self.thresholds.dividend_basic_rate
            remaining_dividends -= basic_rate_dividends
            current_income += basic_rate_dividends

        # Higher rate band
        higher_rate_limit = self.thresholds.higher_rate_threshold - self.thresholds.personal_allowance
        if remaining_dividends > 0 and current_income < higher_rate_limit:
            higher_rate_dividends = min(remaining_dividends, higher_rate_limit - current_income)
            dividend_breakdown["higher_rate_dividends"] = higher_rate_dividends * self.thresholds.dividend_higher_rate
            remaining_dividends -= higher_rate_dividends
            current_income += higher_rate_dividends

        # Additional rate
        if remaining_dividends > 0:
            dividend_breakdown["additional_rate_dividends"] = remaining_dividends * self.thresholds.dividend_additional_rate

        dividend_breakdown["total_dividend_tax"] = (
            dividend_breakdown["basic_rate_dividends"] +
            dividend_breakdown["higher_rate_dividends"] +
            dividend_breakdown["additional_rate_dividends"]
        )

        return dividend_breakdown

    def optimize_pension_contributions(
        self,
        gross_income: float,
        current_pension_contribution: float,
        employer_pension_contribution: float = 0
    ) -> Dict[str, any]:
        """
        Optimize pension contributions for tax efficiency.

        Considers:
        - Annual Allowance (£60,000)
        - Tapered Annual Allowance for high earners
        - Tax relief at marginal rate
        - NI savings via salary sacrifice
        """
        recommendations = {
            "current_contribution": current_pension_contribution,
            "available_annual_allowance": self.thresholds.pension_annual_allowance,
            "optimal_contribution": 0.0,
            "tax_saving": 0.0,
            "ni_saving": 0.0,
            "total_saving": 0.0,
            "reasoning": []
        }

        # Check if taper applies
        threshold_income = gross_income - current_pension_contribution
        if threshold_income > 200000:
            # Taper applies
            adjusted_income = gross_income
            if adjusted_income > 260000:
                taper_reduction = min(50000, (adjusted_income - 260000) / 2)
                recommendations["available_annual_allowance"] = max(
                    10000,
                    self.thresholds.pension_annual_allowance - taper_reduction
                )
                recommendations["reasoning"].append(
                    f"Annual Allowance tapered to £{recommendations['available_annual_allowance']:,.0f} due to high income"
                )

        # Calculate room for additional contributions
        total_contributions = current_pension_contribution + employer_pension_contribution
        available_room = recommendations["available_annual_allowance"] - total_contributions

        if available_room <= 0:
            recommendations["reasoning"].append("Already at or above Annual Allowance limit")
            return recommendations

        # Calculate optimal additional contribution
        # Target: bring income down to avoid higher tax bands or taper
        current_tax = self.calculate_income_tax(gross_income, current_pension_contribution)

        # Try contributing enough to reduce to next band
        optimal_additional = 0.0

        if gross_income > self.thresholds.additional_rate_threshold:
            # Bring down to higher rate threshold
            optimal_additional = min(
                available_room,
                gross_income - self.thresholds.additional_rate_threshold
            )
            recommendations["reasoning"].append(
                f"Reduce income to £{self.thresholds.additional_rate_threshold:,.0f} to avoid 45% rate"
            )
        elif gross_income > self.thresholds.basic_rate_threshold:
            # Bring down to basic rate threshold
            optimal_additional = min(
                available_room,
                gross_income - self.thresholds.basic_rate_threshold
            )
            recommendations["reasoning"].append(
                f"Reduce income to £{self.thresholds.basic_rate_threshold:,.0f} to avoid 40% rate"
            )
        else:
            # Use all available allowance
            optimal_additional = available_room
            recommendations["reasoning"].append(
                "Maximize pension contributions within Annual Allowance"
            )

        recommendations["optimal_contribution"] = current_pension_contribution + optimal_additional

        # Calculate savings
        optimized_tax = self.calculate_income_tax(
            gross_income,
            recommendations["optimal_contribution"]
        )
        recommendations["tax_saving"] = current_tax["total_tax"] - optimized_tax["total_tax"]

        # NI saving (salary sacrifice only)
        if optimal_additional > 0:
            ni_rate = self.thresholds.ni_rate_below_uel if gross_income < self.thresholds.ni_upper_earnings_limit else self.thresholds.ni_rate_above_uel
            recommendations["ni_saving"] = optimal_additional * ni_rate

        recommendations["total_saving"] = recommendations["tax_saving"] + recommendations["ni_saving"]

        return recommendations

    def optimize_salary_dividend_split(
        self,
        total_remuneration: float,
        is_director: bool = True
    ) -> Dict[str, any]:
        """
        Optimize salary/dividend split for company directors.

        Typically optimal: Take salary up to NI threshold, rest as dividends.
        """
        recommendations = {
            "scenarios": []
        }

        # Scenario 1: All salary
        scenario_all_salary = {
            "name": "All Salary",
            "salary": total_remuneration,
            "dividends": 0.0
        }
        income_tax_1 = self.calculate_income_tax(total_remuneration, 0)
        ni_1 = self.calculate_national_insurance(total_remuneration)
        scenario_all_salary.update({
            "income_tax": income_tax_1["total_tax"],
            "ni": ni_1["total_ni"],
            "dividend_tax": 0.0,
            "total_tax": income_tax_1["total_tax"] + ni_1["total_ni"],
            "net_income": total_remuneration - income_tax_1["total_tax"] - ni_1["total_ni"]
        })
        recommendations["scenarios"].append(scenario_all_salary)

        # Scenario 2: Optimal split (salary to NI threshold, rest dividends)
        optimal_salary = self.thresholds.ni_primary_threshold
        optimal_dividends = max(0, total_remuneration - optimal_salary)

        scenario_optimal = {
            "name": "Optimal Split (Salary to NI threshold)",
            "salary": optimal_salary,
            "dividends": optimal_dividends
        }
        income_tax_2 = self.calculate_income_tax(optimal_salary, 0)
        ni_2 = self.calculate_national_insurance(optimal_salary)
        dividend_tax_2 = self.calculate_dividend_tax(optimal_dividends, optimal_salary)

        scenario_optimal.update({
            "income_tax": income_tax_2["total_tax"],
            "ni": ni_2["total_ni"],
            "dividend_tax": dividend_tax_2["total_dividend_tax"],
            "total_tax": income_tax_2["total_tax"] + ni_2["total_ni"] + dividend_tax_2["total_dividend_tax"],
            "net_income": total_remuneration - (income_tax_2["total_tax"] + ni_2["total_ni"] + dividend_tax_2["total_dividend_tax"])
        })
        recommendations["scenarios"].append(scenario_optimal)

        # Scenario 3: Salary to basic rate threshold
        basic_salary = self.thresholds.basic_rate_threshold
        basic_dividends = max(0, total_remuneration - basic_salary)

        if basic_salary < total_remuneration:
            scenario_basic = {
                "name": "Salary to Basic Rate Threshold",
                "salary": basic_salary,
                "dividends": basic_dividends
            }
            income_tax_3 = self.calculate_income_tax(basic_salary, 0)
            ni_3 = self.calculate_national_insurance(basic_salary)
            dividend_tax_3 = self.calculate_dividend_tax(basic_dividends, basic_salary)

            scenario_basic.update({
                "income_tax": income_tax_3["total_tax"],
                "ni": ni_3["total_ni"],
                "dividend_tax": dividend_tax_3["total_dividend_tax"],
                "total_tax": income_tax_3["total_tax"] + ni_3["total_ni"] + dividend_tax_3["total_dividend_tax"],
                "net_income": total_remuneration - (income_tax_3["total_tax"] + ni_3["total_ni"] + dividend_tax_3["total_dividend_tax"])
            })
            recommendations["scenarios"].append(scenario_basic)

        # Find optimal scenario
        optimal = max(recommendations["scenarios"], key=lambda x: x["net_income"])
        recommendations["recommended"] = optimal["name"]
        recommendations["potential_saving"] = optimal["net_income"] - scenario_all_salary["net_income"]

        return recommendations

    def optimize_isa_vs_taxable(
        self,
        available_capital: float,
        expected_annual_return: float,
        investment_years: int,
        current_income: float
    ) -> Dict[str, any]:
        """
        Compare ISA vs taxable investment accounts.

        ISAs: Tax-free growth and withdrawals
        Taxable: Subject to CGT (£3,000 allowance) and dividend tax (£500 allowance)
        """
        # Determine tax rate based on income
        personal_allowance = self._calculate_personal_allowance(current_income)
        taxable_income = max(0, current_income - personal_allowance)

        if taxable_income > self.thresholds.higher_rate_threshold - personal_allowance:
            cgt_rate = self.thresholds.cgt_higher_rate
            dividend_rate = self.thresholds.dividend_additional_rate
        elif taxable_income > self.thresholds.basic_rate_threshold - personal_allowance:
            cgt_rate = self.thresholds.cgt_higher_rate
            dividend_rate = self.thresholds.dividend_higher_rate
        else:
            cgt_rate = self.thresholds.cgt_basic_rate
            dividend_rate = self.thresholds.dividend_basic_rate

        # Calculate ISA scenario (tax-free)
        isa_contribution = min(available_capital, self.thresholds.isa_allowance)
        isa_final_value = isa_contribution * ((1 + expected_annual_return) ** investment_years)
        isa_gain = isa_final_value - isa_contribution

        # Calculate taxable account scenario
        taxable_contribution = available_capital
        taxable_final_value_gross = taxable_contribution * ((1 + expected_annual_return) ** investment_years)
        taxable_gain_gross = taxable_final_value_gross - taxable_contribution

        # Estimate tax on gains (simplified - annual CGT allowance)
        annual_gain = taxable_gain_gross / investment_years
        taxable_gain_per_year = max(0, annual_gain - self.thresholds.cgt_allowance)
        total_cgt = taxable_gain_per_year * investment_years * cgt_rate

        taxable_net_value = taxable_final_value_gross - total_cgt

        recommendations = {
            "isa_scenario": {
                "contribution": isa_contribution,
                "final_value": round(isa_final_value, 2),
                "gain": round(isa_gain, 2),
                "tax_paid": 0.0,
                "net_value": round(isa_final_value, 2)
            },
            "taxable_scenario": {
                "contribution": taxable_contribution,
                "final_value_gross": round(taxable_final_value_gross, 2),
                "gain_gross": round(taxable_gain_gross, 2),
                "estimated_tax": round(total_cgt, 2),
                "net_value": round(taxable_net_value, 2)
            },
            "isa_advantage": round(isa_final_value - taxable_net_value, 2) if isa_contribution == available_capital else None,
            "recommendation": "Maximize ISA contributions first - tax-free growth provides significant advantage"
        }

        # If capital exceeds ISA allowance
        if available_capital > self.thresholds.isa_allowance:
            excess_capital = available_capital - self.thresholds.isa_allowance
            recommendations["recommendation"] += f". Consider pension for additional £{excess_capital:,.0f} (higher tax relief)."

        return recommendations

    def _calculate_personal_allowance(self, income: float) -> float:
        """Calculate personal allowance with taper for high earners."""
        if income <= self.thresholds.personal_allowance_taper_start:
            return self.thresholds.personal_allowance

        # Taper: £1 reduction for every £2 over £100,000
        reduction = (income - self.thresholds.personal_allowance_taper_start) / 2
        return max(0, self.thresholds.personal_allowance - reduction)

    def generate_comprehensive_report(
        self,
        gross_income: float,
        employment_income: float,
        dividend_income: float,
        pension_contribution: float,
        available_capital: float
    ) -> Dict[str, any]:
        """Generate comprehensive tax optimization report."""
        report = {
            "current_position": {},
            "recommendations": [],
            "potential_savings": 0.0
        }

        # Current tax position
        income_tax = self.calculate_income_tax(gross_income, pension_contribution)
        ni = self.calculate_national_insurance(employment_income)
        dividend_tax = self.calculate_dividend_tax(dividend_income, employment_income)

        report["current_position"] = {
            "gross_income": gross_income,
            "income_tax": income_tax["total_tax"],
            "national_insurance": ni["total_ni"],
            "dividend_tax": dividend_tax["total_dividend_tax"],
            "total_tax": income_tax["total_tax"] + ni["total_ni"] + dividend_tax["total_dividend_tax"],
            "effective_rate": ((income_tax["total_tax"] + ni["total_ni"] + dividend_tax["total_dividend_tax"]) / gross_income * 100) if gross_income > 0 else 0
        }

        # Pension optimization
        pension_opt = self.optimize_pension_contributions(gross_income, pension_contribution, 0)
        if pension_opt["total_saving"] > 0:
            report["recommendations"].append({
                "category": "Pension Contributions",
                "priority": "High",
                "saving": pension_opt["total_saving"],
                "action": f"Increase pension contributions to £{pension_opt['optimal_contribution']:,.0f}",
                "details": pension_opt["reasoning"]
            })
            report["potential_savings"] += pension_opt["total_saving"]

        # ISA optimization
        if available_capital > 0:
            isa_opt = self.optimize_isa_vs_taxable(available_capital, 0.06, 10, gross_income)
            if isa_opt.get("isa_advantage") and isa_opt["isa_advantage"] > 0:
                report["recommendations"].append({
                    "category": "ISA Utilization",
                    "priority": "Medium",
                    "saving": isa_opt["isa_advantage"],
                    "action": f"Utilize full ISA allowance (£{self.thresholds.isa_allowance:,.0f})",
                    "details": [isa_opt["recommendation"]]
                })

        # Sort by savings potential
        report["recommendations"].sort(key=lambda x: x["saving"], reverse=True)

        return report