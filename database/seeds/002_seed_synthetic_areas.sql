-- NeuraCity Synthetic City Areas Seed Data
-- Defines 5 fictional city areas with coordinates and initial mood data
-- These areas serve as geographic zones for mood analysis and data aggregation

-- Note: Coordinates are for Atlanta, Georgia
-- Base coordinates: 33.75N, -84.39W (Atlanta, GA)

-- Clear existing data (for re-running seed)
TRUNCATE TABLE mood_areas CASCADE;

-- ============================================================================
-- City Areas with Initial Mood Data
-- ============================================================================

-- MIDTOWN - Commercial and business district
-- High activity, mixed sentiment, prone to traffic stress
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('MIDTOWN', 33.7850, -84.3850, 0.15, 0);

-- DOWNTOWN - Financial and government center
-- High density, professional atmosphere, moderate stress
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('DOWNTOWN', 33.7490, -84.3880, 0.05, 0);

-- CAMPUS - University and educational district (Georgia Tech area)
-- Younger demographic, generally positive, events-driven mood swings
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('CAMPUS', 33.7750, -84.3960, 0.45, 0);

-- PARK_DISTRICT - Green spaces and recreational areas (Piedmont Park area)
-- Generally positive, family-friendly, weather-dependent mood
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('PARK_DISTRICT', 33.7850, -84.3730, 0.65, 0);

-- RESIDENTIAL_ZONE - Mixed residential neighborhoods
-- Diverse demographics, community-oriented, moderate sentiment
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count) VALUES
  ('RESIDENTIAL_ZONE', 33.7600, -84.3800, 0.25, 0);

-- ============================================================================
-- Area Metadata Reference
-- ============================================================================

-- Area Profiles:
--
-- MIDTOWN (33.7850, -84.3850)
--   - Characteristics: Commercial hub, high foot traffic, busy intersections
--   - Base mood: 0.15 (slightly positive)
--   - Expected issues: Traffic congestion, infrastructure stress
--   - Peak hours: 8-10 AM, 5-7 PM
--
-- DOWNTOWN (33.7490, -84.3880)
--   - Characteristics: Financial district, professional environment
--   - Base mood: 0.05 (neutral to slightly positive)
--   - Expected issues: Rush hour traffic, parking problems
--   - Peak hours: 7-9 AM, 4-6 PM
--
-- CAMPUS (33.7750, -84.3960)
--   - Characteristics: University area (Georgia Tech), young demographic
--   - Base mood: 0.45 (positive)
--   - Expected issues: Event-based congestion, pedestrian safety
--   - Peak hours: 9-11 AM, 3-5 PM (class times)
--
-- PARK_DISTRICT (33.7850, -84.3730)
--   - Characteristics: Green spaces (Piedmont Park), recreational areas
--   - Base mood: 0.65 (positive)
--   - Expected issues: Weather-dependent, weekend crowding
--   - Peak hours: Weekends 10 AM-4 PM
--
-- RESIDENTIAL_ZONE (33.7600, -84.3800)
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
--   lat: 33.775 to 33.795, lng: -84.395 to -84.375
--
-- DOWNTOWN:
--   lat: 33.740 to 33.758, lng: -84.398 to -84.378
--
-- CAMPUS:
--   lat: 33.765 to 33.785, lng: -84.406 to -84.386
--
-- PARK_DISTRICT:
--   lat: 33.775 to 33.795, lng: -84.383 to -84.363
--
-- RESIDENTIAL_ZONE:
--   lat: 33.750 to 33.770, lng: -84.390 to -84.370

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
