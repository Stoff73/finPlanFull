"""Database Migration: Add South African Tax Support

This migration adds:
1. TaxProfile table for dual-country tax planning
2. Currency and jurisdiction fields to Product table
3. Currency field to BalanceSheet, ProfitLoss, CashFlow tables
4. Primary/secondary currency fields to User table

Run this migration:
    python migrate_add_sa_tax_support.py
"""

import sys
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "financial_planning.db"


def run_migration():
    """Execute the migration."""
    print(f"Starting migration on database: {DB_PATH}")

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Please run seed_data.py first to create the database.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if migration was already run
        cursor.execute("PRAGMA table_info(tax_profiles)")
        if cursor.fetchall():
            print("⚠️  Migration already applied - tax_profiles table exists")
            response = input("Do you want to re-run the migration? This will drop and recreate tables. (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled")
                return

        print("\n1. Creating tax_profiles table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tax_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,

                -- Domicile Information
                domicile VARCHAR NOT NULL,
                domicile_of_origin VARCHAR,
                domicile_acquired_date DATE,

                -- Deemed Domicile Tracking (UK)
                uk_resident_years_count INTEGER DEFAULT 0,
                uk_deemed_domicile_date DATE,

                -- Tax Residency Status
                tax_residency VARCHAR NOT NULL,
                uk_tax_resident BOOLEAN DEFAULT FALSE,
                sa_tax_resident BOOLEAN DEFAULT FALSE,

                -- Residency Tracking
                uk_years_of_residency INTEGER DEFAULT 0,
                sa_years_of_residency INTEGER DEFAULT 0,

                -- Current Tax Year Residency
                current_tax_year_uk_resident BOOLEAN DEFAULT FALSE,
                current_tax_year_sa_resident BOOLEAN DEFAULT FALSE,

                -- UK Specific Tax Status
                uk_remittance_basis_user BOOLEAN DEFAULT FALSE,
                uk_remittance_basis_charge_paid BOOLEAN DEFAULT FALSE,
                uk_split_year_treatment BOOLEAN DEFAULT FALSE,
                uk_split_year_uk_part_start DATE,
                uk_split_year_uk_part_end DATE,

                -- SA Specific Tax Status
                sa_ordinarily_resident BOOLEAN DEFAULT FALSE,
                sa_year_of_assessment VARCHAR,

                -- Days Tracking (JSON)
                uk_days_by_tax_year TEXT,  -- JSON
                sa_days_by_tax_year TEXT,  -- JSON

                -- Statutory Residence Test (UK)
                uk_srt_automatic_uk_resident BOOLEAN DEFAULT FALSE,
                uk_srt_automatic_non_resident BOOLEAN DEFAULT FALSE,
                uk_srt_sufficient_ties TEXT,  -- JSON

                -- SA Physical Presence Test
                sa_physical_presence_test_met BOOLEAN DEFAULT FALSE,
                sa_days_current_year INTEGER DEFAULT 0,
                sa_days_last_5_years_total INTEGER DEFAULT 0,

                -- Treaty Tie-Breaker
                treaty_tie_breaker_country VARCHAR,
                treaty_tie_breaker_reason VARCHAR,

                -- Migration History
                migration_history TEXT,  -- JSON

                -- Future Migration Plans
                planning_to_relocate BOOLEAN DEFAULT FALSE,
                planned_relocation_country VARCHAR,
                planned_relocation_date DATE,
                planned_relocation_reason VARCHAR,

                -- Review Dates
                last_residency_review_date DATE,
                next_review_due_date DATE,

                -- Metadata
                notes TEXT,
                professional_advice_received BOOLEAN DEFAULT FALSE,
                advisor_name VARCHAR,
                advisor_contact VARCHAR,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("   ✓ tax_profiles table created")

        # 2. Add currency fields to users table
        print("\n2. Adding currency fields to users table...")

        # Check if columns exist
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'primary_currency' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN primary_currency VARCHAR DEFAULT 'GBP'")
            print("   ✓ Added primary_currency column")
        else:
            print("   ⚠️  primary_currency column already exists")

        if 'secondary_currency' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN secondary_currency VARCHAR")
            print("   ✓ Added secondary_currency column")
        else:
            print("   ⚠️  secondary_currency column already exists")

        # 3. Add currency and jurisdiction to products table
        print("\n3. Adding currency and jurisdiction fields to products table...")

        cursor.execute("PRAGMA table_info(products)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'currency' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN currency VARCHAR DEFAULT 'GBP'")
            print("   ✓ Added currency column")
        else:
            print("   ⚠️  currency column already exists")

        if 'jurisdiction' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN jurisdiction VARCHAR DEFAULT 'UK'")
            print("   ✓ Added jurisdiction column")
        else:
            print("   ⚠️  jurisdiction column already exists")

        # 4. Add currency to balance_sheets table
        print("\n4. Adding currency field to balance_sheets table...")

        cursor.execute("PRAGMA table_info(balance_sheets)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'currency' not in columns:
            cursor.execute("ALTER TABLE balance_sheets ADD COLUMN currency VARCHAR DEFAULT 'GBP'")
            print("   ✓ Added currency column to balance_sheets")
        else:
            print("   ⚠️  currency column already exists in balance_sheets")

        # 5. Add currency to profit_loss table
        print("\n5. Adding currency field to profit_loss table...")

        cursor.execute("PRAGMA table_info(profit_loss)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'currency' not in columns:
            cursor.execute("ALTER TABLE profit_loss ADD COLUMN currency VARCHAR DEFAULT 'GBP'")
            print("   ✓ Added currency column to profit_loss")
        else:
            print("   ⚠️  currency column already exists in profit_loss")

        # 6. Add currency to cash_flows table
        print("\n6. Adding currency field to cash_flows table...")

        cursor.execute("PRAGMA table_info(cash_flows)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'currency' not in columns:
            cursor.execute("ALTER TABLE cash_flows ADD COLUMN currency VARCHAR DEFAULT 'GBP'")
            print("   ✓ Added currency column to cash_flows")
        else:
            print("   ⚠️  currency column already exists in cash_flows")

        # Commit all changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("\nSummary:")
        print("  - Created tax_profiles table")
        print("  - Added currency fields to users, products, balance_sheets, profit_loss, cash_flows")
        print("  - Added jurisdiction field to products")

    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("Database Migration: South African Tax Support")
    print("=" * 70)
    run_migration()
    print("\nNext steps:")
    print("  1. Run backend tests: pytest tests/ -v")
    print("  2. Restart backend server")
    print("  3. Verify API endpoints work")
