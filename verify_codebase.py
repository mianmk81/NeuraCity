#!/usr/bin/env python3
"""
NeuraCity Codebase Verification Script
Checks that all required files exist and are not empty.
"""
import os
from pathlib import Path
from typing import List, Tuple

def check_file(filepath: Path, min_size: int = 10) -> Tuple[bool, str]:
    """
    Check if a file exists and has content.

    Args:
        filepath: Path to the file
        min_size: Minimum file size in bytes

    Returns:
        Tuple of (success, message)
    """
    if not filepath.exists():
        return False, f"[MISS] Missing: {filepath}"

    size = filepath.stat().st_size
    if size < min_size:
        return False, f"[WARN] Empty or too small ({size} bytes): {filepath}"

    return True, f"[OK] ({size} bytes): {filepath}"


def verify_database() -> List[Tuple[bool, str]]:
    """Verify database files."""
    results = []
    base = Path("database")

    files = [
        base / "schema.sql",
        base / "setup.py",
        base / "verify.py",
        base / "config.py",
        base / "requirements.txt",
        base / ".env.example",
        base / "README.md",
        base / "SCHEMA.md",
        base / "seeds" / "001_contractors.sql",
        base / "seeds" / "002_city_areas.sql",
        base / "seeds" / "003_initial_data.sql",
        base / "seeds" / "generate_data.py",
    ]

    for file in files:
        results.append(check_file(file))

    return results


def verify_backend() -> List[Tuple[bool, str]]:
    """Verify backend files."""
    results = []
    base = Path("backend")

    # Core files
    files = [
        base / "app" / "main.py",
        base / "app" / "core" / "config.py",
        base / "app" / "core" / "database.py",
        base / "app" / "core" / "dependencies.py",
        base / "requirements.txt",
        base / ".env.example",
        base / "run.py",
        base / "README.md",
    ]

    # Schemas
    schemas = [
        "issue.py", "mood.py", "traffic.py",
        "noise.py", "routing.py", "admin.py"
    ]
    for schema in schemas:
        files.append(base / "app" / "api" / "schemas" / schema)

    # Endpoints
    endpoints = [
        "issues.py", "mood.py", "traffic.py",
        "noise.py", "routing.py", "admin.py"
    ]
    for endpoint in endpoints:
        files.append(base / "app" / "api" / "endpoints" / endpoint)

    # Services
    services = [
        "supabase_service.py", "image_service.py", "scoring_service.py",
        "routing_service.py", "gemini_service.py", "mood_analysis.py",
        "action_engine.py"
    ]
    for service in services:
        files.append(base / "app" / "services" / service)

    # Utils
    utils = ["validators.py", "helpers.py"]
    for util in utils:
        files.append(base / "app" / "utils" / util)

    for file in files:
        results.append(check_file(file))

    return results


def verify_frontend() -> List[Tuple[bool, str]]:
    """Verify frontend files."""
    results = []
    base = Path("frontend")

    files = [
        base / "package.json",
        base / "vite.config.js",
        base / "tailwind.config.js",
        base / "postcss.config.js",
        base / "index.html",
        base / ".env.example",
        base / "README.md",
        base / "src" / "main.jsx",
        base / "src" / "App.jsx",
        base / "src" / "index.css",
    ]

    # Pages
    pages = ["Home.jsx", "ReportIssue.jsx", "PlanRoute.jsx", "MoodMap.jsx", "Admin.jsx"]
    for page in pages:
        files.append(base / "src" / "pages" / page)

    # Components
    components = [
        "ImageUpload.jsx", "GPSCapture.jsx", "IssueForm.jsx",
        "Map2D.jsx", "RouteCard.jsx", "NoiseLegend.jsx",
        "MoodLegend.jsx", "WorkOrderCard.jsx", "Navbar.jsx"
    ]
    for comp in components:
        files.append(base / "src" / "components" / comp)

    # Lib files
    libs = ["api.js", "helpers.js"]
    for lib in libs:
        files.append(base / "src" / "lib" / lib)

    for file in files:
        results.append(check_file(file))

    return results


def main():
    """Main verification function."""
    print("=" * 70)
    print("NEURACITY CODEBASE VERIFICATION")
    print("=" * 70)
    print("\nChecking that all required files exist and have content...\n")

    all_results = []

    # Database
    print("[DATABASE FILES]")
    print("-" * 70)
    db_results = verify_database()
    all_results.extend(db_results)
    for success, msg in db_results:
        print(msg)

    # Backend
    print("\n[BACKEND FILES]")
    print("-" * 70)
    backend_results = verify_backend()
    all_results.extend(backend_results)
    for success, msg in backend_results:
        print(msg)

    # Frontend
    print("\n[FRONTEND FILES]")
    print("-" * 70)
    frontend_results = verify_frontend()
    all_results.extend(frontend_results)
    for success, msg in frontend_results:
        print(msg)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total = len(all_results)
    passed = sum(1 for success, _ in all_results if success)
    failed = total - passed

    print(f"\nTotal files checked: {total}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")

    if failed == 0:
        print("\n" + "=" * 70)
        print("SUCCESS: ALL FILES PRESENT AND COMPLETE!")
        print("=" * 70)
        print("\nYour NeuraCity codebase is ready to use!")
        print("\nNext steps:")
        print("1. Read GETTING_STARTED.md for setup instructions")
        print("2. Configure your .env files with API keys")
        print("3. Run python test_integration.py to verify integration")
        print("4. Start the backend and frontend servers")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("WARNING: SOME FILES ARE MISSING OR EMPTY")
        print("=" * 70)
        print("\nPlease check the failed files above.")
        print("You may need to regenerate or re-download the codebase.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
