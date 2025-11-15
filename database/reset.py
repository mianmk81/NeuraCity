#!/usr/bin/env python3
"""
NeuraCity Database Reset Script

Drops all tables and data to start fresh.
USE WITH CAUTION - This will delete ALL data!

Usage:
    python reset.py [--force]
"""

import sys
import argparse
from pathlib import Path

try:
    from supabase import create_client, Client
    from config import get_config
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


RESET_SQL = """
-- =====================================================
-- NeuraCity Database Reset
-- WARNING: This will delete ALL tables and data!
-- =====================================================

-- Drop views first (they depend on tables)
DROP VIEW IF EXISTS emergency_queue_details CASCADE;
DROP VIEW IF EXISTS pending_work_orders_details CASCADE;
DROP VIEW IF EXISTS active_issues_summary CASCADE;

-- Drop triggers
DROP TRIGGER IF EXISTS update_emergency_queue_updated_at ON emergency_queue;
DROP TRIGGER IF EXISTS update_work_orders_updated_at ON work_orders;
DROP TRIGGER IF EXISTS update_issues_updated_at ON issues;

-- Drop function
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS emergency_queue CASCADE;
DROP TABLE IF EXISTS work_orders CASCADE;
DROP TABLE IF EXISTS contractors CASCADE;
DROP TABLE IF EXISTS noise_segments CASCADE;
DROP TABLE IF EXISTS traffic_segments CASCADE;
DROP TABLE IF EXISTS mood_areas CASCADE;
DROP TABLE IF EXISTS issues CASCADE;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Database reset complete';
    RAISE NOTICE 'All tables, views, triggers, and data have been removed';
    RAISE NOTICE '========================================';
END $$;
"""


def confirm_reset(force: bool = False) -> bool:
    """Confirm with user before proceeding with reset"""
    if force:
        return True

    print("=" * 60)
    print("⚠️  WARNING: DATABASE RESET")
    print("=" * 60)
    print("This will permanently delete:")
    print("  • All tables")
    print("  • All views")
    print("  • All triggers")
    print("  • All data")
    print("\nThis action CANNOT be undone!")
    print("=" * 60)

    response = input("\nAre you absolutely sure? Type 'DELETE ALL DATA' to confirm: ")

    return response == "DELETE ALL DATA"


def execute_reset(supabase: Client) -> bool:
    """Execute the reset SQL"""
    print("\n" + "=" * 60)
    print("Executing Database Reset")
    print("=" * 60)
    print("\nPlease execute the following SQL in your Supabase SQL Editor:")
    print(f"\n{RESET_SQL}\n")
    print("=" * 60)

    response = input("\nHave you executed this SQL? (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def verify_reset(supabase: Client) -> bool:
    """Verify that tables have been dropped"""
    print("\n🔍 Verifying database reset...")

    tables = [
        'issues',
        'mood_areas',
        'traffic_segments',
        'noise_segments',
        'contractors',
        'work_orders',
        'emergency_queue'
    ]

    all_dropped = True

    for table_name in tables:
        try:
            result = supabase.table(table_name).select('id').limit(1).execute()
            print(f"  ⚠️  {table_name} - still exists (reset may not be complete)")
            all_dropped = False
        except Exception:
            print(f"  ✓ {table_name} - successfully dropped")

    return all_dropped


def main():
    parser = argparse.ArgumentParser(
        description='Reset NeuraCity database by dropping all tables and data'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt (dangerous!)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify that tables are dropped, do not execute reset'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("NeuraCity Database Reset")
    print("=" * 60)

    # Load configuration
    try:
        config = get_config()
        print("✓ Configuration loaded successfully")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        sys.exit(1)

    # Connect to Supabase
    try:
        supabase = create_client(config.supabase_url, config.supabase_key)
        print("✓ Connected to Supabase")
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
        sys.exit(1)

    # If verify-only mode, just check tables and exit
    if args.verify_only:
        if verify_reset(supabase):
            print("\n✓ Database is clean (all tables dropped)")
        else:
            print("\n⚠️  Some tables still exist")
        sys.exit(0)

    # Confirm reset
    if not confirm_reset(args.force):
        print("\n✓ Reset cancelled. No changes made.")
        sys.exit(0)

    # Execute reset
    print("\n🗑️  Proceeding with database reset...")

    success = execute_reset(supabase)

    if not success:
        print("✗ Reset cancelled or failed")
        sys.exit(1)

    # Verify reset
    if verify_reset(supabase):
        print("\n" + "=" * 60)
        print("✓ Database reset complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run setup to recreate the database:")
        print("   python setup.py")
        print("=" * 60)
    else:
        print("\n⚠️  Reset may not be complete. Please check manually.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nReset interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
