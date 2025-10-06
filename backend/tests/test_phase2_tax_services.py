"""
Phase 2 Backend Tests - Tax Profile, Residency, Income, Domicile

Tests for dual-country tax planning services:
1. UK Statutory Residence Test (SRT)
2. SA Physical Presence Test
3. Income Sources API
4. Domicile Tracker
5. Tax Profile API
"""

import pytest
from datetime import datetime, date
from app.services.uk_residency import (
    UKResidencyCalculator,
    SRTInput,
    ResidencyStatus,
    TieType
)
from app.services.sa_residency import (
    SAResidencyCalculator,
    SAPhysicalPresenceInput,
    SAResidencyStatus
)
from app.services.domicile_tracker import (
    DomicileTracker,
    DomicileTrackerInput,
    DomicileStatus
)
from app.models.income_source import IncomeSource
from app.models.tax_profile import TaxProfile


# ============================================================================
# UK STATUTORY RESIDENCE TEST (SRT) TESTS
# ============================================================================

class TestUKStatutoryResidenceTest:
    """Tests for UK SRT calculator."""

    def test_automatic_overseas_test_1_fewer_than_16_days(self):
        """Test: Fewer than 16 days → Non-resident"""
        calculator = UKResidencyCalculator()
        input_data = SRTInput(
            tax_year="2024/25",
            days_in_uk=15
        )
        result = calculator.calculate_srt(input_data)

        assert result.status == ResidencyStatus.NON_RESIDENT
        assert "Automatic Overseas Test 1" in result.reason
        assert result.test_applied == "automatic_overseas"

    def test_automatic_overseas_test_2_fewer_than_46_not_prev_resident(self):
        """Test: Fewer than 46 days + not prev resident → Non-resident"""
        calculator = UKResidencyCalculator()
        input_data = SRTInput(
            tax_year="2024/25",
            days_in_uk=45,
            was_uk_resident_in_one_of_previous_3_years=False
        )
        result = calculator.calculate_srt(input_data)

        assert result.status == ResidencyStatus.NON_RESIDENT
        assert "Automatic Overseas Test 2" in result.reason

    def test_automatic_overseas_test_3_full_time_work_abroad(self):
        """Test: Full-time work abroad + <91 days + <31 work days → Non-resident"""
        calculator = UKResidencyCalculator()
        input_data = SRTInput(
            tax_year="2024/25",
            days_in_uk=90,
            full_time_work_abroad=True,
            uk_work_days=30
        )
        result = calculator.calculate_srt(input_data)

        assert result.status == ResidencyStatus.NON_RESIDENT
        assert "Automatic Overseas Test 3" in result.reason

    def test_automatic_uk_test_1_183_days_or_more(self):
        """Test: 183+ days → UK resident"""
        calculator = UKResidencyCalculator()
        input_data = SRTInput(
            tax_year="2024/25",
            days_in_uk=183
        )
        result = calculator.calculate_srt(input_data)

        assert result.status == ResidencyStatus.UK_RESIDENT
        assert "Automatic UK Test 1" in result.reason
        assert result.test_applied == "automatic_uk"

    def test_automatic_uk_test_3_full_time_work_uk(self):
        """Test: Full-time work in UK → UK resident"""
        calculator = UKResidencyCalculator()
        input_data = SRTInput(
            tax_year="2024/25",
            days_in_uk=120,
            full_time_work_uk=True,
            full_time_work_abroad=False
        )
        result = calculator.calculate_srt(input_data)

        assert result.status == ResidencyStatus.UK_RESIDENT
        assert "Automatic UK Test 3" in result.reason

    def test_sufficient_ties_leaver_91_120_days_2_ties(self):
        """Test: Leaver, 91-120 days, 2 ties (threshold=2) → UK resident"""
        calculator = UKResidencyCalculator()
        input_data = SRTInput(
            tax_year="2024/25",
            days_in_uk=100,
            was_uk_resident_in_one_of_previous_3_years=True,
            has_family_tie=True,
            has_accommodation_tie=True
        )
        result = calculator.calculate_srt(input_data)

        assert result.status == ResidencyStatus.UK_RESIDENT
        assert result.ties_count == 2
        assert result.sufficient_ties_threshold == 2
        assert TieType.FAMILY in result.ties_present
        assert TieType.ACCOMMODATION in result.ties_present

    def test_sufficient_ties_arriver_91_120_days_3_ties(self):
        """Test: Arriver, 91-120 days, 3 ties (threshold=3) → UK resident"""
        calculator = UKResidencyCalculator()
        input_data = SRTInput(
            tax_year="2024/25",
            days_in_uk=100,
            was_uk_resident_in_one_of_previous_3_years=False,
            has_family_tie=True,
            has_accommodation_tie=True,
            has_work_tie=True
        )
        result = calculator.calculate_srt(input_data)

        assert result.status == ResidencyStatus.UK_RESIDENT
        assert result.ties_count == 3
        assert result.sufficient_ties_threshold == 3

    def test_90_day_tie_previous_year_1(self):
        """Test: 90-day tie when 90+ days in previous year 1"""
        calculator = UKResidencyCalculator()
        input_data = SRTInput(
            tax_year="2024/25",
            days_in_uk=100,
            days_in_uk_previous_year_1=95,
            was_uk_resident_in_one_of_previous_3_years=True
        )
        result = calculator.calculate_srt(input_data)

        assert TieType.UK_DAYS_90 in result.ties_present

    def test_90_day_tie_previous_year_2(self):
        """Test: 90-day tie when 90+ days in previous year 2"""
        calculator = UKResidencyCalculator()
        input_data = SRTInput(
            tax_year="2024/25",
            days_in_uk=100,
            days_in_uk_previous_year_2=100,
            was_uk_resident_in_one_of_previous_3_years=True
        )
        result = calculator.calculate_srt(input_data)

        assert TieType.UK_DAYS_90 in result.ties_present


# ============================================================================
# SA PHYSICAL PRESENCE TEST TESTS
# ============================================================================

class TestSAPhysicalPresenceTest:
    """Tests for SA Physical Presence Test calculator."""

    def test_physical_presence_met_91_each_year(self):
        """Test: 91+ days current + 91+ each of 5 prior → Resident"""
        calculator = SAResidencyCalculator()
        input_data = SAPhysicalPresenceInput(
            tax_year="2024/25",
            days_current_year=120,
            days_year_1_prior=100,
            days_year_2_prior=95,
            days_year_3_prior=110,
            days_year_4_prior=105,
            days_year_5_prior=92
        )
        result = calculator.calculate_residency(input_data)

        assert result.status == SAResidencyStatus.RESIDENT
        assert result.physical_presence_test_met
        assert result.days_test_91_in_current
        assert result.days_test_91_each_of_5

    def test_physical_presence_met_915_total(self):
        """Test: 91+ current + 915+ total in 5 prior → Resident"""
        calculator = SAResidencyCalculator()
        input_data = SAPhysicalPresenceInput(
            tax_year="2024/25",
            days_current_year=100,
            days_year_1_prior=200,
            days_year_2_prior=200,
            days_year_3_prior=200,
            days_year_4_prior=200,
            days_year_5_prior=115
        )
        result = calculator.calculate_residency(input_data)

        assert result.status == SAResidencyStatus.RESIDENT
        assert result.physical_presence_test_met
        assert result.days_test_915_total_in_5
        assert result.days_prior_5_years_total == 915

    def test_physical_presence_not_met_insufficient_current(self):
        """Test: <91 days current → Non-resident"""
        calculator = SAResidencyCalculator()
        input_data = SAPhysicalPresenceInput(
            tax_year="2024/25",
            days_current_year=90,
            days_year_1_prior=100,
            days_year_2_prior=100,
            days_year_3_prior=100,
            days_year_4_prior=100,
            days_year_5_prior=100
        )
        result = calculator.calculate_residency(input_data)

        assert result.status == SAResidencyStatus.NON_RESIDENT
        assert not result.physical_presence_test_met
        assert not result.days_test_91_in_current

    def test_physical_presence_not_met_insufficient_prior(self):
        """Test: 91+ current but <91 each and <915 total → Non-resident"""
        calculator = SAResidencyCalculator()
        input_data = SAPhysicalPresenceInput(
            tax_year="2024/25",
            days_current_year=100,
            days_year_1_prior=80,
            days_year_2_prior=80,
            days_year_3_prior=80,
            days_year_4_prior=80,
            days_year_5_prior=80
        )
        result = calculator.calculate_residency(input_data)

        assert result.status == SAResidencyStatus.NON_RESIDENT
        assert not result.physical_presence_test_met
        assert result.days_prior_5_years_total == 400

    def test_ordinarily_resident_strong_ties(self):
        """Test: Strong ties to SA → Ordinarily resident"""
        calculator = SAResidencyCalculator()
        input_data = SAPhysicalPresenceInput(
            tax_year="2024/25",
            days_current_year=50,  # Not enough for physical presence
            has_permanent_home_sa=True,
            has_family_sa=True,
            has_business_interests_sa=True,
            has_social_ties_sa=True,
            sa_citizen=True
        )
        result = calculator.calculate_residency(input_data)

        assert result.status == SAResidencyStatus.ORDINARILY_RESIDENT
        assert result.ordinarily_resident_score >= 7
        assert not result.physical_presence_test_met

    def test_ordinarily_resident_moderate_ties(self):
        """Test: Moderate ties to SA → Ordinarily resident"""
        calculator = SAResidencyCalculator()
        input_data = SAPhysicalPresenceInput(
            tax_year="2024/25",
            days_current_year=50,
            has_permanent_home_sa=True,
            has_family_sa=True,
            has_property_sa=True
        )
        result = calculator.calculate_residency(input_data)

        assert result.status == SAResidencyStatus.ORDINARILY_RESIDENT
        assert result.ordinarily_resident_score >= 5


# ============================================================================
# DOMICILE TRACKER TESTS
# ============================================================================

class TestDomicileTracker:
    """Tests for domicile tracking and forecasting."""

    def test_not_deemed_domiciled_10_years(self):
        """Test: 10 of past 20 years UK resident → Not deemed domiciled"""
        tracker = DomicileTracker()
        # Create 10 years of UK residency (2015/16 to 2024/25)
        uk_residency = {}
        for year in range(2015, 2025):
            end_year = (year + 1) % 100
            uk_residency[f"{year}/{end_year:02d}"] = True

        input_data = DomicileTrackerInput(
            domicile_of_origin="SA",
            current_domicile="SA",
            uk_residency_by_tax_year=uk_residency,
            sa_residency_by_tax_year={},
            current_tax_year="2024/25"
        )
        result = tracker.track_domicile(input_data)

        assert not result.is_deemed_uk_domiciled_iht
        assert result.years_uk_resident_in_past_20 == 10
        assert result.years_until_deemed_domiciled == 5

    def test_deemed_domiciled_15_years(self):
        """Test: 15 of past 20 years UK resident → Deemed domiciled"""
        tracker = DomicileTracker()
        # Create 15 years of UK residency
        uk_residency = {}
        for i in range(10, 25):  # 15 years from 2010/11 to 2024/25
            uk_residency[f"20{i}/{i+1:02d}"] = True

        input_data = DomicileTrackerInput(
            domicile_of_origin="SA",
            current_domicile="deemed_uk",
            uk_residency_by_tax_year=uk_residency,
            sa_residency_by_tax_year={},
            current_tax_year="2024/25"
        )
        result = tracker.track_domicile(input_data)

        assert result.is_deemed_uk_domiciled_iht
        assert result.years_uk_resident_in_past_20 >= 15
        assert result.years_until_deemed_domiciled is None

    def test_forecast_years_until_deemed(self):
        """Test: Forecast when deemed domicile will occur"""
        tracker = DomicileTracker()
        # Create 10 years of UK residency (2014/15 to 2024/25 = 11 years, so use 10)
        uk_residency = {}
        for year in range(2015, 2025):  # 2015/16 to 2024/25 = 10 years
            end_year = (year + 1) % 100
            uk_residency[f"{year}/{end_year:02d}"] = True

        input_data = DomicileTrackerInput(
            domicile_of_origin="SA",
            current_domicile="SA",
            uk_residency_by_tax_year=uk_residency,
            sa_residency_by_tax_year={},
            current_tax_year="2024/25"
        )
        result = tracker.track_domicile(input_data)

        assert not result.is_deemed_uk_domiciled_iht
        assert result.years_until_deemed_domiciled == 5
        # Check forecast
        assert len(result.forecast["scenarios"]) > 0
        scenario = result.forecast["scenarios"][0]
        assert scenario["scenario"] == "Continue UK residence"
        assert scenario["outcome"] == "Deemed UK domiciled for IHT"

    def test_years_to_lose_deemed_status(self):
        """Test: Years needed to lose deemed status"""
        tracker = DomicileTracker()
        # 15 years resident (2005/06-2019/20), then 3 years non-resident (2020-2023)
        uk_residency = {}
        # 15 years resident
        for year in range(2005, 2020):
            end_year = (year + 1) % 100
            uk_residency[f"{year}/{end_year:02d}"] = True
        # 3 years non-resident
        uk_residency["2020/21"] = False
        uk_residency["2021/22"] = False
        uk_residency["2022/23"] = False

        input_data = DomicileTrackerInput(
            domicile_of_origin="SA",
            current_domicile="deemed_uk",
            uk_residency_by_tax_year=uk_residency,
            sa_residency_by_tax_year={},
            current_tax_year="2022/23"
        )
        result = tracker.track_domicile(input_data)

        # Need 4 years non-resident, already have 3, need 1 more
        assert result.years_non_resident_to_lose_deemed_status == 1

    def test_recommendations_approaching_deemed(self):
        """Test: Recommendations when approaching deemed domicile"""
        tracker = DomicileTracker()
        uk_residency = {f"201{i}/{i+1:02d}": True for i in range(1, 9)}  # 8 years

        input_data = DomicileTrackerInput(
            domicile_of_origin="SA",
            current_domicile="SA",
            uk_residency_by_tax_year=uk_residency,
            sa_residency_by_tax_year={},
            current_tax_year="2018/19"
        )
        result = tracker.track_domicile(input_data)

        assert not result.is_deemed_uk_domiciled_iht
        assert len(result.recommendations) > 0
        # Should recommend excluded property trusts
        assert any("excluded property" in rec.lower() for rec in result.recommendations)


# ============================================================================
# INCOME SOURCE MODEL TESTS
# ============================================================================

class TestIncomeSourceModel:
    """Tests for IncomeSource model calculations."""

    def test_effective_uk_tax_with_treaty_relief(self, db, fresh_test_user):
        """Test: UK tax with treaty relief"""
        income = IncomeSource(
            user_id=fresh_test_user.id,
            name="SA Salary",
            income_type="salary",
            amount=100000,
            currency="ZAR",
            source_country="SA",
            uk_taxable=True,
            uk_tax_deducted=5000,
            treaty_relief_applicable=True,
            treaty_relief_percentage=50,  # 50% relief
            tax_year="2024/25"
        )
        db.add(income)
        db.commit()

        # UK tax = 5000, relief = 50% = 2500, effective = 2500
        assert income.effective_uk_tax == 2500

    def test_effective_sa_tax_with_treaty_relief(self, db, fresh_test_user):
        """Test: SA tax with treaty relief"""
        income = IncomeSource(
            user_id=fresh_test_user.id,
            name="UK Salary",
            income_type="salary",
            amount=50000,
            currency="GBP",
            source_country="UK",
            sa_taxable=True,
            sa_tax_deducted=3000,
            treaty_relief_applicable=True,
            treaty_relief_percentage=100,  # 100% relief
            tax_year="2024/25"
        )
        db.add(income)
        db.commit()

        # SA tax = 3000, relief = 100% = 3000, effective = 0
        assert income.effective_sa_tax == 0

    def test_net_amount_calculation(self, db, fresh_test_user):
        """Test: Net amount after all taxes"""
        income = IncomeSource(
            user_id=fresh_test_user.id,
            name="Dual Taxed Income",
            income_type="dividend",
            amount=10000,
            currency="GBP",
            source_country="UK",
            uk_taxable=True,
            uk_tax_deducted=1000,
            sa_taxable=True,
            sa_tax_deducted=500,
            tax_withheld=200,
            tax_year="2024/25"
        )
        db.add(income)
        db.commit()

        # Net = 10000 - 1000 - 500 - 200 = 8300
        assert income.net_amount == 8300

    def test_total_tax_burden(self, db, fresh_test_user):
        """Test: Total tax burden across jurisdictions"""
        income = IncomeSource(
            user_id=fresh_test_user.id,
            name="Multi-jurisdiction Income",
            income_type="business",
            amount=50000,
            currency="GBP",
            source_country="offshore",
            uk_taxable=True,
            uk_tax_deducted=5000,
            sa_taxable=True,
            sa_tax_deducted=3000,
            tax_withheld=1000,
            tax_year="2024/25"
        )
        db.add(income)
        db.commit()

        # Total tax = 5000 + 3000 + 1000 = 9000
        assert income.total_tax_burden == 9000

    def test_effective_tax_rate(self, db, fresh_test_user):
        """Test: Effective tax rate calculation"""
        income = IncomeSource(
            user_id=fresh_test_user.id,
            name="Salary",
            income_type="salary",
            amount=100000,
            currency="GBP",
            source_country="UK",
            uk_taxable=True,
            uk_tax_deducted=20000,
            sa_taxable=False,
            tax_year="2024/25"
        )
        db.add(income)
        db.commit()

        # Effective rate = 20000 / 100000 * 100 = 20%
        assert income.effective_tax_rate == 20.0


# ============================================================================
# TAX PROFILE MODEL TESTS
# ============================================================================

class TestTaxProfileModel:
    """Tests for TaxProfile model properties."""

    def test_is_uk_domiciled(self, db, fresh_test_user):
        """Test: UK domiciled property"""
        profile = TaxProfile(
            user_id=fresh_test_user.id,
            domicile="UK",
            tax_residency="UK"
        )
        db.add(profile)
        db.commit()

        assert profile.is_uk_domiciled
        assert not profile.is_sa_domiciled

    def test_is_sa_domiciled(self, db, fresh_test_user):
        """Test: SA domiciled property"""
        profile = TaxProfile(
            user_id=fresh_test_user.id,
            domicile="SA",
            tax_residency="SA"
        )
        db.add(profile)
        db.commit()

        assert profile.is_sa_domiciled
        assert not profile.is_uk_domiciled

    def test_is_dual_resident(self, db, fresh_test_user):
        """Test: Dual resident property"""
        profile = TaxProfile(
            user_id=fresh_test_user.id,
            domicile="SA",
            tax_residency="dual_resident",
            uk_tax_resident=True,
            sa_tax_resident=True
        )
        db.add(profile)
        db.commit()

        assert profile.is_dual_resident

    def test_effective_tax_country_uk(self, db, fresh_test_user):
        """Test: Effective tax country when UK resident"""
        profile = TaxProfile(
            user_id=fresh_test_user.id,
            domicile="SA",
            tax_residency="UK",
            uk_tax_resident=True,
            sa_tax_resident=False
        )
        db.add(profile)
        db.commit()

        assert profile.effective_tax_country == "UK"

    def test_effective_tax_country_dual_with_treaty(self, db, fresh_test_user):
        """Test: Effective tax country for dual residents"""
        profile = TaxProfile(
            user_id=fresh_test_user.id,
            domicile="SA",
            tax_residency="dual_resident",
            uk_tax_resident=True,
            sa_tax_resident=True,
            treaty_tie_breaker_country="UK"
        )
        db.add(profile)
        db.commit()

        assert profile.effective_tax_country == "UK"
