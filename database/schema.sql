-- =====================================================
-- NeuraCity Database Schema
-- Complete production-ready PostgreSQL schema for Supabase
-- =====================================================

-- Enable UUID extension for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- TABLE: issues
-- Citizen-reported infrastructure problems with image evidence and GPS
-- =====================================================
CREATE TABLE IF NOT EXISTS issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lat DOUBLE PRECISION NOT NULL CHECK (lat >= -90 AND lat <= 90),
    lng DOUBLE PRECISION NOT NULL CHECK (lng >= -180 AND lng <= 180),
    issue_type TEXT NOT NULL CHECK (issue_type IN ('accident', 'pothole', 'traffic_light', 'other')),
    description TEXT,
    image_url TEXT NOT NULL,
    severity DOUBLE PRECISION CHECK (severity >= 0 AND severity <= 1),
    urgency DOUBLE PRECISION CHECK (urgency >= 0 AND urgency <= 1),
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    action_type TEXT CHECK (action_type IN ('emergency', 'work_order', 'monitor')),
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE issues IS 'Citizen-reported infrastructure issues with mandatory image evidence and GPS location';
COMMENT ON COLUMN issues.id IS 'Unique identifier for the issue';
COMMENT ON COLUMN issues.lat IS 'GPS latitude coordinate from device';
COMMENT ON COLUMN issues.lng IS 'GPS longitude coordinate from device';
COMMENT ON COLUMN issues.issue_type IS 'Type of issue: accident, pothole, traffic_light, or other';
COMMENT ON COLUMN issues.description IS 'Optional user-provided description';
COMMENT ON COLUMN issues.image_url IS 'Required URL to uploaded image evidence';
COMMENT ON COLUMN issues.severity IS 'AI-calculated severity score (0-1)';
COMMENT ON COLUMN issues.urgency IS 'AI-calculated urgency score (0-1)';
COMMENT ON COLUMN issues.priority IS 'Derived priority level based on severity and urgency';
COMMENT ON COLUMN issues.action_type IS 'Type of automated action triggered';
COMMENT ON COLUMN issues.status IS 'Current status of the issue';

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_issues_location ON issues USING btree (lat, lng);
CREATE INDEX IF NOT EXISTS idx_issues_type ON issues (issue_type);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues (status);
CREATE INDEX IF NOT EXISTS idx_issues_created_at ON issues (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_issues_priority ON issues (priority);
CREATE INDEX IF NOT EXISTS idx_issues_urgency ON issues (urgency DESC);

-- =====================================================
-- TABLE: mood_areas
-- Sentiment analysis results aggregated by geographic area
-- =====================================================
CREATE TABLE IF NOT EXISTS mood_areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    area_id TEXT NOT NULL,
    lat DOUBLE PRECISION CHECK (lat >= -90 AND lat <= 90),
    lng DOUBLE PRECISION CHECK (lng >= -180 AND lng <= 180),
    mood_score DOUBLE PRECISION CHECK (mood_score >= -1 AND mood_score <= 1),
    post_count INTEGER DEFAULT 0 CHECK (post_count >= 0),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE mood_areas IS 'Aggregated sentiment/emotion scores by city area from synthetic social posts';
COMMENT ON COLUMN mood_areas.area_id IS 'Area identifier (e.g., MIDTOWN, DOWNTOWN, CAMPUS)';
COMMENT ON COLUMN mood_areas.lat IS 'Center latitude of the area';
COMMENT ON COLUMN mood_areas.lng IS 'Center longitude of the area';
COMMENT ON COLUMN mood_areas.mood_score IS 'Sentiment score: -1 (very negative) to +1 (very positive)';
COMMENT ON COLUMN mood_areas.post_count IS 'Number of posts analyzed for this mood score';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_mood_areas_area_id ON mood_areas (area_id);
CREATE INDEX IF NOT EXISTS idx_mood_areas_location ON mood_areas (lat, lng);
CREATE INDEX IF NOT EXISTS idx_mood_areas_created_at ON mood_areas (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_mood_areas_score ON mood_areas (mood_score);

-- =====================================================
-- TABLE: traffic_segments
-- Real-time traffic congestion data for road segments
-- =====================================================
CREATE TABLE IF NOT EXISTS traffic_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    segment_id TEXT NOT NULL,
    lat DOUBLE PRECISION CHECK (lat >= -90 AND lat <= 90),
    lng DOUBLE PRECISION CHECK (lng >= -180 AND lng <= 180),
    congestion DOUBLE PRECISION CHECK (congestion >= 0 AND congestion <= 1),
    ts TIMESTAMPTZ NOT NULL
);

COMMENT ON TABLE traffic_segments IS 'Synthetic traffic congestion data for routing and urgency calculations';
COMMENT ON COLUMN traffic_segments.segment_id IS 'Identifier for road segment';
COMMENT ON COLUMN traffic_segments.lat IS 'Latitude of segment center';
COMMENT ON COLUMN traffic_segments.lng IS 'Longitude of segment center';
COMMENT ON COLUMN traffic_segments.congestion IS 'Congestion level: 0 (free flow) to 1 (gridlock)';
COMMENT ON COLUMN traffic_segments.ts IS 'Timestamp of traffic measurement';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_traffic_segment_id ON traffic_segments (segment_id);
CREATE INDEX IF NOT EXISTS idx_traffic_location ON traffic_segments (lat, lng);
CREATE INDEX IF NOT EXISTS idx_traffic_ts ON traffic_segments (ts DESC);
CREATE INDEX IF NOT EXISTS idx_traffic_congestion ON traffic_segments (congestion DESC);

-- =====================================================
-- TABLE: noise_segments
-- Noise level data for quiet route planning
-- =====================================================
CREATE TABLE IF NOT EXISTS noise_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    segment_id TEXT NOT NULL,
    lat DOUBLE PRECISION CHECK (lat >= -90 AND lat <= 90),
    lng DOUBLE PRECISION CHECK (lng >= -180 AND lng <= 180),
    noise_db DOUBLE PRECISION CHECK (noise_db >= 0 AND noise_db <= 120),
    ts TIMESTAMPTZ NOT NULL
);

COMMENT ON TABLE noise_segments IS 'Noise level measurements in decibels for quiet walking route calculations';
COMMENT ON COLUMN noise_segments.segment_id IS 'Identifier for road segment';
COMMENT ON COLUMN noise_segments.lat IS 'Latitude of segment center';
COMMENT ON COLUMN noise_segments.lng IS 'Longitude of segment center';
COMMENT ON COLUMN noise_segments.noise_db IS 'Noise level in decibels (40-85 typical range)';
COMMENT ON COLUMN noise_segments.ts IS 'Timestamp of noise measurement';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_noise_segment_id ON noise_segments (segment_id);
CREATE INDEX IF NOT EXISTS idx_noise_location ON noise_segments (lat, lng);
CREATE INDEX IF NOT EXISTS idx_noise_ts ON noise_segments (ts DESC);
CREATE INDEX IF NOT EXISTS idx_noise_level ON noise_segments (noise_db);

-- =====================================================
-- TABLE: contractors
-- Approved contractors with specialties for work orders
-- =====================================================
CREATE TABLE IF NOT EXISTS contractors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    contact_email TEXT NOT NULL CHECK (contact_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    has_city_contract BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE contractors IS 'Approved contractors available for automated work order assignments';
COMMENT ON COLUMN contractors.name IS 'Contractor company name';
COMMENT ON COLUMN contractors.specialty IS 'Primary specialty (e.g., pothole_repair, electrical, traffic_signals)';
COMMENT ON COLUMN contractors.contact_email IS 'Email contact for work order notifications';
COMMENT ON COLUMN contractors.has_city_contract IS 'Whether contractor has active city contract';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contractors_specialty ON contractors (specialty);
CREATE INDEX IF NOT EXISTS idx_contractors_has_contract ON contractors (has_city_contract) WHERE has_city_contract = TRUE;

-- =====================================================
-- TABLE: work_orders
-- AI-generated work orders for infrastructure repairs
-- =====================================================
CREATE TABLE IF NOT EXISTS work_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    contractor_id UUID REFERENCES contractors(id) ON DELETE SET NULL,
    material_suggestion TEXT,
    status TEXT DEFAULT 'pending_review' CHECK (status IN ('pending_review', 'approved', 'rejected', 'in_progress', 'completed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE work_orders IS 'AI-generated work orders linking issues to contractors with material suggestions';
COMMENT ON COLUMN work_orders.issue_id IS 'Reference to the reported issue';
COMMENT ON COLUMN work_orders.contractor_id IS 'Assigned contractor (can be null if not yet assigned)';
COMMENT ON COLUMN work_orders.material_suggestion IS 'AI-generated material and equipment recommendations';
COMMENT ON COLUMN work_orders.status IS 'Current work order status';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_work_orders_issue_id ON work_orders (issue_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_contractor_id ON work_orders (contractor_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders (status);
CREATE INDEX IF NOT EXISTS idx_work_orders_created_at ON work_orders (created_at DESC);

-- =====================================================
-- TABLE: emergency_queue
-- Emergency summaries for accident reports requiring immediate attention
-- =====================================================
CREATE TABLE IF NOT EXISTS emergency_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'dispatched', 'resolved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE emergency_queue IS 'AI-generated emergency summaries for accident reports awaiting admin review';
COMMENT ON COLUMN emergency_queue.issue_id IS 'Reference to the accident issue';
COMMENT ON COLUMN emergency_queue.summary IS 'AI-generated dispatcher-ready emergency summary';
COMMENT ON COLUMN emergency_queue.status IS 'Current emergency status';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_emergency_queue_issue_id ON emergency_queue (issue_id);
CREATE INDEX IF NOT EXISTS idx_emergency_queue_status ON emergency_queue (status);
CREATE INDEX IF NOT EXISTS idx_emergency_queue_created_at ON emergency_queue (created_at DESC);

-- =====================================================
-- TRIGGERS: Auto-update updated_at timestamps
-- =====================================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to issues table
DROP TRIGGER IF EXISTS update_issues_updated_at ON issues;
CREATE TRIGGER update_issues_updated_at
    BEFORE UPDATE ON issues
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to work_orders table
DROP TRIGGER IF EXISTS update_work_orders_updated_at ON work_orders;
CREATE TRIGGER update_work_orders_updated_at
    BEFORE UPDATE ON work_orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to emergency_queue table
DROP TRIGGER IF EXISTS update_emergency_queue_updated_at ON emergency_queue;
CREATE TRIGGER update_emergency_queue_updated_at
    BEFORE UPDATE ON emergency_queue
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS: Useful query shortcuts
-- =====================================================

-- Active issues summary
CREATE OR REPLACE VIEW active_issues_summary AS
SELECT
    issue_type,
    priority,
    status,
    COUNT(*) as count,
    AVG(severity) as avg_severity,
    AVG(urgency) as avg_urgency
FROM issues
WHERE status IN ('open', 'in_progress')
GROUP BY issue_type, priority, status
ORDER BY priority DESC, count DESC;

COMMENT ON VIEW active_issues_summary IS 'Summary statistics of active issues by type, priority, and status';

-- Pending work orders with issue details
CREATE OR REPLACE VIEW pending_work_orders_details AS
SELECT
    wo.id as work_order_id,
    wo.status as work_order_status,
    wo.material_suggestion,
    wo.created_at as work_order_created,
    i.id as issue_id,
    i.issue_type,
    i.lat,
    i.lng,
    i.severity,
    i.urgency,
    i.priority,
    i.image_url,
    i.description,
    c.id as contractor_id,
    c.name as contractor_name,
    c.specialty as contractor_specialty,
    c.contact_email as contractor_email
FROM work_orders wo
JOIN issues i ON wo.issue_id = i.id
LEFT JOIN contractors c ON wo.contractor_id = c.id
WHERE wo.status IN ('pending_review', 'approved')
ORDER BY i.priority DESC, wo.created_at DESC;

COMMENT ON VIEW pending_work_orders_details IS 'Detailed view of pending work orders with full issue and contractor information';

-- Emergency queue with issue details
CREATE OR REPLACE VIEW emergency_queue_details AS
SELECT
    eq.id as emergency_id,
    eq.summary,
    eq.status as emergency_status,
    eq.created_at as emergency_created,
    i.id as issue_id,
    i.lat,
    i.lng,
    i.severity,
    i.urgency,
    i.image_url,
    i.description,
    i.created_at as issue_created
FROM emergency_queue eq
JOIN issues i ON eq.issue_id = i.id
WHERE eq.status IN ('pending', 'reviewed')
ORDER BY i.urgency DESC, eq.created_at DESC;

COMMENT ON VIEW emergency_queue_details IS 'Emergency queue items with full issue details for dispatcher review';

-- =====================================================
-- GRANTS: Set up permissions (adjust as needed for Supabase)
-- =====================================================

-- Note: In Supabase, you'll typically use Row Level Security (RLS)
-- instead of traditional grants. This is included for reference.

-- Grant usage on schema
-- GRANT USAGE ON SCHEMA public TO authenticated, anon;

-- Grant access to tables
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'NeuraCity Database Schema Created Successfully';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables created: 7';
    RAISE NOTICE '  - issues';
    RAISE NOTICE '  - mood_areas';
    RAISE NOTICE '  - traffic_segments';
    RAISE NOTICE '  - noise_segments';
    RAISE NOTICE '  - contractors';
    RAISE NOTICE '  - work_orders';
    RAISE NOTICE '  - emergency_queue';
    RAISE NOTICE '';
    RAISE NOTICE 'Views created: 3';
    RAISE NOTICE '  - active_issues_summary';
    RAISE NOTICE '  - pending_work_orders_details';
    RAISE NOTICE '  - emergency_queue_details';
    RAISE NOTICE '';
    RAISE NOTICE 'Triggers created: 3 (auto-update timestamps)';
    RAISE NOTICE '========================================';
END $$;
