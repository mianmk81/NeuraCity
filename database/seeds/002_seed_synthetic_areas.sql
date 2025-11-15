-- NeuraCity Synthetic City Areas Seed Data
-- Defines 5 fictional city areas with coordinates and initial mood data
-- These areas serve as geographic zones for mood analysis and data aggregation

-- Note: Coordinates are fictional but use realistic lat/lng format
-- Base coordinates roughly centered around a fictional city (40.7N, -74.0W)

-- Clear existing data (for re-running seed)
TRUNCATE TABLE mood_areas CASCADE;

-- ============================================================================
-- City Areas with Initial Mood Data
-- ============================================================================

-- MIDTOWN - Commercial and business district
-- High activity, mixed sentiment, prone to traffic stress
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('MIDTOWN', 40.7580, -73.9855, 0.15, 0);

-- DOWNTOWN - Financial and government center
-- High density, professional atmosphere, moderate stress
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('DOWNTOWN', 40.7489, -73.9680, 0.05, 0);

-- CAMPUS - University and educational district
-- Younger demographic, generally positive, events-driven mood swings
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('CAMPUS', 40.7295, -73.9965, 0.45, 0);

-- PARK_DISTRICT - Green spaces and recreational areas
-- Generally positive, family-friendly, weather-dependent mood
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('PARK_DISTRICT', 40.7829, -73.9654, 0.65, 0);

-- RESIDENTIAL_ZONE - Mixed residential neighborhoods
-- Diverse demographics, community-oriented, moderate sentiment
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('RESIDENTIAL_ZONE', 40.7189, -73.9842, 0.25, 0);

-- ============================================================================
-- Area Metadata Reference
-- ============================================================================

-- Area Profiles:
--
-- MIDTOWN (40.7580, -73.9855)
--   - Characteristics: Commercial hub, high foot traffic, busy intersections
--   - Base mood: 0.15 (slightly positive)
--   - Expected issues: Traffic congestion, infrastructure stress
--   - Peak hours: 8-10 AM, 5-7 PM
--
-- DOWNTOWN (40.7489, -73.9680)
--   - Characteristics: Financial district, professional environment
--   - Base mood: 0.05 (neutral to slightly positive)
--   - Expected issues: Rush hour traffic, parking problems
--   - Peak hours: 7-9 AM, 4-6 PM
--
-- CAMPUS (40.7295, -73.9965)
--   - Characteristics: University area, young demographic
--   - Base mood: 0.45 (positive)
--   - Expected issues: Event-based congestion, pedestrian safety
--   - Peak hours: 9-11 AM, 3-5 PM (class times)
--
-- PARK_DISTRICT (40.7829, -73.9654)
--   - Characteristics: Green spaces, recreational areas
--   - Base mood: 0.65 (positive)
--   - Expected issues: Weather-dependent, weekend crowding
--   - Peak hours: Weekends 10 AM-4 PM
--
-- RESIDENTIAL_ZONE (40.7189, -73.9842)
--   - Characteristics: Mixed neighborhoods, community-focused
--   - Base mood: 0.25 (moderately positive)
--   - Expected issues: Local traffic, parking, street maintenance
--   - Peak hours: 7-9 AM, 5-7 PM (commute times)

-- ============================================================================
-- Geographic Boundaries (for reference in application code)
-- ============================================================================

-- These approximate boundaries can be used for area detection:
--
-- MIDTOWN:
--   lat: 40.750 to 40.765, lng: -73.995 to -73.975
--
-- DOWNTOWN:
--   lat: 40.740 to 40.755, lng: -73.978 to -73.958
--
-- CAMPUS:
--   lat: 40.720 to 40.738, lng: -74.006 to -73.986
--
-- PARK_DISTRICT:
--   lat: 40.775 to 40.790, lng: -73.975 to -73.955
--
-- RESIDENTIAL_ZONE:
--   lat: 40.710 to 40.728, lng: -73.994 to -73.974

-- ============================================================================
-- Verification Query
-- ============================================================================

-- View all seeded areas with their initial mood scores
-- SELECT
--   area_id,
--   lat,
--   lng,
--   mood_score,
--   post_count,
--   created_at
-- FROM mood_areas
-- ORDER BY mood_score DESC;

-- ============================================================================
-- Usage Notes
-- ============================================================================

-- 1. Mood scores range from -1 (very negative) to +1 (very positive)
-- 2. Post_count starts at 0 and will increment as synthetic posts are generated
-- 3. The generate_synthetic_data.py script will create time-series mood data
-- 4. New mood_areas entries should be created for time-series tracking
-- 5. These initial entries represent the baseline mood for each area

-- ============================================================================
-- Seed complete
-- ============================================================================
