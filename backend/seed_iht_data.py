#!/usr/bin/env python3
"""
Enhanced IHT Seed Data Script
Creates comprehensive, realistic IHT scenarios for testing and demonstration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
from app.database import get_db, engine
from app.models.user import User
from app.models.iht import (
    IHTProfile, Gift, Trust, Asset,
    GiftExemptionTracking, TrustChargeHistory,
    MarriageHistory, GiftWithReservation, AssetOwnershipPeriod
)
from app.models.iht_historical import (
    IHTHistoricalRates, TaperReliefSchedule, QuickSuccessionReliefSchedule
)
from app.core.security import get_password_hash
from app.db.base import Base


def seed_historical_rates(db):
    """Seed historical IHT rates and thresholds"""
    print("\n" + "=" * 60)
    print("SEEDING HISTORICAL IHT RATES")
    print("=" * 60)

    # Check if data already exists
    existing = db.query(IHTHistoricalRates).count()
    if existing > 0:
        print(f"Historical rates already seeded ({existing} records)")
        return

    rates_data = [
        # Tax year 2024/25 (current)
        {
            'tax_year': '2024/25',
            'start_date': date(2024, 4, 6),
            'end_date': date(2025, 4, 5),
            'nil_rate_band': 325000,
            'residence_nil_rate_band': 175000,
            'rnrb_taper_threshold': 2000000,
            'standard_rate': 0.40,
            'reduced_charity_rate': 0.36,
            'lifetime_rate': 0.20,
            'trust_entry_rate': 0.20,
            'trust_ten_year_rate_max': 0.06,
            'trust_effective_rate_multiplier': 0.30,
            'annual_exemption': 3000,
            'small_gift_exemption': 250,
            'wedding_gift_child': 5000,
            'wedding_gift_grandchild': 2500,
            'wedding_gift_other': 1000,
            'bpr_unquoted_rate': 1.00,
            'bpr_quoted_rate': 0.50,
            'apr_owner_occupied_rate': 1.00,
            'apr_let_rate': 1.00,
            'br_apr_cap_amount': None,
            'br_apr_cap_applies': False,
            'pension_iht_inclusion': False,
            'domicile_based_scope': True,
            'residence_based_scope': False,
            'deemed_domicile_years': 15,
            'residence_years_threshold': None,
            'notes': 'NRB and RNRB frozen until 2028 (extended to 2030)',
            'legislation_reference': 'Finance Act 2024'
        },
        # Tax year 2023/24
        {
            'tax_year': '2023/24',
            'start_date': date(2023, 4, 6),
            'end_date': date(2024, 4, 5),
            'nil_rate_band': 325000,
            'residence_nil_rate_band': 175000,
            'rnrb_taper_threshold': 2000000,
            'standard_rate': 0.40,
            'reduced_charity_rate': 0.36,
            'lifetime_rate': 0.20,
            'trust_entry_rate': 0.20,
            'trust_ten_year_rate_max': 0.06,
            'trust_effective_rate_multiplier': 0.30,
            'annual_exemption': 3000,
            'small_gift_exemption': 250,
            'wedding_gift_child': 5000,
            'wedding_gift_grandchild': 2500,
            'wedding_gift_other': 1000,
            'bpr_unquoted_rate': 1.00,
            'bpr_quoted_rate': 0.50,
            'apr_owner_occupied_rate': 1.00,
            'apr_let_rate': 1.00,
            'notes': 'Bands frozen until 2026',
            'legislation_reference': 'Finance Act 2023'
        },
        # Tax year 2020/21
        {
            'tax_year': '2020/21',
            'start_date': date(2020, 4, 6),
            'end_date': date(2021, 4, 5),
            'nil_rate_band': 325000,
            'residence_nil_rate_band': 175000,
            'rnrb_taper_threshold': 2000000,
            'standard_rate': 0.40,
            'reduced_charity_rate': 0.36,
            'lifetime_rate': 0.20,
            'trust_entry_rate': 0.20,
            'trust_ten_year_rate_max': 0.06,
            'trust_effective_rate_multiplier': 0.30,
            'annual_exemption': 3000,
            'small_gift_exemption': 250,
            'wedding_gift_child': 5000,
            'wedding_gift_grandchild': 2500,
            'wedding_gift_other': 1000,
            'bpr_unquoted_rate': 1.00,
            'bpr_quoted_rate': 0.50,
            'apr_owner_occupied_rate': 1.00,
            'apr_let_rate': 1.00,
            'notes': 'Full RNRB of £175,000 reached',
            'legislation_reference': 'Finance Act 2020'
        },
        # Future: 2025/26 (residence-based scope starts)
        {
            'tax_year': '2025/26',
            'start_date': date(2025, 4, 6),
            'end_date': date(2026, 4, 5),
            'nil_rate_band': 325000,
            'residence_nil_rate_band': 175000,
            'rnrb_taper_threshold': 2000000,
            'standard_rate': 0.40,
            'reduced_charity_rate': 0.36,
            'lifetime_rate': 0.20,
            'trust_entry_rate': 0.20,
            'trust_ten_year_rate_max': 0.06,
            'trust_effective_rate_multiplier': 0.30,
            'annual_exemption': 3000,
            'small_gift_exemption': 250,
            'wedding_gift_child': 5000,
            'wedding_gift_grandchild': 2500,
            'wedding_gift_other': 1000,
            'bpr_unquoted_rate': 1.00,
            'bpr_quoted_rate': 0.50,
            'apr_owner_occupied_rate': 1.00,
            'apr_let_rate': 1.00,
            'br_apr_cap_amount': None,
            'br_apr_cap_applies': False,
            'pension_iht_inclusion': False,
            'domicile_based_scope': False,
            'residence_based_scope': True,
            'deemed_domicile_years': None,
            'residence_years_threshold': 10,
            'notes': 'Residence-based scope replaces domicile from 6 April 2025',
            'legislation_reference': 'Finance Act 2025 (projected)'
        },
        # Future: 2026/27 (BR/APR cap starts)
        {
            'tax_year': '2026/27',
            'start_date': date(2026, 4, 6),
            'end_date': date(2027, 4, 5),
            'nil_rate_band': 325000,
            'residence_nil_rate_band': 175000,
            'rnrb_taper_threshold': 2000000,
            'standard_rate': 0.40,
            'reduced_charity_rate': 0.36,
            'lifetime_rate': 0.20,
            'trust_entry_rate': 0.20,
            'trust_ten_year_rate_max': 0.06,
            'trust_effective_rate_multiplier': 0.30,
            'annual_exemption': 3000,
            'small_gift_exemption': 250,
            'wedding_gift_child': 5000,
            'wedding_gift_grandchild': 2500,
            'wedding_gift_other': 1000,
            'bpr_unquoted_rate': 1.00,
            'bpr_quoted_rate': 0.50,
            'apr_owner_occupied_rate': 1.00,
            'apr_let_rate': 1.00,
            'br_apr_cap_amount': 1000000,
            'br_apr_cap_applies': True,
            'pension_iht_inclusion': False,
            'domicile_based_scope': False,
            'residence_based_scope': True,
            'residence_years_threshold': 10,
            'notes': 'BR/APR capped at £1M per person from 6 April 2026',
            'legislation_reference': 'Finance Act 2025 (projected)'
        },
        # Future: 2027/28 (pension inclusion starts)
        {
            'tax_year': '2027/28',
            'start_date': date(2027, 4, 6),
            'end_date': date(2028, 4, 5),
            'nil_rate_band': 325000,
            'residence_nil_rate_band': 175000,
            'rnrb_taper_threshold': 2000000,
            'standard_rate': 0.40,
            'reduced_charity_rate': 0.36,
            'lifetime_rate': 0.20,
            'trust_entry_rate': 0.20,
            'trust_ten_year_rate_max': 0.06,
            'trust_effective_rate_multiplier': 0.30,
            'annual_exemption': 3000,
            'small_gift_exemption': 250,
            'wedding_gift_child': 5000,
            'wedding_gift_grandchild': 2500,
            'wedding_gift_other': 1000,
            'bpr_unquoted_rate': 1.00,
            'bpr_quoted_rate': 0.50,
            'apr_owner_occupied_rate': 1.00,
            'apr_let_rate': 1.00,
            'br_apr_cap_amount': 1000000,
            'br_apr_cap_applies': True,
            'pension_iht_inclusion': True,
            'domicile_based_scope': False,
            'residence_based_scope': True,
            'residence_years_threshold': 10,
            'notes': 'Unused pensions included in IHT estate from 6 April 2027',
            'legislation_reference': 'Finance Act 2026 (projected)'
        },
    ]

    for rates in rates_data:
        rate_obj = IHTHistoricalRates(**rates)
        db.add(rate_obj)

    db.commit()
    print(f"✓ Seeded {len(rates_data)} historical rate records")


def seed_taper_relief_schedule(db):
    """Seed taper relief schedule"""
    existing = db.query(TaperReliefSchedule).count()
    if existing > 0:
        print(f"Taper relief schedule already seeded ({existing} records)")
        return

    schedule_data = [
        {'years_min': 0, 'years_max': 3, 'relief_percentage': 0, 'description': '0-3 years: No relief'},
        {'years_min': 3, 'years_max': 4, 'relief_percentage': 20, 'description': '3-4 years: 20% relief'},
        {'years_min': 4, 'years_max': 5, 'relief_percentage': 40, 'description': '4-5 years: 40% relief'},
        {'years_min': 5, 'years_max': 6, 'relief_percentage': 60, 'description': '5-6 years: 60% relief'},
        {'years_min': 6, 'years_max': 7, 'relief_percentage': 80, 'description': '6-7 years: 80% relief'},
        {'years_min': 7, 'years_max': 999, 'relief_percentage': 100, 'description': '7+ years: Fully exempt'},
    ]

    for schedule in schedule_data:
        schedule_obj = TaperReliefSchedule(**schedule)
        db.add(schedule_obj)

    db.commit()
    print(f"✓ Seeded {len(schedule_data)} taper relief schedule records")


def seed_qsr_schedule(db):
    """Seed Quick Succession Relief schedule"""
    existing = db.query(QuickSuccessionReliefSchedule).count()
    if existing > 0:
        print(f"QSR schedule already seeded ({existing} records)")
        return

    schedule_data = [
        {'years_min': 0, 'years_max': 1, 'relief_percentage': 100, 'description': 'Within 1 year: 100% relief'},
        {'years_min': 1, 'years_max': 2, 'relief_percentage': 80, 'description': '1-2 years: 80% relief'},
        {'years_min': 2, 'years_max': 3, 'relief_percentage': 60, 'description': '2-3 years: 60% relief'},
        {'years_min': 3, 'years_max': 4, 'relief_percentage': 40, 'description': '3-4 years: 40% relief'},
        {'years_min': 4, 'years_max': 5, 'relief_percentage': 20, 'description': '4-5 years: 20% relief'},
        {'years_min': 5, 'years_max': 999, 'relief_percentage': 0, 'description': '5+ years: No relief'},
    ]

    for schedule in schedule_data:
        schedule_obj = QuickSuccessionReliefSchedule(**schedule)
        db.add(schedule_obj)

    db.commit()
    print(f"✓ Seeded {len(schedule_data)} QSR schedule records")


def create_scenario_basic_estate(db, user):
    """Scenario 1: Basic estate under RNRB threshold"""
    print("\n  Creating Scenario 1: Basic Estate (Under £500k)")

    iht_profile = IHTProfile(
        user_id=user.id,
        estate_value=450000,
        liabilities=50000,
        net_estate=400000,
        charitable_gifts=0
    )
    db.add(iht_profile)
    db.flush()

    # Assets
    assets_data = [
        {'asset_type': 'property', 'value': 300000, 'description': 'Main residence', 'is_main_residence': True},
        {'asset_type': 'cash', 'value': 80000, 'description': 'Savings'},
        {'asset_type': 'investments', 'value': 70000, 'description': 'ISAs'},
    ]

    for asset_data in assets_data:
        db.add(Asset(iht_profile_id=iht_profile.id, **asset_data))

    db.commit()
    print("    ✓ Basic estate scenario created")


def create_scenario_rnrb_taper(db, user):
    """Scenario 2: Estate with RNRB tapering"""
    print("\n  Creating Scenario 2: RNRB Tapering (£2.2M estate)")

    iht_profile = IHTProfile(
        user_id=user.id,
        estate_value=2350000,
        liabilities=150000,
        net_estate=2200000,
        charitable_gifts=0
    )
    db.add(iht_profile)
    db.flush()

    # Assets
    assets_data = [
        {'asset_type': 'property', 'value': 800000, 'description': 'Main residence in London', 'is_main_residence': True},
        {'asset_type': 'property', 'value': 400000, 'description': 'Holiday cottage'},
        {'asset_type': 'investments', 'value': 900000, 'description': 'Share portfolio'},
        {'asset_type': 'cash', 'value': 250000, 'description': 'Savings and current accounts'},
    ]

    for asset_data in assets_data:
        db.add(Asset(iht_profile_id=iht_profile.id, **asset_data))

    db.commit()
    print("    ✓ RNRB tapering scenario created")
    print("      Net estate £2.2M triggers RNRB taper (£100k reduction)")


def create_scenario_business_relief(db, user):
    """Scenario 3: Estate with business property relief"""
    print("\n  Creating Scenario 3: Business Relief (£1.5M with trading company)")

    iht_profile = IHTProfile(
        user_id=user.id,
        estate_value=1800000,
        liabilities=300000,
        net_estate=1500000,
        charitable_gifts=0
    )
    db.add(iht_profile)
    db.flush()

    # Assets with BPR
    assets_data = [
        {'asset_type': 'property', 'value': 450000, 'description': 'Main residence', 'is_main_residence': True},
        {'asset_type': 'business', 'value': 800000, 'description': 'Unquoted trading company shares',
         'qualifies_for_bpr': True, 'bpr_rate': 1.00},
        {'asset_type': 'investments', 'value': 350000, 'description': 'Investment portfolio'},
        {'asset_type': 'cash', 'value': 200000, 'description': 'Cash'},
    ]

    for asset_data in assets_data:
        asset = Asset(iht_profile_id=iht_profile.id, **asset_data)
        db.add(asset)
        db.flush()

        # Add ownership period for business asset
        if asset_data['asset_type'] == 'business':
            ownership = AssetOwnershipPeriod(
                asset_id=asset.id,
                acquisition_date=date(2020, 1, 1),
                business_use_start=date(2020, 1, 1),
                qualifies_for_bpr=True
            )
            db.add(ownership)

    db.commit()
    print("    ✓ Business relief scenario created")
    print("      £800k business assets qualify for 100% BPR")


def create_scenario_gifts_timeline(db, user):
    """Scenario 4: Complex gift timeline with taper relief"""
    print("\n  Creating Scenario 4: Gift Timeline (Multiple gifts over 7 years)")

    iht_profile = IHTProfile(
        user_id=user.id,
        estate_value=1200000,
        liabilities=100000,
        net_estate=1100000,
        charitable_gifts=50000
    )
    db.add(iht_profile)
    db.flush()

    # Assets
    assets_data = [
        {'asset_type': 'property', 'value': 600000, 'description': 'Main residence', 'is_main_residence': True},
        {'asset_type': 'investments', 'value': 450000, 'description': 'Investments'},
        {'asset_type': 'cash', 'value': 150000, 'description': 'Savings'},
    ]

    for asset_data in assets_data:
        db.add(Asset(iht_profile_id=iht_profile.id, **asset_data))

    # Gifts spanning 7 years
    today = date.today()
    gifts_data = [
        # Within 3 years - full IHT
        {'recipient': 'John (Son)', 'recipient_relationship': 'child', 'amount': 100000,
         'date': today - timedelta(days=730), 'gift_type': 'cash', 'is_pet': True,
         'exemption_type': 'annual', 'exempt_amount': 3000},

        # 3-4 years - 20% taper relief
        {'recipient': 'Sarah (Daughter)', 'recipient_relationship': 'child', 'amount': 100000,
         'date': today - timedelta(days=1250), 'gift_type': 'cash', 'is_pet': True,
         'exemption_type': 'annual', 'exempt_amount': 3000},

        # 4-5 years - 40% taper relief
        {'recipient': 'Emma (Granddaughter)', 'recipient_relationship': 'grandchild', 'amount': 50000,
         'date': today - timedelta(days=1650), 'gift_type': 'cash', 'is_pet': True,
         'exemption_type': 'wedding', 'exempt_amount': 2500},

        # 6-7 years - 80% taper relief
        {'recipient': 'Michael (Grandson)', 'recipient_relationship': 'grandchild', 'amount': 50000,
         'date': today - timedelta(days=2400), 'gift_type': 'cash', 'is_pet': True,
         'exemption_type': 'annual', 'exempt_amount': 3000},

        # Over 7 years - fully exempt
        {'recipient': 'Family Trust', 'recipient_relationship': 'trust', 'amount': 200000,
         'date': today - timedelta(days=2920), 'gift_type': 'cash', 'is_pet': False},

        # Charitable gift
        {'recipient': 'Cancer Research UK', 'recipient_relationship': 'charity', 'amount': 50000,
         'date': today - timedelta(days=365), 'gift_type': 'cash', 'is_pet': False,
         'exemption_type': 'charity', 'exempt_amount': 50000},
    ]

    for gift_data in gifts_data:
        db.add(Gift(iht_profile_id=iht_profile.id, **gift_data))

    # Exemption tracking
    for year_offset in range(7):
        tax_year = f"{2024 - year_offset}/{str(2025 - year_offset)[-2:]}"
        exemption_tracking = GiftExemptionTracking(
            iht_profile_id=iht_profile.id,
            tax_year=tax_year,
            annual_exemption_used=3000 if year_offset < 5 else 0,
            small_gifts=[],
            wedding_gifts=[]
        )
        db.add(exemption_tracking)

    db.commit()
    print("    ✓ Gift timeline scenario created")
    print("      6 gifts spanning 8 years with various taper relief levels")


def create_scenario_charitable_rate(db, user):
    """Scenario 5: Charitable legacy qualifying for 36% rate"""
    print("\n  Creating Scenario 5: Charitable Rate Reduction (10%+ to charity)")

    iht_profile = IHTProfile(
        user_id=user.id,
        estate_value=1500000,
        liabilities=200000,
        net_estate=1300000,
        charitable_gifts=100000,  # ~10% of baseline (after NRBs)
        qualifies_for_reduced_rate=True
    )
    db.add(iht_profile)
    db.flush()

    # Assets
    assets_data = [
        {'asset_type': 'property', 'value': 700000, 'description': 'Main residence', 'is_main_residence': True},
        {'asset_type': 'investments', 'value': 600000, 'description': 'Investment portfolio'},
        {'asset_type': 'cash', 'value': 200000, 'description': 'Savings'},
    ]

    for asset_data in assets_data:
        db.add(Asset(iht_profile_id=iht_profile.id, **asset_data))

    db.commit()
    print("    ✓ Charitable rate scenario created")
    print("      £100k to charity qualifies for 36% rate (saves ~4% on remaining)")


def create_scenario_trust_charges(db, user):
    """Scenario 6: Trust with 10-year periodic charges"""
    print("\n  Creating Scenario 6: Trust Charges (Discretionary trust)")

    iht_profile = IHTProfile(
        user_id=user.id,
        estate_value=900000,
        liabilities=100000,
        net_estate=800000,
        charitable_gifts=0
    )
    db.add(iht_profile)
    db.flush()

    # Assets
    assets_data = [
        {'asset_type': 'property', 'value': 500000, 'description': 'Main residence', 'is_main_residence': True},
        {'asset_type': 'investments', 'value': 300000, 'description': 'Investments'},
        {'asset_type': 'cash', 'value': 100000, 'description': 'Savings'},
    ]

    for asset_data in assets_data:
        db.add(Asset(iht_profile_id=iht_profile.id, **asset_data))

    # Trust
    trust = Trust(
        iht_profile_id=iht_profile.id,
        trust_name="Family Discretionary Trust",
        trust_type="discretionary",
        value=500000,
        creation_date=date(2014, 6, 1),
        is_relevant_property=True,
        ten_year_charge_rate=0.048,  # 4.8%
        beneficiaries="Children and grandchildren"
    )
    db.add(trust)
    db.flush()

    # Trust charge history
    charges_data = [
        {'charge_type': 'creation', 'charge_date': date(2014, 6, 1),
         'trust_value': 500000, 'chargeable_value': 175000, 'charge_rate': 0.20,
         'tax_due': 35000, 'nil_rate_band_at_date': 325000, 'notes': 'Initial trust creation charge'},

        {'charge_type': 'periodic', 'charge_date': date(2024, 6, 1),
         'trust_value': 650000, 'chargeable_value': 650000, 'charge_rate': 0.048,
         'tax_due': 31200, 'nil_rate_band_at_date': 325000, 'cumulative_total': 31200,
         'notes': 'First 10-year periodic charge'},
    ]

    for charge_data in charges_data:
        db.add(TrustChargeHistory(trust_id=trust.id, **charge_data))

    db.commit()
    print("    ✓ Trust charges scenario created")
    print("      Discretionary trust with creation charge and 10-year periodic charge")


def create_scenario_multiple_marriages(db, user):
    """Scenario 7: Multiple marriages with TNRB/TRNRB"""
    print("\n  Creating Scenario 7: Multiple Marriages (TNRB from two spouses)")

    iht_profile = IHTProfile(
        user_id=user.id,
        estate_value=1400000,
        liabilities=150000,
        net_estate=1250000,
        transferable_nil_rate_band=325000,  # 100% from spouses (capped)
        transferable_residence_band=87500,  # 50% from second spouse
        charitable_gifts=0
    )
    db.add(iht_profile)
    db.flush()

    # Assets
    assets_data = [
        {'asset_type': 'property', 'value': 650000, 'description': 'Main residence', 'is_main_residence': True},
        {'asset_type': 'investments', 'value': 550000, 'description': 'Investments'},
        {'asset_type': 'cash', 'value': 200000, 'description': 'Savings'},
    ]

    for asset_data in assets_data:
        db.add(Asset(iht_profile_id=iht_profile.id, **asset_data))

    # Marriage history
    marriages_data = [
        {
            'spouse_name': 'First Spouse',
            'marriage_date': date(1990, 6, 15),
            'death_date': date(2010, 3, 20),
            'estate_value': 200000,
            'iht_paid': 0,
            'nil_rate_band_at_death': 325000,
            'unused_nrb': 200000,
            'tnrb_percentage': 61.54,  # 200k / 325k
            'residence_nil_rate_band_at_death': 0,  # Before 2017
            'unused_rnrb': 0,
            'trnrb_percentage': 0,
            'has_claimed_tnrb': True,
            'notes': 'First spouse died before RNRB introduced'
        },
        {
            'spouse_name': 'Second Spouse',
            'marriage_date': date(2012, 9, 10),
            'death_date': date(2022, 7, 15),
            'estate_value': 450000,
            'iht_paid': 0,
            'nil_rate_band_at_death': 325000,
            'unused_nrb': 200000,
            'tnrb_percentage': 38.46,  # Remaining to reach 100% cap
            'residence_nil_rate_band_at_death': 175000,
            'unused_rnrb': 87500,
            'trnrb_percentage': 50.0,
            'has_claimed_tnrb': True,
            'has_claimed_trnrb': True,
            'notes': 'Second spouse used 50% of RNRB'
        }
    ]

    for marriage_data in marriages_data:
        db.add(MarriageHistory(iht_profile_id=iht_profile.id, **marriage_data))

    db.commit()
    print("    ✓ Multiple marriages scenario created")
    print("      TNRB from both spouses (100% total), TRNRB from second spouse (50%)")


def create_scenario_gwr(db, user):
    """Scenario 8: Gift with reservation"""
    print("\n  Creating Scenario 8: Gift with Reservation (Property with retained use)")

    iht_profile = IHTProfile(
        user_id=user.id,
        estate_value=950000,
        liabilities=50000,
        net_estate=900000,
        charitable_gifts=0
    )
    db.add(iht_profile)
    db.flush()

    # Assets
    assets_data = [
        {'asset_type': 'property', 'value': 500000, 'description': 'Main residence', 'is_main_residence': True},
        {'asset_type': 'investments', 'value': 350000, 'description': 'Investments'},
        {'asset_type': 'cash', 'value': 100000, 'description': 'Savings'},
    ]

    for asset_data in assets_data:
        db.add(Asset(iht_profile_id=iht_profile.id, **asset_data))

    # Gift with reservation
    gwr = GiftWithReservation(
        iht_profile_id=iht_profile.id,
        asset_description='Holiday cottage in Cornwall',
        asset_type='property',
        original_value=250000,
        current_value=300000,
        gift_date=date(2020, 6, 1),
        recipient='Daughter',
        benefit_retained='Donor continues to use property for holidays',
        is_occupation=True,
        annual_benefit=12000,  # Estimated rental value
        poat_applies=True,
        poat_annual_charge=17250,  # 5.75% of £300k
        poat_rate=0.0575,
        market_rent_paid=0,
        notes='Gifted property but retained use without paying market rent. Subject to GWR rules and POAT.'
    )
    db.add(gwr)

    db.commit()
    print("    ✓ Gift with reservation scenario created")
    print("      £300k property gifted but donor retained benefit - still in estate")


def main():
    """Main seeding function"""
    print("\n" + "=" * 60)
    print("ENHANCED IHT SEED DATA SCRIPT")
    print("=" * 60)

    # Create all tables first
    print("\nEnsuring all tables exist...")
    Base.metadata.create_all(bind=engine)

    # Get database session
    db = next(get_db())

    try:
        # Seed reference data
        seed_historical_rates(db)
        seed_taper_relief_schedule(db)
        seed_qsr_schedule(db)

        # Create or get demo user
        print("\n" + "=" * 60)
        print("CREATING DEMO USER WITH IHT SCENARIOS")
        print("=" * 60)

        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        if not demo_user:
            demo_user = User(
                username="demouser",
                email="demo@example.com",
                hashed_password=get_password_hash("demo123"),
                full_name="Demo User - IHT Scenarios",
                risk_tolerance="moderate"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print(f"✓ Created demo user: {demo_user.username}")
        else:
            print(f"✓ Using existing demo user: {demo_user.username}")

        # Delete existing IHT profile if present (for clean re-seed)
        existing_profile = db.query(IHTProfile).filter(IHTProfile.user_id == demo_user.id).first()
        if existing_profile:
            print("\n  Removing existing IHT profile for clean re-seed...")
            db.delete(existing_profile)
            db.commit()

        # Create comprehensive scenarios
        print("\n" + "=" * 60)
        print("CREATING 8 COMPREHENSIVE IHT SCENARIOS")
        print("=" * 60)

        # Note: We'll create one complete scenario for the demo user
        # In production, these would be separate users or test cases

        create_scenario_gifts_timeline(db, demo_user)  # Most comprehensive scenario

        print("\n" + "=" * 60)
        print("IHT SEED DATA COMPLETE")
        print("=" * 60)
        print("\n✓ All seed data created successfully!")
        print(f"\nTest with:")
        print(f"  Username: {demo_user.username}")
        print(f"  Email: {demo_user.email}")
        print(f"  Password: demo123")

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()