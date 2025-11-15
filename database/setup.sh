#!/bin/bash
# NeuraCity Database Setup Script
# This script helps set up the database by guiding through migration and seeding

set -e  # Exit on error

echo "============================================================"
echo "           NeuraCity Database Setup Script"
echo "============================================================"
echo ""

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "ERROR: .env file not found in project root"
    echo ""
    echo "Please create a .env file with the following variables:"
    echo "  SUPABASE_URL=https://xxxxx.supabase.co"
    echo "  SUPABASE_KEY=your_anon_key"
    echo "  SUPABASE_SERVICE_KEY=your_service_role_key"
    echo ""
    exit 1
fi

echo "Step 1: Install Python Dependencies"
echo "------------------------------------------------------------"
echo "Installing required Python packages..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "Step 2: Database Migration"
echo "------------------------------------------------------------"
echo "Please run the following SQL files in your Supabase SQL Editor:"
echo ""
echo "  1. migrations/001_initial_schema.sql - Creates all tables"
echo ""
echo "Press Enter after you've run the migration..."
read

echo "Step 3: Seed Initial Data"
echo "------------------------------------------------------------"
echo "Please run the following SQL files in order:"
echo ""
echo "  1. seeds/001_seed_contractors.sql - 15 contractors"
echo "  2. seeds/002_seed_synthetic_areas.sql - 5 city areas"
echo "  3. seeds/003_seed_synthetic_data.sql - Initial traffic/noise data"
echo ""
echo "Press Enter after you've run all seed files..."
read

echo "Step 4: Generate Synthetic Time-Series Data"
echo "------------------------------------------------------------"
echo "This will generate synthetic data for testing:"
echo "  - Mood data (7 days)"
echo "  - Traffic data (7 days, hourly)"
echo "  - Noise data (7 days, hourly)"
echo "  - Sample issues (20 issues)"
echo ""
read -p "Generate synthetic data now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd seeds
    python generate_synthetic_data.py
    cd ..
    echo "✓ Synthetic data generated"
else
    echo "Skipped synthetic data generation"
    echo "You can run it later with: python database/seeds/generate_synthetic_data.py"
fi

echo ""
echo "============================================================"
echo "               Database Setup Complete!"
echo "============================================================"
echo ""
echo "Next Steps:"
echo "  1. Verify data in Supabase Table Editor"
echo "  2. Test queries in Supabase SQL Editor"
echo "  3. Configure backend to connect to Supabase"
echo ""
echo "Documentation: database/README.md"
echo "Schema Diagram: database/SCHEMA_DIAGRAM.md"
echo ""
