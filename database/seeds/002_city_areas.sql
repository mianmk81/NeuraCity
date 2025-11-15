-- =====================================================
-- Seed Data: City Areas
-- Define synthetic city areas with coordinates
-- =====================================================

-- These areas will be used for mood analysis and geographic clustering
-- Coordinates are centered around Atlanta, Georgia
-- Base coordinates: ~33.75N, -84.39W (Atlanta, GA)

-- Clear existing mood area data (optional)
-- TRUNCATE TABLE mood_areas CASCADE;

-- Insert city areas with initial neutral mood scores
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count, created_at) VALUES
-- Downtown (business district, high activity)
('DOWNTOWN', 33.7490, -84.3880, 0.15, 150, NOW() - INTERVAL '1 hour'),

-- Midtown (mixed commercial/residential)
('MIDTOWN', 33.7850, -84.3850, -0.05, 180, NOW() - INTERVAL '1 hour'),

-- Campus (university area, generally positive - Georgia Tech area)
('CAMPUS', 33.7750, -84.3960, 0.35, 120, NOW() - INTERVAL '1 hour'),

-- Park District (recreational, positive mood - Piedmont Park area)
('PARK_DISTRICT', 33.7850, -84.3730, 0.55, 90, NOW() - INTERVAL '1 hour'),

-- Residential Zone (quiet suburban area)
('RESIDENTIAL', 33.7600, -84.3800, 0.25, 110, NOW() - INTERVAL '1 hour'),

-- Industrial Zone (lower mood, work-focused)
('INDUSTRIAL', 33.7200, -84.4100, -0.15, 75, NOW() - INTERVAL '1 hour'),

-- Waterfront (mixed, tourism - Chattahoochee area)
('WATERFRONT', 33.7300, -84.4000, 0.40, 95, NOW() - INTERVAL '1 hour'),

-- Arts District (cultural, positive - Little Five Points area)
('ARTS_DISTRICT', 33.7650, -84.3500, 0.30, 85, NOW() - INTERVAL '1 hour');

-- Add some historical mood data (showing mood variations over time)
INSERT INTO mood_areas (area_id, lat, lng, mood_score, post_count, created_at) VALUES
-- Morning rush hour (lower mood)
('DOWNTOWN', 33.7490, -84.3880, -0.10, 200, NOW() - INTERVAL '8 hours'),
('MIDTOWN', 33.7850, -84.3850, -0.25, 220, NOW() - INTERVAL '8 hours'),

-- Lunch time (improved mood)
('DOWNTOWN', 33.7490, -84.3880, 0.20, 180, NOW() - INTERVAL '5 hours'),
('CAMPUS', 33.7750, -84.3960, 0.45, 140, NOW() - INTERVAL '5 hours'),

-- Evening (mixed)
('PARK_DISTRICT', 33.7850, -84.3730, 0.65, 110, NOW() - INTERVAL '2 hours'),
('RESIDENTIAL', 33.7600, -84.3800, 0.40, 130, NOW() - INTERVAL '2 hours'),
('ARTS_DISTRICT', 33.7650, -84.3500, 0.50, 95, NOW() - INTERVAL '2 hours');

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
