"""
Database Migration: Add extra_metadata column to users table

This script adds a JSON column 'extra_metadata' to the users table
to store user profile information like age, retirement_age, etc.

Run this script once to migrate existing databases.
"""

import sys
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.core.config import get_settings

settings = get_settings()


def migrate_add_extra_metadata():
    """Add extra_metadata column to users table."""

    print("=" * 60)
    print("Database Migration: Add extra_metadata to users table")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Check if column already exists
        result = db.execute(text("""
            PRAGMA table_info(users)
        """))

        columns = [row[1] for row in result.fetchall()]
        column_exists = 'extra_metadata' in columns

        if column_exists:
            print("✓ Column 'extra_metadata' already exists in users table")
        else:
            print("Adding 'extra_metadata' column to users table...")

            # Add column (SQLite syntax)
            db.execute(text("""
                ALTER TABLE users ADD COLUMN extra_metadata JSON
            """))

            db.commit()
            print("✓ Column 'extra_metadata' added successfully")

        # Verify migration
        print("\nVerifying migration...")
        result = db.execute(text("""
            PRAGMA table_info(users)
        """))

        columns = [row[1] for row in result.fetchall()]
        if 'extra_metadata' in columns:
            print("✓ Column 'extra_metadata' exists in users table")
            print(f"✓ Total columns in users table: {len(columns)}")
        else:
            print("✗ Column 'extra_metadata' NOT found in users table")
            sys.exit(1)

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print("\nNote: The extra_metadata column can store JSON data like:")
        print('  {"age": 40, "retirement_age": 65, "monthly_expenses": 3000}')
        print("\n" + "=" * 60)

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
        migrate_add_extra_metadata()
    else:
        print("Migration cancelled")
        sys.exit(0)
