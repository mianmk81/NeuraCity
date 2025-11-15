#!/usr/bin/env python3
"""
NeuraCity Database Verification Script

Verifies that the database is properly set up with all tables and data.

Usage:
    python verify.py [--detailed]
"""

import sys
import argparse
from datetime import datetime

try:
    from supabase import create_client, Client
    from config import get_config
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


def check_table_exists(supabase: Client, table_name: str) -> tuple[bool, int]:
    """
    Check if table exists and count records

    Returns:
        Tuple of (exists, record_count)
    """
    try:
        result = supabase.table(table_name).select('id', count='exact').limit(1).execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        return True, count
    except Exception as e:
        return False, 0


def check_table_structure(supabase: Client, table_name: str, required_columns: list) -> tuple[bool, list]:
    """
    Check if table has required columns

    Returns:
        Tuple of (all_present, missing_columns)
    """
    try:
        # Try to select all required columns
        select_fields = ','.join(required_columns)
        result = supabase.table(table_name).select(select_fields).limit(1).execute()
        return True, []
    except Exception as e:
        # If error, try to identify missing columns
        missing = []
        for col in required_columns:
            try:
                supabase.table(table_name).select(col).limit(1).execute()
            except:
                missing.append(col)
        return len(missing) == 0, missing


def verify_database(supabase: Client, detailed: bool = False) -> dict:
    """
    Verify all database tables and return status

    Returns:
        Dictionary with verification results
    """
    results = {
        'all_tables_exist': True,
        'all_structures_valid': True,
        'has_data': False,
        'tables': {}
    }

    # Define expected table structures
    table_specs = {
        'issues': {
            'required_columns': ['id', 'lat', 'lng', 'issue_type', 'image_url', 'status', 'created_at'],
            'description': 'Citizen-reported infrastructure issues'
        },
        'mood_areas': {
            'required_columns': ['id', 'area_id', 'lat', 'lng', 'mood_score', 'created_at'],
            'description': 'Sentiment analysis by area'
        },
        'traffic_segments': {
            'required_columns': ['id', 'segment_id', 'lat', 'lng', 'congestion', 'ts'],
            'description': 'Traffic congestion data'
        },
        'noise_segments': {
            'required_columns': ['id', 'segment_id', 'lat', 'lng', 'noise_db', 'ts'],
            'description': 'Noise level measurements'
        },
        'contractors': {
            'required_columns': ['id', 'name', 'specialty', 'contact_email', 'has_city_contract'],
            'description': 'Approved contractors'
        },
        'work_orders': {
            'required_columns': ['id', 'issue_id', 'material_suggestion', 'status', 'created_at'],
            'description': 'AI-generated work orders'
        },
        'emergency_queue': {
            'required_columns': ['id', 'issue_id', 'summary', 'status', 'created_at'],
            'description': 'Emergency summaries for accidents'
        }
    }

    print("\n" + "=" * 60)
    print("Database Verification")
    print("=" * 60)

    for table_name, spec in table_specs.items():
        print(f"\n📋 Checking table: {table_name}")
        print(f"   Description: {spec['description']}")

        # Check existence
        exists, count = check_table_exists(supabase, table_name)

        if not exists:
            print(f"   ✗ Table does not exist or is not accessible")
            results['all_tables_exist'] = False
            results['tables'][table_name] = {
                'exists': False,
                'structure_valid': False,
                'record_count': 0
            }
            continue

        print(f"   ✓ Table exists")

        # Check structure
        if detailed:
            structure_valid, missing_cols = check_table_structure(
                supabase,
                table_name,
                spec['required_columns']
            )

            if not structure_valid:
                print(f"   ✗ Missing columns: {', '.join(missing_cols)}")
                results['all_structures_valid'] = False
            else:
                print(f"   ✓ All required columns present")
        else:
            structure_valid = True

        # Record count
        print(f"   📊 Record count: {count:,}")

        if count > 0:
            results['has_data'] = True

        results['tables'][table_name] = {
            'exists': True,
            'structure_valid': structure_valid,
            'record_count': count
        }

    return results


def verify_views(supabase: Client) -> bool:
    """Verify that views are accessible"""
    print("\n" + "=" * 60)
    print("Checking Views")
    print("=" * 60)

    views = [
        'active_issues_summary',
        'pending_work_orders_details',
        'emergency_queue_details'
    ]

    all_good = True

    for view_name in views:
        try:
            result = supabase.table(view_name).select('*').limit(1).execute()
            print(f"   ✓ {view_name} - accessible")
        except Exception as e:
            print(f"   ✗ {view_name} - error: {e}")
            all_good = False

    return all_good


def check_data_quality(supabase: Client) -> dict:
    """Check data quality and consistency"""
    print("\n" + "=" * 60)
    print("Data Quality Checks")
    print("=" * 60)

    checks = {
        'all_passed': True,
        'checks': []
    }

    # Check 1: Issues have valid coordinates
    try:
        result = supabase.table('issues').select('id').or_(
            'lat.gt.90,lat.lt.-90,lng.gt.180,lng.lt.-180'
        ).execute()
        invalid_count = len(result.data)

        if invalid_count > 0:
            print(f"   ⚠️  Found {invalid_count} issues with invalid coordinates")
            checks['all_passed'] = False
        else:
            print(f"   ✓ All issues have valid coordinates")

        checks['checks'].append({
            'name': 'Issue coordinates',
            'passed': invalid_count == 0,
            'details': f'{invalid_count} invalid'
        })
    except Exception as e:
        print(f"   ⚠️  Could not check issue coordinates: {e}")

    # Check 2: Work orders reference existing issues
    try:
        result = supabase.table('work_orders').select('id, issue_id').execute()
        work_orders = result.data

        if work_orders:
            issue_ids = [wo['issue_id'] for wo in work_orders]
            result = supabase.table('issues').select('id').in_('id', issue_ids).execute()
            valid_count = len(result.data)

            if valid_count == len(work_orders):
                print(f"   ✓ All work orders reference valid issues ({valid_count}/{len(work_orders)})")
                checks['checks'].append({
                    'name': 'Work order references',
                    'passed': True,
                    'details': f'{valid_count}/{len(work_orders)} valid'
                })
            else:
                print(f"   ⚠️  Some work orders have invalid issue references ({valid_count}/{len(work_orders)})")
                checks['all_passed'] = False
                checks['checks'].append({
                    'name': 'Work order references',
                    'passed': False,
                    'details': f'{valid_count}/{len(work_orders)} valid'
                })
    except Exception as e:
        print(f"   ⚠️  Could not check work order references: {e}")

    # Check 3: Contractors have valid emails
    try:
        result = supabase.table('contractors').select('id, contact_email').execute()
        contractors = result.data

        invalid_emails = [c for c in contractors if '@' not in c.get('contact_email', '')]

        if len(invalid_emails) > 0:
            print(f"   ⚠️  Found {len(invalid_emails)} contractors with invalid emails")
            checks['all_passed'] = False
        else:
            print(f"   ✓ All contractors have valid email formats")

        checks['checks'].append({
            'name': 'Contractor emails',
            'passed': len(invalid_emails) == 0,
            'details': f'{len(invalid_emails)} invalid'
        })
    except Exception as e:
        print(f"   ⚠️  Could not check contractor emails: {e}")

    return checks


def print_summary(results: dict, views_ok: bool, data_quality: dict):
    """Print verification summary"""
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    total_tables = len(results['tables'])
    existing_tables = sum(1 for t in results['tables'].values() if t['exists'])
    valid_structures = sum(1 for t in results['tables'].values() if t['structure_valid'])
    total_records = sum(t['record_count'] for t in results['tables'].values())

    print(f"\n📊 Tables: {existing_tables}/{total_tables} exist")
    print(f"📐 Structure: {valid_structures}/{total_tables} valid")
    print(f"📈 Total records: {total_records:,}")
    print(f"👁️  Views: {'✓ All accessible' if views_ok else '✗ Some inaccessible'}")
    print(f"✅ Data quality: {'✓ All checks passed' if data_quality['all_passed'] else '⚠️  Some issues found'}")

    # Overall status
    print("\n" + "=" * 60)

    if results['all_tables_exist'] and results['all_structures_valid'] and results['has_data'] and views_ok:
        print("✓ Database is fully set up and ready to use!")
        print("=" * 60)
        return 0
    elif results['all_tables_exist'] and results['all_structures_valid']:
        print("⚠️  Database structure is valid but needs data")
        print("=" * 60)
        print("\nRun the data generator to populate the database:")
        print("  python seeds/generate_data.py --days=7")
        return 1
    else:
        print("✗ Database setup is incomplete")
        print("=" * 60)
        print("\nRun the setup script to create tables:")
        print("  python setup.py")
        return 2


def main():
    parser = argparse.ArgumentParser(
        description='Verify NeuraCity database setup and data'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Perform detailed structure validation'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("NeuraCity Database Verification")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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

    # Run verification
    results = verify_database(supabase, args.detailed)
    views_ok = verify_views(supabase)
    data_quality = check_data_quality(supabase)

    # Print summary and exit
    exit_code = print_summary(results, views_ok, data_quality)
    sys.exit(exit_code)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
