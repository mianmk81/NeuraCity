-- =====================================================
-- NeuraCity Database Schema Extensions
-- Additional tables for gamification, accident history, and risk index
-- =====================================================

-- =====================================================
-- TABLE: users
-- User profiles for gamification system
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    full_name TEXT,
    avatar_url TEXT,
    total_points INTEGER DEFAULT 0 CHECK (total_points >= 0),
    rank INTEGER DEFAULT 0,
    issues_reported INTEGER DEFAULT 0 CHECK (issues_reported >= 0),
    issues_verified INTEGER DEFAULT 0 CHECK (issues_verified >= 0),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE users IS 'User profiles for gamification system with points and rankings';
COMMENT ON COLUMN users.id IS 'Unique identifier for the user';
COMMENT ON COLUMN users.username IS 'Unique username for the user';
COMMENT ON COLUMN users.email IS 'User email address';
COMMENT ON COLUMN users.total_points IS 'Total gamification points earned';
COMMENT ON COLUMN users.rank IS 'Current rank position in leaderboard';
COMMENT ON COLUMN users.issues_reported IS 'Number of issues reported by user';
COMMENT ON COLUMN users.issues_verified IS 'Number of issues verified by user';

-- Indexes for users
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_total_points ON users (total_points DESC);
CREATE INDEX IF NOT EXISTS idx_users_rank ON users (rank);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at DESC);

-- =====================================================
-- TABLE: user_points_history
-- Point transaction history for transparency
-- =====================================================
CREATE TABLE IF NOT EXISTS user_points_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points INTEGER NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN ('issue_reported', 'issue_verified', 'issue_resolved', 'bonus')),
    issue_id UUID REFERENCES issues(id) ON DELETE SET NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE user_points_history IS 'History of point transactions for each user';
COMMENT ON COLUMN user_points_history.user_id IS 'Reference to the user';
COMMENT ON COLUMN user_points_history.points IS 'Points awarded (positive) or deducted (negative)';
COMMENT ON COLUMN user_points_history.action_type IS 'Type of action that earned/lost points';
COMMENT ON COLUMN user_points_history.issue_id IS 'Related issue if applicable';

-- Indexes for user_points_history
CREATE INDEX IF NOT EXISTS idx_user_points_history_user_id ON user_points_history (user_id);
CREATE INDEX IF NOT EXISTS idx_user_points_history_issue_id ON user_points_history (issue_id);
CREATE INDEX IF NOT EXISTS idx_user_points_history_created_at ON user_points_history (created_at DESC);

-- =====================================================
-- TABLE: risk_blocks
-- Precomputed risk scores for geographic blocks
-- =====================================================
CREATE TABLE IF NOT EXISTS risk_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    block_id TEXT NOT NULL UNIQUE,
    center_lat DOUBLE PRECISION NOT NULL CHECK (center_lat >= -90 AND center_lat <= 90),
    center_lng DOUBLE PRECISION NOT NULL CHECK (center_lng >= -180 AND center_lng <= 180),
    bounds_min_lat DOUBLE PRECISION NOT NULL,
    bounds_min_lng DOUBLE PRECISION NOT NULL,
    bounds_max_lat DOUBLE PRECISION NOT NULL,
    bounds_max_lng DOUBLE PRECISION NOT NULL,

    -- Risk components
    accident_count INTEGER DEFAULT 0,
    pothole_count INTEGER DEFAULT 0,
    traffic_light_count INTEGER DEFAULT 0,
    avg_congestion DOUBLE PRECISION DEFAULT 0 CHECK (avg_congestion >= 0 AND avg_congestion <= 1),
    avg_noise_db DOUBLE PRECISION DEFAULT 0,
    avg_severity DOUBLE PRECISION DEFAULT 0 CHECK (avg_severity >= 0 AND avg_severity <= 1),

    -- Composite scores
    accident_risk DOUBLE PRECISION DEFAULT 0 CHECK (accident_risk >= 0 AND accident_risk <= 1),
    infrastructure_risk DOUBLE PRECISION DEFAULT 0 CHECK (infrastructure_risk >= 0 AND infrastructure_risk <= 1),
    traffic_risk DOUBLE PRECISION DEFAULT 0 CHECK (traffic_risk >= 0 AND traffic_risk <= 1),
    overall_risk DOUBLE PRECISION DEFAULT 0 CHECK (overall_risk >= 0 AND overall_risk <= 1),

    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE risk_blocks IS 'Precomputed risk scores for geographic blocks based on multiple factors';
COMMENT ON COLUMN risk_blocks.block_id IS 'Unique identifier for the block (e.g., lat_lng grid)';
COMMENT ON COLUMN risk_blocks.accident_count IS 'Number of accidents in this block';
COMMENT ON COLUMN risk_blocks.pothole_count IS 'Number of potholes in this block';
COMMENT ON COLUMN risk_blocks.accident_risk IS 'Risk score based on accident frequency (0-1)';
COMMENT ON COLUMN risk_blocks.infrastructure_risk IS 'Risk score based on infrastructure issues (0-1)';
COMMENT ON COLUMN risk_blocks.traffic_risk IS 'Risk score based on traffic congestion (0-1)';
COMMENT ON COLUMN risk_blocks.overall_risk IS 'Composite risk score (0-1)';

-- Indexes for risk_blocks
CREATE INDEX IF NOT EXISTS idx_risk_blocks_block_id ON risk_blocks (block_id);
CREATE INDEX IF NOT EXISTS idx_risk_blocks_location ON risk_blocks (center_lat, center_lng);
CREATE INDEX IF NOT EXISTS idx_risk_blocks_overall_risk ON risk_blocks (overall_risk DESC);
CREATE INDEX IF NOT EXISTS idx_risk_blocks_updated_at ON risk_blocks (updated_at DESC);

-- Add user_id to issues table (nullable for backward compatibility)
ALTER TABLE issues ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_issues_user_id ON issues (user_id);

-- =====================================================
-- TRIGGERS: Auto-update updated_at timestamps
-- =====================================================

-- Apply trigger to users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to risk_blocks table
DROP TRIGGER IF EXISTS update_risk_blocks_updated_at ON risk_blocks;
CREATE TRIGGER update_risk_blocks_updated_at
    BEFORE UPDATE ON risk_blocks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS: Useful query shortcuts
-- =====================================================

-- Leaderboard view
CREATE OR REPLACE VIEW leaderboard AS
SELECT
    u.id,
    u.username,
    u.full_name,
    u.avatar_url,
    u.total_points,
    u.rank,
    u.issues_reported,
    u.issues_verified,
    u.created_at
FROM users
ORDER BY total_points DESC, created_at ASC;

COMMENT ON VIEW leaderboard IS 'User leaderboard sorted by points';

-- Accident hotspots view
CREATE OR REPLACE VIEW accident_hotspots AS
SELECT
    ROUND(lat::numeric, 3) as lat_grid,
    ROUND(lng::numeric, 3) as lng_grid,
    COUNT(*) as accident_count,
    AVG(severity) as avg_severity,
    AVG(urgency) as avg_urgency,
    MAX(created_at) as last_accident_at
FROM issues
WHERE issue_type = 'accident'
GROUP BY lat_grid, lng_grid
HAVING COUNT(*) >= 2
ORDER BY accident_count DESC, avg_severity DESC;

COMMENT ON VIEW accident_hotspots IS 'Geographic areas with multiple accidents';

-- High risk areas view
CREATE OR REPLACE VIEW high_risk_areas AS
SELECT
    block_id,
    center_lat,
    center_lng,
    overall_risk,
    accident_risk,
    infrastructure_risk,
    traffic_risk,
    accident_count,
    pothole_count,
    traffic_light_count,
    updated_at
FROM risk_blocks
WHERE overall_risk >= 0.6
ORDER BY overall_risk DESC;

COMMENT ON VIEW high_risk_areas IS 'Blocks with high overall risk scores (>= 0.6)';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'NeuraCity Schema Extensions Created Successfully';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'New Tables created: 3';
    RAISE NOTICE '  - users';
    RAISE NOTICE '  - user_points_history';
    RAISE NOTICE '  - risk_blocks';
    RAISE NOTICE '';
    RAISE NOTICE 'New Views created: 3';
    RAISE NOTICE '  - leaderboard';
    RAISE NOTICE '  - accident_hotspots';
    RAISE NOTICE '  - high_risk_areas';
    RAISE NOTICE '';
    RAISE NOTICE 'Column added to issues: user_id';
    RAISE NOTICE '========================================';
END $$;
