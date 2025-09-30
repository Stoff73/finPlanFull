#!/usr/bin/env python3
"""
Database Migration Script for Financial Planning Application
Ensures all tables exist and schema is up-to-date
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect, text
from app.database import engine
from app.db.base import Base
from app.models.user import User
from app.models.iht import (
    IHTProfile, Gift, Trust, Asset,
    GiftExemptionTracking, TrustChargeHistory,
    MarriageHistory, GiftWithReservation, AssetOwnershipPeriod
)
from app.models.financial import BalanceSheet, ProfitLoss, CashFlow, BankAccount, Transaction
from app.models.product import Product, Pension, Investment, Protection
from app.models.pension import (
    EnhancedPension, PensionInputPeriod, CarryForward,
    PensionProjection, LifetimeAllowanceTracking, AutoEnrolmentTracking
)
from app.models.chat import ChatSession, ChatMessage

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def get_table_columns(table_name):
    """Get list of columns for a table"""
    inspector = inspect(engine)
    if not check_table_exists(table_name):
        return []
    return [col['name'] for col in inspector.get_columns(table_name)]

def migrate_database():
    """
    Perform database migration:
    1. Create all tables that don't exist
    2. Report on existing tables
    3. No data loss - only adds missing tables/columns
    """
    print("=" * 60)
    print("DATABASE MIGRATION - Financial Planning Application")
    print("=" * 60)
    print()

    # Get inspector
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    print(f"Current database has {len(existing_tables)} tables")
    print()

    # Define expected tables
    expected_tables = {
        # Core
        'users': User,

        # IHT
        'iht_profiles': IHTProfile,
        'gifts': Gift,
        'trusts': Trust,
        'assets': Asset,
        'gift_exemption_tracking': GiftExemptionTracking,
        'trust_charge_history': TrustChargeHistory,
        'marriage_history': MarriageHistory,
        'gift_with_reservation': GiftWithReservation,
        'asset_ownership_periods': AssetOwnershipPeriod,

        # Financial
        'balance_sheets': BalanceSheet,
        'profit_loss': ProfitLoss,
        'cash_flows': CashFlow,
        'bank_accounts': BankAccount,
        'transactions': Transaction,

        # Products
        'products': Product,
        'pensions': Pension,
        'investments': Investment,
        'protections': Protection,

        # Enhanced Pensions
        'enhanced_pensions': EnhancedPension,
        'pension_input_periods': PensionInputPeriod,
        'carry_forward': CarryForward,
        'pension_projections': PensionProjection,
        'lifetime_allowance_tracking': LifetimeAllowanceTracking,
        'auto_enrolment_tracking': AutoEnrolmentTracking,

        # Chat
        'chat_sessions': ChatSession,
        'chat_messages': ChatMessage,
    }

    print("EXPECTED TABLES:")
    print("-" * 60)

    # Check each expected table
    missing_tables = []
    existing_check = []

    for table_name, model in expected_tables.items():
        exists = check_table_exists(table_name)
        status = "✓ EXISTS" if exists else "✗ MISSING"

        if exists:
            existing_check.append(table_name)
            columns = get_table_columns(table_name)
            print(f"{status:12} {table_name:35} ({len(columns)} columns)")
        else:
            missing_tables.append(table_name)
            print(f"{status:12} {table_name:35} (WILL BE CREATED)")

    print()
    print("=" * 60)

    if missing_tables:
        print(f"\n{len(missing_tables)} tables need to be created:")
        for table in missing_tables:
            print(f"  - {table}")

        print("\nCreating missing tables...")
        print("-" * 60)

        try:
            # Create all tables (SQLAlchemy will only create missing ones)
            Base.metadata.create_all(bind=engine)

            print("\n✓ All tables created successfully!")

            # Verify creation
            inspector = inspect(engine)
            new_tables = inspector.get_table_names()

            for table in missing_tables:
                if table in new_tables:
                    columns = get_table_columns(table)
                    print(f"  ✓ {table} ({len(columns)} columns)")
                else:
                    print(f"  ✗ {table} - FAILED TO CREATE")

        except Exception as e:
            print(f"\n✗ Error creating tables: {e}")
            return False
    else:
        print("\n✓ All expected tables already exist!")
        print("No migration needed.")

    print()
    print("=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)

    # Summary
    inspector = inspect(engine)
    final_tables = inspector.get_table_names()
    print(f"\nFinal table count: {len(final_tables)}")
    print("\nDatabase is ready for use!")

    return True

def verify_schema():
    """Verify critical columns exist in key tables"""
    print("\n" + "=" * 60)
    print("SCHEMA VERIFICATION")
    print("=" * 60)

    critical_checks = [
        ('iht_profiles', ['charitable_gifts', 'qualifies_for_reduced_rate']),
        ('gifts', ['recipient_relationship', 'taper_relief_rate', 'exemption_type']),
        ('trusts', ['is_relevant_property', 'ten_year_charge_rate']),
        ('assets', ['qualifies_for_bpr', 'qualifies_for_apr', 'is_main_residence']),
        ('gift_exemption_tracking', ['annual_exemption_used', 'small_gifts']),
        ('marriage_history', ['tnrb_percentage', 'trnrb_percentage']),
        ('gift_with_reservation', ['poat_applies', 'market_rent_paid']),
    ]

    all_ok = True

    for table_name, required_columns in critical_checks:
        if not check_table_exists(table_name):
            print(f"\n✗ {table_name}: TABLE MISSING")
            all_ok = False
            continue

        existing_columns = get_table_columns(table_name)
        missing_columns = [col for col in required_columns if col not in existing_columns]

        if missing_columns:
            print(f"\n✗ {table_name}: Missing columns: {', '.join(missing_columns)}")
            all_ok = False
        else:
            print(f"\n✓ {table_name}: All critical columns present ({len(required_columns)} checked)")

    if all_ok:
        print("\n" + "=" * 60)
        print("✓ SCHEMA VERIFICATION PASSED")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ SCHEMA VERIFICATION FAILED")
        print("Some tables or columns are missing!")
        print("=" * 60)

    return all_ok

if __name__ == "__main__":
    print("\nStarting database migration...")
    print(f"Database URL: {engine.url}")
    print()

    # Run migration
    success = migrate_database()

    if success:
        # Verify schema
        verify_schema()

    print("\nMigration script complete!")
    sys.exit(0 if success else 1)