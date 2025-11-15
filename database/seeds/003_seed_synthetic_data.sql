-- NeuraCity Synthetic Traffic and Noise Data Seed
-- Populates initial traffic and noise segment data for testing
-- This provides baseline data before the Python generator creates time-series data

-- Clear existing data (for re-running seed)
TRUNCATE TABLE traffic_segments CASCADE;
TRUNCATE TABLE noise_segments CASCADE;

-- ============================================================================
-- Traffic Segments
-- Major road segments with initial congestion levels
-- ============================================================================

-- MIDTOWN - High traffic commercial area
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
  -- Main Avenue (North-South)
  ('MIDTOWN_MAIN_N1', 40.7580, -73.9855, 0.65, now()),
  ('MIDTOWN_MAIN_N2', 40.7590, -73.9855, 0.70, now()),
  ('MIDTOWN_MAIN_N3', 40.7600, -73.9855, 0.68, now()),

  -- Cross Street (East-West)
  ('MIDTOWN_CROSS_E1', 40.7580, -73.9865, 0.60, now()),
  ('MIDTOWN_CROSS_E2', 40.7580, -73.9875, 0.55, now()),
  ('MIDTOWN_CROSS_E3', 40.7580, -73.9885, 0.58, now());

-- DOWNTOWN - Financial district
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
  -- Financial Boulevard
  ('DOWNTOWN_FIN_N1', 40.7489, -73.9680, 0.75, now()),
  ('DOWNTOWN_FIN_N2', 40.7499, -73.9680, 0.78, now()),
  ('DOWNTOWN_FIN_N3', 40.7509, -73.9680, 0.72, now()),

  -- Market Street
  ('DOWNTOWN_MKT_E1', 40.7489, -73.9690, 0.68, now()),
  ('DOWNTOWN_MKT_E2', 40.7489, -73.9700, 0.70, now());

-- CAMPUS - University area
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
  -- College Drive
  ('CAMPUS_DRIVE_N1', 40.7295, -73.9965, 0.35, now()),
  ('CAMPUS_DRIVE_N2', 40.7305, -73.9965, 0.30, now()),
  ('CAMPUS_DRIVE_N3', 40.7315, -73.9965, 0.28, now()),

  -- University Circle
  ('CAMPUS_CIRCLE_E1', 40.7295, -73.9975, 0.25, now()),
  ('CAMPUS_CIRCLE_E2', 40.7295, -73.9985, 0.22, now());

-- PARK_DISTRICT - Low traffic recreational areas
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
  -- Park Loop Road
  ('PARK_LOOP_N1', 40.7829, -73.9654, 0.15, now()),
  ('PARK_LOOP_N2', 40.7839, -73.9654, 0.12, now()),
  ('PARK_LOOP_N3', 40.7849, -73.9654, 0.10, now()),

  -- Scenic Drive
  ('PARK_SCENIC_E1', 40.7829, -73.9664, 0.18, now()),
  ('PARK_SCENIC_E2', 40.7829, -73.9674, 0.20, now());

-- RESIDENTIAL_ZONE - Moderate neighborhood traffic
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
  -- Residential Avenue
  ('RESID_AVE_N1', 40.7189, -73.9842, 0.40, now()),
  ('RESID_AVE_N2', 40.7199, -73.9842, 0.38, now()),
  ('RESID_AVE_N3', 40.7209, -73.9842, 0.42, now()),

  -- Neighborhood Street
  ('RESID_ST_E1', 40.7189, -73.9852, 0.35, now()),
  ('RESID_ST_E2', 40.7189, -73.9862, 0.33, now());

-- ============================================================================
-- Noise Segments
-- Road segments with noise level measurements (dB)
-- ============================================================================

-- MIDTOWN - High noise commercial area (70-85 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
  -- Main Avenue (busy commercial)
  ('MIDTOWN_MAIN_N1', 40.7580, -73.9855, 78.5, now()),
  ('MIDTOWN_MAIN_N2', 40.7590, -73.9855, 82.0, now()),
  ('MIDTOWN_MAIN_N3', 40.7600, -73.9855, 80.5, now()),

  -- Cross Street
  ('MIDTOWN_CROSS_E1', 40.7580, -73.9865, 75.0, now()),
  ('MIDTOWN_CROSS_E2', 40.7580, -73.9875, 72.5, now()),
  ('MIDTOWN_CROSS_E3', 40.7580, -73.9885, 74.0, now());

-- DOWNTOWN - Very high noise financial district (75-85 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
  -- Financial Boulevard (heavy traffic)
  ('DOWNTOWN_FIN_N1', 40.7489, -73.9680, 83.0, now()),
  ('DOWNTOWN_FIN_N2', 40.7499, -73.9680, 85.0, now()),
  ('DOWNTOWN_FIN_N3', 40.7509, -73.9680, 81.5, now()),

  -- Market Street
  ('DOWNTOWN_MKT_E1', 40.7489, -73.9690, 79.0, now()),
  ('DOWNTOWN_MKT_E2', 40.7489, -73.9700, 80.5, now());

-- CAMPUS - Moderate noise university area (55-65 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
  -- College Drive
  ('CAMPUS_DRIVE_N1', 40.7295, -73.9965, 58.0, now()),
  ('CAMPUS_DRIVE_N2', 40.7305, -73.9965, 55.5, now()),
  ('CAMPUS_DRIVE_N3', 40.7315, -73.9965, 56.0, now()),

  -- University Circle (pedestrian area)
  ('CAMPUS_CIRCLE_E1', 40.7295, -73.9975, 52.0, now()),
  ('CAMPUS_CIRCLE_E2', 40.7295, -73.9985, 50.5, now());

-- PARK_DISTRICT - Very low noise (40-50 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
  -- Park Loop Road (quiet, nature sounds)
  ('PARK_LOOP_N1', 40.7829, -73.9654, 42.0, now()),
  ('PARK_LOOP_N2', 40.7839, -73.9654, 40.5, now()),
  ('PARK_LOOP_N3', 40.7849, -73.9654, 41.0, now()),

  -- Scenic Drive
  ('PARK_SCENIC_E1', 40.7829, -73.9664, 45.0, now()),
  ('PARK_SCENIC_E2', 40.7829, -73.9674, 46.5, now());

-- RESIDENTIAL_ZONE - Low to moderate noise (50-65 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
  -- Residential Avenue
  ('RESID_AVE_N1', 40.7189, -73.9842, 58.0, now()),
  ('RESID_AVE_N2', 40.7199, -73.9842, 56.5, now()),
  ('RESID_AVE_N3', 40.7209, -73.9842, 60.0, now()),

  -- Neighborhood Street (quieter side streets)
  ('RESID_ST_E1', 40.7189, -73.9852, 52.0, now()),
  ('RESID_ST_E2', 40.7189, -73.9862, 51.5, now());

-- ============================================================================
-- Highway/Interstate Segments - Very high traffic and noise
-- ============================================================================

INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
  ('HIGHWAY_1_N1', 40.7450, -73.9900, 0.85, now()),
  ('HIGHWAY_1_N2', 40.7460, -73.9900, 0.88, now()),
  ('HIGHWAY_1_N3', 40.7470, -73.9900, 0.82, now()),
  ('HIGHWAY_1_N4', 40.7480, -73.9900, 0.87, now());

INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
  ('HIGHWAY_1_N1', 40.7450, -73.9900, 88.0, now()),
  ('HIGHWAY_1_N2', 40.7460, -73.9900, 90.5, now()),
  ('HIGHWAY_1_N3', 40.7470, -73.9900, 87.5, now()),
  ('HIGHWAY_1_N4', 40.7480, -73.9900, 89.0, now());

-- ============================================================================
-- Data Summary and Reference
-- ============================================================================

-- Noise Level Reference:
-- 40-50 dB: Quiet (library, park, residential at night)
-- 50-60 dB: Moderate (normal conversation, residential daytime)
-- 60-70 dB: Noisy (busy office, busy street)
-- 70-80 dB: Loud (heavy traffic, construction)
-- 80-90 dB: Very loud (highway, industrial area)
-- 90+ dB: Extremely loud (subway, heavy machinery)

-- Congestion Level Reference:
-- 0.0-0.2: Free flow
-- 0.2-0.4: Light traffic
-- 0.4-0.6: Moderate traffic
-- 0.6-0.8: Heavy traffic
-- 0.8-1.0: Gridlock/standstill

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Traffic summary by area
-- SELECT
--   SUBSTRING(segment_id FROM '^[^_]+') as area,
--   COUNT(*) as segment_count,
--   ROUND(AVG(congestion)::numeric, 2) as avg_congestion,
--   ROUND(MIN(congestion)::numeric, 2) as min_congestion,
--   ROUND(MAX(congestion)::numeric, 2) as max_congestion
-- FROM traffic_segments
-- GROUP BY SUBSTRING(segment_id FROM '^[^_]+')
-- ORDER BY avg_congestion DESC;

-- Noise summary by area
-- SELECT
--   SUBSTRING(segment_id FROM '^[^_]+') as area,
--   COUNT(*) as segment_count,
--   ROUND(AVG(noise_db)::numeric, 1) as avg_noise_db,
--   ROUND(MIN(noise_db)::numeric, 1) as min_noise_db,
--   ROUND(MAX(noise_db)::numeric, 1) as max_noise_db
-- FROM noise_segments
-- GROUP BY SUBSTRING(segment_id FROM '^[^_]+')
-- ORDER BY avg_noise_db DESC;

-- ============================================================================
-- Seed complete
-- ============================================================================
