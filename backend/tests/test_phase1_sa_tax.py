"""Tests for Phase 1: South African Tax Support - Foundation

Tests cover:
- Currency conversion service
- TaxProfile model CRUD operations
- User model currency fields
- Product model currency/jurisdiction fields
- Financial statement currency fields
- SA tax constants
"""

import pytest
from datetime import date
from sqlalchemy.orm import Session

from app.models.tax_profile import TaxProfile
from app.models.user import User
from app.models.product import Product
from app.models.financial import BalanceSheet, ProfitLoss, CashFlow
from app.services.currency import (
    CurrencyConverter,
    convert_currency,
    get_exchange_rate,
    format_currency,
    get_currency_symbol
)
from app.services.sa_tax_constants import (
    sa_tax_rates_2024_25,
    get_age_category,
    get_tax_rebate,
    get_tax_threshold,
    AgeCategory
)


class TestCurrencyConverter:
    """Test currency conversion functionality."""

    def test_get_exchange_rate_same_currency(self):
        """Test rate is 1.0 for same currency."""
        converter = CurrencyConverter()
        rate = converter.get_exchange_rate("GBP", "GBP")
        assert rate == 1.0

    def test_get_exchange_rate_gbp_to_zar(self):
        """Test GBP to ZAR conversion rate."""
        converter = CurrencyConverter()
        rate = converter.get_exchange_rate("GBP", "ZAR")
        assert rate == 24.0  # 1 GBP = 24 ZAR

    def test_get_exchange_rate_zar_to_gbp(self):
        """Test ZAR to GBP conversion rate (inverse)."""
        converter = CurrencyConverter()
        rate = converter.get_exchange_rate("ZAR", "GBP")
        expected_rate = 1.0 / 24.0
        assert abs(rate - expected_rate) < 0.0001  # Allow small floating point error

    def test_get_exchange_rate_cross_rate(self):
        """Test cross rate (ZAR to USD)."""
        converter = CurrencyConverter()
        rate = converter.get_exchange_rate("ZAR", "USD")
        # 1 ZAR = 0.054 USD (approximately)
        assert abs(rate - 0.054) < 0.01

    def test_convert_currency_gbp_to_zar(self):
        """Test currency conversion GBP to ZAR."""
        converter = CurrencyConverter()
        result = converter.convert_currency(100, "GBP", "ZAR")
        assert result == 2400.0  # £100 = R2,400

    def test_convert_currency_zar_to_gbp(self):
        """Test currency conversion ZAR to GBP."""
        converter = CurrencyConverter()
        result = converter.convert_currency(1000, "ZAR", "GBP")
        expected = 1000 / 24.0
        assert abs(result - expected) < 0.01

    def test_get_currency_symbol_gbp(self):
        """Test GBP symbol."""
        converter = CurrencyConverter()
        symbol = converter.get_currency_symbol("GBP")
        assert symbol == "£"

    def test_get_currency_symbol_zar(self):
        """Test ZAR symbol."""
        converter = CurrencyConverter()
        symbol = converter.get_currency_symbol("ZAR")
        assert symbol == "R"

    def test_format_currency_gbp(self):
        """Test currency formatting for GBP."""
        converter = CurrencyConverter()
        formatted = converter.format_currency(1234.56, "GBP")
        assert formatted == "£1,234.56"

    def test_format_currency_zar(self):
        """Test currency formatting for ZAR."""
        converter = CurrencyConverter()
        formatted = converter.format_currency(50000, "ZAR")
        assert formatted == "R50,000.00"

    def test_convenience_functions(self):
        """Test convenience wrapper functions."""
        # convert_currency
        result = convert_currency(100, "GBP", "ZAR")
        assert result == 2400.0

        # get_exchange_rate
        rate = get_exchange_rate("GBP", "ZAR")
        assert rate == 24.0

        # format_currency
        formatted = format_currency(1000, "GBP")
        assert formatted == "£1,000.00"

        # get_currency_symbol
        symbol = get_currency_symbol("ZAR")
        assert symbol == "R"


class TestSATaxConstants:
    """Test South African tax constants and calculations."""

    def test_sa_tax_rates_exist(self):
        """Test SA tax rates are properly loaded."""
        assert sa_tax_rates_2024_25 is not None
        assert sa_tax_rates_2024_25.primary_rebate == 17235
        assert sa_tax_rates_2024_25.cgt_annual_exclusion == 40000
        assert sa_tax_rates_2024_25.tfsa_annual_limit == 36000

    def test_income_tax_brackets_loaded(self):
        """Test income tax brackets are loaded."""
        brackets = sa_tax_rates_2024_25.income_tax_brackets
        assert len(brackets) == 7  # 7 tax brackets
        assert brackets[0].rate == 0.18  # First bracket is 18%
        assert brackets[0].min_income == 0
        assert brackets[0].max_income == 237100

    def test_get_age_category_under_65(self):
        """Test age category for person under 65."""
        dob = date(1990, 1, 1)  # 34 years old
        as_of = date(2024, 10, 6)
        category = get_age_category(dob, as_of)
        assert category == AgeCategory.UNDER_65

    def test_get_age_category_65_to_74(self):
        """Test age category for person aged 65-74."""
        dob = date(1954, 1, 1)  # 70 years old
        as_of = date(2024, 10, 6)
        category = get_age_category(dob, as_of)
        assert category == AgeCategory.AGE_65_TO_74

    def test_get_age_category_75_plus(self):
        """Test age category for person 75+."""
        dob = date(1945, 1, 1)  # 79 years old
        as_of = date(2024, 10, 6)
        category = get_age_category(dob, as_of)
        assert category == AgeCategory.AGE_75_PLUS

    def test_get_tax_rebate_under_65(self):
        """Test tax rebate for person under 65."""
        rebate = get_tax_rebate(AgeCategory.UNDER_65)
        assert rebate == 17235  # Primary rebate only

    def test_get_tax_rebate_65_to_74(self):
        """Test tax rebate for person aged 65-74."""
        rebate = get_tax_rebate(AgeCategory.AGE_65_TO_74)
        expected = 17235 + 9444  # Primary + Secondary
        assert rebate == expected

    def test_get_tax_rebate_75_plus(self):
        """Test tax rebate for person 75+."""
        rebate = get_tax_rebate(AgeCategory.AGE_75_PLUS)
        expected = 17235 + 9444 + 3145  # Primary + Secondary + Tertiary
        assert rebate == expected

    def test_get_tax_threshold(self):
        """Test tax thresholds for different age groups."""
        threshold_under_65 = get_tax_threshold(AgeCategory.UNDER_65)
        threshold_65_74 = get_tax_threshold(AgeCategory.AGE_65_TO_74)
        threshold_75_plus = get_tax_threshold(AgeCategory.AGE_75_PLUS)

        assert threshold_under_65 == 95750
        assert threshold_65_74 == 148217
        assert threshold_75_plus == 165689

    def test_transfer_duty_brackets(self):
        """Test transfer duty brackets are loaded."""
        brackets = sa_tax_rates_2024_25.transfer_duty_brackets
        assert len(brackets) == 6
        assert brackets[0]["min_value"] == 0
        assert brackets[0]["max_value"] == 1100000
        assert brackets[0]["rate"] == 0.0  # No duty below R1.1m


class TestTaxProfileModel:
    """Test TaxProfile model and database operations."""

    def test_tax_profile_creation(self, db: Session, fresh_test_user: User):
        """Test creating a tax profile."""
        tax_profile = TaxProfile(
            user_id=fresh_test_user.id,
            domicile="UK",
            domicile_of_origin="SA",
            tax_residency="dual_resident",
            uk_tax_resident=True,
            sa_tax_resident=True,
            uk_years_of_residency=10,
            sa_years_of_residency=25
        )
        db.add(tax_profile)
        db.commit()
        db.refresh(tax_profile)

        assert tax_profile.id is not None
        assert tax_profile.domicile == "UK"
        assert tax_profile.tax_residency == "dual_resident"
        assert tax_profile.is_dual_resident is True

    def test_tax_profile_relationship_with_user(self, db: Session, fresh_test_user: User):
        """Test relationship between TaxProfile and User."""
        tax_profile = TaxProfile(
            user_id=fresh_test_user.id,
            domicile="SA",
            tax_residency="SA",
            sa_tax_resident=True
        )
        db.add(tax_profile)
        db.commit()

        # Access via user
        db.refresh(fresh_test_user)
        assert fresh_test_user.tax_profile is not None
        assert fresh_test_user.tax_profile.domicile == "SA"

    def test_tax_profile_properties(self, db: Session, fresh_test_user: User):
        """Test TaxProfile computed properties."""
        tax_profile = TaxProfile(
            user_id=fresh_test_user.id,
            domicile="deemed_domicile_uk",
            tax_residency="dual_resident",
            uk_tax_resident=True,
            sa_tax_resident=True,
            treaty_tie_breaker_country="UK"
        )
        db.add(tax_profile)
        db.commit()

        assert tax_profile.is_uk_domiciled is True
        assert tax_profile.is_sa_domiciled is False
        assert tax_profile.is_dual_resident is True
        assert tax_profile.effective_tax_country == "UK"


class TestUserModelCurrencyFields:
    """Test User model currency fields."""

    def test_user_has_primary_currency_field(self, db: Session):
        """Test User model has primary_currency field."""
        user = User(
            email="currency_test@example.com",
            username="currencytest",
            hashed_password="hashed",
            primary_currency="ZAR"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.primary_currency == "ZAR"

    def test_user_primary_currency_defaults_to_gbp(self, db: Session):
        """Test primary_currency defaults to GBP."""
        user = User(
            email="default_currency@example.com",
            username="defaultcurrency",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.primary_currency == "GBP"

    def test_user_has_secondary_currency_field(self, db: Session):
        """Test User model has secondary_currency field."""
        user = User(
            email="dual_currency@example.com",
            username="dualcurrency",
            hashed_password="hashed",
            primary_currency="GBP",
            secondary_currency="ZAR"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.primary_currency == "GBP"
        assert user.secondary_currency == "ZAR"


class TestProductModelCurrencyJurisdiction:
    """Test Product model currency and jurisdiction fields."""

    def test_product_has_currency_field(self, db: Session, fresh_test_user: User):
        """Test Product model has currency field."""
        product = Product(
            user_id=fresh_test_user.id,
            product_type="investment",
            product_name="SA Unit Trust",
            currency="ZAR"
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        assert product.currency == "ZAR"

    def test_product_currency_defaults_to_gbp(self, db: Session, fresh_test_user: User):
        """Test currency defaults to GBP."""
        product = Product(
            user_id=fresh_test_user.id,
            product_type="pension",
            product_name="UK Pension"
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        assert product.currency == "GBP"

    def test_product_has_jurisdiction_field(self, db: Session, fresh_test_user: User):
        """Test Product model has jurisdiction field."""
        product = Product(
            user_id=fresh_test_user.id,
            product_type="savings",
            product_name="TFSA",
            jurisdiction="SA"
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        assert product.jurisdiction == "SA"

    def test_product_jurisdiction_defaults_to_uk(self, db: Session, fresh_test_user: User):
        """Test jurisdiction defaults to UK."""
        product = Product(
            user_id=fresh_test_user.id,
            product_type="protection",
            product_name="Life Insurance"
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        assert product.jurisdiction == "UK"


class TestFinancialStatementCurrencyFields:
    """Test financial statement models have currency fields."""

    def test_balance_sheet_has_currency(self, db: Session, fresh_test_user: User):
        """Test BalanceSheet has currency field."""
        bs = BalanceSheet(
            user_id=fresh_test_user.id,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 12, 31),
            currency="ZAR",
            total_assets=1000000,
            total_liabilities=200000,
            net_worth=800000
        )
        db.add(bs)
        db.commit()
        db.refresh(bs)

        assert bs.currency == "ZAR"

    def test_profit_loss_has_currency(self, db: Session, fresh_test_user: User):
        """Test ProfitLoss has currency field."""
        pl = ProfitLoss(
            user_id=fresh_test_user.id,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 12, 31),
            currency="ZAR",
            total_income=500000,
            total_expenses=300000,
            net_income=200000
        )
        db.add(pl)
        db.commit()
        db.refresh(pl)

        assert pl.currency == "ZAR"

    def test_cash_flow_has_currency(self, db: Session, fresh_test_user: User):
        """Test CashFlow has currency field."""
        cf = CashFlow(
            user_id=fresh_test_user.id,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 12, 31),
            currency="ZAR",
            opening_balance=100000
        )
        db.add(cf)
        db.commit()
        db.refresh(cf)

        assert cf.currency == "ZAR"
