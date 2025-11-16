-- =====================================================
-- NeuraCity Database Migration 002
-- Gamification System, Accident History, and Community Risk Index
-- =====================================================

-- This migration adds three new feature sets:
-- 1. Gamification System (users, points_transactions, leaderboard)
-- 2. Accident History Tracking (accident_history)
-- 3. Community Risk Index (block_risk_scores)

-- =====================================================
-- EXTENSIONS: Enable PostGIS for spatial queries
-- =====================================================
CREATE EXTENSION IF NOT EXISTS postgis;

-- =====================================================
-- TABLE: users
-- Gamification user accounts with point tracking
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 50),
    email TEXT NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    total_points INTEGER DEFAULT 0 CHECK (total_points >= 0),
    rank TEXT DEFAULT 'bronze' CHECK (rank IN ('bronze', 'silver', 'gold', 'platinum', 'diamond')),
    profile_image_url TEXT,
    bio TEXT CHECK (LENGTH(bio) <= 500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE users IS 'Gamification user accounts tracking points and ranks for civic engagement';
COMMENT ON COLUMN users.id IS 'Unique identifier for the user';
COMMENT ON COLUMN users.username IS 'Unique username (3-50 characters)';
COMMENT ON COLUMN users.email IS 'User email address (unique, validated format)';
COMMENT ON COLUMN users.total_points IS 'Cumulative points earned from all activities';
COMMENT ON COLUMN users.rank IS 'Current rank based on total points: bronze, silver, gold, platinum, diamond';
COMMENT ON COLUMN users.profile_image_url IS 'Optional profile picture URL';
COMMENT ON COLUMN users.bio IS 'Optional user bio (max 500 characters)';

-- Indexes for users
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_total_points ON users (total_points DESC);
CREATE INDEX IF NOT EXISTS idx_users_rank ON users (rank);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at DESC);

-- =====================================================
-- TABLE: points_transactions
-- Individual point-earning events linked to user actions
-- =====================================================
CREATE TABLE IF NOT EXISTS points_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    issue_id UUID REFERENCES issues(id) ON DELETE SET NULL,
    points_earned INTEGER NOT NULL CHECK (points_earned > 0),
    transaction_type TEXT NOT NULL CHECK (transaction_type IN (
        'issue_report',
        'issue_verified',
        'issue_resolved',
        'community_vote',
        'helpful_description',
        'photo_quality',
        'repeat_reporter',
        'first_in_area',
        'streak_bonus'
    )),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE points_transactions IS 'Individual point-earning events for gamification tracking';
COMMENT ON COLUMN points_transactions.id IS 'Unique transaction identifier';
COMMENT ON COLUMN points_transactions.user_id IS 'Reference to user who earned points';
COMMENT ON COLUMN points_transactions.issue_id IS 'Optional reference to related issue';
COMMENT ON COLUMN points_transactions.points_earned IS 'Number of points awarded in this transaction';
COMMENT ON COLUMN points_transactions.transaction_type IS 'Type of action that earned points';
COMMENT ON COLUMN points_transactions.description IS 'Optional human-readable description of why points were awarded';

-- Indexes for points_transactions
CREATE INDEX IF NOT EXISTS idx_points_transactions_user_id ON points_transactions (user_id);
CREATE INDEX IF NOT EXISTS idx_points_transactions_issue_id ON points_transactions (issue_id);
CREATE INDEX IF NOT EXISTS idx_points_transactions_type ON points_transactions (transaction_type);
CREATE INDEX IF NOT EXISTS idx_points_transactions_created_at ON points_transactions (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_points_transactions_user_created ON points_transactions (user_id, created_at DESC);

-- =====================================================
-- TABLE: leaderboard (materialized view for performance)
-- Pre-calculated leaderboard rankings
-- =====================================================
CREATE TABLE IF NOT EXISTS leaderboard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    username TEXT NOT NULL,
    total_points INTEGER NOT NULL,
    rank TEXT NOT NULL,
    position INTEGER NOT NULL,
    issues_reported INTEGER DEFAULT 0,
    issues_verified INTEGER DEFAULT 0,
    last_activity_at TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE leaderboard IS 'Pre-calculated leaderboard rankings for efficient querying';
COMMENT ON COLUMN leaderboard.user_id IS 'Reference to user';
COMMENT ON COLUMN leaderboard.username IS 'Cached username for fast display';
COMMENT ON COLUMN leaderboard.total_points IS 'Cached total points';
COMMENT ON COLUMN leaderboard.rank IS 'Cached user rank';
COMMENT ON COLUMN leaderboard.position IS 'Leaderboard position (1 = top)';
COMMENT ON COLUMN leaderboard.issues_reported IS 'Count of issues reported by user';
COMMENT ON COLUMN leaderboard.issues_verified IS 'Count of issues verified by user';
COMMENT ON COLUMN leaderboard.last_activity_at IS 'Timestamp of most recent activity';
COMMENT ON COLUMN leaderboard.last_updated IS 'When this leaderboard entry was last recalculated';

-- Indexes for leaderboard
CREATE UNIQUE INDEX IF NOT EXISTS idx_leaderboard_user_id ON leaderboard (user_id);
CREATE INDEX IF NOT EXISTS idx_leaderboard_position ON leaderboard (position);
CREATE INDEX IF NOT EXISTS idx_leaderboard_points ON leaderboard (total_points DESC);
CREATE INDEX IF NOT EXISTS idx_leaderboard_rank ON leaderboard (rank);

-- =====================================================
-- TABLE: accident_history
-- Historical accident tracking with spatial indexing
-- =====================================================
CREATE TABLE IF NOT EXISTS accident_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    lat DOUBLE PRECISION NOT NULL CHECK (lat >= -90 AND lat <= 90),
    lng DOUBLE PRECISION NOT NULL CHECK (lng >= -180 AND lng <= 180),
    severity DOUBLE PRECISION CHECK (severity >= 0 AND severity <= 1),
    urgency DOUBLE PRECISION CHECK (urgency >= 0 AND urgency <= 1),
    area_name TEXT,
    description TEXT,
    image_url TEXT,
    weather_conditions TEXT,
    time_of_day TEXT CHECK (time_of_day IN ('morning', 'afternoon', 'evening', 'night')),
    occurred_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE accident_history IS 'Historical accident records with spatial data for pattern analysis';
COMMENT ON COLUMN accident_history.id IS 'Unique accident history identifier';
COMMENT ON COLUMN accident_history.issue_id IS 'Reference to original issue report';
COMMENT ON COLUMN accident_history.location IS 'PostGIS geography point for spatial queries';
COMMENT ON COLUMN accident_history.lat IS 'Latitude coordinate';
COMMENT ON COLUMN accident_history.lng IS 'Longitude coordinate';
COMMENT ON COLUMN accident_history.severity IS 'Accident severity score (0-1)';
COMMENT ON COLUMN accident_history.urgency IS 'Accident urgency score (0-1)';
COMMENT ON COLUMN accident_history.area_name IS 'City area where accident occurred';
COMMENT ON COLUMN accident_history.description IS 'Accident description from issue';
COMMENT ON COLUMN accident_history.image_url IS 'Evidence photo URL';
COMMENT ON COLUMN accident_history.weather_conditions IS 'Weather at time of accident (if available)';
COMMENT ON COLUMN accident_history.time_of_day IS 'Time period when accident occurred';
COMMENT ON COLUMN accident_history.occurred_at IS 'Timestamp when accident happened';

-- Indexes for accident_history (including spatial)
CREATE INDEX IF NOT EXISTS idx_accident_history_issue_id ON accident_history (issue_id);
CREATE INDEX IF NOT EXISTS idx_accident_history_location ON accident_history USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_accident_history_coords ON accident_history (lat, lng);
CREATE INDEX IF NOT EXISTS idx_accident_history_occurred_at ON accident_history (occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_accident_history_area ON accident_history (area_name);
CREATE INDEX IF NOT EXISTS idx_accident_history_severity ON accident_history (severity DESC);
CREATE INDEX IF NOT EXISTS idx_accident_history_time_of_day ON accident_history (time_of_day);

-- =====================================================
-- TABLE: block_risk_scores
-- Community risk assessment by geographic blocks
-- =====================================================
CREATE TABLE IF NOT EXISTS block_risk_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    block_id TEXT NOT NULL UNIQUE,
    lat DOUBLE PRECISION NOT NULL CHECK (lat >= -90 AND lat <= 90),
    lng DOUBLE PRECISION NOT NULL CHECK (lng >= -180 AND lng <= 180),
    geometry GEOGRAPHY(POINT, 4326) NOT NULL,
    overall_risk_score DOUBLE PRECISION NOT NULL CHECK (overall_risk_score >= 0 AND overall_risk_score <= 1),
    crime_score DOUBLE PRECISION CHECK (crime_score >= 0 AND crime_score <= 1),
    blight_score DOUBLE PRECISION CHECK (blight_score >= 0 AND blight_score <= 1),
    wait_time_score DOUBLE PRECISION CHECK (wait_time_score >= 0 AND wait_time_score <= 1),
    air_quality_score DOUBLE PRECISION CHECK (air_quality_score >= 0 AND air_quality_score <= 1),
    heat_score DOUBLE PRECISION CHECK (heat_score >= 0 AND heat_score <= 1),
    traffic_score DOUBLE PRECISION CHECK (traffic_score >= 0 AND traffic_score <= 1),
    noise_score DOUBLE PRECISION CHECK (noise_score >= 0 AND noise_score <= 1),
    accident_count INTEGER DEFAULT 0 CHECK (accident_count >= 0),
    issue_count INTEGER DEFAULT 0 CHECK (issue_count >= 0),
    area_name TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE block_risk_scores IS 'Community risk assessment scores aggregated by geographic blocks';
COMMENT ON COLUMN block_risk_scores.id IS 'Unique risk score identifier';
COMMENT ON COLUMN block_risk_scores.block_id IS 'Unique block identifier (e.g., BLOCK_001)';
COMMENT ON COLUMN block_risk_scores.lat IS 'Block center latitude';
COMMENT ON COLUMN block_risk_scores.lng IS 'Block center longitude';
COMMENT ON COLUMN block_risk_scores.geometry IS 'PostGIS geography point for spatial queries';
COMMENT ON COLUMN block_risk_scores.overall_risk_score IS 'Composite risk score (0 = safe, 1 = high risk)';
COMMENT ON COLUMN block_risk_scores.crime_score IS 'Crime risk component (0-1)';
COMMENT ON COLUMN block_risk_scores.blight_score IS 'Blight/neglect risk component (0-1)';
COMMENT ON COLUMN block_risk_scores.wait_time_score IS 'Service delay risk component (0-1)';
COMMENT ON COLUMN block_risk_scores.air_quality_score IS 'Air quality risk component (0-1, higher = worse)';
COMMENT ON COLUMN block_risk_scores.heat_score IS 'Heat island effect component (0-1)';
COMMENT ON COLUMN block_risk_scores.traffic_score IS 'Traffic danger component (0-1)';
COMMENT ON COLUMN block_risk_scores.noise_score IS 'Noise pollution component (0-1)';
COMMENT ON COLUMN block_risk_scores.accident_count IS 'Number of accidents in this block';
COMMENT ON COLUMN block_risk_scores.issue_count IS 'Number of reported issues in this block';
COMMENT ON COLUMN block_risk_scores.area_name IS 'City area name for grouping';
COMMENT ON COLUMN block_risk_scores.last_updated IS 'When scores were last recalculated';

-- Indexes for block_risk_scores (including spatial)
CREATE UNIQUE INDEX IF NOT EXISTS idx_block_risk_scores_block_id ON block_risk_scores (block_id);
CREATE INDEX IF NOT EXISTS idx_block_risk_scores_geometry ON block_risk_scores USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_block_risk_scores_coords ON block_risk_scores (lat, lng);
CREATE INDEX IF NOT EXISTS idx_block_risk_scores_overall ON block_risk_scores (overall_risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_block_risk_scores_area ON block_risk_scores (area_name);
CREATE INDEX IF NOT EXISTS idx_block_risk_scores_last_updated ON block_risk_scores (last_updated DESC);
CREATE INDEX IF NOT EXISTS idx_block_risk_scores_crime ON block_risk_scores (crime_score DESC);
CREATE INDEX IF NOT EXISTS idx_block_risk_scores_traffic ON block_risk_scores (traffic_score DESC);

-- =====================================================
-- TRIGGERS: Auto-update timestamps and calculations
-- =====================================================

-- Trigger for users updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-calculate user rank based on points
CREATE OR REPLACE FUNCTION update_user_rank()
RETURNS TRIGGER AS $$
BEGIN
    -- Update rank based on total points
    NEW.rank = CASE
        WHEN NEW.total_points >= 10000 THEN 'diamond'
        WHEN NEW.total_points >= 5000 THEN 'platinum'
        WHEN NEW.total_points >= 2000 THEN 'gold'
        WHEN NEW.total_points >= 500 THEN 'silver'
        ELSE 'bronze'
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_user_rank ON users;
CREATE TRIGGER trigger_update_user_rank
    BEFORE INSERT OR UPDATE OF total_points ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_user_rank();

-- Trigger to update user total_points when points_transaction is added
CREATE OR REPLACE FUNCTION add_points_to_user()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users
    SET total_points = total_points + NEW.points_earned,
        updated_at = NOW()
    WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_add_points_to_user ON points_transactions;
CREATE TRIGGER trigger_add_points_to_user
    AFTER INSERT ON points_transactions
    FOR EACH ROW
    EXECUTE FUNCTION add_points_to_user();

-- Trigger to auto-populate accident_history location from lat/lng
CREATE OR REPLACE FUNCTION set_accident_location()
RETURNS TRIGGER AS $$
BEGIN
    NEW.location = ST_SetSRID(ST_MakePoint(NEW.lng, NEW.lat), 4326)::geography;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_set_accident_location ON accident_history;
CREATE TRIGGER trigger_set_accident_location
    BEFORE INSERT OR UPDATE ON accident_history
    FOR EACH ROW
    EXECUTE FUNCTION set_accident_location();

-- Trigger to auto-populate block_risk_scores geometry from lat/lng
CREATE OR REPLACE FUNCTION set_block_geometry()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geometry = ST_SetSRID(ST_MakePoint(NEW.lng, NEW.lat), 4326)::geography;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_set_block_geometry ON block_risk_scores;
CREATE TRIGGER trigger_set_block_geometry
    BEFORE INSERT OR UPDATE ON block_risk_scores
    FOR EACH ROW
    EXECUTE FUNCTION set_block_geometry();

-- =====================================================
-- VIEWS: Useful query shortcuts
-- =====================================================

-- Top performers leaderboard view
CREATE OR REPLACE VIEW top_users_leaderboard AS
SELECT
    u.id,
    u.username,
    u.total_points,
    u.rank,
    u.created_at,
    COUNT(DISTINCT pt.id) as total_transactions,
    COUNT(DISTINCT CASE WHEN pt.transaction_type = 'issue_report' THEN pt.id END) as issues_reported,
    COUNT(DISTINCT CASE WHEN pt.transaction_type = 'issue_verified' THEN pt.id END) as issues_verified,
    MAX(pt.created_at) as last_activity_at,
    ROW_NUMBER() OVER (ORDER BY u.total_points DESC, u.created_at ASC) as position
FROM users u
LEFT JOIN points_transactions pt ON u.id = pt.user_id
GROUP BY u.id, u.username, u.total_points, u.rank, u.created_at
ORDER BY u.total_points DESC, u.created_at ASC;

COMMENT ON VIEW top_users_leaderboard IS 'Real-time leaderboard with rankings and activity stats';

-- Accident hotspots view
CREATE OR REPLACE VIEW accident_hotspots AS
SELECT
    area_name,
    COUNT(*) as accident_count,
    AVG(severity) as avg_severity,
    AVG(urgency) as avg_urgency,
    MIN(occurred_at) as first_accident,
    MAX(occurred_at) as most_recent_accident,
    AVG(lat) as center_lat,
    AVG(lng) as center_lng
FROM accident_history
WHERE occurred_at >= NOW() - INTERVAL '90 days'
GROUP BY area_name
HAVING COUNT(*) >= 3
ORDER BY accident_count DESC;

COMMENT ON VIEW accident_hotspots IS 'Areas with highest accident concentrations in last 90 days';

-- High risk blocks view
CREATE OR REPLACE VIEW high_risk_blocks AS
SELECT
    block_id,
    area_name,
    lat,
    lng,
    overall_risk_score,
    crime_score,
    blight_score,
    traffic_score,
    accident_count,
    issue_count,
    last_updated
FROM block_risk_scores
WHERE overall_risk_score >= 0.7
ORDER BY overall_risk_score DESC, accident_count DESC;

COMMENT ON VIEW high_risk_blocks IS 'Blocks with high risk scores (>= 0.7) requiring attention';

-- User activity summary
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT
    u.id as user_id,
    u.username,
    u.total_points,
    u.rank,
    COUNT(DISTINCT pt.id) as total_activities,
    SUM(CASE WHEN pt.created_at >= NOW() - INTERVAL '7 days' THEN pt.points_earned ELSE 0 END) as points_last_7_days,
    SUM(CASE WHEN pt.created_at >= NOW() - INTERVAL '30 days' THEN pt.points_earned ELSE 0 END) as points_last_30_days,
    MAX(pt.created_at) as last_activity
FROM users u
LEFT JOIN points_transactions pt ON u.id = pt.user_id
GROUP BY u.id, u.username, u.total_points, u.rank
ORDER BY u.total_points DESC;

COMMENT ON VIEW user_activity_summary IS 'User engagement metrics with recent activity tracking';

-- =====================================================
-- HELPER FUNCTIONS: Spatial queries
-- =====================================================

-- Function to find accidents near a location (within radius in meters)
CREATE OR REPLACE FUNCTION get_nearby_accidents(
    p_lat DOUBLE PRECISION,
    p_lng DOUBLE PRECISION,
    p_radius_meters INTEGER DEFAULT 500
)
RETURNS TABLE (
    id UUID,
    issue_id UUID,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    severity DOUBLE PRECISION,
    occurred_at TIMESTAMPTZ,
    distance_meters DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ah.id,
        ah.issue_id,
        ah.lat,
        ah.lng,
        ah.severity,
        ah.occurred_at,
        ST_Distance(
            ah.location,
            ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography
        ) as distance_meters
    FROM accident_history ah
    WHERE ST_DWithin(
        ah.location,
        ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography,
        p_radius_meters
    )
    ORDER BY distance_meters ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_nearby_accidents IS 'Find all accidents within specified radius (meters) of a location';

-- Function to get risk score for a location
CREATE OR REPLACE FUNCTION get_location_risk_score(
    p_lat DOUBLE PRECISION,
    p_lng DOUBLE PRECISION
)
RETURNS TABLE (
    block_id TEXT,
    overall_risk_score DOUBLE PRECISION,
    distance_meters DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        brs.block_id,
        brs.overall_risk_score,
        ST_Distance(
            brs.geometry,
            ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography
        ) as distance_meters
    FROM block_risk_scores brs
    ORDER BY distance_meters ASC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_location_risk_score IS 'Get risk score for nearest block to given coordinates';

-- Function to refresh leaderboard (materialized view alternative)
CREATE OR REPLACE FUNCTION refresh_leaderboard()
RETURNS void AS $$
BEGIN
    -- Clear existing leaderboard
    DELETE FROM leaderboard;

    -- Repopulate from current data
    INSERT INTO leaderboard (user_id, username, total_points, rank, position, issues_reported, issues_verified, last_activity_at, last_updated)
    SELECT
        id,
        username,
        total_points,
        rank,
        position,
        issues_reported,
        issues_verified,
        last_activity_at,
        NOW()
    FROM top_users_leaderboard;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_leaderboard IS 'Refresh the leaderboard table with current rankings';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migration 002 Completed Successfully';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'New tables created: 5';
    RAISE NOTICE '  - users (gamification)';
    RAISE NOTICE '  - points_transactions (gamification)';
    RAISE NOTICE '  - leaderboard (gamification)';
    RAISE NOTICE '  - accident_history (spatial tracking)';
    RAISE NOTICE '  - block_risk_scores (community risk)';
    RAISE NOTICE '';
    RAISE NOTICE 'New views created: 4';
    RAISE NOTICE '  - top_users_leaderboard';
    RAISE NOTICE '  - accident_hotspots';
    RAISE NOTICE '  - high_risk_blocks';
    RAISE NOTICE '  - user_activity_summary';
    RAISE NOTICE '';
    RAISE NOTICE 'New functions created: 3';
    RAISE NOTICE '  - get_nearby_accidents(lat, lng, radius)';
    RAISE NOTICE '  - get_location_risk_score(lat, lng)';
    RAISE NOTICE '  - refresh_leaderboard()';
    RAISE NOTICE '';
    RAISE NOTICE 'Triggers created: 5';
    RAISE NOTICE '  - Auto-update user rank based on points';
    RAISE NOTICE '  - Auto-add points to user total';
    RAISE NOTICE '  - Auto-set accident location geometry';
    RAISE NOTICE '  - Auto-set block geometry';
    RAISE NOTICE '  - Auto-update timestamps';
    RAISE NOTICE '========================================';
END $$;
