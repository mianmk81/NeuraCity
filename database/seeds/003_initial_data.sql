-- =====================================================
-- Seed Data: Initial Sample Data
-- Sample traffic, noise, and issue data for testing
-- =====================================================

-- =====================================================
-- TRAFFIC SEGMENTS
-- =====================================================

-- Main Street segments (Downtown corridor)
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
('MAIN_ST_01', 40.7128, -74.0060, 0.75, NOW() - INTERVAL '5 minutes'),
('MAIN_ST_02', 40.7138, -74.0050, 0.80, NOW() - INTERVAL '5 minutes'),
('MAIN_ST_03', 40.7148, -74.0040, 0.65, NOW() - INTERVAL '5 minutes'),
('MAIN_ST_04', 40.7158, -74.0030, 0.70, NOW() - INTERVAL '5 minutes');

-- Broadway segments (Midtown corridor)
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
('BROADWAY_01', 40.7589, -73.9851, 0.85, NOW() - INTERVAL '5 minutes'),
('BROADWAY_02', 40.7599, -73.9841, 0.90, NOW() - INTERVAL '5 minutes'),
('BROADWAY_03', 40.7609, -73.9831, 0.80, NOW() - INTERVAL '5 minutes'),
('BROADWAY_04', 40.7619, -73.9821, 0.75, NOW() - INTERVAL '5 minutes');

-- Campus Drive segments (Lower traffic)
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
('CAMPUS_DR_01', 40.7295, -73.9965, 0.30, NOW() - INTERVAL '5 minutes'),
('CAMPUS_DR_02', 40.7305, -73.9955, 0.25, NOW() - INTERVAL '5 minutes'),
('CAMPUS_DR_03', 40.7315, -73.9945, 0.35, NOW() - INTERVAL '5 minutes');

-- Park Avenue segments (Moderate traffic)
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
('PARK_AVE_01', 40.7812, -73.9665, 0.40, NOW() - INTERVAL '5 minutes'),
('PARK_AVE_02', 40.7822, -73.9655, 0.35, NOW() - INTERVAL '5 minutes'),
('PARK_AVE_03', 40.7832, -73.9645, 0.45, NOW() - INTERVAL '5 minutes');

-- Residential streets (Low traffic)
INSERT INTO traffic_segments (segment_id, lat, lng, congestion, ts) VALUES
('RESI_ST_01', 40.7480, -73.9862, 0.15, NOW() - INTERVAL '5 minutes'),
('RESI_ST_02', 40.7490, -73.9852, 0.20, NOW() - INTERVAL '5 minutes'),
('RESI_ST_03', 40.7500, -73.9842, 0.10, NOW() - INTERVAL '5 minutes');

-- =====================================================
-- NOISE SEGMENTS
-- =====================================================

-- Highway segments (Very loud: 75-85 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
('HIGHWAY_01', 40.7015, -74.0150, 82.5, NOW() - INTERVAL '10 minutes'),
('HIGHWAY_02', 40.7025, -74.0140, 80.0, NOW() - INTERVAL '10 minutes'),
('HIGHWAY_03', 40.7035, -74.0130, 78.5, NOW() - INTERVAL '10 minutes');

-- Main commercial streets (Moderate-loud: 65-75 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
('MAIN_ST_01', 40.7128, -74.0060, 70.5, NOW() - INTERVAL '10 minutes'),
('MAIN_ST_02', 40.7138, -74.0050, 72.0, NOW() - INTERVAL '10 minutes'),
('BROADWAY_01', 40.7589, -73.9851, 73.5, NOW() - INTERVAL '10 minutes'),
('BROADWAY_02', 40.7599, -73.9841, 75.0, NOW() - INTERVAL '10 minutes');

-- Campus area (Quiet: 45-55 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
('CAMPUS_DR_01', 40.7295, -73.9965, 48.5, NOW() - INTERVAL '10 minutes'),
('CAMPUS_DR_02', 40.7305, -73.9955, 50.0, NOW() - INTERVAL '10 minutes'),
('CAMPUS_DR_03', 40.7315, -73.9945, 47.0, NOW() - INTERVAL '10 minutes');

-- Park District (Very quiet: 40-50 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
('PARK_AVE_01', 40.7812, -73.9665, 42.5, NOW() - INTERVAL '10 minutes'),
('PARK_AVE_02', 40.7822, -73.9655, 41.0, NOW() - INTERVAL '10 minutes'),
('PARK_AVE_03', 40.7832, -73.9645, 43.5, NOW() - INTERVAL '10 minutes');

-- Residential streets (Quiet: 45-55 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
('RESI_ST_01', 40.7480, -73.9862, 46.0, NOW() - INTERVAL '10 minutes'),
('RESI_ST_02', 40.7490, -73.9852, 48.5, NOW() - INTERVAL '10 minutes'),
('RESI_ST_03', 40.7500, -73.9842, 44.0, NOW() - INTERVAL '10 minutes');

-- Waterfront (Moderate: 55-65 dB)
INSERT INTO noise_segments (segment_id, lat, lng, noise_db, ts) VALUES
('WATER_01', 40.7061, -74.0087, 58.5, NOW() - INTERVAL '10 minutes'),
('WATER_02', 40.7071, -74.0077, 60.0, NOW() - INTERVAL '10 minutes');

-- =====================================================
-- SAMPLE ISSUES
-- =====================================================

-- Sample pothole issues
INSERT INTO issues (lat, lng, issue_type, description, image_url, severity, urgency, priority, action_type, status, created_at) VALUES
(40.7128, -74.0055, 'pothole', 'Large pothole on Main Street near intersection', 'https://example.com/images/pothole_001.jpg', 0.75, 0.80, 'high', 'work_order', 'open', NOW() - INTERVAL '2 hours'),
(40.7295, -73.9960, 'pothole', 'Medium pothole in campus parking lot', 'https://example.com/images/pothole_002.jpg', 0.50, 0.45, 'medium', 'work_order', 'open', NOW() - INTERVAL '4 hours'),
(40.7480, -73.9860, 'pothole', 'Small pothole on residential street', 'https://example.com/images/pothole_003.jpg', 0.30, 0.35, 'low', 'work_order', 'open', NOW() - INTERVAL '1 day');

-- Sample traffic light issues
INSERT INTO issues (lat, lng, issue_type, description, image_url, severity, urgency, priority, action_type, status, created_at) VALUES
(40.7589, -73.9851, 'traffic_light', 'Traffic signal not working - stuck on red', 'https://example.com/images/signal_001.jpg', 0.85, 0.90, 'critical', 'work_order', 'in_progress', NOW() - INTERVAL '30 minutes'),
(40.7812, -73.9665, 'traffic_light', 'Pedestrian crossing signal bulb out', 'https://example.com/images/signal_002.jpg', 0.55, 0.60, 'medium', 'work_order', 'open', NOW() - INTERVAL '6 hours');

-- Sample accident
INSERT INTO issues (lat, lng, issue_type, description, image_url, severity, urgency, priority, action_type, status, created_at) VALUES
(40.7138, -74.0050, 'accident', 'Two-car collision on Main Street', 'https://example.com/images/accident_001.jpg', 0.95, 0.98, 'critical', 'emergency', 'open', NOW() - INTERVAL '15 minutes');

-- Sample other issues
INSERT INTO issues (lat, lng, issue_type, description, image_url, severity, urgency, priority, action_type, status, created_at) VALUES
(40.7250, -73.9967, 'other', 'Fallen tree blocking sidewalk', 'https://example.com/images/tree_001.jpg', 0.60, 0.70, 'high', 'work_order', 'open', NOW() - INTERVAL '1 hour'),
(40.7061, -74.0087, 'other', 'Graffiti on public building', 'https://example.com/images/graffiti_001.jpg', 0.25, 0.20, 'low', 'monitor', 'open', NOW() - INTERVAL '2 days');

-- =====================================================
-- SAMPLE WORK ORDERS
-- =====================================================

-- Work order for critical traffic light issue
INSERT INTO work_orders (issue_id, contractor_id, material_suggestion, status, created_at)
SELECT
    i.id,
    c.id,
    'LED traffic signal replacement unit (red), electrical wiring kit, junction box, mounting hardware. Estimated repair time: 2-3 hours.',
    'approved',
    NOW() - INTERVAL '25 minutes'
FROM issues i
CROSS JOIN contractors c
WHERE i.issue_type = 'traffic_light'
    AND i.priority = 'critical'
    AND c.specialty = 'traffic_signals'
    AND c.name = 'SignalTech Systems'
LIMIT 1;

-- Work order for high priority pothole
INSERT INTO work_orders (issue_id, contractor_id, material_suggestion, status, created_at)
SELECT
    i.id,
    c.id,
    'Cold patch asphalt mix (200 lbs), asphalt emulsion tack coat, compactor plate rental. Area: approximately 4 sq ft, depth 3 inches.',
    'pending_review',
    NOW() - INTERVAL '1 hour 50 minutes'
FROM issues i
CROSS JOIN contractors c
WHERE i.issue_type = 'pothole'
    AND i.priority = 'high'
    AND c.specialty = 'pothole_repair'
    AND c.name = 'QuickFix Paving Co.'
LIMIT 1;

-- Work order for fallen tree
INSERT INTO work_orders (issue_id, contractor_id, material_suggestion, status, created_at)
SELECT
    i.id,
    c.id,
    'Chain saw, wood chipper, safety equipment, truck for debris removal. Tree appears to be approximately 20ft tall.',
    'pending_review',
    NOW() - INTERVAL '55 minutes'
FROM issues i
CROSS JOIN contractors c
WHERE i.description LIKE '%tree%'
    AND c.specialty = 'landscaping'
LIMIT 1;

-- =====================================================
-- SAMPLE EMERGENCY QUEUE
-- =====================================================

-- Emergency summary for accident
INSERT INTO emergency_queue (issue_id, summary, status, created_at)
SELECT
    id,
    'EMERGENCY REPORT - Two-vehicle collision on Main Street at coordinates 40.7138, -74.0050. Incident reported 15 minutes ago.

SEVERITY: Critical (0.95/1.0)
URGENCY: Extreme (0.98/1.0)

LOCATION: Main Street, high-traffic downtown corridor near intersection

SITUATION: Two-car collision reported with visual evidence. Area currently experiencing high congestion (0.80/1.0). Immediate response recommended.

RECOMMENDED ACTIONS:
1. Dispatch emergency services immediately
2. Deploy traffic control to Main Street
3. Request tow services for vehicle removal
4. Check for injuries and provide medical assistance
5. Clear roadway to restore traffic flow

PRIORITY: CRITICAL - Immediate dispatcher attention required.',
    'pending',
    NOW() - INTERVAL '14 minutes'
FROM issues
WHERE issue_type = 'accident'
LIMIT 1;

-- =====================================================
-- SUMMARY
-- =====================================================

DO $$
DECLARE
    traffic_count INTEGER;
    noise_count INTEGER;
    issue_count INTEGER;
    work_order_count INTEGER;
    emergency_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO traffic_count FROM traffic_segments;
    SELECT COUNT(*) INTO noise_count FROM noise_segments;
    SELECT COUNT(*) INTO issue_count FROM issues;
    SELECT COUNT(*) INTO work_order_count FROM work_orders;
    SELECT COUNT(*) INTO emergency_count FROM emergency_queue;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'Initial data seeded successfully';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Traffic segments: %', traffic_count;
    RAISE NOTICE 'Noise segments: %', noise_count;
    RAISE NOTICE 'Sample issues: %', issue_count;
    RAISE NOTICE 'Work orders: %', work_order_count;
    RAISE NOTICE 'Emergency queue: %', emergency_count;
    RAISE NOTICE '========================================';
END $$;
