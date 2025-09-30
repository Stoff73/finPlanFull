#!/usr/bin/env python3
"""
Seed data script for Financial Planning Application
Run this to populate the database with sample data for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
from app.database import get_db, engine
from app.models.user import User
from app.models.iht import IHTProfile, Gift, Trust, Asset
from app.models.financial import BalanceSheet, ProfitLoss, CashFlow
from app.models.product import Product, Pension, Investment, Protection
from app.core.security import get_password_hash
from app.db.base import Base

def create_demo_user(db):
    """Create demo user with full seed data if it doesn't exist"""
    existing_user = db.query(User).filter(User.email == "demo@example.com").first()
    if existing_user:
        print("Demo user already exists")
        return existing_user

    demo_user = User(
        username="demouser",
        email="demo@example.com",
        hashed_password=get_password_hash("demo123"),
        full_name="Demo User",
        risk_tolerance="moderate",
        created_at=datetime.utcnow()
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    print(f"Created demo user: {demo_user.username}")
    return demo_user

def create_test_user(db):
    """Create basic test user if it doesn't exist"""
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        print("Test user already exists")
        return existing_user

    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        risk_tolerance="moderate",
        created_at=datetime.utcnow()
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"Created test user: {test_user.username}")
    return test_user

def create_iht_profile(db, user_id):
    """Create IHT profile with sample data"""
    # Check if profile exists
    existing = db.query(IHTProfile).filter(IHTProfile.user_id == user_id).first()
    if existing:
        print("IHT profile already exists")
        return existing

    iht_profile = IHTProfile(
        user_id=user_id,
        estate_value=1750000,
        liabilities=435000,
        net_estate=1315000,
        charitable_gifts=25000
    )
    db.add(iht_profile)
    db.commit()
    db.refresh(iht_profile)

    # Add assets
    assets_data = [
        ("property", 650000, "Main residence in London"),
        ("property", 250000, "Buy-to-let property"),
        ("investments", 450000, "ISAs and general investments"),
        ("cash", 125000, "Savings accounts"),
        ("business", 200000, "Private company shares"),
        ("other", 75000, "Personal belongings and car")
    ]

    for asset_type, value, description in assets_data:
        asset = Asset(
            iht_profile_id=iht_profile.id,
            asset_type=asset_type,
            value=value,
            description=description
        )
        db.add(asset)

    # Add gifts
    gifts_data = [
        ("John (Son)", "child", 50000, date(2021, 6, 15), "cash"),
        ("Sarah (Daughter)", "child", 50000, date(2021, 6, 15), "cash"),
        ("Cancer Research UK", "charity", 25000, date(2023, 12, 1), "cash"),
        ("Emma (Granddaughter)", "other", 10000, date(2022, 9, 1), "cash")
    ]

    for recipient, relationship, amount, gift_date, gift_type in gifts_data:
        gift = Gift(
            iht_profile_id=iht_profile.id,
            recipient=recipient,
            recipient_relationship=relationship,
            amount=amount,
            date=gift_date,
            gift_type=gift_type
        )
        db.add(gift)

    # Add trusts
    trust = Trust(
        iht_profile_id=iht_profile.id,
        trust_name="Family Discretionary Trust",
        trust_type="discretionary",
        value=150000,
        creation_date=date(2020, 1, 1)
    )
    db.add(trust)

    db.commit()
    print("Created IHT profile with assets, gifts, and trusts")
    return iht_profile

def create_financial_statements(db, user_id):
    """Create sample financial statement entries"""

    # Create a simple balance sheet
    existing_bs = db.query(BalanceSheet).filter(
        BalanceSheet.user_id == user_id
    ).first()

    if not existing_bs:
        balance_sheet = BalanceSheet(
            user_id=user_id,
            period_start=date.today() - timedelta(days=365),
            period_end=date.today(),
            cash_and_equivalents=125000,
            investments=450000,
            property=900000,
            other_assets=75000,
            total_assets=1550000,
            current_liabilities=30000,
            long_term_debt=430000,
            total_liabilities=460000,
            net_worth=1090000
        )
        db.add(balance_sheet)

    # Create a simple P&L
    existing_pl = db.query(ProfitLoss).filter(
        ProfitLoss.user_id == user_id
    ).first()

    if not existing_pl:
        profit_loss = ProfitLoss(
            user_id=user_id,
            period_start=date.today() - timedelta(days=365),
            period_end=date.today(),
            salary_income=120000,
            rental_income=18000,
            investment_income=25000,
            other_income=15000,
            total_income=178000,
            housing_expenses=36000,
            transport_expenses=8000,
            food_expenses=12000,
            total_expenses=79600,
            net_income=98400
        )
        db.add(profit_loss)

    # Create simple cash flow
    existing_cf = db.query(CashFlow).filter(
        CashFlow.user_id == user_id
    ).first()

    if not existing_cf:
        cash_flow = CashFlow(
            user_id=user_id,
            period_start=date.today() - timedelta(days=365),
            period_end=date.today(),
            opening_balance=96600,
            income_received=178000,
            operating_expenses_paid=-79600,
            closing_balance=125000
        )
        db.add(cash_flow)

    db.commit()
    print("Created financial statement entries")

def create_products(db, user_id):
    """Create sample financial products"""

    # Pension products
    pension = Pension(
        user_id=user_id,
        product_name="Workplace Pension",
        provider="Aviva",
        product_type="pension",
        current_value=185000,
        contributions_monthly=1500,
        pension_type="defined_contribution",
        employer_contribution=750,
        retirement_age=65,
        projected_value=850000
    )

    existing = db.query(Product).filter(
        Product.user_id == user_id,
        Product.product_name == pension.product_name
    ).first()

    if not existing:
        db.add(pension)

    # Investment products
    investments = [
        {
            "product_name": "Stocks & Shares ISA",
            "provider": "Vanguard",
            "current_value": 85000,
            "contributions_monthly": 500,
            "investment_type": "isa",
            "risk_level": "moderate",
            "annual_return": 0.07
        },
        {
            "product_name": "General Investment Account",
            "provider": "Hargreaves Lansdown",
            "current_value": 125000,
            "contributions_monthly": 1000,
            "investment_type": "gia",
            "risk_level": "moderate",
            "annual_return": 0.065
        }
    ]

    for inv_data in investments:
        existing = db.query(Product).filter(
            Product.user_id == user_id,
            Product.product_name == inv_data["product_name"]
        ).first()

        if not existing:
            investment = Investment(
                user_id=user_id,
                product_type="investment",
                **inv_data
            )
            db.add(investment)

    # Protection products
    protection_products = [
        {
            "product_name": "Life Insurance",
            "provider": "Legal & General",
            "premium_monthly": 85,
            "protection_type": "life",
            "sum_assured": 500000,
            "term_years": 20,
            "beneficiaries": "Spouse and Children"
        },
        {
            "product_name": "Critical Illness Cover",
            "provider": "Vitality",
            "premium_monthly": 120,
            "protection_type": "critical_illness",
            "sum_assured": 250000,
            "term_years": 15,
            "beneficiaries": "Spouse"
        }
    ]

    for prot_data in protection_products:
        existing = db.query(Product).filter(
            Product.user_id == user_id,
            Product.product_name == prot_data["product_name"]
        ).first()

        if not existing:
            protection = Protection(
                user_id=user_id,
                product_type="protection",
                current_value=0,
                **prot_data
            )
            db.add(protection)

    db.commit()
    print("Created financial products")

def main():
    """Main function to run seed data script"""
    print("Starting seed data creation...")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")

    # Get database session
    db = next(get_db())

    try:
        # Create demo user with full seed data
        demo_user = create_demo_user(db)

        # Create IHT profile for demo user
        create_iht_profile(db, demo_user.id)

        # Create financial statements for demo user
        create_financial_statements(db, demo_user.id)

        # Create test user (basic account without seed data)
        test_user = create_test_user(db)

        # Skip products for now - models are complex
        # create_products(db, demo_user.id)

        print("\n" + "="*50)
        print("Seed data created successfully!")
        print("="*50)
        print("\nTest credentials:")
        print("\n1. Demo User (with full seed data):")
        print("  Username: demouser")
        print("  Email: demo@example.com")
        print("  Password: demo123")
        print("\n2. Test User (basic account):")
        print("  Username: testuser")
        print("  Email: test@example.com")
        print("  Password: testpass123")
        print("\nYou can now login and explore the application!")

    except Exception as e:
        print(f"Error creating seed data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()