-- =====================================================
-- Seed Data: City Areas
-- Define synthetic city areas with coordinates
-- =====================================================

-- These areas will be used for mood analysis and geographic clustering
-- Coordinates are centered around a fictional city
-- Base coordinates: ~40.7N, 74.0W (similar to NYC area for realism)

-- Clear existing mood area data (optional)
-- TRUNCATE TABLE mood_areas CASCADE;

-- Insert city areas with initial neutral mood scores
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count, created_at) VALUES
-- Downtown (business district, high activity)
('DOWNTOWN', 40.7128, -74.0060, 0.15, 150, NOW() - INTERVAL '1 hour'),

-- Midtown (mixed commercial/residential)
('MIDTOWN', 40.7589, -73.9851, -0.05, 180, NOW() - INTERVAL '1 hour'),

-- Campus (university area, generally positive)
('CAMPUS', 40.7295, -73.9965, 0.35, 120, NOW() - INTERVAL '1 hour'),

-- Park District (recreational, positive mood)
('PARK_DISTRICT', 40.7812, -73.9665, 0.55, 90, NOW() - INTERVAL '1 hour'),

-- Residential Zone (quiet suburban area)
('RESIDENTIAL', 40.7480, -73.9862, 0.25, 110, NOW() - INTERVAL '1 hour'),

-- Industrial Zone (lower mood, work-focused)
('INDUSTRIAL', 40.7015, -74.0150, -0.15, 75, NOW() - INTERVAL '1 hour'),

-- Waterfront (mixed, tourism)
('WATERFRONT', 40.7061, -74.0087, 0.40, 95, NOW() - INTERVAL '1 hour'),

-- Arts District (cultural, positive)
('ARTS_DISTRICT', 40.7250, -73.9967, 0.30, 85, NOW() - INTERVAL '1 hour');

-- Add some historical mood data (showing mood variations over time)
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count, created_at) VALUES
-- Morning rush hour (lower mood)
('DOWNTOWN', 40.7128, -74.0060, -0.10, 200, NOW() - INTERVAL '8 hours'),
('MIDTOWN', 40.7589, -73.9851, -0.25, 220, NOW() - INTERVAL '8 hours'),

-- Lunch time (improved mood)
('DOWNTOWN', 40.7128, -74.0060, 0.20, 180, NOW() - INTERVAL '5 hours'),
('CAMPUS', 40.7295, -73.9965, 0.45, 140, NOW() - INTERVAL '5 hours'),

-- Evening (mixed)
('PARK_DISTRICT', 40.7812, -73.9665, 0.65, 110, NOW() - INTERVAL '2 hours'),
('RESIDENTIAL', 40.7480, -73.9862, 0.40, 130, NOW() - INTERVAL '2 hours'),
('ARTS_DISTRICT', 40.7250, -73.9967, 0.50, 95, NOW() - INTERVAL '2 hours');

-- Insert summary message
DO $$
DECLARE
    area_count INTEGER;
    unique_areas INTEGER;
BEGIN
    SELECT COUNT(*) INTO area_count FROM mood_areas;
    SELECT COUNT(DISTINCT area_id) INTO unique_areas FROM mood_areas;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'City areas seeded successfully';
    RAISE NOTICE 'Total mood data points: %', area_count;
    RAISE NOTICE 'Unique areas: %', unique_areas;
    RAISE NOTICE '========================================';
END $$;
