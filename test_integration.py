#!/usr/bin/env python3
"""
NeuraCity Integration Test
Tests that database and backend are properly integrated and working.
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_environment_variables():
    """Test that required environment variables are set."""
    print("=" * 60)
    print("1. Testing Environment Variables")
    print("=" * 60)

    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "GEMINI_API_KEY"
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            print(f"❌ {var}: Not set")
        else:
            value = os.getenv(var)
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {masked}")

    if missing:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        print("Please create a .env file in backend/ directory with these variables.")
        return False

    print("\n✅ All required environment variables are set!")
    return True


def test_backend_imports():
    """Test that backend modules can be imported."""
    print("\n" + "=" * 60)
    print("2. Testing Backend Imports")
    print("=" * 60)

    try:
        from app.core.config import get_settings
        print("✅ Config module imported")

        from app.core.database import get_supabase_client
        print("✅ Database module imported")

        from app.services.supabase_service import SupabaseService
        print("✅ Supabase service imported")

        from app.main import app
        print("✅ Main FastAPI app imported")

        print("\n✅ All backend modules imported successfully!")
        return True
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False


def test_database_connection():
    """Test that we can connect to Supabase."""
    print("\n" + "=" * 60)
    print("3. Testing Database Connection")
    print("=" * 60)

    try:
        from app.core.database import get_supabase_client

        client = get_supabase_client()
        print("✅ Supabase client created")

        # Try a simple query
        response = client.table("contractors").select("id").limit(1).execute()
        print("✅ Successfully queried database")

        print("\n✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"\n❌ Database connection error: {e}")
        print("\nMake sure:")
        print("1. Your Supabase project is created")
        print("2. The schema has been created (run database/schema.sql)")
        print("3. Your SUPABASE_URL and SUPABASE_KEY are correct")
        return False


def test_database_tables():
    """Test that all required tables exist."""
    print("\n" + "=" * 60)
    print("4. Testing Database Tables")
    print("=" * 60)

    required_tables = [
        "issues",
        "mood_areas",
        "traffic_segments",
        "noise_segments",
        "contractors",
        "work_orders",
        "emergency_queue"
    ]

    try:
        from app.core.database import get_supabase_client

        client = get_supabase_client()
        missing_tables = []

        for table in required_tables:
            try:
                client.table(table).select("id").limit(1).execute()
                print(f"✅ Table '{table}' exists")
            except Exception:
                print(f"❌ Table '{table}' not found")
                missing_tables.append(table)

        if missing_tables:
            print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
            print("Please run database/schema.sql in your Supabase SQL Editor")
            return False

        print("\n✅ All required tables exist!")
        return True
    except Exception as e:
        print(f"\n❌ Error checking tables: {e}")
        return False


def test_backend_services():
    """Test that backend services work."""
    print("\n" + "=" * 60)
    print("5. Testing Backend Services")
    print("=" * 60)

    try:
        from app.core.database import get_supabase_client
        from app.services.supabase_service import SupabaseService
        import asyncio

        client = get_supabase_client()
        service = SupabaseService(client)

        # Test getting contractors
        async def test_get_contractors():
            contractors = await service.get_contractors()
            return contractors

        contractors = asyncio.run(test_get_contractors())
        print(f"✅ SupabaseService works (found {len(contractors)} contractors)")

        if len(contractors) == 0:
            print("\n⚠️  No contractors found in database")
            print("Run: python database/seeds/generate_data.py")
            print("Or manually run: database/seeds/001_contractors.sql")

        print("\n✅ Backend services are working!")
        return True
    except Exception as e:
        print(f"\n❌ Service error: {e}")
        return False


def test_fastapi_app():
    """Test that FastAPI app can start."""
    print("\n" + "=" * 60)
    print("6. Testing FastAPI Application")
    print("=" * 60)

    try:
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        print("✅ Root endpoint works")

        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        print("✅ Health endpoint works")

        # Test API docs
        response = client.get("/docs")
        assert response.status_code == 200
        print("✅ API docs accessible")

        print("\n✅ FastAPI application is working!")
        return True
    except Exception as e:
        print(f"\n❌ FastAPI error: {e}")
        return False


def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("NEURACITY INTEGRATION TEST")
    print("=" * 60)
    print("\nThis script tests that the database and backend are")
    print("properly integrated and ready to run.\n")

    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / "backend" / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Loaded environment from: {env_path}\n")
        else:
            print(f"⚠️  No .env file found at: {env_path}")
            print("Please create one from .env.example\n")
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping .env loading\n")

    results = []

    # Run tests
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("Backend Imports", test_backend_imports()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Database Tables", test_database_tables()))
    results.append(("Backend Services", test_backend_services()))
    results.append(("FastAPI Application", test_fastapi_app()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour NeuraCity backend and database are fully integrated!")
        print("\nTo start the backend server:")
        print("  cd backend")
        print("  python run.py")
        print("\nThen visit: http://localhost:8000/docs")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("⚠️  SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the failed tests before running the backend.")
        print("See error messages above for details.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
