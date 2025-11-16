-- =====================================================
-- Migration 002: Example Queries
-- Quick reference for common queries on new tables
-- =====================================================

-- =====================================================
-- GAMIFICATION QUERIES
-- =====================================================

-- Get top 10 users on leaderboard
SELECT
    position,
    username,
    total_points,
    rank,
    issues_reported,
    issues_verified,
    last_activity_at
FROM top_users_leaderboard
LIMIT 10;

-- Get user's point history with details
SELECT
    pt.created_at,
    pt.transaction_type,
    pt.points_earned,
    pt.description,
    i.issue_type,
    i.lat,
    i.lng
FROM points_transactions pt
LEFT JOIN issues i ON pt.issue_id = i.id
WHERE pt.user_id = 'USER_ID_HERE'
ORDER BY pt.created_at DESC;

-- Get users by rank
SELECT rank, COUNT(*) as user_count, AVG(total_points) as avg_points
FROM users
GROUP BY rank
ORDER BY
    CASE rank
        WHEN 'diamond' THEN 5
        WHEN 'platinum' THEN 4
        WHEN 'gold' THEN 3
        WHEN 'silver' THEN 2
        WHEN 'bronze' THEN 1
    END DESC;

-- Get most active users in last 7 days
SELECT
    u.username,
    u.rank,
    COUNT(pt.id) as recent_transactions,
    SUM(pt.points_earned) as points_last_week
FROM users u
JOIN points_transactions pt ON u.id = pt.user_id
WHERE pt.created_at >= NOW() - INTERVAL '7 days'
GROUP BY u.id, u.username, u.rank
ORDER BY points_last_week DESC
LIMIT 20;

-- Get transaction type distribution
SELECT
    transaction_type,
    COUNT(*) as transaction_count,
    SUM(points_earned) as total_points_awarded,
    AVG(points_earned) as avg_points_per_transaction
FROM points_transactions
GROUP BY transaction_type
ORDER BY total_points_awarded DESC;

-- Find users close to next rank
SELECT
    username,
    total_points,
    rank,
    CASE rank
        WHEN 'bronze' THEN 500 - total_points
        WHEN 'silver' THEN 2000 - total_points
        WHEN 'gold' THEN 5000 - total_points
        WHEN 'platinum' THEN 10000 - total_points
        ELSE 0
    END as points_to_next_rank
FROM users
WHERE rank != 'diamond'
    AND CASE rank
        WHEN 'bronze' THEN total_points >= 400
        WHEN 'silver' THEN total_points >= 1800
        WHEN 'gold' THEN total_points >= 4500
        WHEN 'platinum' THEN total_points >= 9000
        ELSE false
    END
ORDER BY points_to_next_rank ASC
LIMIT 10;

-- =====================================================
-- ACCIDENT HISTORY QUERIES
-- =====================================================

-- Get all accident hotspots (90 day default)
SELECT
    area_name,
    accident_count,
    avg_severity,
    avg_urgency,
    first_accident,
    most_recent_accident,
    center_lat,
    center_lng
FROM accident_hotspots
ORDER BY accident_count DESC;

-- Get accidents near a specific location (1km radius)
SELECT
    id,
    lat,
    lng,
    severity,
    occurred_at,
    area_name,
    weather_conditions,
    time_of_day,
    distance_meters
FROM get_nearby_accidents(40.7128, -74.0060, 1000)
ORDER BY distance_meters ASC;

-- Accident trends by time of day
SELECT
    time_of_day,
    COUNT(*) as accident_count,
    AVG(severity) as avg_severity,
    AVG(urgency) as avg_urgency
FROM accident_history
WHERE occurred_at >= NOW() - INTERVAL '90 days'
GROUP BY time_of_day
ORDER BY accident_count DESC;

-- Accidents by weather conditions
SELECT
    weather_conditions,
    COUNT(*) as accident_count,
    AVG(severity) as avg_severity,
    COUNT(*) FILTER (WHERE time_of_day = 'night') as night_accidents
FROM accident_history
WHERE occurred_at >= NOW() - INTERVAL '90 days'
GROUP BY weather_conditions
ORDER BY accident_count DESC;

-- Most dangerous intersections (clustering accidents)
SELECT
    ROUND(lat::numeric, 4) as approx_lat,
    ROUND(lng::numeric, 4) as approx_lng,
    COUNT(*) as accident_count,
    AVG(severity) as avg_severity,
    area_name
FROM accident_history
WHERE occurred_at >= NOW() - INTERVAL '180 days'
GROUP BY ROUND(lat::numeric, 4), ROUND(lng::numeric, 4), area_name
HAVING COUNT(*) >= 3
ORDER BY accident_count DESC, avg_severity DESC
LIMIT 20;

-- Recent severe accidents
SELECT
    occurred_at,
    lat,
    lng,
    area_name,
    severity,
    urgency,
    weather_conditions,
    time_of_day,
    description
FROM accident_history
WHERE severity >= 0.7
    AND occurred_at >= NOW() - INTERVAL '30 days'
ORDER BY occurred_at DESC;

-- Accidents during rush hours
SELECT
    area_name,
    COUNT(*) as rush_hour_accidents,
    AVG(severity) as avg_severity
FROM accident_history
WHERE occurred_at >= NOW() - INTERVAL '90 days'
    AND (
        (EXTRACT(HOUR FROM occurred_at) BETWEEN 7 AND 9)
        OR (EXTRACT(HOUR FROM occurred_at) BETWEEN 17 AND 19)
    )
GROUP BY area_name
ORDER BY rush_hour_accidents DESC;

-- =====================================================
-- RISK INDEX QUERIES
-- =====================================================

-- Get all high risk blocks
SELECT
    block_id,
    area_name,
    overall_risk_score,
    crime_score,
    traffic_score,
    accident_count,
    issue_count
FROM high_risk_blocks
ORDER BY overall_risk_score DESC
LIMIT 20;

-- Get risk score for specific location
SELECT
    block_id,
    overall_risk_score,
    distance_meters
FROM get_location_risk_score(40.7589, -73.9851);

-- Compare risk across areas
SELECT
    area_name,
    COUNT(*) as block_count,
    AVG(overall_risk_score) as avg_overall_risk,
    AVG(crime_score) as avg_crime,
    AVG(traffic_score) as avg_traffic,
    AVG(air_quality_score) as avg_air_quality,
    SUM(accident_count) as total_accidents,
    SUM(issue_count) as total_issues
FROM block_risk_scores
GROUP BY area_name
ORDER BY avg_overall_risk DESC;

-- Find blocks with high crime but low other risks (targeted intervention)
SELECT
    block_id,
    area_name,
    lat,
    lng,
    overall_risk_score,
    crime_score,
    traffic_score,
    blight_score
FROM block_risk_scores
WHERE crime_score >= 0.7
    AND traffic_score < 0.5
    AND blight_score < 0.5
ORDER BY crime_score DESC
LIMIT 10;

-- Environmental health risk blocks
SELECT
    block_id,
    area_name,
    air_quality_score,
    noise_score,
    heat_score,
    (air_quality_score + noise_score + heat_score) / 3 as environmental_risk
FROM block_risk_scores
WHERE (air_quality_score + noise_score + heat_score) / 3 >= 0.6
ORDER BY environmental_risk DESC
LIMIT 20;

-- Blocks with many issues but low risk scores (possible data quality issues)
SELECT
    block_id,
    area_name,
    overall_risk_score,
    issue_count,
    accident_count,
    last_updated
FROM block_risk_scores
WHERE issue_count >= 10
    AND overall_risk_score < 0.4
ORDER BY issue_count DESC;

-- Traffic danger blocks
SELECT
    block_id,
    area_name,
    lat,
    lng,
    traffic_score,
    accident_count,
    noise_score
FROM block_risk_scores
WHERE traffic_score >= 0.7
ORDER BY traffic_score DESC, accident_count DESC
LIMIT 20;

-- =====================================================
-- COMBINED ANALYSIS QUERIES
-- =====================================================

-- User engagement correlated with issue resolution
SELECT
    u.username,
    u.total_points,
    u.rank,
    COUNT(DISTINCT pt.id) as total_transactions,
    COUNT(DISTINCT CASE WHEN pt.transaction_type = 'issue_resolved' THEN pt.id END) as issues_resolved,
    COUNT(DISTINCT CASE WHEN pt.transaction_type = 'issue_verified' THEN pt.id END) as issues_verified
FROM users u
LEFT JOIN points_transactions pt ON u.id = pt.user_id
GROUP BY u.id, u.username, u.total_points, u.rank
HAVING COUNT(DISTINCT CASE WHEN pt.transaction_type = 'issue_resolved' THEN pt.id END) >= 5
ORDER BY issues_resolved DESC, u.total_points DESC
LIMIT 20;

-- Accidents in high-risk blocks
SELECT
    brs.block_id,
    brs.area_name,
    brs.overall_risk_score,
    brs.traffic_score,
    COUNT(ah.id) as accidents_in_block,
    AVG(ah.severity) as avg_accident_severity
FROM block_risk_scores brs
LEFT JOIN accident_history ah ON
    ST_DWithin(
        brs.geometry,
        ah.location,
        100  -- 100 meter radius around block center
    )
WHERE ah.occurred_at >= NOW() - INTERVAL '90 days'
GROUP BY brs.block_id, brs.area_name, brs.overall_risk_score, brs.traffic_score
HAVING COUNT(ah.id) >= 2
ORDER BY brs.overall_risk_score DESC, accidents_in_block DESC;

-- Top issue reporters in high-risk areas
SELECT
    u.username,
    u.total_points,
    u.rank,
    COUNT(DISTINCT pt.issue_id) as issues_in_high_risk_areas,
    AVG(brs.overall_risk_score) as avg_area_risk
FROM users u
JOIN points_transactions pt ON u.id = pt.user_id
JOIN issues i ON pt.issue_id = i.id
JOIN block_risk_scores brs ON
    ST_DWithin(
        brs.geometry,
        ST_SetSRID(ST_MakePoint(i.lng, i.lat), 4326)::geography,
        200
    )
WHERE pt.transaction_type = 'issue_report'
    AND brs.overall_risk_score >= 0.6
GROUP BY u.id, u.username, u.total_points, u.rank
HAVING COUNT(DISTINCT pt.issue_id) >= 3
ORDER BY issues_in_high_risk_areas DESC, avg_area_risk DESC
LIMIT 10;

-- Recent activity summary (last 7 days)
SELECT
    'Users' as metric,
    COUNT(DISTINCT id) as count
FROM users
WHERE created_at >= NOW() - INTERVAL '7 days'

UNION ALL

SELECT
    'Points Transactions' as metric,
    COUNT(*) as count
FROM points_transactions
WHERE created_at >= NOW() - INTERVAL '7 days'

UNION ALL

SELECT
    'Accidents Reported' as metric,
    COUNT(*) as count
FROM accident_history
WHERE occurred_at >= NOW() - INTERVAL '7 days'

UNION ALL

SELECT
    'High Risk Blocks Updated' as metric,
    COUNT(*) as count
FROM block_risk_scores
WHERE last_updated >= NOW() - INTERVAL '7 days';

-- =====================================================
-- MAINTENANCE QUERIES
-- =====================================================

-- Refresh leaderboard (run periodically)
SELECT refresh_leaderboard();

-- Check leaderboard freshness
SELECT
    COUNT(*) as total_entries,
    MAX(last_updated) as most_recent_update,
    NOW() - MAX(last_updated) as time_since_update
FROM leaderboard;

-- Verify data consistency
SELECT
    'Users without transactions' as check_name,
    COUNT(*) as count
FROM users u
LEFT JOIN points_transactions pt ON u.id = pt.user_id
WHERE pt.id IS NULL
    AND u.total_points > 0

UNION ALL

SELECT
    'Accidents without issues' as check_name,
    COUNT(*) as count
FROM accident_history ah
LEFT JOIN issues i ON ah.issue_id = i.id
WHERE i.id IS NULL

UNION ALL

SELECT
    'Blocks never updated' as check_name,
    COUNT(*) as count
FROM block_risk_scores
WHERE last_updated < NOW() - INTERVAL '30 days';

-- Table size report
SELECT
    table_name,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as total_size,
    pg_size_pretty(pg_relation_size(quote_ident(table_name)::regclass)) as table_size,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass) - pg_relation_size(quote_ident(table_name)::regclass)) as indexes_size
FROM (
    VALUES
        ('users'),
        ('points_transactions'),
        ('leaderboard'),
        ('accident_history'),
        ('block_risk_scores')
) AS t(table_name)
ORDER BY pg_total_relation_size(quote_ident(table_name)::regclass) DESC;
