"""
Populate demouser with realistic mock data based on mockData.md

Profile:
- Dual citizenship (SA/UK)
- Born in SA, lives in UK
- Wife + 2 kids
- UK employment £140k/year + SA rental income
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.tax_profile import TaxProfile
from app.models.income_source import IncomeSource
from app.models.product import Product
from datetime import datetime, date


def get_demouser(db: Session) -> User:
    """Get the demouser"""
    user = db.query(User).filter(User.username == "demouser").first()
    if not user:
        raise Exception("demouser not found! Run seed_data.py first.")
    return user


def clear_existing_data(db: Session, user_id: int):
    """Clear existing mock data for demouser"""
    print("Clearing existing data...")

    # Delete existing data
    db.query(TaxProfile).filter(TaxProfile.user_id == user_id).delete()
    db.query(IncomeSource).filter(IncomeSource.user_id == user_id).delete()
    db.query(Product).filter(Product.user_id == user_id).delete()

    db.commit()
    print("✓ Existing data cleared")


def populate_tax_profile(db: Session, user_id: int):
    """Create tax profile for dual-citizenship UK/SA resident"""
    print("\nPopulating Tax Profile...")

    tax_profile = TaxProfile(
        user_id=user_id,
        domicile="SA",  # Born in South Africa
        domicile_of_origin="SA",
        tax_residency="dual_resident",  # Lives in UK but has SA ties
        uk_tax_resident=True,
        sa_tax_resident=True,  # SA rental income makes him SA tax resident
        uk_years_of_residency=12,  # Living in UK for 12 years
        sa_years_of_residency=25,  # Born in SA, lived there 25 years before moving
        current_tax_year_uk_resident=True,
        current_tax_year_sa_resident=True,
        uk_remittance_basis_user=False,
        uk_remittance_basis_charge_paid=False,
        uk_split_year_treatment=False,
        sa_ordinarily_resident=True,
        sa_days_current_year=90,  # Visits SA for rental property
        uk_srt_automatic_uk_resident=True,  # Lives in UK full-time
        sa_physical_presence_test_met=True,
        treaty_tie_breaker_country="UK",  # UK is primary residence
        treaty_tie_breaker_reason="permanent_home",
        notes="Dual citizenship (SA/UK). Born in SA, moved to UK 12 years ago. "
              "Maintains SA tax residency due to rental property income."
    )

    db.add(tax_profile)
    db.commit()
    print("✓ Tax Profile created")


def populate_income_sources(db: Session, user_id: int):
    """Create income sources: UK employment + SA rental"""
    print("\nPopulating Income Sources...")

    # UK Employment Income
    uk_employment = IncomeSource(
        user_id=user_id,
        name="UK Employment Salary",
        tax_year="2024/25",
        income_type="employment",
        amount=140000.00,
        currency="GBP",
        source_country="UK",
        uk_taxable=True,
        sa_taxable=False,  # UK employment not taxable in SA (treaty)
        uk_tax_deducted=42000.00,  # Approx 30% tax (40% rate taxpayer)
        sa_tax_deducted=0.00,
        treaty_relief_applicable=False,  # No relief needed as not taxable in SA
        treaty_relief_percentage=0.0,
        notes="UK employment income - £140,000/year",
        is_active=True,
        is_recurring=True
    )

    # SA Rental Income
    sa_rental = IncomeSource(
        user_id=user_id,
        name="South Africa Rental Property",
        tax_year="2024/25",
        income_type="rental",
        amount=450000.00,  # ZAR 450,000 per year
        currency="ZAR",
        source_country="SA",
        uk_taxable=True,
        sa_taxable=True,
        uk_tax_deducted=0.00,
        sa_tax_deducted=157500.00,  # 35% SA tax
        treaty_relief_applicable=True,
        treaty_relief_percentage=100.0,  # Credit in UK for SA tax paid
        notes="South African rental property income - R450,000/year",
        is_active=True,
        is_recurring=True
    )

    db.add_all([uk_employment, sa_rental])
    db.commit()
    print("✓ Income Sources created (2)")


def populate_protection(db: Session, user_id: int):
    """Create protection products"""
    print("\nPopulating Protection...")

    life_policy = Product(
        user_id=user_id,
        product_type="protection",
        module="protection",
        product_name="Life Insurance Policy",
        provider="Legal & General",
        reference_number="LG-12345678",
        current_value=500000.00,  # Sum assured
        start_date=date(2020, 3, 15),
        maturity_date=date(2045, 3, 15),  # 25 year term
        annual_charge=1.2,  # £85/month = £1020/year ≈ 1.2% of cover
        notes="Life insurance policy. Beneficiary: Wife. NOT in trust. £500k cover, £85/month premium.",
        currency="GBP",
        jurisdiction="UK",
        status="active"
    )

    db.add(life_policy)
    db.commit()
    print("✓ Protection created (1 policy)")


def populate_savings(db: Session, user_id: int):
    """Create savings accounts"""
    print("\nPopulating Savings...")

    # SA Bank Account
    sa_account = Product(
        user_id=user_id,
        product_type="savings",
        module="savings",
        product_name="SA Current Account",
        provider="Standard Bank (SA)",
        reference_number="SA-****5678",
        current_value=300000.00,  # ZAR 300,000
        annual_charge=0.0,
        currency="ZAR",
        jurisdiction="SA",
        notes="South African current account for rental property income. 4.5% interest. R300,000 balance.",
        status="active"
    )

    # UK Current Account
    uk_current = Product(
        user_id=user_id,
        product_type="savings",
        module="savings",
        product_name="UK Current Account",
        provider="Barclays",
        reference_number="UK-****1234",
        current_value=8500.00,
        annual_charge=0.0,
        currency="GBP",
        jurisdiction="UK",
        notes="Primary UK current account. 0.5% interest",
        status="active"
    )

    # Cash ISA
    cash_isa = Product(
        user_id=user_id,
        product_type="savings",
        module="savings",
        product_name="Cash ISA",
        provider="Nationwide",
        reference_number="ISA-****9876",
        current_value=18500.00,
        annual_charge=0.0,
        currency="GBP",
        jurisdiction="UK",
        notes="Cash ISA - tax-free savings. 4.75% interest",
        status="active"
    )

    db.add_all([sa_account, uk_current, cash_isa])
    db.commit()
    print("✓ Savings created (3 accounts)")


def populate_investments(db: Session, user_id: int):
    """Create investment products"""
    print("\nPopulating Investments...")

    # Stocks & Shares ISA
    ss_isa = Product(
        user_id=user_id,
        product_type="investment",
        module="investment",
        product_name="Stocks & Shares ISA",
        provider="Vanguard",
        reference_number="VGISA-****4567",
        current_value=45000.00,
        initial_investment=38000.00,
        annual_charge=0.22,
        performance_ytd=8.5,
        performance_1yr=12.3,
        currency="GBP",
        jurisdiction="UK",
        notes="Stocks & Shares ISA - FTSE Global All Cap. Tax-free wrapper.",
        status="active"
    )

    # Offshore Bond (Tax Wrapper)
    offshore_bond = Product(
        user_id=user_id,
        product_type="investment",
        module="investment",
        product_name="Offshore Bond",
        provider="RL360",
        reference_number="RL-****7890",
        current_value=125000.00,
        initial_investment=100000.00,
        annual_charge=1.35,
        performance_ytd=7.2,
        performance_1yr=10.1,
        currency="GBP",
        jurisdiction="offshore",
        notes="Offshore bond (tax wrapper) - medium risk portfolio. Isle of Man.",
        status="active"
    )

    db.add_all([ss_isa, offshore_bond])
    db.commit()
    print("✓ Investments created (2 products)")


def populate_retirement(db: Session, user_id: int):
    """Create retirement/pension products"""
    print("\nPopulating Retirement...")

    # QROPS (Isle of Man)
    qrops = Product(
        user_id=user_id,
        product_type="pension",
        module="retirement",
        product_name="QROPS",
        provider="Ardan International",
        reference_number="QROPS-****2345",
        current_value=280000.00,
        initial_investment=220000.00,
        annual_charge=1.2,
        performance_ytd=6.8,
        performance_1yr=9.5,
        currency="GBP",
        jurisdiction="offshore",
        notes="QROPS - Qualified Recognised Overseas Pension Scheme. Isle of Man.",
        status="active"
    )

    # UK Occupational Pension
    occupational = Product(
        user_id=user_id,
        product_type="pension",
        module="retirement",
        product_name="UK Occupational Pension",
        provider="Company Pension Scheme",
        reference_number="OCC-****6789",
        current_value=95000.00,
        annual_charge=0.45,
        performance_ytd=7.5,
        performance_1yr=11.2,
        currency="GBP",
        jurisdiction="UK",
        notes="UK occupational pension - employer contributes 10% (£14k), employee matches £14k",
        status="active"
    )

    # UK Personal Pension
    personal = Product(
        user_id=user_id,
        product_type="pension",
        module="retirement",
        product_name="UK Personal Pension",
        provider="Aviva",
        reference_number="PP-****3456",
        current_value=185000.00,
        annual_charge=0.65,
        performance_ytd=8.2,
        performance_1yr=12.8,
        currency="GBP",
        jurisdiction="UK",
        notes="UK personal pension - £25k annual contribution",
        status="active"
    )

    # SA Retirement Annuity
    sa_ra = Product(
        user_id=user_id,
        product_type="pension",
        module="retirement",
        product_name="SA Retirement Annuity",
        provider="Allan Gray",
        reference_number="RA-****8901",
        current_value=700000.00,  # ZAR 700,000
        annual_charge=1.0,
        performance_ytd=5.5,
        performance_1yr=8.9,
        currency="ZAR",
        jurisdiction="SA",
        notes="South African retirement annuity - no longer contributing (moved to UK). R700,000 value.",
        status="active"
    )

    db.add_all([qrops, occupational, personal, sa_ra])
    db.commit()
    print("✓ Retirement created (4 pensions)")


def main():
    """Main function to populate all mock data"""
    print("=" * 60)
    print("POPULATING DEMOUSER WITH MOCK DATA")
    print("=" * 60)

    # Create database session
    db = SessionLocal()

    try:
        # Get demouser
        user = get_demouser(db)
        print(f"\n✓ Found demouser (ID: {user.id})")

        # Clear existing data
        clear_existing_data(db, user.id)

        # Populate all data
        populate_tax_profile(db, user.id)
        populate_income_sources(db, user.id)
        populate_protection(db, user.id)
        populate_savings(db, user.id)
        populate_investments(db, user.id)
        populate_retirement(db, user.id)

        print("\n" + "=" * 60)
        print("✓ ALL MOCK DATA POPULATED SUCCESSFULLY")
        print("=" * 60)
        print("\nSummary:")
        print("  - Tax Profile: Dual SA/UK resident")
        print("  - Income: UK employment £140k + SA rental")
        print("  - Protection: 1 life policy")
        print("  - Savings: 3 accounts (1 SA, 2 UK including Cash ISA)")
        print("  - Investments: 2 products (S&S ISA, Offshore bond)")
        print("  - Retirement: 4 pensions (QROPS, UK occ, UK personal, SA RA)")
        print("\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
