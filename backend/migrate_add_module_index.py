"""
Database Migration: Add module index to products table

This script adds an index on the module column and updates
existing products to have appropriate module assignments.

Run this script once to migrate existing databases.
"""

import sys
from sqlalchemy import create_index, text, Index
from app.database import engine, SessionLocal
from app.models.product import Product
from app.core.config import get_settings

settings = get_settings()


def migrate_add_module_index():
    """Add index to module column in products table."""

    print("=" * 60)
    print("Database Migration: Add module index to products")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Check if index already exists
        result = db.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='products' AND name='ix_products_module'
        """))

        index_exists = result.fetchone() is not None

        if index_exists:
            print("✓ Index on products.module already exists")
        else:
            print("Creating index on products.module...")

            # Create index
            db.execute(text("""
                CREATE INDEX ix_products_module ON products(module)
            """))

            db.commit()
            print("✓ Index created successfully")

        # Update existing products with module assignments
        print("\nUpdating existing products with module assignments...")

        # Count products without module
        unassigned = db.query(Product).filter(Product.module.is_(None)).count()

        if unassigned == 0:
            print("✓ All products already have module assignments")
        else:
            print(f"Found {unassigned} products without module assignment")
            print("Assigning modules based on product_type...")

            # Protection products
            protection_count = db.query(Product).filter(
                Product.product_type == 'protection',
                Product.module.is_(None)
            ).update({Product.module: 'protection'})

            # Savings products
            savings_count = db.query(Product).filter(
                Product.product_type == 'savings',
                Product.module.is_(None)
            ).update({Product.module: 'savings'})

            # Investment products
            investment_count = db.query(Product).filter(
                Product.product_type == 'investment',
                Product.module.is_(None)
            ).update({Product.module: 'investment'})

            # Pension products -> retirement module
            pension_count = db.query(Product).filter(
                Product.product_type == 'pension',
                Product.module.is_(None)
            ).update({Product.module: 'retirement'})

            db.commit()

            print(f"✓ Updated {protection_count} protection products")
            print(f"✓ Updated {savings_count} savings products")
            print(f"✓ Updated {investment_count} investment products")
            print(f"✓ Updated {pension_count} pension products → retirement module")

            total_updated = protection_count + savings_count + investment_count + pension_count
            print(f"\n✓ Total products updated: {total_updated}")

        # Verify migration
        print("\nVerifying migration...")
        total_products = db.query(Product).count()
        assigned_products = db.query(Product).filter(Product.module.isnot(None)).count()

        print(f"Total products: {total_products}")
        print(f"Products with module: {assigned_products}")

        if total_products == assigned_products:
            print("✓ All products have module assignments")
        else:
            print(f"⚠ Warning: {total_products - assigned_products} products still without module")

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during migration: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("\nStarting migration...")
    print(f"Database: {settings.DATABASE_URL}\n")

    response = input("Proceed with migration? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        migrate_add_module_index()
    else:
        print("Migration cancelled")
        sys.exit(0)