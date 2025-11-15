#!/usr/bin/env python3
"""
NeuraCity Database Connection Test

This script tests the connection to Supabase and verifies the schema.

Requirements:
- pip install supabase python-dotenv

Environment variables required (in .env):
- SUPABASE_URL
- SUPABASE_KEY
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test connection to Supabase and verify schema."""

    print("=" * 70)
    print("NeuraCity Database Connection Test")
    print("=" * 70)
    print()

    # Check environment variables
    print("Step 1: Checking environment variables...")
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url:
        print("  ✗ SUPABASE_URL not found in environment")
        print("  Please set SUPABASE_URL in your .env file")
        return False
    else:
        print(f"  ✓ SUPABASE_URL: {url}")

    if not key:
        print("  ✗ SUPABASE_KEY not found in environment")
        print("  Please set SUPABASE_KEY in your .env file")
        return False
    else:
        print(f"  ✓ SUPABASE_KEY: {key[:20]}...")

    print()

    # Import Supabase
    print("Step 2: Importing Supabase client...")
    try:
        from supabase import create_client, Client
        print("  ✓ Supabase client imported successfully")
    except ImportError:
        print("  ✗ Supabase library not installed")
        print("  Run: pip install supabase")
        return False

    print()

    # Create client
    print("Step 3: Creating Supabase client...")
    try:
        supabase: Client = create_client(url, key)
        print("  ✓ Supabase client created")
    except Exception as e:
        print(f"  ✗ Failed to create client: {e}")
        return False

    print()

    # Test connection by checking each table
    print("Step 4: Verifying database schema...")

    tables = [
        'issues',
        'mood_areas',
        'traffic_segments',
        'noise_segments',
        'contractors',
        'work_orders',
        'emergency_queue'
    ]

    table_status = {}

    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            table_status[table] = {
                'exists': True,
                'row_count': len(result.data)
            }
            print(f"  ✓ {table}: exists")
        except Exception as e:
            table_status[table] = {
                'exists': False,
                'error': str(e)
            }
            print(f"  ✗ {table}: {e}")

    print()

    # Check seeded data
    print("Step 5: Checking seeded data...")

    try:
        contractors = supabase.table('contractors').select('id').execute()
        contractor_count = len(contractors.data)
        print(f"  ✓ Contractors: {contractor_count} rows")

        if contractor_count == 0:
            print("    WARNING: No contractors found. Run seeds/001_seed_contractors.sql")
    except Exception as e:
        print(f"  ✗ Failed to check contractors: {e}")

    try:
        areas = supabase.table('mood_areas').select('id').execute()
        area_count = len(areas.data)
        print(f"  ✓ Mood Areas: {area_count} rows")

        if area_count == 0:
            print("    WARNING: No mood areas found. Run seeds/002_seed_synthetic_areas.sql")
    except Exception as e:
        print(f"  ✗ Failed to check mood areas: {e}")

    try:
        traffic = supabase.table('traffic_segments').select('id').execute()
        traffic_count = len(traffic.data)
        print(f"  ✓ Traffic Segments: {traffic_count} rows")

        if traffic_count == 0:
            print("    WARNING: No traffic data found. Run seeds/003_seed_synthetic_data.sql")
    except Exception as e:
        print(f"  ✗ Failed to check traffic segments: {e}")

    try:
        noise = supabase.table('noise_segments').select('id').execute()
        noise_count = len(noise.data)
        print(f"  ✓ Noise Segments: {noise_count} rows")

        if noise_count == 0:
            print("    WARNING: No noise data found. Run seeds/003_seed_synthetic_data.sql")
    except Exception as e:
        print(f"  ✗ Failed to check noise segments: {e}")

    try:
        issues = supabase.table('issues').select('id').execute()
        issue_count = len(issues.data)
        print(f"  ✓ Issues: {issue_count} rows")

        if issue_count == 0:
            print("    INFO: No issues found (expected for fresh installation)")
    except Exception as e:
        print(f"  ✗ Failed to check issues: {e}")

    print()

    # Summary
    print("=" * 70)
    print("Connection Test Summary")
    print("=" * 70)

    all_exist = all(status['exists'] for status in table_status.values())

    if all_exist:
        print("✓ All tables exist and are accessible")
        print()
        print("Next steps:")
        print("  1. If seed data is missing, run the SQL seed files in Supabase SQL Editor")
        print("  2. Run generate_synthetic_data.py to populate time-series data")
        print("  3. Start building your backend API endpoints")
        print()
        return True
    else:
        print("✗ Some tables are missing or inaccessible")
        print()
        print("Required action:")
        print("  1. Run migrations/001_initial_schema.sql in Supabase SQL Editor")
        print("  2. Verify all tables were created")
        print("  3. Run this test again")
        print()
        return False


if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
