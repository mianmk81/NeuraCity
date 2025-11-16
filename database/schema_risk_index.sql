-- =====================================================
-- NeuraCity Community Risk Index Schema Extension
-- Add-on schema for comprehensive community risk scoring
-- =====================================================

-- =====================================================
-- TABLE: risk_blocks
-- Geographic blocks with composite risk scores
-- =====================================================
CREATE TABLE IF NOT EXISTS risk_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    block_id TEXT NOT NULL UNIQUE,
    lat DOUBLE PRECISION NOT NULL CHECK (lat >= -90 AND lat <= 90),
    lng DOUBLE PRECISION NOT NULL CHECK (lng >= -180 AND lng <= 180),

    -- Individual risk factor scores (0-1 scale)
    crime_score DOUBLE PRECISION DEFAULT 0 CHECK (crime_score >= 0 AND crime_score <= 1),
    blight_score DOUBLE PRECISION DEFAULT 0 CHECK (blight_score >= 0 AND blight_score <= 1),
    emergency_response_score DOUBLE PRECISION DEFAULT 0 CHECK (emergency_response_score >= 0 AND emergency_response_score <= 1),
    air_quality_score DOUBLE PRECISION DEFAULT 0 CHECK (air_quality_score >= 0 AND air_quality_score <= 1),
    heat_exposure_score DOUBLE PRECISION DEFAULT 0 CHECK (heat_exposure_score >= 0 AND heat_exposure_score <= 1),
    traffic_speed_score DOUBLE PRECISION DEFAULT 0 CHECK (traffic_speed_score >= 0 AND traffic_speed_score <= 1),

    -- Composite risk index (0-1 scale, weighted combination)
    composite_risk_index DOUBLE PRECISION DEFAULT 0 CHECK (composite_risk_index >= 0 AND composite_risk_index <= 1),

    -- Risk category for quick filtering
    risk_category TEXT DEFAULT 'low' CHECK (risk_category IN ('low', 'moderate', 'high', 'critical')),

    -- Metadata
    last_calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE risk_blocks IS 'Geographic blocks with multi-factor risk scores for community safety assessment';
COMMENT ON COLUMN risk_blocks.block_id IS 'Unique block identifier (e.g., BLK_40.712_-74.006)';
COMMENT ON COLUMN risk_blocks.lat IS 'Block center latitude';
COMMENT ON COLUMN risk_blocks.lng IS 'Block center longitude';
COMMENT ON COLUMN risk_blocks.crime_score IS 'Crime risk: 0 (safest) to 1 (highest crime)';
COMMENT ON COLUMN risk_blocks.blight_score IS 'Blight risk: 0 (pristine) to 1 (severe abandonment)';
COMMENT ON COLUMN risk_blocks.emergency_response_score IS 'Emergency response risk: 0 (fast) to 1 (slow)';
COMMENT ON COLUMN risk_blocks.air_quality_score IS 'Air quality risk: 0 (clean) to 1 (polluted)';
COMMENT ON COLUMN risk_blocks.heat_exposure_score IS 'Heat island risk: 0 (cool) to 1 (extreme heat)';
COMMENT ON COLUMN risk_blocks.traffic_speed_score IS 'Traffic speed risk: 0 (safe speeds) to 1 (dangerous speeds)';
COMMENT ON COLUMN risk_blocks.composite_risk_index IS 'Weighted composite of all risk factors';
COMMENT ON COLUMN risk_blocks.risk_category IS 'Risk level: low (<0.3), moderate (0.3-0.5), high (0.5-0.7), critical (>0.7)';

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_risk_blocks_location ON risk_blocks USING btree (lat, lng);
CREATE INDEX IF NOT EXISTS idx_risk_blocks_block_id ON risk_blocks (block_id);
CREATE INDEX IF NOT EXISTS idx_risk_blocks_composite ON risk_blocks (composite_risk_index DESC);
CREATE INDEX IF NOT EXISTS idx_risk_blocks_category ON risk_blocks (risk_category);
CREATE INDEX IF NOT EXISTS idx_risk_blocks_calculated_at ON risk_blocks (last_calculated_at DESC);

-- =====================================================
-- TABLE: risk_factors
-- Raw data points for each risk factor calculation
-- =====================================================
CREATE TABLE IF NOT EXISTS risk_factors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    block_id TEXT NOT NULL,
    factor_type TEXT NOT NULL CHECK (factor_type IN ('crime', 'blight', 'emergency_response', 'air_quality', 'heat_exposure', 'traffic_speed')),

    -- Raw values (factor-specific)
    raw_value DOUBLE PRECISION NOT NULL,
    raw_unit TEXT, -- e.g., 'incidents', 'minutes', 'aqi', 'celsius', 'mph'

    -- Normalized score (0-1)
    normalized_score DOUBLE PRECISION CHECK (normalized_score >= 0 AND normalized_score <= 1),

    -- Metadata
    data_source TEXT DEFAULT 'synthetic',
    measurement_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE risk_factors IS 'Individual risk factor measurements with raw values and normalized scores';
COMMENT ON COLUMN risk_factors.block_id IS 'Reference to block identifier';
COMMENT ON COLUMN risk_factors.factor_type IS 'Type of risk factor being measured';
COMMENT ON COLUMN risk_factors.raw_value IS 'Original measurement value before normalization';
COMMENT ON COLUMN risk_factors.raw_unit IS 'Unit of measurement for raw value';
COMMENT ON COLUMN risk_factors.normalized_score IS 'Score normalized to 0-1 scale';
COMMENT ON COLUMN risk_factors.data_source IS 'Source of data (synthetic, city_api, sensor, etc.)';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_risk_factors_block_id ON risk_factors (block_id);
CREATE INDEX IF NOT EXISTS idx_risk_factors_type ON risk_factors (factor_type);
CREATE INDEX IF NOT EXISTS idx_risk_factors_measurement_date ON risk_factors (measurement_date DESC);
CREATE INDEX IF NOT EXISTS idx_risk_factors_composite ON risk_factors (block_id, factor_type, measurement_date DESC);

-- =====================================================
-- TABLE: risk_history
-- Historical tracking of risk index changes over time
-- =====================================================
CREATE TABLE IF NOT EXISTS risk_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    block_id TEXT NOT NULL,
    composite_risk_index DOUBLE PRECISION CHECK (composite_risk_index >= 0 AND composite_risk_index <= 1),
    risk_category TEXT CHECK (risk_category IN ('low', 'moderate', 'high', 'critical')),

    -- Factor scores at this snapshot
    crime_score DOUBLE PRECISION,
    blight_score DOUBLE PRECISION,
    emergency_response_score DOUBLE PRECISION,
    air_quality_score DOUBLE PRECISION,
    heat_exposure_score DOUBLE PRECISION,
    traffic_speed_score DOUBLE PRECISION,

    snapshot_date TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE risk_history IS 'Historical snapshots of risk scores for trend analysis';
COMMENT ON COLUMN risk_history.block_id IS 'Reference to block identifier';
COMMENT ON COLUMN risk_history.snapshot_date IS 'Timestamp of this risk calculation';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_risk_history_block_id ON risk_history (block_id);
CREATE INDEX IF NOT EXISTS idx_risk_history_snapshot_date ON risk_history (snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_risk_history_composite ON risk_history (block_id, snapshot_date DESC);

-- =====================================================
-- TABLE: risk_config
-- Configurable weights and thresholds for risk calculations
-- =====================================================
CREATE TABLE IF NOT EXISTS risk_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_name TEXT NOT NULL UNIQUE,

    -- Factor weights (sum should be 1.0)
    crime_weight DOUBLE PRECISION DEFAULT 0.25 CHECK (crime_weight >= 0 AND crime_weight <= 1),
    blight_weight DOUBLE PRECISION DEFAULT 0.15 CHECK (blight_weight >= 0 AND blight_weight <= 1),
    emergency_response_weight DOUBLE PRECISION DEFAULT 0.20 CHECK (emergency_response_weight >= 0 AND emergency_response_weight <= 1),
    air_quality_weight DOUBLE PRECISION DEFAULT 0.15 CHECK (air_quality_weight >= 0 AND air_quality_weight <= 1),
    heat_exposure_weight DOUBLE PRECISION DEFAULT 0.10 CHECK (heat_exposure_weight >= 0 AND heat_exposure_weight <= 1),
    traffic_speed_weight DOUBLE PRECISION DEFAULT 0.15 CHECK (traffic_speed_weight >= 0 AND traffic_speed_weight <= 1),

    -- Normalization thresholds (max values for each factor)
    crime_max_incidents INT DEFAULT 50,
    blight_max_properties INT DEFAULT 20,
    emergency_max_minutes INT DEFAULT 30,
    air_quality_max_aqi INT DEFAULT 200,
    heat_exposure_max_celsius DOUBLE PRECISION DEFAULT 45.0,
    traffic_speed_max_mph INT DEFAULT 65,

    -- Spatial influence (how much nearby blocks affect each other)
    spatial_radius_meters DOUBLE PRECISION DEFAULT 500.0,
    spatial_decay_factor DOUBLE PRECISION DEFAULT 0.5 CHECK (spatial_decay_factor >= 0 AND spatial_decay_factor <= 1),

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE risk_config IS 'Configurable parameters for risk index calculations';
COMMENT ON COLUMN risk_config.config_name IS 'Configuration profile name (e.g., default, public_safety_focus, environmental_focus)';
COMMENT ON COLUMN risk_config.spatial_radius_meters IS 'Radius for spatial aggregation influence';
COMMENT ON COLUMN risk_config.spatial_decay_factor IS 'How much influence decays with distance (0-1)';

-- Insert default configuration
INSERT INTO risk_config (config_name, config_name) VALUES ('default', 'default')
ON CONFLICT (config_name) DO NOTHING;

-- =====================================================
-- TRIGGERS: Auto-update updated_at timestamps
-- =====================================================

-- Apply trigger to risk_blocks table
DROP TRIGGER IF EXISTS update_risk_blocks_updated_at ON risk_blocks;
CREATE TRIGGER update_risk_blocks_updated_at
    BEFORE UPDATE ON risk_blocks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to risk_config table
DROP TRIGGER IF EXISTS update_risk_config_updated_at ON risk_config;
CREATE TRIGGER update_risk_config_updated_at
    BEFORE UPDATE ON risk_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS: Useful query shortcuts
-- =====================================================

-- High-risk blocks summary
CREATE OR REPLACE VIEW high_risk_blocks AS
SELECT
    block_id,
    lat,
    lng,
    composite_risk_index,
    risk_category,
    crime_score,
    blight_score,
    emergency_response_score,
    air_quality_score,
    heat_exposure_score,
    traffic_speed_score,
    last_calculated_at
FROM risk_blocks
WHERE risk_category IN ('high', 'critical')
ORDER BY composite_risk_index DESC;

COMMENT ON VIEW high_risk_blocks IS 'Quick access to blocks with high or critical risk levels';

-- Risk factor trends by block
CREATE OR REPLACE VIEW risk_trends AS
SELECT
    block_id,
    COUNT(*) as snapshot_count,
    MIN(composite_risk_index) as min_risk,
    MAX(composite_risk_index) as max_risk,
    AVG(composite_risk_index) as avg_risk,
    STDDEV(composite_risk_index) as risk_volatility,
    MAX(snapshot_date) as latest_snapshot,
    MIN(snapshot_date) as earliest_snapshot
FROM risk_history
GROUP BY block_id
ORDER BY avg_risk DESC;

COMMENT ON VIEW risk_trends IS 'Statistical summary of risk trends per block';

-- Latest risk factors by block
CREATE OR REPLACE VIEW latest_risk_factors AS
SELECT DISTINCT ON (block_id, factor_type)
    block_id,
    factor_type,
    raw_value,
    raw_unit,
    normalized_score,
    data_source,
    measurement_date
FROM risk_factors
ORDER BY block_id, factor_type, measurement_date DESC;

COMMENT ON VIEW latest_risk_factors IS 'Most recent measurement for each risk factor per block';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'NeuraCity Risk Index Schema Created Successfully';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables created: 4';
    RAISE NOTICE '  - risk_blocks (composite scores)';
    RAISE NOTICE '  - risk_factors (raw measurements)';
    RAISE NOTICE '  - risk_history (time-series tracking)';
    RAISE NOTICE '  - risk_config (configurable parameters)';
    RAISE NOTICE '';
    RAISE NOTICE 'Views created: 3';
    RAISE NOTICE '  - high_risk_blocks';
    RAISE NOTICE '  - risk_trends';
    RAISE NOTICE '  - latest_risk_factors';
    RAISE NOTICE '';
    RAISE NOTICE 'Risk Factors Tracked: 6';
    RAISE NOTICE '  - Crime (incidents)';
    RAISE NOTICE '  - Blight (property condition)';
    RAISE NOTICE '  - Emergency Response (911 wait time)';
    RAISE NOTICE '  - Air Quality (pollution)';
    RAISE NOTICE '  - Heat Exposure (urban heat island)';
    RAISE NOTICE '  - Traffic Speed (dangerous speeds)';
    RAISE NOTICE '========================================';
END $$;
