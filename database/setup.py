#!/usr/bin/env python3
"""
NeuraCity Database Setup Script

Runs all migrations and seeds in the correct order to set up a complete database.

Usage:
    python setup.py [--skip-seeds] [--skip-schema]
"""

import os
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


def read_sql_file(file_path: Path) -> str:
    """Read SQL file contents"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Failed to read {file_path}: {e}")


def execute_sql(supabase: Client, sql: str, description: str) -> bool:
    """
    Execute SQL against Supabase

    Note: Supabase doesn't provide direct SQL execution via the client library.
    This function provides the SQL that needs to be executed via the Supabase SQL Editor.
    """
    print(f"\n{'=' * 60}")
    print(f"SQL to execute: {description}")
    print(f"{'=' * 60}")
    print("\nPlease execute the following SQL in your Supabase SQL Editor:")
    print(f"\n{sql}\n")
    print(f"{'=' * 60}")

    response = input("\nHave you executed this SQL? (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def execute_sql_file(supabase: Client, file_path: Path, description: str) -> bool:
    """Execute a SQL file"""
    print(f"\n📄 Processing: {file_path.name}")
    sql = read_sql_file(file_path)
    return execute_sql(supabase, sql, description)


def verify_tables(supabase: Client) -> bool:
    """Verify that all tables exist and are accessible"""
    print("\n🔍 Verifying database tables...")

    tables = [
        'issues',
        'mood_areas',
        'traffic_segments',
        'noise_segments',
        'contractors',
        'work_orders',
        'emergency_queue'
    ]

    all_good = True

    for table_name in tables:
        try:
            result = supabase.table(table_name).select('id').limit(1).execute()
            print(f"  ✓ {table_name} - accessible")
        except Exception as e:
            print(f"  ✗ {table_name} - error: {e}")
            all_good = False

    return all_good


def count_records(supabase: Client) -> dict:
    """Count records in each table"""
    print("\n📊 Counting records in tables...")

    tables = [
        'issues',
        'mood_areas',
        'traffic_segments',
        'noise_segments',
        'contractors',
        'work_orders',
        'emergency_queue'
    ]

    counts = {}

    for table_name in tables:
        try:
            result = supabase.table(table_name).select('id', count='exact').execute()
            count = result.count if hasattr(result, 'count') else len(result.data)
            counts[table_name] = count
            print(f"  {table_name:<20} {count:>6} records")
        except Exception as e:
            print(f"  {table_name:<20} Error: {e}")
            counts[table_name] = -1

    return counts


def main():
    parser = argparse.ArgumentParser(
        description='Set up NeuraCity database with schema and seed data'
    )
    parser.add_argument(
        '--skip-schema',
        action='store_true',
        help='Skip schema creation (use if schema already exists)'
    )
    parser.add_argument(
        '--skip-seeds',
        action='store_true',
        help='Skip seed data insertion'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify tables and count records, do not run setup'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("NeuraCity Database Setup")
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
        verify_tables(supabase)
        count_records(supabase)
        sys.exit(0)

    # Get script directory
    script_dir = Path(__file__).parent
    seeds_dir = script_dir / 'seeds'

    print("\n" + "=" * 60)
    print("IMPORTANT: Supabase SQL Execution")
    print("=" * 60)
    print("The Python Supabase client doesn't support raw SQL execution.")
    print("This script will display SQL that you need to run manually in")
    print("the Supabase SQL Editor (https://app.supabase.com)")
    print("\nSteps:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste each SQL block when prompted")
    print("4. Execute the SQL")
    print("5. Return here and confirm execution")
    print("=" * 60)

    proceed = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if proceed not in ['yes', 'y']:
        print("Setup cancelled.")
        sys.exit(0)

    # Step 1: Create schema
    if not args.skip_schema:
        print("\n" + "=" * 60)
        print("STEP 1: Create Database Schema")
        print("=" * 60)

        schema_file = script_dir / 'schema.sql'
        if not schema_file.exists():
            print(f"✗ Schema file not found: {schema_file}")
            sys.exit(1)

        success = execute_sql_file(
            supabase,
            schema_file,
            "Create all tables, indexes, triggers, and views"
        )

        if not success:
            print("✗ Schema setup cancelled or failed")
            sys.exit(1)

        print("✓ Schema creation completed")
    else:
        print("\n⏭️  Skipping schema creation")

    # Verify tables exist
    if not verify_tables(supabase):
        print("\n✗ Table verification failed. Please check the schema execution.")
        sys.exit(1)

    # Step 2: Load seed data
    if not args.skip_seeds:
        print("\n" + "=" * 60)
        print("STEP 2: Load Seed Data")
        print("=" * 60)

        seed_files = [
            ('001_contractors.sql', 'Insert contractor data'),
            ('002_city_areas.sql', 'Insert city areas and initial mood data'),
            ('003_initial_data.sql', 'Insert sample traffic, noise, and issue data')
        ]

        for filename, description in seed_files:
            seed_file = seeds_dir / filename
            if not seed_file.exists():
                print(f"⚠️  Seed file not found: {seed_file} (skipping)")
                continue

            success = execute_sql_file(supabase, seed_file, description)

            if not success:
                print(f"⚠️  Skipped: {filename}")
                continue

            print(f"✓ Loaded: {filename}")
    else:
        print("\n⏭️  Skipping seed data")

    # Step 3: Summary
    print("\n" + "=" * 60)
    print("Setup Summary")
    print("=" * 60)

    counts = count_records(supabase)

    print("\n" + "=" * 60)
    print("✓ Database setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run the data generator to create synthetic data:")
    print("   python seeds/generate_data.py --days=7")
    print("\n2. Verify the database:")
    print("   python verify.py")
    print("\n3. Start building your backend API!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
