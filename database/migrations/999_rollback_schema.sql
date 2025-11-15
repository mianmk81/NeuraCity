-- NeuraCity Schema Rollback Script
-- WARNING: This will DROP ALL TABLES and data
-- Use this only for development/testing or when you need to reset the database

-- ============================================================================
-- ROLLBACK INSTRUCTIONS
-- ============================================================================
-- This script performs a complete rollback of the NeuraCity schema.
-- It will:
-- 1. Drop all triggers
-- 2. Drop all functions
-- 3. Drop all tables (with CASCADE to handle foreign keys)
--
-- To execute this rollback:
-- 1. Ensure you have a backup if needed
-- 2. Run this script in Supabase SQL Editor or via psql
-- 3. Re-run 001_initial_schema.sql to recreate the schema

-- ============================================================================
-- DROP TRIGGERS
-- ============================================================================

DROP TRIGGER IF EXISTS update_issues_updated_at ON issues;
DROP TRIGGER IF EXISTS update_contractors_updated_at ON contractors;
DROP TRIGGER IF EXISTS update_work_orders_updated_at ON work_orders;
DROP TRIGGER IF EXISTS update_emergency_queue_updated_at ON emergency_queue;

-- ============================================================================
-- DROP FUNCTIONS
-- ============================================================================

DROP FUNCTION IF EXISTS update_updated_at_column();

-- ============================================================================
-- DROP TABLES (in reverse dependency order)
-- ============================================================================

-- Child tables first (tables with foreign keys)
DROP TABLE IF EXISTS emergency_queue CASCADE;
DROP TABLE IF EXISTS work_orders CASCADE;

-- Independent tables
DROP TABLE IF EXISTS contractors CASCADE;
DROP TABLE IF EXISTS noise_segments CASCADE;
DROP TABLE IF EXISTS traffic_segments CASCADE;
DROP TABLE IF EXISTS mood_areas CASCADE;

-- Parent tables last
DROP TABLE IF EXISTS issues CASCADE;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- After running this script, verify all tables are dropped:
-- SELECT table_name
-- FROM information_schema.tables
-- WHERE table_schema = 'public'
-- ORDER BY table_name;

-- Expected result: No tables listed (or only Supabase system tables)

-- ============================================================================
-- NEXT STEPS
-- ============================================================================

-- To recreate the schema:
-- 1. Run: database/migrations/001_initial_schema.sql
-- 2. Run: database/seeds/001_seed_contractors.sql
-- 3. Run: database/seeds/002_seed_synthetic_areas.sql
-- 4. Run: database/seeds/003_seed_synthetic_data.sql
-- 5. Optionally run: python database/seeds/generate_synthetic_data.py

-- ============================================================================
-- Rollback complete
-- ============================================================================
