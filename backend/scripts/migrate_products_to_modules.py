#!/usr/bin/env python3
"""
Database Migration Script: Assign Module Field to Products

This script migrates existing products to the new module-based structure by
assigning the appropriate module value based on product_type.

Module Assignment:
- protection → module = 'protection'
- savings/cash → module = 'savings'
- investment → module = 'investment'
- pension → module = 'retirement'

Usage:
    python scripts/migrate_products_to_modules.py [--dry-run]

Options:
    --dry-run: Preview changes without committing to database
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import argparse

# Import database URL from app config
from app.core.config import get_settings

settings = get_settings()


def backup_database(db_path: str):
    """Create a timestamped backup of the database."""
    if not os.path.exists(db_path):
        print(f"⚠️  Warning: Database not found at {db_path}")
        return None

    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to backup database: {e}")
        return None


def ensure_module_column_exists(session):
    """Ensure the module column exists in the products table."""
    print("\n🔧 Checking database schema...")

    try:
        # Try to query the module column
        session.execute(text("SELECT module FROM products LIMIT 1"))
        print("  ✅ Module column exists")
        return True
    except Exception:
        print("  ⚠️  Module column does not exist. Creating it...")
        try:
            # Add the module column
            session.execute(text("""
                ALTER TABLE products
                ADD COLUMN module VARCHAR(50)
            """))
            session.commit()

            # Create index on module column
            try:
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_products_module ON products(module)
                """))
                session.commit()
                print("  ✅ Module column created with index")
            except Exception as idx_error:
                print(f"  ⚠️  Index creation failed (non-critical): {idx_error}")

            return True
        except Exception as e:
            print(f"  ❌ Failed to create module column: {e}")
            session.rollback()
            return False


def validate_migration(session, dry_run=False):
    """Validate the migration logic before applying."""
    print("\n📊 Analyzing current data...")

    # Check current product distribution
    result = session.execute(text("""
        SELECT product_type, COUNT(*) as count, COUNT(module) as with_module
        FROM products
        GROUP BY product_type
        ORDER BY product_type
    """))

    print("\nCurrent Product Distribution:")
    print("=" * 60)
    print(f"{'Product Type':<20} {'Total':<10} {'Has Module':<15}")
    print("-" * 60)

    total_products = 0
    products_needing_migration = 0

    for row in result:
        product_type = row[0] or 'NULL'
        count = row[1]
        with_module = row[2]
        needs_migration = count - with_module

        total_products += count
        products_needing_migration += needs_migration

        print(f"{product_type:<20} {count:<10} {with_module:<15}")

    print("-" * 60)
    print(f"{'TOTAL':<20} {total_products:<10} {total_products - products_needing_migration:<15}")
    print(f"\n📌 Products needing migration: {products_needing_migration}")

    return products_needing_migration


def migrate_products(session, dry_run=False):
    """Execute the migration."""
    print("\n🚀 Starting migration...")

    # Define migration mapping
    migration_mapping = {
        'protection': 'protection',
        'savings': 'savings',
        'cash': 'savings',
        'investment': 'investment',
        'pension': 'retirement'
    }

    updates = {}

    for product_type, module in migration_mapping.items():
        # Count products that need updating
        count_result = session.execute(text(f"""
            SELECT COUNT(*) FROM products
            WHERE product_type = :product_type
            AND (module IS NULL OR module = '')
        """), {"product_type": product_type})

        count = count_result.scalar()

        if count > 0:
            if not dry_run:
                # Execute update
                result = session.execute(text(f"""
                    UPDATE products
                    SET module = :module
                    WHERE product_type = :product_type
                    AND (module IS NULL OR module = '')
                """), {"module": module, "product_type": product_type})

                updated = result.rowcount
                updates[product_type] = updated
                print(f"  ✅ Updated {updated} {product_type} → {module}")
            else:
                updates[product_type] = count
                print(f"  🔍 Would update {count} {product_type} → {module}")

    return updates


def validate_results(session):
    """Validate migration results."""
    print("\n🔍 Validating migration results...")

    # Check for NULL modules
    null_modules = session.execute(text("""
        SELECT COUNT(*) FROM products
        WHERE module IS NULL OR module = ''
    """)).scalar()

    if null_modules > 0:
        print(f"  ⚠️  Warning: {null_modules} products still have NULL module")

        # Show which product types
        result = session.execute(text("""
            SELECT product_type, COUNT(*) FROM products
            WHERE module IS NULL OR module = ''
            GROUP BY product_type
        """))

        print("  Products with NULL module:")
        for row in result:
            print(f"    - {row[0]}: {row[1]} products")

        return False
    else:
        print("  ✅ All products have assigned modules")

    # Show final distribution
    print("\n📊 Final Module Distribution:")
    print("=" * 60)
    print(f"{'Module':<20} {'Count':<10}")
    print("-" * 60)

    result = session.execute(text("""
        SELECT module, COUNT(*) as count
        FROM products
        GROUP BY module
        ORDER BY module
    """))

    for row in result:
        module = row[0] or 'NULL'
        count = row[1]
        print(f"{module:<20} {count:<10}")

    print("=" * 60)

    return True


def main():
    parser = argparse.ArgumentParser(description="Migrate products to module-based structure")
    parser.add_argument('--dry-run', action='store_true', help="Preview changes without committing")
    parser.add_argument('--no-backup', action='store_true', help="Skip database backup")
    args = parser.parse_args()

    print("=" * 60)
    print("📦 Product Module Migration Script")
    print("=" * 60)

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be committed\n")

    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Backup database (SQLite only)
        if not args.no_backup and not args.dry_run:
            if 'sqlite' in settings.DATABASE_URL:
                db_path = settings.DATABASE_URL.replace('sqlite:///', '')
                backup_path = backup_database(db_path)
                if not backup_path:
                    print("⚠️  Proceeding without backup...")

        # Ensure module column exists
        if not ensure_module_column_exists(session):
            print("❌ Cannot proceed without module column. Exiting.")
            return

        # Validate current state
        products_needing_migration = validate_migration(session, dry_run=args.dry_run)

        if products_needing_migration == 0:
            print("\n✅ No products need migration. All products already have modules assigned.")
            return

        # Confirm migration
        if not args.dry_run:
            print("\n⚠️  This will modify the database.")
            confirm = input("Continue? (yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ Migration cancelled")
                return

        # Execute migration
        updates = migrate_products(session, dry_run=args.dry_run)

        if not args.dry_run:
            # Commit changes
            session.commit()
            print("\n✅ Migration committed to database")

            # Validate results
            if validate_results(session):
                print("\n🎉 Migration completed successfully!")
            else:
                print("\n⚠️  Migration completed with warnings")
        else:
            print("\n🔍 Dry run completed. No changes made to database.")
            print(f"\nTo apply changes, run: python {__file__}")

        # Summary
        print("\n" + "=" * 60)
        print("📊 Migration Summary")
        print("=" * 60)
        total_updated = sum(updates.values())
        for product_type, count in updates.items():
            print(f"  {product_type}: {count} products")
        print(f"\nTotal: {total_updated} products {'would be ' if args.dry_run else ''}updated")
        print("=" * 60)

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during migration: {e}")
        print("   Database rolled back. No changes made.")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
