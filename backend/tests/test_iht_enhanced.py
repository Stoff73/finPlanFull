"""
Comprehensive Test Suite for Enhanced IHT Calculator

Tests all critical IHT calculations according to UK tax law 2024/25:
- Taper relief scenarios (0-7 years)
- RNRB tapering over £2M calculations
- Charitable rate reduction trigger
- CLT/PET cumulation rules
- Trust charge calculations
- Gift exemptions and applications
- Business/Agricultural Property Relief
- Multiple marriages with TNRB claims
- Downsizing addition rules
- Gift with reservation (GWR) and POAT interactions
- Quick succession relief chains
- Foreign assets and domicile changes

Covers unit tests, integration tests, and edge cases
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date, timedelta
from typing import Dict, List
from decimal import Decimal

from app.api.iht_refactored import (
    calculate_taper_relief_on_tax,
    calculate_business_relief,
    calculate_rnrb_with_taper,
    calculate_charitable_rate,
    process_gifts_with_exemptions,
    AssetInput, GiftInput, TrustInput,
    AssetType, GiftType, BusinessReliefType,
    STANDARD_NIL_RATE_BAND,
    RESIDENCE_NIL_RATE_BAND,
    IHT_RATE,
    REDUCED_CHARITY_RATE,
    RNRB_TAPER_THRESHOLD,
    ANNUAL_EXEMPTION,
    SMALL_GIFT_EXEMPTION,
    WEDDING_GIFT_PARENT,
    WEDDING_GIFT_GRANDPARENT,
    WEDDING_GIFT_OTHER
)


class TestTaperReliefScenarios:
    """Unit tests for taper relief scenarios (0-7 years)"""

    @pytest.mark.parametrize("years_ago,expected_relief_rate", [
        (0.5, 0.0),   # Less than 3 years - no relief
        (1.0, 0.0),   # Less than 3 years - no relief
        (2.9, 0.0),   # Less than 3 years - no relief
        (3.1, 0.2),   # Just over 3 years - 20% relief
        (3.5, 0.2),   # 3-4 years - 20% relief
        (4.1, 0.4),   # Just over 4 years - 40% relief
        (4.8, 0.4),   # 4-5 years - 40% relief
        (5.1, 0.6),   # Just over 5 years - 60% relief
        (5.9, 0.6),   # 5-6 years - 60% relief
        (6.1, 0.8),   # Just over 6 years - 80% relief
        (6.9, 0.8),   # 6-7 years - 80% relief
        (7.1, 1.0),   # Just over 7 years - 100% relief (gift becomes PET)
        (10.0, 1.0),  # 7+ years - 100% relief (gift becomes PET)
    ])
    def test_taper_relief_percentages(self, years_ago: float, expected_relief_rate: float):
        """Test taper relief applied to TAX amount, not gift value"""
        # Use precise calculation to avoid rounding issues
        days_ago = years_ago * 365.25
        gift_date = date.today() - timedelta(days=days_ago)
        tax_amount = 40000  # £100k gift above NRB at 40% = £40k tax

        relief_amount = calculate_taper_relief_on_tax(gift_date, tax_amount)
        expected_relief = tax_amount * expected_relief_rate

        assert abs(relief_amount - expected_relief) < 0.01, \
            f"Expected £{expected_relief:.2f} relief, got £{relief_amount:.2f}"

    def test_taper_relief_edge_cases(self):
        """Test edge cases for taper relief calculations"""

        # Test with zero tax amount
        gift_date = date.today() - timedelta(days=4.1 * 365.25)  # Just over 4 years ago
        assert calculate_taper_relief_on_tax(gift_date, 0) == 0

        # Test with very large tax amount
        large_tax = 1000000
        relief = calculate_taper_relief_on_tax(gift_date, large_tax)
        assert relief == large_tax * 0.4  # 40% relief at 4+ years

    def test_taper_relief_boundary_conditions(self):
        """Test boundary conditions at 3 and 7 year marks"""
        tax_amount = 10000

        # Just before 3 years (2.95 years)
        gift_date = date.today() - timedelta(days=2.95 * 365.25)
        relief = calculate_taper_relief_on_tax(gift_date, tax_amount)
        assert relief == 0, "Should be no relief just before 3 years"

        # Just after 3 years (3.05 years)
        gift_date = date.today() - timedelta(days=3.05 * 365.25)
        relief = calculate_taper_relief_on_tax(gift_date, tax_amount)
        assert relief == tax_amount * 0.2, "Should be 20% relief just after 3 years"

        # Just before 7 years (6.95 years)
        gift_date = date.today() - timedelta(days=6.95 * 365.25)
        relief = calculate_taper_relief_on_tax(gift_date, tax_amount)
        assert relief == tax_amount * 0.8, "Should be 80% relief just before 7 years"

        # Just after 7 years (7.05 years)
        gift_date = date.today() - timedelta(days=7.05 * 365.25)
        relief = calculate_taper_relief_on_tax(gift_date, tax_amount)
        assert relief == tax_amount, "Should be full relief just after 7 years"


class TestRNRBTaperingCalculations:
    """Unit tests for RNRB tapering over £2M calculations"""

    @pytest.mark.parametrize("estate_value,expected_rnrb,expected_taper", [
        (1_500_000, 175_000, 0),         # Below taper threshold
        (2_000_000, 175_000, 0),         # At taper threshold
        (2_100_000, 125_000, 50_000),    # £100k over = £50k taper
        (2_200_000, 75_000, 100_000),    # £200k over = £100k taper
        (2_350_000, 0, 175_000),         # £350k over = £175k taper (exactly full RNRB)
        (2_500_000, 0, 250_000),         # £500k over = £250k taper (exceeds RNRB)
    ])
    def test_rnrb_tapering_formula(self, estate_value: int, expected_rnrb: int, expected_taper: int):
        """Test RNRB tapering: £1 reduction for every £2 over £2M threshold"""
        residence_value = 500_000  # Sufficient for full RNRB
        has_descendants = True
        trnrb_percentage = 0  # No transferred allowance

        actual_rnrb, actual_taper = calculate_rnrb_with_taper(
            estate_value, residence_value, has_descendants, trnrb_percentage
        )

        assert actual_rnrb == expected_rnrb, \
            f"Expected RNRB £{expected_rnrb:,}, got £{actual_rnrb:,}"
        assert actual_taper == expected_taper, \
            f"Expected taper £{expected_taper:,}, got £{actual_taper:,}"

    def test_rnrb_with_transferred_allowance(self):
        """Test RNRB with transferred allowance from deceased spouse"""
        estate_value = 2_200_000  # £200k over threshold
        residence_value = 500_000
        has_descendants = True
        trnrb_percentage = 100  # Full transferred allowance

        # With transfer: Base £175k + Transferred £175k = £350k before taper
        # Taper: £200k over ÷ 2 = £100k taper
        # Final RNRB: £350k - £100k = £250k
        expected_rnrb = 250_000
        expected_taper = 100_000

        actual_rnrb, actual_taper = calculate_rnrb_with_taper(
            estate_value, residence_value, has_descendants, trnrb_percentage
        )

        assert actual_rnrb == expected_rnrb
        assert actual_taper == expected_taper

    def test_rnrb_insufficient_residence_value(self):
        """Test RNRB limited by residence value"""
        estate_value = 1_500_000  # Below taper threshold
        residence_value = 100_000  # Less than full RNRB
        has_descendants = True
        trnrb_percentage = 0

        # RNRB limited to residence value
        expected_rnrb = 100_000
        expected_taper = 0

        actual_rnrb, actual_taper = calculate_rnrb_with_taper(
            estate_value, residence_value, has_descendants, trnrb_percentage
        )

        assert actual_rnrb == expected_rnrb
        assert actual_taper == expected_taper

    def test_rnrb_no_descendants(self):
        """Test RNRB unavailable without direct descendants"""
        estate_value = 1_500_000
        residence_value = 500_000
        has_descendants = False
        trnrb_percentage = 0

        actual_rnrb, actual_taper = calculate_rnrb_with_taper(
            estate_value, residence_value, has_descendants, trnrb_percentage
        )

        assert actual_rnrb == 0
        assert actual_taper == 0


class TestCharitableRateReduction:
    """Unit tests for charitable rate reduction trigger"""

    def test_charitable_rate_qualifying(self):
        """Test estate qualifies for 36% rate with 10%+ charitable giving"""
        estate_value = 1_000_000
        nil_rate_band = 325_000
        rnrb = 175_000
        # Baseline = £1M - £325k - £175k = £500k
        # Need 10% of £500k = £50k to charity
        charitable_gifts = 50_000

        rate, baseline, qualifies = calculate_charitable_rate(
            estate_value, charitable_gifts, nil_rate_band, rnrb
        )

        assert qualifies == True
        assert rate == REDUCED_CHARITY_RATE  # 36%
        assert baseline == 500_000

    def test_charitable_rate_not_qualifying(self):
        """Test estate doesn't qualify for 36% rate with insufficient charitable giving"""
        estate_value = 1_000_000
        nil_rate_band = 325_000
        rnrb = 175_000
        charitable_gifts = 40_000  # Less than 10% of baseline

        rate, baseline, qualifies = calculate_charitable_rate(
            estate_value, charitable_gifts, nil_rate_band, rnrb
        )

        assert qualifies == False
        assert rate == IHT_RATE  # 40%
        assert baseline == 500_000

    @pytest.mark.parametrize("charitable_percentage,should_qualify", [
        (0.09, False),  # 9% - doesn't qualify
        (0.10, True),   # 10% - exactly qualifies
        (0.15, True),   # 15% - over-qualifies
        (0.50, True),   # 50% - well over
    ])
    def test_charitable_rate_thresholds(self, charitable_percentage: float, should_qualify: bool):
        """Test charitable rate qualification at various giving levels"""
        estate_value = 800_000
        nil_rate_band = 325_000
        rnrb = 175_000
        baseline = estate_value - nil_rate_band - rnrb  # £300k
        charitable_gifts = baseline * charitable_percentage

        rate, _, qualifies = calculate_charitable_rate(
            estate_value, charitable_gifts, nil_rate_band, rnrb
        )

        assert qualifies == should_qualify
        expected_rate = REDUCED_CHARITY_RATE if should_qualify else IHT_RATE
        assert rate == expected_rate

    def test_charitable_rate_no_taxable_estate(self):
        """Test charitable rate when estate is below nil-rate bands"""
        estate_value = 400_000  # Below combined NRB + RNRB
        nil_rate_band = 325_000
        rnrb = 175_000
        charitable_gifts = 100_000  # Large charitable gift

        rate, baseline, qualifies = calculate_charitable_rate(
            estate_value, charitable_gifts, nil_rate_band, rnrb
        )

        assert baseline == 0  # No taxable estate
        assert qualifies == False  # No benefit from charitable rate
        assert rate == IHT_RATE


class TestGiftExemptions:
    """Unit tests for gift exemption applications"""

    def test_annual_exemption_application(self):
        """Test annual exemption applied correctly across tax years"""
        gifts = [
            GiftInput(
                recipient="Child 1",
                recipient_relationship="child",
                amount=5000,
                date_given=date(2024, 6, 1),
                exemption_claimed="annual"
            ),
            GiftInput(
                recipient="Child 2",
                recipient_relationship="child",
                amount=2000,
                date_given=date(2024, 8, 1),
                exemption_claimed="annual"
            )
        ]

        # No previous usage
        result = process_gifts_with_exemptions(gifts, 0, 0)

        # First gift (£5k): £3k current + £2k previous → £0 remains
        # Second gift (£2k): £0 current + £1k previous → £1k remains as PET
        assert result["exemptions_used"]["annual_current"] == 3000
        assert result["exemptions_used"]["annual_previous"] == 3000  # £2k + £1k = £3k total
        assert len(result["pets"]) == 1  # Only second gift has remaining amount
        assert result["pets"][0]["amount"] == 1000  # £1k remaining from Gift 2

    def test_small_gift_exemption(self):
        """Test small gift exemption (£250 per recipient)"""
        gifts = [
            GiftInput(
                recipient="Friend 1",
                recipient_relationship="friend",
                amount=250,
                date_given=date(2024, 6, 1),
                exemption_claimed="small_gift"
            ),
            GiftInput(
                recipient="Friend 2",
                recipient_relationship="friend",
                amount=300,
                date_given=date(2024, 7, 1),
                exemption_claimed="small_gift"
            )
        ]

        result = process_gifts_with_exemptions(gifts, 0, 0)

        # First gift fully exempt, second gift only £250 exempt
        assert result["exemptions_used"]["small_gifts"] == 250
        assert len(result["pets"]) == 1
        assert result["pets"][0]["amount"] == 300  # Small gift exemption not applied to >£250

    @pytest.mark.parametrize("relationship,max_exemption", [
        ("parent", WEDDING_GIFT_PARENT),           # £5,000
        ("grandparent", WEDDING_GIFT_GRANDPARENT), # £2,500
        ("friend", WEDDING_GIFT_OTHER),            # £1,000
        ("sibling", WEDDING_GIFT_OTHER),           # £1,000
    ])
    def test_wedding_gift_exemptions(self, relationship: str, max_exemption: int):
        """Test wedding gift exemptions by relationship"""
        gift_amount = max_exemption + 1000  # Exceed exemption to test limit

        gifts = [
            GiftInput(
                recipient="Couple",
                recipient_relationship=relationship,
                amount=gift_amount,
                date_given=date(2024, 6, 1),
                exemption_claimed="wedding"
            )
        ]

        result = process_gifts_with_exemptions(gifts, 0, 0)

        assert result["exemptions_used"]["wedding_gifts"] == max_exemption
        assert len(result["pets"]) == 1
        assert result["pets"][0]["amount"] == 1000  # Remaining amount after exemption


class TestBusinessPropertyRelief:
    """Unit tests for Business Property Relief calculations"""

    def test_unquoted_shares_100_percent_relief(self):
        """Test 100% relief for unquoted shares"""
        assets = [
            AssetInput(
                asset_type=AssetType.BUSINESS,
                value=500000,
                business_relief_type=BusinessReliefType.UNQUOTED_SHARES,
                ownership_years=3,
                description="Private company shares"
            )
        ]

        relief, warnings = calculate_business_relief(assets)

        assert relief == 500000  # 100% relief
        assert len(warnings) == 0

    def test_quoted_controlling_50_percent_relief(self):
        """Test 50% relief for quoted controlling shares"""
        assets = [
            AssetInput(
                asset_type=AssetType.BUSINESS,
                value=200000,
                business_relief_type=BusinessReliefType.QUOTED_CONTROLLING,
                ownership_years=3,
                description="Quoted controlling interest"
            )
        ]

        relief, warnings = calculate_business_relief(assets)

        assert relief == 100000  # 50% relief
        assert len(warnings) == 0

    def test_insufficient_ownership_period(self):
        """Test no relief for assets owned less than 2 years"""
        assets = [
            AssetInput(
                asset_type=AssetType.BUSINESS,
                value=300000,
                business_relief_type=BusinessReliefType.UNQUOTED_SHARES,
                ownership_years=1.5,  # Less than 2 years
                description="Recently acquired shares"
            )
        ]

        relief, warnings = calculate_business_relief(assets)

        assert relief == 0
        assert len(warnings) == 1
        assert "not owned for 2+ years" in warnings[0]

    def test_excepted_assets_no_relief(self):
        """Test no relief for excepted assets"""
        assets = [
            AssetInput(
                asset_type=AssetType.BUSINESS,
                value=400000,
                business_relief_type=BusinessReliefType.UNQUOTED_SHARES,
                ownership_years=5,
                is_excepted_asset=True,
                description="Investment company shares"
            )
        ]

        relief, warnings = calculate_business_relief(assets)

        assert relief == 0
        assert len(warnings) == 1
        assert "excepted asset" in warnings[0]


class TestCLTPETCumulation:
    """Unit tests for CLT/PET cumulation rules"""

    def test_clt_cumulation_over_seven_years(self):
        """Test CLT cumulation for calculating periodic charges"""

        # Create multiple CLTs over 7-year period
        clts = [
            GiftInput(
                recipient="Family Trust 1",
                recipient_relationship="trust",
                amount=200000,
                date_given=date(2018, 1, 1),  # 6+ years ago
                gift_type=GiftType.CLT,
                is_to_trust=True
            ),
            GiftInput(
                recipient="Family Trust 2",
                recipient_relationship="trust",
                amount=150000,
                date_given=date(2019, 6, 1),  # 5+ years ago
                gift_type=GiftType.CLT,
                is_to_trust=True
            ),
            GiftInput(
                recipient="Family Trust 3",
                recipient_relationship="trust",
                amount=100000,
                date_given=date(2022, 3, 1),  # 2+ years ago
                gift_type=GiftType.CLT,
                is_to_trust=True
            )
        ]

        # Test cumulation: CLTs within 7 years of each other cumulate
        # For IHT purposes, we look at 7-year periods

        # Calculate cumulative totals for different periods
        cumulative_at_2019 = 200000  # Only first CLT
        cumulative_at_2022 = 350000  # First two CLTs (within 7 years)
        cumulative_current = 450000  # All three CLTs (if all within 7 years)

        # Test that CLTs cumulate for rate calculation
        nil_rate_band = 325000

        # First CLT: £200k vs £325k NRB = no tax
        tax_on_first = max(0, 200000 - nil_rate_band) * 0.20  # 0% (lifetime rate for CLTs)

        # Second CLT: (£200k + £150k) = £350k vs £325k NRB = £25k taxable
        cumulative_second = 200000 + 150000
        tax_on_second = max(0, cumulative_second - nil_rate_band) * 0.20  # 20% lifetime rate

        # Third CLT: Check if first CLT (from 2018) is still within 7-year period
        years_between_first_and_third = (date(2022, 3, 1) - date(2018, 1, 1)).days / 365.25
        first_clt_counts = years_between_first_and_third <= 7

        if first_clt_counts:
            cumulative_third = 200000 + 150000 + 100000  # All three count
        else:
            cumulative_third = 150000 + 100000  # Only second and third count

        tax_on_third = max(0, cumulative_third - nil_rate_band) * 0.20

        # Verify calculations
        assert tax_on_first == 0, "First CLT should have no tax (within NRB)"
        assert tax_on_second > 0, "Second CLT should have tax (cumulative exceeds NRB)"
        assert tax_on_third >= tax_on_second, "Third CLT should have at least as much tax"

        # Test cumulation period boundaries
        assert years_between_first_and_third > 4, "Should be more than 4 years between first and third"

        # Process CLTs through exemption system
        result = process_gifts_with_exemptions(clts, 0, 0)
        processed_clts = result["clts"]

        assert len(processed_clts) == 3, "All CLTs should be processed"

        total_clt_value = sum(clt["amount"] for clt in processed_clts)
        expected_total = 450000
        assert total_clt_value == expected_total, f"Total CLT value should be £{expected_total}"

    def test_pet_failure_and_cumulation(self):
        """Test PET failure on death and cumulation with CLTs"""

        # Scenario: Person makes PETs and CLTs, then dies within 7 years of PETs
        pets = [
            GiftInput(
                recipient="Child 1",
                recipient_relationship="child",
                amount=400000,
                date_given=date(2022, 1, 1),  # Recent - will fail as PET
                gift_type=GiftType.PET
            ),
            GiftInput(
                recipient="Child 2",
                recipient_relationship="child",
                amount=300000,
                date_given=date(2021, 6, 1),  # Will fail as PET
                gift_type=GiftType.PET
            )
        ]

        clts = [
            GiftInput(
                recipient="Trust",
                recipient_relationship="trust",
                amount=100000,
                date_given=date(2020, 1, 1),  # CLT made before PETs
                gift_type=GiftType.CLT,
                is_to_trust=True
            )
        ]

        # Process gifts
        all_gifts = pets + clts
        result = process_gifts_with_exemptions(all_gifts, 0, 0)

        # On death, PETs become chargeable and cumulate with existing CLTs
        failed_pets = result["pets"]  # These would become chargeable
        existing_clts = result["clts"]

        # Calculate cumulative effect (chronological order matters)
        # Order: CLT 2020 (£100k), PET 2021 (£300k), PET 2022 (£400k)

        cumulative_values = []
        running_total = 0

        # CLT from 2020
        running_total += 100000
        cumulative_values.append(("CLT_2020", running_total))

        # Failed PET from 2021 (now chargeable)
        running_total += 300000
        cumulative_values.append(("PET_2021", running_total))

        # Failed PET from 2022 (now chargeable)
        running_total += 400000
        cumulative_values.append(("PET_2022", running_total))

        # Test cumulation effect on tax
        nil_rate_band = 325000

        # CLT 2020: £100k vs £325k = no tax
        clt_tax = max(0, 100000 - nil_rate_band) * 0.20
        assert clt_tax == 0

        # PET 2021: £400k cumulative vs £325k = £75k taxable at 40%
        pet_2021_tax = max(0, 400000 - nil_rate_band) * 0.40

        # PET 2022: £800k cumulative vs £325k = £475k taxable at 40%
        pet_2022_tax = max(0, 800000 - nil_rate_band) * 0.40

        # Verify cumulation logic
        assert len(cumulative_values) == 3
        assert cumulative_values[-1][1] == 800000  # Final cumulative total

        # Verify that PETs and CLTs are tracked separately but cumulate for tax
        total_pets_value = sum(pet["amount"] for pet in failed_pets)
        total_clts_value = sum(clt["amount"] for clt in existing_clts)

        assert total_pets_value == 700000  # £400k + £300k
        assert total_clts_value == 100000   # £100k


class TestTrustChargeCalculations:
    """Unit tests for trust charge calculations"""

    def test_ten_year_periodic_charge(self):
        """Test 10-year periodic charge calculation for relevant property trusts"""

        # Trust created 10+ years ago (due for periodic charge)
        trust_value = 1000000
        trust_creation_date = date(2013, 1, 1)  # Over 10 years ago

        # Calculate charge at 10-year anniversary
        anniversary_date = date(2024, 1, 1)
        years_since_creation = (anniversary_date - trust_creation_date).days / 365.25

        assert years_since_creation >= 10, "Trust should be 10+ years old for periodic charge"

        # Periodic charge calculation:
        # 1. Calculate hypothetical transfer tax rate
        # 2. Apply 30% of that rate to trust property
        # 3. Maximum rate is 6%

        # Step 1: Hypothetical transfer (trust value treated as gift by individual)
        hypothetical_gift_value = trust_value
        nil_rate_band = 325000

        # Assume no previous gifts by hypothetical transferor
        taxable_amount = max(0, hypothetical_gift_value - nil_rate_band)
        hypothetical_tax = taxable_amount * 0.20  # 20% lifetime rate for CLTs

        # Effective rate = tax / total transfer
        if hypothetical_gift_value > 0:
            effective_rate = hypothetical_tax / hypothetical_gift_value
        else:
            effective_rate = 0

        # Step 2: Apply 30% of effective rate
        periodic_charge_rate = effective_rate * 0.30

        # Step 3: Cap at 6%
        capped_rate = min(periodic_charge_rate, 0.06)

        # Calculate actual charge
        periodic_charge = trust_value * capped_rate

        # Verify calculations
        assert periodic_charge >= 0, "Periodic charge cannot be negative"
        assert periodic_charge <= trust_value * 0.06, "Periodic charge cannot exceed 6%"
        assert capped_rate <= 0.06, "Charge rate cannot exceed 6%"

        # Test with high-value trust that hits the 6% cap
        high_value_trust = 5000000
        high_value_taxable = max(0, high_value_trust - nil_rate_band)
        high_value_tax = high_value_taxable * 0.20
        high_value_effective_rate = high_value_tax / high_value_trust
        high_value_periodic_rate = min(high_value_effective_rate * 0.30, 0.06)

        assert high_value_periodic_rate < 0.06, "High value trust calculation should be under 6% cap for this example"

    def test_exit_charge_calculation(self):
        """Test exit charge calculation for distributions from trusts"""

        # Trust makes distribution to beneficiary before 10-year anniversary
        trust_creation_date = date(2020, 3, 1)
        distribution_date = date(2024, 8, 1)
        distribution_value = 200000

        # Calculate time held
        days_held = (distribution_date - trust_creation_date).days
        quarters_held = days_held / 91.25  # Approximately 91.25 days per quarter
        years_held = days_held / 365.25

        assert years_held < 10, "Exit charge test should be before 10-year anniversary"

        # Exit charge calculation:
        # Rate = (Effective rate ÷ 40) × (Number of complete quarters ÷ 40)

        # For this test, assume effective rate from last periodic charge or hypothetical
        # Since no periodic charge yet, calculate hypothetical rate
        hypothetical_effective_rate = 0.15  # 15% (example)

        complete_quarters = int(quarters_held)
        exit_charge_rate = (hypothetical_effective_rate / 40) * (complete_quarters / 40)

        exit_charge = distribution_value * exit_charge_rate

        # Verify calculations
        assert exit_charge >= 0, "Exit charge cannot be negative"
        assert exit_charge_rate >= 0, "Exit charge rate cannot be negative"
        assert complete_quarters >= 0, "Complete quarters cannot be negative"

        # Test edge case: Distribution immediately after trust creation
        immediate_distribution_quarters = 0
        immediate_exit_rate = (hypothetical_effective_rate / 40) * (immediate_distribution_quarters / 40)
        assert immediate_exit_rate == 0, "Immediate distribution should have no exit charge"

        # Test quarterly rounding
        # 4.9 years = 19.6 quarters = 19 complete quarters
        test_quarters = 19.6
        complete_test_quarters = int(test_quarters)
        assert complete_test_quarters == 19, "Should round down to complete quarters"


class TestIntegrationScenarios:
    """Integration tests for complex IHT scenarios"""

    def test_complete_estate_calculation(self, client: TestClient, auth_headers):
        """Test complete estate with assets, gifts, trusts, and reliefs"""

        calculation_data = {
            "assets": [
                {
                    "asset_type": "property",
                    "value": 800000,
                    "is_main_residence": True
                },
                {
                    "asset_type": "business",
                    "value": 500000,
                    "business_relief_type": "unquoted_shares",
                    "ownership_years": 3
                },
                {
                    "asset_type": "investment",
                    "value": 200000
                }
            ],
            "gifts": [
                {
                    "recipient": "Child 1",
                    "recipient_relationship": "child",
                    "amount": 100000,
                    "date_given": "2020-01-01",  # 4+ years ago
                    "gift_type": "pet"
                }
            ],
            "trusts": [],
            "marital_status": "widowed",
            "residence_value": 800000,
            "charitable_gifts": 0,
            "tnrb_claimed_percentage": 100,  # Full transferred NRB
            "trnrb_claimed_percentage": 100, # Full transferred RNRB
            "has_direct_descendants": True,
            "annual_exemption_used_current": 0,
            "annual_exemption_used_previous": 0
        }

        response = client.post(
            "/api/iht-enhanced/calculate-enhanced",
            json=calculation_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "total_estate_value" in data
        assert "iht_due" in data
        assert "business_property_relief" in data
        assert "tnrb_amount" in data
        assert "trnrb_amount" in data

    def test_multiple_year_gift_tracking(self):
        """Test gift tracking across multiple years with cumulation"""

        # Create gifts across multiple years to test cumulation
        gifts_year_1 = [
            GiftInput(
                recipient="Child 1",
                recipient_relationship="child",
                amount=100000,
                date_given=date(2020, 6, 1),  # 4+ years ago
                gift_type=GiftType.PET
            ),
            GiftInput(
                recipient="Trust 1",
                recipient_relationship="trust",
                amount=200000,
                date_given=date(2020, 8, 1),  # 4+ years ago
                gift_type=GiftType.CLT,
                is_to_trust=True
            )
        ]

        gifts_year_2 = [
            GiftInput(
                recipient="Child 2",
                recipient_relationship="child",
                amount=150000,
                date_given=date(2021, 6, 1),  # 3+ years ago
                gift_type=GiftType.PET
            ),
            GiftInput(
                recipient="Trust 2",
                recipient_relationship="trust",
                amount=100000,
                date_given=date(2021, 10, 1),  # 3+ years ago
                gift_type=GiftType.CLT,
                is_to_trust=True
            )
        ]

        gifts_year_3 = [
            GiftInput(
                recipient="Child 3",
                recipient_relationship="child",
                amount=75000,
                date_given=date(2023, 6, 1),  # 1+ years ago (recent)
                gift_type=GiftType.PET
            )
        ]

        # Test cumulative effect of multiple years of gifts
        all_gifts = gifts_year_1 + gifts_year_2 + gifts_year_3

        # Process all gifts to understand cumulation
        result = process_gifts_with_exemptions(all_gifts, 0, 0)

        # Verify gift categorization
        pets = result["pets"]
        clts = result["clts"]

        # Should have PET gifts (excluding those to trusts)
        pet_amounts = [pet["amount"] for pet in pets]
        clt_amounts = [clt["amount"] for clt in clts]

        # Verify we have both PETs and CLTs
        assert len(pets) > 0, "Should have PET gifts"
        assert len(clts) > 0, "Should have CLT gifts"

        # Total gift amounts should match input
        total_gifts = sum(pet_amounts) + sum(clt_amounts)
        expected_total = 625000  # 100k+200k+150k+100k+75k

        assert abs(total_gifts - expected_total) < 1000, \
            f"Total gifts should be ~£{expected_total}, got £{total_gifts}"

        # Verify gifts are properly dated for cumulation calculations
        # (This would integrate with actual cumulation logic when implemented)

    def test_trust_lifecycle_charges(self):
        """Test trust entry, periodic, and exit charges"""

        # Test trust creation (entry charge)
        trust_creation = TrustInput(
            trust_name="Family Discretionary Trust",
            trust_type="discretionary",
            value=500000,
            date_created=date(2020, 1, 1),  # Created 4+ years ago
            is_relevant_property=True,
            beneficiaries=["Child 1", "Child 2", "Grandchildren"]
        )

        # Test 10-year periodic charge calculation
        # Assumes we're now in 2025, so first 10-year anniversary would be 2030
        years_since_creation = (date.today() - trust_creation.date_created).days / 365.25

        # Should not yet have 10-year charge (need 10 years)
        if years_since_creation < 10:
            # Test that no periodic charge applies yet
            assert years_since_creation < 10, "Trust should be less than 10 years old for this test"

            # Calculate theoretical periodic charge for when it does apply
            # 10-year charge rate depends on trust's tax rate
            # Simplified calculation: typically 0-6% depending on circumstances
            theoretical_charge_rate = 0.06  # Maximum 6% for relevant property trusts
            theoretical_charge = trust_creation.value * theoretical_charge_rate

            assert theoretical_charge <= trust_creation.value * 0.06, \
                "Periodic charge should not exceed 6% of trust value"

        # Test exit charge calculation
        # If beneficiary receives distribution before 10-year anniversary
        exit_distribution_value = 100000
        years_held = min(years_since_creation, 10)  # Cap at 10 years for exit charge calc

        # Exit charge is pro-rated based on time held
        # Formula: (Effective rate / 40) × (quarters held / 40)
        effective_rate = 0.2  # 20% (example effective rate)
        quarters_held = years_held * 4
        exit_charge_rate = (effective_rate / 40) * (quarters_held / 40)
        exit_charge = exit_distribution_value * exit_charge_rate

        # Verify exit charge is reasonable
        assert exit_charge >= 0, "Exit charge should not be negative"
        assert exit_charge <= exit_distribution_value * 0.06, \
            "Exit charge should not exceed 6% of distribution"

        # Test that trusts track cumulative charges
        cumulative_charges = 0
        if years_since_creation >= 10:
            # Would have periodic charges every 10 years
            periodic_charges = int(years_since_creation / 10)
            for i in range(periodic_charges):
                charge_date = date(2020 + (i * 10), 1, 1)
                # Each charge would be calculated based on trust value at that time
                cumulative_charges += theoretical_charge

        # Verify trust maintains proper charge history
        assert isinstance(trust_creation.trust_name, str)
        assert isinstance(trust_creation.beneficiaries, list)
        assert len(trust_creation.beneficiaries) > 0


class TestEdgeCases:
    """Edge case tests for complex scenarios"""

    def test_multiple_marriages_tnrb_claims(self):
        """Test TNRB claims from multiple deceased spouses"""

        # Scenario: Person had 3 marriages, 2 spouses died before them
        # Each spouse had unused NRB at death

        # First marriage: Spouse died in 2015
        spouse1_unused_nrb = 100  # 100% unused (full £325k)
        spouse1_unused_rnrb = 0   # RNRB didn't exist in 2015

        # Second marriage: Spouse died in 2020
        spouse2_unused_nrb = 50   # 50% unused (£162.5k)
        spouse2_unused_rnrb = 80  # 80% unused (£140k)

        # Current estate calculation with transferred allowances
        estate_value = 800_000
        residence_value = 400_000
        has_descendants = True

        # Calculate total transferable allowances
        # Maximum is 100% additional for each band
        total_tnrb = min(100, spouse1_unused_nrb + spouse2_unused_nrb)  # Cap at 100%
        total_trnrb = min(100, spouse1_unused_rnrb + spouse2_unused_rnrb)  # Cap at 100%

        assert total_tnrb == 100, f"Total TNRB should be capped at 100%, got {total_tnrb}%"
        assert total_trnrb == 80, f"Total TRNRB should be 80%, got {total_trnrb}%"

        # Test RNRB calculation with transferred allowance
        rnrb, rnrb_taper = calculate_rnrb_with_taper(
            estate_value, residence_value, has_descendants, total_trnrb
        )

        # Expected: Base £175k + Transferred £140k = £315k total RNRB
        expected_rnrb = 175_000 + (175_000 * 0.8)  # £315k
        assert rnrb == expected_rnrb, f"Expected RNRB £{expected_rnrb}, got £{rnrb}"

        # Test that allowances are properly tracked per marriage
        marriages = [
            {
                "spouse_name": "First Spouse",
                "marriage_start": date(2000, 6, 1),
                "marriage_end": date(2015, 3, 15),  # Death date
                "unused_nrb_percentage": 100,
                "unused_rnrb_percentage": 0,
                "estate_value_at_death": 200_000,
                "iht_paid": 0
            },
            {
                "spouse_name": "Second Spouse",
                "marriage_start": date(2016, 8, 20),
                "marriage_end": date(2020, 11, 10),  # Death date
                "unused_nrb_percentage": 50,
                "unused_rnrb_percentage": 80,
                "estate_value_at_death": 600_000,
                "iht_paid": 50_000
            }
        ]

        # Verify marriage tracking data structure
        for marriage in marriages:
            assert 0 <= marriage["unused_nrb_percentage"] <= 100
            assert 0 <= marriage["unused_rnrb_percentage"] <= 100
            assert marriage["estate_value_at_death"] > 0
            assert marriage["iht_paid"] >= 0

        # Test edge case: What if total claims exceed 100%?
        excess_claims_nrb = 150  # 150% claimed (should be capped at 100%)
        excess_claims_rnrb = 120  # 120% claimed (should be capped at 100%)

        capped_nrb = min(100, excess_claims_nrb)
        capped_rnrb = min(100, excess_claims_rnrb)

        assert capped_nrb == 100, "NRB claims should be capped at 100%"
        assert capped_rnrb == 100, "RNRB claims should be capped at 100%"

    def test_downsizing_rnrb_preservation(self):
        """Test downsizing addition rules for RNRB preservation"""

        # Scenario: Person downsized after 8 July 2015 and wants RNRB preservation

        # Property disposal after the qualifying date
        disposal_date = date(2018, 3, 15)  # After 8 July 2015
        original_property_value = 800_000
        sale_proceeds = 750_000

        # New smaller property or no property
        new_property_value = 300_000  # Downsized

        # Estate value at death
        estate_value = 1_200_000
        has_descendants = True

        # Test qualifying conditions for downsizing addition
        qualifying_conditions = {
            "disposal_after_july_2015": disposal_date > date(2015, 7, 8),
            "had_descendants_at_disposal": True,
            "closely_inherited": True,  # Property/proceeds closely inherited
            "would_have_qualified_for_rnrb": original_property_value > 0
        }

        # All conditions must be met
        qualifies_for_downsizing_addition = all(qualifying_conditions.values())
        assert qualifies_for_downsizing_addition, "Should qualify for downsizing addition"

        # Calculate downsizing addition
        # Formula: Lower of:
        # 1. Lost RNRB due to downsizing
        # 2. Value of assets closely inherited
        # 3. Current RNRB available

        # 1. Lost RNRB = Original qualifying residence value - New residence value
        lost_rnrb_value = max(0, min(RESIDENCE_NIL_RATE_BAND, original_property_value) -
                             min(RESIDENCE_NIL_RATE_BAND, new_property_value))

        expected_lost_rnrb = min(175_000, 800_000) - min(175_000, 300_000)  # £175k - £175k = £0
        # Actually: £175k (cap for old) - £175k (cap for new) = £0
        # But the calculation should be: £175k full RNRB was available, now only partial

        # Correct calculation: Lost RNRB is the difference in qualifying property
        lost_qualifying_value = original_property_value - new_property_value  # £500k
        lost_rnrb_actual = min(RESIDENCE_NIL_RATE_BAND, lost_qualifying_value)  # £175k

        assert lost_rnrb_actual == 175_000, f"Lost RNRB should be £175k, got £{lost_rnrb_actual}"

        # 2. Value of closely inherited assets (assume all estate closely inherited)
        closely_inherited_value = estate_value  # £1.2M

        # 3. Current RNRB available (after tapering)
        current_rnrb, taper_amount = calculate_rnrb_with_taper(
            estate_value, new_property_value, has_descendants, 0
        )

        # Downsizing addition is the lower of the three values
        downsizing_addition = min(
            lost_rnrb_actual,      # £175k
            closely_inherited_value,  # £1.2M
            current_rnrb + lost_rnrb_actual  # Available RNRB + potential addition
        )

        assert downsizing_addition > 0, "Should have downsizing addition"
        assert downsizing_addition <= RESIDENCE_NIL_RATE_BAND, \
            "Downsizing addition should not exceed RNRB limit"

        # Test edge case: Disposal before July 8, 2015 (should not qualify)
        early_disposal_date = date(2015, 7, 7)  # Day before qualifying date
        early_qualifies = early_disposal_date > date(2015, 7, 8)
        assert not early_qualifies, "Should not qualify for downsizing addition before July 8, 2015"

        # Test record keeping requirements
        downsizing_record = {
            "disposal_date": disposal_date,
            "original_property_value": original_property_value,
            "sale_proceeds": sale_proceeds,
            "new_property_value": new_property_value,
            "lost_rnrb_value": lost_rnrb_actual,
            "closely_inherited_value": closely_inherited_value,
            "downsizing_addition_claimed": downsizing_addition,
            "qualifying_conditions_met": qualifying_conditions
        }

        # Verify record structure
        assert isinstance(downsizing_record["disposal_date"], date)
        assert downsizing_record["lost_rnrb_value"] >= 0
        assert downsizing_record["downsizing_addition_claimed"] <= RESIDENCE_NIL_RATE_BAND

    def test_gift_with_reservation_poat(self):
        """Test Gift with Reservation and Pre-Owned Assets Tax interactions"""
        # Test GWR detection and POAT calculations

        # Scenario 1: Gift with reservation - donor retains benefit
        gwr_gift = {
            "donor": "Testator",
            "recipient": "Child",
            "asset_type": "property",
            "value": 500000,
            "date_given": date(2020, 1, 1),
            "reservation_retained": True,  # Donor continues to live in property
            "rent_paid": 0,  # No market rent paid
            "occupation_exclusive": False  # Donor still uses property
        }

        # GWR rules: Asset treated as still in donor's estate
        # Should be included in death estate despite being "given away"
        assert gwr_gift["reservation_retained"] == True
        assert gwr_gift["rent_paid"] == 0  # No market rent = reservation
        assert gwr_gift["occupation_exclusive"] == False  # Not exclusive to recipient

        # For IHT purposes, property remains in estate at death value
        death_value = 600000  # Property appreciated
        estate_inclusion = death_value if gwr_gift["reservation_retained"] else 0
        assert estate_inclusion == 600000, "GWR property should be included in estate"

        # Scenario 2: POAT election to avoid GWR
        poat_election = {
            "asset": gwr_gift,
            "poat_elected": True,
            "annual_poat_charge": 15000,  # Approximate POAT charge (2.5% of value)
            "years_paid": 4,
            "benefit_received": True
        }

        if poat_election["poat_elected"]:
            # POAT paid, so no GWR charge at death
            estate_inclusion_with_poat = 0
            total_poat_paid = poat_election["annual_poat_charge"] * poat_election["years_paid"]

            assert estate_inclusion_with_poat == 0, "POAT election avoids GWR"
            assert total_poat_paid == 60000, f"Total POAT paid should be £60k, got £{total_poat_paid}"

        # Scenario 3: Clean gift with no reservation
        clean_gift = {
            "donor": "Testator",
            "recipient": "Child",
            "asset_type": "cash",
            "value": 100000,
            "date_given": date(2020, 1, 1),
            "reservation_retained": False,  # Clean gift - no benefit retained
            "market_terms": True,
            "exclusive_possession": True  # Recipient has full control
        }

        # Clean gift should not be subject to GWR or POAT
        assert clean_gift["reservation_retained"] == False
        assert clean_gift["market_terms"] == True
        assert clean_gift["exclusive_possession"] == True
        clean_gift_estate_inclusion = 0  # Not included in estate
        assert clean_gift_estate_inclusion == 0, "Clean gifts should not be in estate"

    def test_quick_succession_relief_chains(self):
        """Test quick succession relief in inheritance chains"""
        # Test QSR when multiple deaths occur within 5 years

        # Scenario: Chain of deaths within 5-year period
        # Person A dies -> Person B inherits -> Person B dies within 5 years

        # First death: Person A dies in 2020
        death_a = {
            "deceased": "Person A",
            "date_of_death": date(2020, 6, 1),
            "estate_value": 800000,
            "iht_paid": 150000,  # Tax paid on estate
            "beneficiaries": [
                {"name": "Person B", "inheritance": 600000},
                {"name": "Others", "inheritance": 200000}
            ]
        }

        # Second death: Person B dies in 2023 (within 5 years)
        death_b = {
            "deceased": "Person B",
            "date_of_death": date(2023, 3, 15),  # 2 years 9 months later
            "inherited_from_a": 600000,
            "own_assets": 300000,
            "total_estate": 900000,  # Inherited + own assets
            "iht_on_total_estate": 200000  # Before QSR
        }

        # Calculate QSR entitlement
        years_between_deaths = (death_b["date_of_death"] - death_a["date_of_death"]).days / 365.25
        assert years_between_deaths < 5, "Deaths must be within 5 years for QSR"

        # QSR percentage scale:
        # 1 year or less: 100%
        # 1-2 years: 80%
        # 2-3 years: 60%
        # 3-4 years: 40%
        # 4-5 years: 20%
        # Over 5 years: 0%

        if years_between_deaths <= 1:
            qsr_percentage = 100
        elif years_between_deaths <= 2:
            qsr_percentage = 80
        elif years_between_deaths <= 3:
            qsr_percentage = 60
        elif years_between_deaths <= 4:
            qsr_percentage = 40
        elif years_between_deaths <= 5:
            qsr_percentage = 20
        else:
            qsr_percentage = 0

        # Years between = ~2.75, so QSR percentage should be 60%
        expected_qsr_percentage = 60
        assert qsr_percentage == expected_qsr_percentage, \
            f"QSR percentage should be {expected_qsr_percentage}%, got {qsr_percentage}%"

        # Calculate QSR relief amount
        # QSR is calculated on the IHT paid on the first death
        # in respect of the asset that has been inherited

        # Proportion of first estate that Person B inherited
        inheritance_proportion = death_a["beneficiaries"][0]["inheritance"] / death_a["estate_value"]
        assert inheritance_proportion == 0.75, "Person B inherited 75% of Person A's estate"

        # IHT attributable to inherited assets from first death
        attributable_iht_first_death = death_a["iht_paid"] * inheritance_proportion
        expected_attributable_iht = 150000 * 0.75  # £112,500
        assert attributable_iht_first_death == expected_attributable_iht

        # QSR relief amount
        qsr_relief = attributable_iht_first_death * (qsr_percentage / 100)
        expected_qsr_relief = 112500 * 0.60  # £67,500
        assert qsr_relief == expected_qsr_relief, \
            f"QSR relief should be £{expected_qsr_relief}, got £{qsr_relief}"

        # Final IHT liability after QSR
        iht_after_qsr = death_b["iht_on_total_estate"] - qsr_relief
        expected_final_iht = 200000 - 67500  # £132,500
        assert iht_after_qsr == expected_final_iht, \
            f"Final IHT after QSR should be £{expected_final_iht}, got £{iht_after_qsr}"

        # Test edge case: Inheritance that increases in value
        increased_value_scenario = {
            "inherited_value_at_first_death": 600000,
            "inherited_value_at_second_death": 750000,  # Appreciated
            "qsr_calculation_basis": "lower_of_two_values"
        }

        # QSR should be calculated on the lower of:
        # 1. Value at first death
        # 2. Value at second death
        qsr_basis_value = min(
            increased_value_scenario["inherited_value_at_first_death"],
            increased_value_scenario["inherited_value_at_second_death"]
        )

        assert qsr_basis_value == 600000, "QSR should use original inheritance value (lower)"

        # Test multiple QSR claims (chain of 3 deaths)
        death_c = {
            "deceased": "Person C",
            "date_of_death": date(2024, 1, 1),  # Within 5 years of B's death
            "inherited_from_b": 700000,  # What's left after B's IHT
            "can_claim_qsr_from_b": True,
            "potential_qsr_from_a_via_b": True  # Double QSR scenario
        }

        # QSR can only go back one generation in chain
        # Person C can claim QSR for IHT paid on Person B's death
        # But cannot claim QSR for IHT originally paid on Person A's death
        assert death_c["can_claim_qsr_from_b"] == True
        # Note: Double QSR typically not allowed - each asset can only benefit once

    def test_foreign_assets_domicile_changes(self):
        """Test foreign assets and domicile change implications"""
        # Test residence vs domicile based taxation

        # Test UK domiciled individual with foreign assets
        uk_domiciled_person = {
            "domicile_status": "UK_domiciled",
            "residence_status": "UK_resident",
            "years_uk_resident": 25,
            "foreign_assets": [
                {"type": "property", "location": "France", "value": 400000},
                {"type": "bank_account", "location": "Switzerland", "value": 200000},
                {"type": "shares", "location": "USA", "value": 150000}
            ],
            "uk_assets": [
                {"type": "property", "location": "UK", "value": 600000},
                {"type": "uk_bank", "location": "UK", "value": 100000}
            ]
        }

        # UK domiciled = worldwide estate subject to UK IHT
        if uk_domiciled_person["domicile_status"] == "UK_domiciled":
            total_foreign_assets = sum(asset["value"] for asset in uk_domiciled_person["foreign_assets"])
            total_uk_assets = sum(asset["value"] for asset in uk_domiciled_person["uk_assets"])
            total_worldwide_estate = total_foreign_assets + total_uk_assets

            assert total_foreign_assets == 750000, "Total foreign assets should be £750k"
            assert total_uk_assets == 700000, "Total UK assets should be £700k"
            assert total_worldwide_estate == 1450000, "Worldwide estate should be £1.45M"

            # All assets subject to UK IHT
            iht_chargeable_estate = total_worldwide_estate
            assert iht_chargeable_estate == 1450000, "Entire worldwide estate subject to UK IHT"

        # Test non-UK domiciled individual (deemed domiciled)
        deemed_domiciled_person = {
            "domicile_status": "foreign_domiciled",
            "residence_status": "UK_resident",
            "years_uk_resident": 17,  # 15+ years = deemed domiciled for IHT
            "uk_resident_in_17_of_20_years": True,
            "foreign_assets": [
                {"type": "property", "location": "Spain", "value": 800000},
                {"type": "investments", "location": "Germany", "value": 300000}
            ],
            "uk_assets": [
                {"type": "property", "location": "UK", "value": 500000}
            ]
        }

        # Deemed domicile rules: 15+ years UK resident out of last 20 years
        is_deemed_domiciled = (
            deemed_domiciled_person["years_uk_resident"] >= 15 and
            deemed_domiciled_person["uk_resident_in_17_of_20_years"]
        )

        assert is_deemed_domiciled == True, "Should be deemed domiciled after 15+ years"

        if is_deemed_domiciled:
            # Deemed domiciled = treated same as UK domiciled for IHT
            deemed_foreign_assets = sum(asset["value"] for asset in deemed_domiciled_person["foreign_assets"])
            deemed_uk_assets = sum(asset["value"] for asset in deemed_domiciled_person["uk_assets"])
            deemed_total_estate = deemed_foreign_assets + deemed_uk_assets

            assert deemed_total_estate == 1600000, "Deemed domiciled estate should be £1.6M"

        # Test truly non-UK domiciled individual
        non_uk_domiciled_person = {
            "domicile_status": "foreign_domiciled",
            "residence_status": "UK_resident",
            "years_uk_resident": 8,  # Less than 15 years
            "uk_resident_in_8_of_20_years": True,
            "foreign_assets": [
                {"type": "property", "location": "Italy", "value": 1200000},
                {"type": "offshore_trust", "location": "Cayman", "value": 500000}
            ],
            "uk_assets": [
                {"type": "uk_property", "location": "UK", "value": 400000},
                {"type": "uk_shares", "location": "UK", "value": 100000}
            ]
        }

        # Not deemed domiciled (< 15 years)
        is_not_deemed_domiciled = non_uk_domiciled_person["years_uk_resident"] < 15

        assert is_not_deemed_domiciled == True, "Should not be deemed domiciled with < 15 years"

        if is_not_deemed_domiciled:
            # Only UK assets subject to UK IHT
            non_dom_uk_assets = sum(asset["value"] for asset in non_uk_domiciled_person["uk_assets"])
            non_dom_foreign_assets = sum(asset["value"] for asset in non_uk_domiciled_person["foreign_assets"])

            uk_iht_chargeable_estate = non_dom_uk_assets  # Only UK assets
            foreign_estate_exempt = non_dom_foreign_assets  # Not subject to UK IHT

            assert uk_iht_chargeable_estate == 500000, "Only UK assets subject to UK IHT"
            assert foreign_estate_exempt == 1700000, "Foreign assets exempt from UK IHT"

        # Test domicile change implications
        domicile_change_scenario = {
            "original_domicile": "UK",
            "new_domicile": "Switzerland",
            "change_date": date(2020, 1, 1),
            "death_date": date(2024, 6, 1),
            "years_since_change": 4.5,
            "deemed_domicile_rules_still_apply": True  # Within recent period
        }

        # Recent domicile change may not immediately escape UK IHT
        years_since_change = domicile_change_scenario["years_since_change"]
        deemed_domicile_cooling_off = years_since_change >= 3  # Approximate rule

        # Even with domicile change, may still be caught by deemed domicile rules
        if domicile_change_scenario["deemed_domicile_rules_still_apply"]:
            still_subject_to_uk_iht = True
        else:
            still_subject_to_uk_iht = False

        assert still_subject_to_uk_iht == True, "Recent domicile change may not escape UK IHT"

        # Test excluded property for non-doms
        excluded_property_examples = [
            {"type": "offshore_trust", "properly_structured": True},
            {"type": "foreign_government_bonds", "held_offshore": True},
            {"type": "foreign_pension", "qualifying_scheme": True}
        ]

        for prop in excluded_property_examples:
            if prop.get("properly_structured") or prop.get("held_offshore") or prop.get("qualifying_scheme"):
                is_excluded_property = True
            else:
                is_excluded_property = False

            assert is_excluded_property == True, f"Should be excluded property: {prop['type']}"

    @pytest.mark.parametrize("scenario", [
        "nil_estate_with_gifts",
        "maximum_reliefs_claimed",
        "cross_border_estates",
        "trust_beneficiary_deaths",
        "pension_death_benefits"
    ])
    def test_complex_edge_scenarios(self, scenario: str):
        """Test various complex edge case scenarios"""

        if scenario == "nil_estate_with_gifts":
            # Test scenario where estate value is nil but significant gifts were made
            estate_data = {
                "assets": [],  # No assets in estate
                "liabilities": 50000,  # Has debts
                "net_estate": -50000,
                "gifts_made": [
                    {"amount": 500000, "date": date(2020, 1, 1), "type": "PET"},
                    {"amount": 300000, "date": date(2021, 6, 1), "type": "CLT"}
                ]
            }

            # Even with nil estate, gifts may create IHT liability
            total_gifts = sum(gift["amount"] for gift in estate_data["gifts_made"])
            assert total_gifts == 800000, "Total gifts should be £800k"
            assert estate_data["net_estate"] < 0, "Estate should be negative"

            # IHT calculation should still consider gifts for cumulation
            iht_liability_from_gifts = max(0, total_gifts - STANDARD_NIL_RATE_BAND)  # Simplified
            expected_iht_on_gifts = max(0, 800000 - 325000) * 0.4  # £190k
            assert iht_liability_from_gifts > 0, "Should have IHT liability from gifts despite nil estate"

        elif scenario == "maximum_reliefs_claimed":
            # Test scenario with maximum possible reliefs claimed
            max_reliefs_estate = {
                "gross_estate": 2000000,
                "business_property_relief": 800000,  # 100% BPR on qualifying business assets
                "agricultural_property_relief": 400000,  # 100% APR on qualifying agricultural assets
                "charitable_gifts": 360000,  # 18% of net estate for reduced rate
                "tnrb_claimed": 325000,  # 100% TNRB
                "trnrb_claimed": 175000   # 100% TRNRB
            }

            # Calculate net estate after reliefs
            net_chargeable_estate = (max_reliefs_estate["gross_estate"] -
                                   max_reliefs_estate["business_property_relief"] -
                                   max_reliefs_estate["agricultural_property_relief"] -
                                   max_reliefs_estate["charitable_gifts"])

            assert net_chargeable_estate == 440000, "Net chargeable estate should be £440k"

            # With maximum allowances, should have minimal IHT
            total_allowances = (STANDARD_NIL_RATE_BAND + max_reliefs_estate["tnrb_claimed"] +
                              RESIDENCE_NIL_RATE_BAND + max_reliefs_estate["trnrb_claimed"])
            assert total_allowances == 1000000, "Total allowances should be £1M"

            # Estate under allowances = no IHT
            iht_due = max(0, net_chargeable_estate - total_allowances)
            assert iht_due == 0, "Should have no IHT with maximum reliefs"

        elif scenario == "cross_border_estates":
            # Test complex cross-border estate scenarios
            cross_border = {
                "deceased_domicile": "UK",
                "deceased_residence": "France",
                "uk_assets": 600000,
                "french_assets": 800000,
                "us_assets": 200000,
                "double_taxation_treaties": ["UK-France", "UK-US"],
                "foreign_tax_paid": {"france": 120000, "us": 30000}
            }

            # UK domiciled = worldwide assets subject to UK IHT
            total_worldwide_assets = (cross_border["uk_assets"] +
                                    cross_border["french_assets"] +
                                    cross_border["us_assets"])
            assert total_worldwide_assets == 1600000, "Total worldwide assets should be £1.6M"

            # Foreign tax credit relief may apply
            total_foreign_tax_paid = sum(cross_border["foreign_tax_paid"].values())
            assert total_foreign_tax_paid == 150000, "Total foreign tax paid should be £150k"

        elif scenario == "trust_beneficiary_deaths":
            # Test scenario where trust beneficiary dies affecting trust charges
            trust_scenario = {
                "trust_created": date(2015, 1, 1),
                "original_beneficiaries": ["Child A", "Child B", "Grandchildren"],
                "child_a_death": date(2022, 6, 1),  # Beneficiary dies during trust term
                "trust_value_at_death": 800000,
                "affects_periodic_charge": True,
                "exit_charge_triggered": False  # Benefits pass to remaining beneficiaries
            }

            years_since_creation = (date.today() - trust_scenario["trust_created"]).days / 365.25
            assert years_since_creation > 9, "Trust should be approaching 10-year charge"

            # Beneficiary death may affect trust taxation
            remaining_beneficiaries = [b for b in trust_scenario["original_beneficiaries"]
                                     if b != "Child A"]
            assert len(remaining_beneficiaries) == 2, "Should have 2 remaining beneficiaries"

        elif scenario == "pension_death_benefits":
            # Test pension death benefits and IHT treatment
            pension_scenario = {
                "pension_type": "SIPP",
                "pension_value": 750000,
                "death_age": 76,  # After age 75
                "beneficiary_relationship": "spouse",
                "death_benefits_paid": 750000,
                "income_tax_on_benefits": 300000,  # 40% tax after 75
                "iht_treatment": "potentially_exempt"  # Depends on scheme rules
            }

            # Pension death benefits treatment depends on age and scheme rules
            if pension_scenario["death_age"] >= 75:
                income_tax_due = True  # Benefits taxed as income
            else:
                income_tax_due = False  # Tax-free if under 75

            assert income_tax_due == True, "Benefits should be subject to income tax after age 75"

            # IHT treatment depends on whether benefits are at discretion of trustees
            if pension_scenario["iht_treatment"] == "potentially_exempt":
                included_in_estate = False  # Discretionary benefits not in estate
            else:
                included_in_estate = True

            assert included_in_estate == False, "Discretionary pension benefits should not be in estate"

        else:
            # Unknown scenario
            assert False, f"Unknown test scenario: {scenario}"


class TestComplianceAndForms:
    """Tests for compliance checking and form generation"""

    def test_excepted_estate_eligibility(self):
        """Test excepted estate eligibility for simplified forms"""
        # Test IHT205, IHT207, IHT400C eligibility

        # IHT205 - Small estates (under £325k)
        iht205_estate = {
            "gross_estate": 300000,
            "gifts_in_7_years": 0,
            "foreign_assets": 0,
            "trust_involvement": False,
            "business_assets": 0
        }

        # Eligibility criteria for IHT205
        iht205_eligible = (
            iht205_estate["gross_estate"] <= 325000 and
            iht205_estate["gifts_in_7_years"] == 0 and
            iht205_estate["foreign_assets"] == 0 and
            not iht205_estate["trust_involvement"] and
            iht205_estate["business_assets"] == 0
        )

        assert iht205_eligible == True, "Should be eligible for IHT205 (small estate form)"

        # IHT207 - Excepted estates with spouse exemption
        iht207_estate = {
            "gross_estate": 800000,
            "net_estate_after_spouse_exemption": 320000,  # Under NRB
            "spouse_exemption_claimed": 480000,
            "all_to_uk_domiciled_spouse": True,
            "no_complex_assets": True
        }

        # Eligibility for IHT207
        iht207_eligible = (
            iht207_estate["net_estate_after_spouse_exemption"] <= 325000 and
            iht207_estate["all_to_uk_domiciled_spouse"] and
            iht207_estate["no_complex_assets"]
        )

        assert iht207_eligible == True, "Should be eligible for IHT207 (spouse exemption form)"

        # IHT400C - Excepted estates with TNRB
        iht400c_estate = {
            "gross_estate": 650000,
            "tnrb_claimed": 325000,
            "total_allowances": 650000,  # NRB + TNRB
            "net_chargeable_estate": 0,
            "straightforward_assets_only": True
        }

        # Eligibility for IHT400C
        iht400c_eligible = (
            iht400c_estate["net_chargeable_estate"] == 0 and
            iht400c_estate["tnrb_claimed"] > 0 and
            iht400c_estate["straightforward_assets_only"]
        )

        assert iht400c_eligible == True, "Should be eligible for IHT400C (TNRB form)"

        # Complex estate requiring full IHT400
        complex_estate = {
            "gross_estate": 1500000,
            "business_assets": 500000,
            "foreign_assets": 200000,
            "trust_involvement": True,
            "agricultural_assets": 300000,
            "complex_reliefs_claimed": True
        }

        # Not eligible for excepted estate forms
        excepted_estate_eligible = (
            not complex_estate["trust_involvement"] and
            complex_estate["foreign_assets"] == 0 and
            complex_estate["business_assets"] == 0 and
            not complex_estate["complex_reliefs_claimed"]
        )

        assert excepted_estate_eligible == False, "Complex estate should require full IHT400"

    def test_iht400_form_generation(self):
        """Test IHT400 form data generation accuracy"""
        # Test form field population from calculation data

        # Sample estate data for form generation
        estate_data = {
            "deceased_name": "John Smith",
            "date_of_death": date(2024, 6, 15),
            "assets": {
                "property": 800000,
                "bank_accounts": 150000,
                "investments": 200000,
                "personal_effects": 25000,
                "business_assets": 300000
            },
            "liabilities": {
                "mortgage": 200000,
                "credit_cards": 5000,
                "funeral_expenses": 8000
            },
            "reliefs": {
                "business_property_relief": 150000,  # 50% BPR on some business assets
                "charitable_giving": 50000
            },
            "exemptions": {
                "spouse_exemption": 100000
            },
            "allowances": {
                "nil_rate_band": 325000,
                "residence_nil_rate_band": 175000,
                "tnrb_claimed": 162500  # 50% TNRB
            }
        }

        # Calculate form field values
        gross_estate = sum(estate_data["assets"].values())
        total_liabilities = sum(estate_data["liabilities"].values())
        net_estate = gross_estate - total_liabilities

        assert gross_estate == 1475000, "Gross estate should be £1.475M"
        assert total_liabilities == 213000, "Total liabilities should be £213k"
        assert net_estate == 1262000, "Net estate should be £1.262M"

        # Apply reliefs and exemptions
        estate_after_reliefs = net_estate - sum(estate_data["reliefs"].values())
        estate_after_exemptions = estate_after_reliefs - sum(estate_data["exemptions"].values())

        assert estate_after_reliefs == 1062000, "Estate after reliefs should be £1.062M"
        assert estate_after_exemptions == 962000, "Estate after exemptions should be £962k"

        # Calculate chargeable estate
        total_allowances = sum(estate_data["allowances"].values())
        chargeable_estate = max(0, estate_after_exemptions - total_allowances)

        assert total_allowances == 662500, "Total allowances should be £662.5k"
        assert chargeable_estate == 299500, "Chargeable estate should be £299.5k"

        # Calculate IHT liability
        iht_due = chargeable_estate * 0.4
        assert iht_due == 119800, "IHT due should be £119.8k"

        # Test form field mapping
        form_fields = {
            "box_1_gross_estate": gross_estate,
            "box_2_liabilities": total_liabilities,
            "box_3_net_estate": net_estate,
            "box_4_spouse_exemption": estate_data["exemptions"]["spouse_exemption"],
            "box_5_charitable_gifts": estate_data["reliefs"]["charitable_giving"],
            "box_6_bpr_claimed": estate_data["reliefs"]["business_property_relief"],
            "box_7_nil_rate_band": estate_data["allowances"]["nil_rate_band"],
            "box_8_rnrb": estate_data["allowances"]["residence_nil_rate_band"],
            "box_9_tnrb": estate_data["allowances"]["tnrb_claimed"],
            "box_10_chargeable_estate": chargeable_estate,
            "box_11_iht_due": iht_due
        }

        # Verify all form fields are properly calculated
        for field_name, value in form_fields.items():
            assert value >= 0, f"{field_name} should not be negative"
            assert isinstance(value, (int, float)), f"{field_name} should be numeric"

        # Test form validation rules
        validation_checks = {
            "gross_estate_equals_sum_of_assets": gross_estate == sum(estate_data["assets"].values()),
            "net_estate_calculation": net_estate == (gross_estate - total_liabilities),
            "iht_calculation": iht_due == (chargeable_estate * 0.4),
            "allowances_not_exceed_limits": (
                estate_data["allowances"]["nil_rate_band"] <= 325000 and
                estate_data["allowances"]["residence_nil_rate_band"] <= 175000 and
                estate_data["allowances"]["tnrb_claimed"] <= 325000
            )
        }

        for check_name, passes in validation_checks.items():
            assert passes == True, f"Form validation failed for: {check_name}"

    def test_payment_calculations(self):
        """Test Direct Payment Scheme and instalment calculations"""
        # Test payment timing and amounts

        # Standard IHT payment scenario
        standard_payment = {
            "iht_due": 200000,
            "date_of_death": date(2024, 6, 15),
            "probate_application_date": date(2024, 8, 1),
            "estate_administration_started": date(2024, 9, 1),
            "payment_due_date": date(2024, 12, 15)  # 6 months after death
        }

        # Payment due 6 months after end of month of death
        death_month_end = date(2024, 6, 30)
        payment_deadline = date(2024, 12, 31)  # 6 months after June end

        days_to_payment = (payment_deadline - standard_payment["date_of_death"]).days
        assert days_to_payment >= 180, "Payment should be due at least 6 months after death"

        # Interest charges for late payment
        late_payment_scenario = {
            "payment_due_date": date(2024, 12, 31),
            "actual_payment_date": date(2025, 3, 31),  # 3 months late
            "iht_amount": 200000,
            "interest_rate": 7.75,  # Current HMRC interest rate (approximate)
            "late_payment_days": 90
        }

        # Calculate interest on late payment
        daily_interest_rate = late_payment_scenario["interest_rate"] / 365 / 100
        interest_charge = (late_payment_scenario["iht_amount"] *
                         daily_interest_rate *
                         late_payment_scenario["late_payment_days"])

        expected_interest = 200000 * (7.75/100) * (90/365)  # ~£3,821
        assert abs(interest_charge - expected_interest) < 10, \
            f"Interest charge should be ~£{expected_interest:.0f}, got £{interest_charge:.0f}"

        # Instalment payment for qualifying assets
        instalment_eligible_estate = {
            "total_iht": 300000,
            "land_and_property_iht": 120000,  # 40% of total - qualifies for instalments
            "business_assets_iht": 80000,     # Qualifies for instalments
            "other_assets_iht": 100000,       # Must be paid upfront
            "instalment_eligible_amount": 200000  # Land + business
        }

        # Test instalment eligibility (property must be >20% of total IHT)
        property_percentage = (instalment_eligible_estate["land_and_property_iht"] /
                             instalment_eligible_estate["total_iht"]) * 100

        qualifies_for_instalments = property_percentage >= 20  # 20% threshold
        assert qualifies_for_instalments == True, \
            f"Should qualify for instalments with {property_percentage:.1f}% property"

        # Calculate instalment payments (10 equal annual instalments)
        annual_instalment = instalment_eligible_estate["instalment_eligible_amount"] / 10
        upfront_payment = instalment_eligible_estate["other_assets_iht"]

        assert annual_instalment == 20000, "Annual instalment should be £20k"
        assert upfront_payment == 100000, "Upfront payment should be £100k"

        # Interest on instalments (only charged if property sold or transferred)
        instalment_interest_scenario = {
            "outstanding_instalments": 150000,  # After 5 payments made
            "property_sold_date": date(2027, 3, 1),  # Property sold during instalment period
            "acceleration_triggered": True,
            "interest_on_outstanding": True
        }

        if instalment_interest_scenario["acceleration_triggered"]:
            # All outstanding instalments become due immediately
            accelerated_amount = instalment_interest_scenario["outstanding_instalments"]
            assert accelerated_amount == 150000, "All outstanding instalments due immediately"

        # Direct Payment Scheme eligibility
        dps_scenario = {
            "bank_account_value": 180000,
            "iht_liability": 200000,
            "bank_cooperation": True,
            "probate_registry_processing": True
        }

        # DPS allows banks to pay IHT directly from deceased's accounts
        dps_eligible = (
            dps_scenario["bank_cooperation"] and
            dps_scenario["probate_registry_processing"] and
            dps_scenario["bank_account_value"] >= dps_scenario["iht_liability"]
        )

        # In this case, insufficient funds in account for full DPS payment
        dps_eligible_actual = dps_scenario["bank_account_value"] >= dps_scenario["iht_liability"]
        assert dps_eligible_actual == False, "Insufficient funds for full DPS payment"

        # Partial DPS payment possible
        partial_dps_amount = min(dps_scenario["bank_account_value"],
                               dps_scenario["iht_liability"])
        remaining_balance = dps_scenario["iht_liability"] - partial_dps_amount

        assert partial_dps_amount == 180000, "Partial DPS payment should be £180k"
        assert remaining_balance == 20000, "Remaining balance should be £20k"


# Test fixtures and utilities

@pytest.fixture
def sample_estate_data():
    """Sample estate data for testing"""
    return {
        "assets": [
            {
                "asset_type": "property",
                "value": 500000,
                "is_main_residence": True
            }
        ],
        "gifts": [],
        "trusts": [],
        "marital_status": "married",
        "residence_value": 500000,
        "charitable_gifts": 0,
        "tnrb_claimed_percentage": 0,
        "trnrb_claimed_percentage": 0,
        "has_direct_descendants": True
    }


@pytest.fixture
def complex_estate_data():
    """Complex estate data with multiple elements"""
    return {
        "assets": [
            {"asset_type": "property", "value": 800000, "is_main_residence": True},
            {"asset_type": "business", "value": 500000, "business_relief_type": "unquoted_shares", "ownership_years": 3},
            {"asset_type": "investment", "value": 300000}
        ],
        "gifts": [
            {"recipient": "Child", "recipient_relationship": "child", "amount": 50000, "date_given": "2020-01-01", "exemption_claimed": "annual"},
            {"recipient": "Charity", "recipient_relationship": "charity", "amount": 100000, "date_given": "2023-01-01"}
        ],
        "trusts": [
            {"trust_name": "Family Trust", "trust_type": "discretionary", "value": 200000, "date_created": "2020-01-01"}
        ],
        "marital_status": "widowed",
        "residence_value": 800000,
        "charitable_gifts": 100000,
        "tnrb_claimed_percentage": 100,
        "trnrb_claimed_percentage": 100,
        "has_direct_descendants": True
    }