-- NeuraCity Initial Database Schema
-- This migration creates all tables required for the NeuraCity smart city platform
-- Database: PostgreSQL (Supabase)
-- Created: 2025-11-14

-- ============================================================================
-- TABLE: issues
-- Stores citizen-reported infrastructure problems with image evidence and GPS
-- ============================================================================
CREATE TABLE issues (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lat double precision NOT NULL,
  lng double precision NOT NULL,
  issue_type text NOT NULL CHECK (issue_type IN ('accident', 'pothole', 'traffic_light', 'other')),
  description text,
  image_url text NOT NULL,
  severity double precision CHECK (severity >= 0 AND severity <= 1),
  urgency double precision CHECK (urgency >= 0 AND urgency <= 1),
  priority text CHECK (priority IN ('low', 'medium', 'high', 'critical')),
  action_type text CHECK (action_type IN ('emergency_summary', 'work_order', 'none')),
  status text DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Index for geospatial queries (finding issues near a location)
CREATE INDEX idx_issues_location ON issues (lat, lng);

-- Index for filtering by status and type
CREATE INDEX idx_issues_status ON issues (status);
CREATE INDEX idx_issues_type ON issues (issue_type);
CREATE INDEX idx_issues_created_at ON issues (created_at DESC);

-- Index for urgency-based queries (routing and prioritization)
CREATE INDEX idx_issues_urgency ON issues (urgency DESC) WHERE urgency IS NOT NULL;

-- Composite index for status + urgency queries
CREATE INDEX idx_issues_status_urgency ON issues (status, urgency DESC);

-- ============================================================================
-- TABLE: mood_areas
-- Stores aggregated mood/sentiment data by city area
-- ============================================================================
CREATE TABLE mood_areas (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  area_id text NOT NULL,
  lat double precision NOT NULL,
  lng double precision NOT NULL,
  mood_score double precision CHECK (mood_score >= -1 AND mood_score <= 1),
  post_count integer DEFAULT 0 CHECK (post_count >= 0),
  created_at timestamptz DEFAULT now()
);

-- Index for area lookups
CREATE INDEX idx_mood_areas_area_id ON mood_areas (area_id);

-- Index for geospatial queries
CREATE INDEX idx_mood_areas_location ON mood_areas (lat, lng);

-- Index for time-series analysis
CREATE INDEX idx_mood_areas_created_at ON mood_areas (created_at DESC);

-- Composite index for area + time queries
CREATE INDEX idx_mood_areas_area_time ON mood_areas (area_id, created_at DESC);

-- ============================================================================
-- TABLE: traffic_segments
-- Stores real-time synthetic traffic congestion data
-- ============================================================================
CREATE TABLE traffic_segments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  segment_id text NOT NULL,
  lat double precision NOT NULL,
  lng double precision NOT NULL,
  congestion double precision CHECK (congestion >= 0 AND congestion <= 1),
  ts timestamptz NOT NULL DEFAULT now()
);

-- Index for segment lookups
CREATE INDEX idx_traffic_segments_segment_id ON traffic_segments (segment_id);

-- Index for geospatial queries
CREATE INDEX idx_traffic_segments_location ON traffic_segments (lat, lng);

-- Index for time-series queries (latest traffic data)
CREATE INDEX idx_traffic_segments_ts ON traffic_segments (ts DESC);

-- Composite index for segment + time queries
CREATE INDEX idx_traffic_segments_segment_ts ON traffic_segments (segment_id, ts DESC);

-- ============================================================================
-- TABLE: noise_segments
-- Stores noise level data (dB) for road segments
-- ============================================================================
CREATE TABLE noise_segments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  segment_id text NOT NULL,
  lat double precision NOT NULL,
  lng double precision NOT NULL,
  noise_db double precision CHECK (noise_db >= 0 AND noise_db <= 120),
  ts timestamptz NOT NULL DEFAULT now()
);

-- Index for segment lookups
CREATE INDEX idx_noise_segments_segment_id ON noise_segments (segment_id);

-- Index for geospatial queries
CREATE INDEX idx_noise_segments_location ON noise_segments (lat, lng);

-- Index for time-series queries
CREATE INDEX idx_noise_segments_ts ON noise_segments (ts DESC);

-- Composite index for segment + time queries
CREATE INDEX idx_noise_segments_segment_ts ON noise_segments (segment_id, ts DESC);

-- Index for noise level filtering (quiet route queries)
CREATE INDEX idx_noise_segments_noise_db ON noise_segments (noise_db);

-- ============================================================================
-- TABLE: contractors
-- Stores city-approved contractors with specialties
-- ============================================================================
CREATE TABLE contractors (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  specialty text NOT NULL,
  contact_email text NOT NULL,
  has_city_contract boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Index for specialty-based contractor selection
CREATE INDEX idx_contractors_specialty ON contractors (specialty);

-- Index for filtering active contractors
CREATE INDEX idx_contractors_has_city_contract ON contractors (has_city_contract);

-- Composite index for active contractors by specialty
CREATE INDEX idx_contractors_specialty_contract ON contractors (specialty, has_city_contract);

-- ============================================================================
-- TABLE: work_orders
-- Stores AI-generated work orders for infrastructure issues
-- ============================================================================
CREATE TABLE work_orders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id uuid REFERENCES issues(id) ON DELETE CASCADE,
  contractor_id uuid REFERENCES contractors(id) ON DELETE SET NULL,
  material_suggestion text,
  status text DEFAULT 'pending_review' CHECK (status IN ('pending_review', 'approved', 'in_progress', 'completed', 'rejected')),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Index for issue-to-work-order lookups
CREATE INDEX idx_work_orders_issue_id ON work_orders (issue_id);

-- Index for contractor workload queries
CREATE INDEX idx_work_orders_contractor_id ON work_orders (contractor_id);

-- Index for status filtering
CREATE INDEX idx_work_orders_status ON work_orders (status);

-- Index for time-based queries
CREATE INDEX idx_work_orders_created_at ON work_orders (created_at DESC);

-- Composite index for status + time queries
CREATE INDEX idx_work_orders_status_created ON work_orders (status, created_at DESC);

-- ============================================================================
-- TABLE: emergency_queue
-- Stores AI-generated emergency summaries for accidents
-- ============================================================================
CREATE TABLE emergency_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id uuid REFERENCES issues(id) ON DELETE CASCADE,
  summary text NOT NULL,
  status text DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'dispatched', 'resolved')),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Index for issue-to-emergency lookups
CREATE INDEX idx_emergency_queue_issue_id ON emergency_queue (issue_id);

-- Index for status filtering (admin queue management)
CREATE INDEX idx_emergency_queue_status ON emergency_queue (status);

-- Index for time-based queries (urgent emergencies)
CREATE INDEX idx_emergency_queue_created_at ON emergency_queue (created_at DESC);

-- Composite index for status + time queries
CREATE INDEX idx_emergency_queue_status_created ON emergency_queue (status, created_at DESC);

-- ============================================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for auto-updating updated_at
CREATE TRIGGER update_issues_updated_at
  BEFORE UPDATE ON issues
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contractors_updated_at
  BEFORE UPDATE ON contractors
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_orders_updated_at
  BEFORE UPDATE ON work_orders
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_emergency_queue_updated_at
  BEFORE UPDATE ON emergency_queue
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS: Table and column documentation
-- ============================================================================

COMMENT ON TABLE issues IS 'Citizen-reported infrastructure issues with image evidence and automatic GPS location';
COMMENT ON COLUMN issues.severity IS 'AI-calculated severity score (0-1), based on issue type and context';
COMMENT ON COLUMN issues.urgency IS 'AI-calculated urgency score (0-1), based on traffic, location, and time';
COMMENT ON COLUMN issues.priority IS 'Human-readable priority level derived from severity and urgency';
COMMENT ON COLUMN issues.action_type IS 'Type of automated action triggered (emergency_summary for accidents, work_order for infrastructure)';

COMMENT ON TABLE mood_areas IS 'Aggregated sentiment/mood data by city area from synthetic social posts';
COMMENT ON COLUMN mood_areas.mood_score IS 'Normalized mood score: -1 (very negative) to +1 (very positive)';
COMMENT ON COLUMN mood_areas.post_count IS 'Number of social posts analyzed for this area';

COMMENT ON TABLE traffic_segments IS 'Real-time synthetic traffic congestion data for road segments';
COMMENT ON COLUMN traffic_segments.congestion IS 'Congestion level (0-1): 0=free flow, 1=gridlock';

COMMENT ON TABLE noise_segments IS 'Noise level measurements (dB) for road segments';
COMMENT ON COLUMN noise_segments.noise_db IS 'Noise level in decibels (40-50=quiet, 55-65=moderate, 70-85=loud)';

COMMENT ON TABLE contractors IS 'City-approved contractors with specialties for infrastructure work';
COMMENT ON COLUMN contractors.specialty IS 'Contractor specialty (e.g., road_repair, electrical, traffic_engineering)';
COMMENT ON COLUMN contractors.has_city_contract IS 'Whether contractor currently has an active city contract';

COMMENT ON TABLE work_orders IS 'AI-generated work orders for infrastructure issues (potholes, traffic lights)';
COMMENT ON COLUMN work_orders.material_suggestion IS 'Gemini AI-generated material recommendations';
COMMENT ON COLUMN work_orders.status IS 'Work order approval and completion status';

COMMENT ON TABLE emergency_queue IS 'AI-generated emergency summaries for accident reports';
COMMENT ON COLUMN emergency_queue.summary IS 'Gemini AI-generated dispatcher-ready emergency summary';
COMMENT ON COLUMN emergency_queue.status IS 'Emergency processing status (pending review, dispatched, etc.)';

-- ============================================================================
-- Migration complete
-- ============================================================================
