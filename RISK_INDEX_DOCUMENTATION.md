# NeuraCity Community Risk Index

## Overview

The Community Risk Index is a comprehensive scoring system that evaluates neighborhood safety and livability by combining six key risk factors into a single composite metric (0-1 scale). This system helps city planners, emergency services, and community stakeholders identify areas requiring intervention.

## Table of Contents

1. [Risk Factors](#risk-factors)
2. [Scoring Methodology](#scoring-methodology)
3. [Composite Score Calculation](#composite-score-calculation)
4. [Spatial Aggregation](#spatial-aggregation)
5. [Database Schema](#database-schema)
6. [API Usage](#api-usage)
7. [Data Generation](#data-generation)
8. [Performance Considerations](#performance-considerations)

---

## Risk Factors

Each factor is scored on a 0-1 scale where **0 = lowest risk** and **1 = highest risk**.

### 1. Crime Score

**Definition**: Risk based on crime incident frequency and severity.

**Methodology**:
- Linear normalization based on incidents per month
- Severity multiplier for violent crimes (1.5x) vs. property crimes (1.0x)
- Threshold: 50 incidents/month = 1.0 score

**Formula**:
```
crime_score = min(1.0, (incidents_per_month * severity_multiplier) / max_incidents)
```

**Example**:
- 10 property crimes/month: 10 * 1.0 / 50 = **0.20**
- 15 violent crimes/month: 15 * 1.5 / 50 = **0.45**

**Data Sources** (synthetic):
- Historical crime reports
- Incident type classification
- Temporal patterns

---

### 2. Blight Score

**Definition**: Risk based on property abandonment and deterioration.

**Methodology**:
- Weighted sum of three components:
  - Abandoned buildings: 3x weight (highest impact)
  - Code violations: 2x weight (moderate impact)
  - Vacant lots: 1x weight (lower impact)
- Normalized against max threshold

**Formula**:
```
weighted_blight = (abandoned_buildings * 3) + (code_violations * 2) + (vacant_lots * 1)
blight_score = min(1.0, weighted_blight / (max_properties * 6))
```

**Example**:
- 2 abandoned buildings, 5 violations, 3 vacant lots
- Weighted sum: (2*3) + (5*2) + (3*1) = 6 + 10 + 3 = 19
- Score: 19 / (20 * 6) = 19/120 = **0.158**

**Data Sources** (synthetic):
- Building inspection records
- Property assessment data
- Code enforcement database

---

### 3. Emergency Response Score

**Definition**: Risk based on 911 response time delays.

**Methodology**:
- Combines average response time (70%) and 90th percentile (30%)
- 90th percentile captures worst-case scenarios
- Non-linear scaling (square root) to emphasize severe delays
- Threshold: 30 minutes = 1.0 score

**Formula**:
```
avg_component = avg_response_time / max_minutes
p90_component = p90_response_time / max_minutes
combined = (0.7 * avg_component) + (0.3 * p90_component)
emergency_score = min(1.0, sqrt(combined))
```

**Example**:
- Average: 8.5 minutes, P90: 12 minutes, Max: 30 minutes
- Combined: (0.7 * 8.5/30) + (0.3 * 12/30) = 0.198 + 0.120 = 0.318
- Score: sqrt(0.318) = **0.564**

**Data Sources** (synthetic):
- 911 dispatch logs
- CAD (Computer-Aided Dispatch) data
- Geographic routing analysis

---

### 4. Air Quality Score

**Definition**: Risk based on pollution levels (AQI and PM2.5).

**Methodology**:
- Primary: AQI-based with non-linear scaling matching EPA categories
- Secondary: PM2.5 concentration (if available)
- Blended score: 70% AQI + 30% PM2.5

**AQI Categories**:
| AQI Range | Health Category | Score Range |
|-----------|----------------|-------------|
| 0-50 | Good | 0.00 - 0.25 |
| 51-100 | Moderate | 0.25 - 0.50 |
| 101-150 | Unhealthy for Sensitive | 0.50 - 0.75 |
| 151-200 | Unhealthy | 0.75 - 1.00 |
| 200+ | Very Unhealthy/Hazardous | 1.00 |

**Formula**:
```
if AQI <= 50:   aqi_score = AQI / 200
if AQI <= 100:  aqi_score = 0.25 + (AQI - 50) / 200
if AQI <= 150:  aqi_score = 0.50 + (AQI - 100) / 200
if AQI > 150:   aqi_score = 0.75 + (AQI - 150) / 200

pm25_score = min(1.0, PM2.5 / 100)  # Cap at 100 µg/m³
final_score = (0.7 * aqi_score) + (0.3 * pm25_score)
```

**Example**:
- AQI: 75, PM2.5: 20 µg/m³
- AQI score: 0.25 + (75-50)/200 = 0.375
- PM2.5 score: 20/100 = 0.20
- Final: (0.7 * 0.375) + (0.3 * 0.20) = **0.323**

**Data Sources** (synthetic):
- Air quality monitoring stations
- EPA AirNow API
- Satellite pollution data

---

### 5. Heat Exposure Score

**Definition**: Risk from urban heat island effect.

**Methodology**:
- Temperature component (60%): Average and max temperatures
- Environmental component (40%): Tree canopy and impervious surfaces
- Heat islands: concrete/asphalt areas run 2-5°C hotter than parks

**Formula**:
```
# Temperature component (60%)
avg_temp_score = (avg_temp - 20) / (max_celsius - 20)
max_temp_score = (max_temp - 25) / (max_celsius - 25)
temp_component = (0.6 * avg_temp_score) + (0.4 * max_temp_score)

# Environmental component (40%)
canopy_risk = 1.0 - (tree_canopy_percent / 100)  # Low canopy = high risk
impervious_risk = impervious_surface_percent / 100  # High concrete = high risk
env_component = (0.5 * canopy_risk) + (0.5 * impervious_risk)

# Combine
heat_score = (0.6 * temp_component) + (0.4 * env_component)
```

**Example**:
- Avg temp: 28°C, Max temp: 35°C
- Tree canopy: 15%, Impervious surface: 75%
- Temp component: (0.6 * (28-20)/(45-20)) + (0.4 * (35-25)/(45-25)) = 0.192 + 0.200 = 0.392
- Env component: (0.5 * 0.85) + (0.5 * 0.75) = 0.425 + 0.375 = 0.800
- Final: (0.6 * 0.392) + (0.4 * 0.800) = **0.555**

**Data Sources** (synthetic):
- Weather station data
- Satellite thermal imaging
- Land cover analysis
- Urban tree inventory

---

### 6. Traffic Speed Score

**Definition**: Risk from dangerous vehicle speeds in pedestrian areas.

**Methodology**:
- Speed thresholds vary by road type
- 85th percentile speed indicates speeding behavior
- Pedestrian volume multiplier increases risk at same speed

**Safe Speed Thresholds**:
| Road Type | Safe Speed |
|-----------|-----------|
| Residential | 25 mph |
| Arterial | 35 mph |
| Highway | 55 mph |

**Pedestrian Multiplier**:
| Daily Volume | Multiplier |
|--------------|-----------|
| < 50 | 1.0x |
| 50-200 | 1.3x |
| 200+ | 1.6x |

**Formula**:
```
avg_speed_score = max(0, (avg_speed - safe_threshold) / (max_speed - safe_threshold))
p85_speed_score = max(0, (p85_speed - safe_threshold - 10) / (max_speed - safe_threshold))
speed_component = (0.6 * avg_speed_score) + (0.4 * p85_speed_score)

# Apply pedestrian multiplier
traffic_score = min(1.0, speed_component * ped_multiplier)
```

**Example**:
- Arterial road (35 mph safe threshold)
- Avg speed: 40 mph, P85: 48 mph
- Pedestrian volume: 150/day (1.3x multiplier)
- Speed component: (0.6 * (40-35)/(65-35)) + (0.4 * (48-35-10)/(65-35)) = 0.100 + 0.043 = 0.143
- Final: 0.143 * 1.3 = **0.186**

**Data Sources** (synthetic):
- Traffic speed sensors
- GPS probe data
- Pedestrian counters
- Road classification database

---

## Composite Score Calculation

The **Composite Risk Index** combines all six factors using configurable weights.

### Default Weights

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Crime | 0.25 | Public safety is primary concern |
| Emergency Response | 0.20 | Critical for acute incidents |
| Blight | 0.15 | Indicates neighborhood decline |
| Air Quality | 0.15 | Long-term health impact |
| Traffic Speed | 0.15 | Pedestrian safety |
| Heat Exposure | 0.10 | Seasonal/climate impact |
| **Total** | **1.00** | |

### Formula

```
composite_risk_index =
    (crime_score * 0.25) +
    (blight_score * 0.15) +
    (emergency_response_score * 0.20) +
    (air_quality_score * 0.15) +
    (heat_exposure_score * 0.10) +
    (traffic_speed_score * 0.15)
```

### Risk Categories

The composite score maps to four categories:

| Composite Score | Category | Description | Action Required |
|----------------|----------|-------------|----------------|
| 0.00 - 0.29 | **Low** | Minimal risk | Routine monitoring |
| 0.30 - 0.49 | **Moderate** | Some concerns | Enhanced monitoring |
| 0.50 - 0.69 | **High** | Significant risk | Active intervention |
| 0.70 - 1.00 | **Critical** | Severe risk | Urgent intervention |

### Example Calculation

**Block: BLK_40.712_-74.006**

Individual scores:
- Crime: 0.30
- Blight: 0.16
- Emergency Response: 0.56
- Air Quality: 0.32
- Heat Exposure: 0.56
- Traffic Speed: 0.19

Composite:
```
(0.30 * 0.25) + (0.16 * 0.15) + (0.56 * 0.20) + (0.32 * 0.15) + (0.56 * 0.10) + (0.19 * 0.15)
= 0.075 + 0.024 + 0.112 + 0.048 + 0.056 + 0.029
= 0.344
```

**Result**: Composite Risk Index = **0.344** → **MODERATE** category

---

## Spatial Aggregation

### Spatial Smoothing

Risk doesn't exist in isolation. Nearby high-risk blocks influence target block risk through **spatial smoothing**.

**Why Smoothing?**
- Prevents isolated "islands" of low risk in high-risk zones
- Reflects geographic reality (crime/blight spreads)
- More accurate than block-by-block analysis

### Formula

```
smoothed_risk = (target_risk * 1.0 + Σ(nearby_risk * weight)) / (1.0 + Σ(weight))

where:
weight = decay_factor ^ (distance / radius)
```

### Parameters

- **Spatial Radius**: 500 meters (default)
- **Decay Factor**: 0.5 (default)
  - 0.0 = no influence from neighbors
  - 1.0 = full influence regardless of distance

### Example

**Target Block**: Risk = 0.40, Location = (40.712, -74.006)

**Nearby Blocks** (within 500m):
| Block | Risk | Distance | Weight | Contribution |
|-------|------|----------|--------|--------------|
| Block A | 0.60 | 200m | 0.5^(200/500) = 0.76 | 0.60 * 0.76 = 0.456 |
| Block B | 0.35 | 350m | 0.5^(350/500) = 0.61 | 0.35 * 0.61 = 0.214 |
| Block C | 0.80 | 450m | 0.5^(450/500) = 0.53 | 0.80 * 0.53 = 0.424 |

Calculation:
```
smoothed_risk = (0.40 * 1.0 + 0.456 + 0.214 + 0.424) / (1.0 + 0.76 + 0.61 + 0.53)
              = 1.494 / 2.90
              = 0.515
```

**Result**: Smoothed risk increases from 0.40 to **0.515** due to nearby high-risk blocks.

---

## Database Schema

### Tables

#### 1. `risk_blocks`

Primary table storing current risk scores per block.

```sql
CREATE TABLE risk_blocks (
    id UUID PRIMARY KEY,
    block_id TEXT UNIQUE,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,

    -- Individual factor scores (0-1)
    crime_score DOUBLE PRECISION,
    blight_score DOUBLE PRECISION,
    emergency_response_score DOUBLE PRECISION,
    air_quality_score DOUBLE PRECISION,
    heat_exposure_score DOUBLE PRECISION,
    traffic_speed_score DOUBLE PRECISION,

    -- Composite results
    composite_risk_index DOUBLE PRECISION,
    risk_category TEXT,  -- low, moderate, high, critical

    last_calculated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

**Indexes**:
- `(lat, lng)` - Spatial queries
- `block_id` - Unique identifier
- `composite_risk_index DESC` - High-risk queries
- `risk_category` - Category filtering

---

#### 2. `risk_factors`

Raw measurements for each risk factor.

```sql
CREATE TABLE risk_factors (
    id UUID PRIMARY KEY,
    block_id TEXT,
    factor_type TEXT,  -- crime, blight, emergency_response, etc.

    raw_value DOUBLE PRECISION,
    raw_unit TEXT,
    normalized_score DOUBLE PRECISION,

    data_source TEXT,
    measurement_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ
);
```

**Purpose**: Store raw data before normalization for auditing and recalculation.

---

#### 3. `risk_history`

Time-series snapshots for trend analysis.

```sql
CREATE TABLE risk_history (
    id UUID PRIMARY KEY,
    block_id TEXT,

    composite_risk_index DOUBLE PRECISION,
    risk_category TEXT,

    -- Factor scores at snapshot
    crime_score DOUBLE PRECISION,
    blight_score DOUBLE PRECISION,
    -- ... (all factor scores)

    snapshot_date TIMESTAMPTZ
);
```

**Purpose**: Track risk changes over time, identify improving/declining areas.

---

#### 4. `risk_config`

Configurable parameters for calculations.

```sql
CREATE TABLE risk_config (
    id UUID PRIMARY KEY,
    config_name TEXT UNIQUE,

    -- Weights (must sum to 1.0)
    crime_weight DOUBLE PRECISION,
    blight_weight DOUBLE PRECISION,
    -- ... (all weights)

    -- Normalization thresholds
    crime_max_incidents INT,
    blight_max_properties INT,
    -- ... (all max values)

    -- Spatial parameters
    spatial_radius_meters DOUBLE PRECISION,
    spatial_decay_factor DOUBLE PRECISION,

    is_active BOOLEAN
);
```

**Purpose**: Support multiple configuration profiles (default, public_safety_focus, environmental_focus).

---

## API Usage

### Base URL
```
http://localhost:8000/api/v1/risk-index
```

### Endpoints

#### Get Risk Blocks

```http
GET /risk-index/blocks?risk_category=high&limit=100
```

**Query Parameters**:
- `risk_category`: Filter by category (low, moderate, high, critical)
- `min_risk`: Minimum composite score (0-1)
- `max_risk`: Maximum composite score (0-1)
- `limit`: Max results (default: 1000)

**Response**:
```json
[
  {
    "block_id": "BLK_40.712_-74.006",
    "lat": 40.712,
    "lng": -74.006,
    "crime_score": 0.30,
    "blight_score": 0.16,
    "emergency_response_score": 0.56,
    "air_quality_score": 0.32,
    "heat_exposure_score": 0.56,
    "traffic_speed_score": 0.19,
    "composite_risk_index": 0.344,
    "risk_category": "moderate",
    "last_calculated_at": "2025-11-15T10:30:00Z"
  }
]
```

---

#### Get Risk Block by ID

```http
GET /risk-index/blocks/BLK_40.712_-74.006
```

**Response**: Single block object (same format as above).

---

#### Get Blocks in Geographic Bounds

```http
GET /risk-index/blocks/bounds?lat_min=40.71&lat_max=40.72&lng_min=-74.01&lng_max=-74.00
```

**Use Case**: Map view showing risk blocks in visible area.

---

#### Recalculate Risk for Block

```http
POST /risk-index/recalculate
```

**Request Body**:
```json
{
  "block_id": "BLK_40.712_-74.006",
  "lat": 40.712,
  "lng": -74.006,
  "crime_data": {
    "incidents_per_month": 15,
    "severity_multiplier": 1.2
  },
  "blight_data": {
    "abandoned_buildings": 2,
    "vacant_lots": 3,
    "code_violations": 5
  },
  "emergency_data": {
    "avg_response_time_minutes": 8.5,
    "percentile_90_time_minutes": 12.0
  },
  "air_quality_data": {
    "aqi_value": 75,
    "pm25_concentration": 20.0
  },
  "heat_data": {
    "avg_temperature_celsius": 28,
    "max_temperature_celsius": 35,
    "tree_canopy_percent": 15,
    "impervious_surface_percent": 75
  },
  "traffic_data": {
    "avg_speed_mph": 35,
    "percentile_85_speed_mph": 42,
    "pedestrian_volume": 150,
    "road_type": "arterial"
  },
  "apply_spatial_smoothing": true,
  "save_to_database": true,
  "config_name": "default"
}
```

**Response**: Calculated risk scores (same format as GET response).

---

#### Get Risk Statistics

```http
GET /risk-index/statistics
```

**Response**:
```json
{
  "total_blocks": 200,
  "average_risk_index": 0.423,
  "max_risk_index": 0.856,
  "max_risk_block_id": "BLK_40.750_-74.012",
  "category_distribution": {
    "low": {"count": 45, "percentage": 22.5},
    "moderate": {"count": 78, "percentage": 39.0},
    "high": {"count": 62, "percentage": 31.0},
    "critical": {"count": 15, "percentage": 7.5}
  }
}
```

---

#### Get Risk History

```http
GET /risk-index/history/BLK_40.712_-74.006?days=30
```

**Response**: Array of historical snapshots for trend analysis.

---

## Data Generation

### Synthetic Data Generator

**Location**: `database/seeds/generate_risk_data.py`

**Usage**:
```bash
cd database/seeds
python generate_risk_data.py --blocks=200 --days=30
```

**Parameters**:
- `--blocks`: Number of geographic blocks to generate (default: 200)
- `--days`: Days of historical data (default: 30)

**What It Generates**:
1. **200 risk blocks** in NYC area (40.70-40.80 lat, -74.02 to -73.95 lng)
2. **Area-specific risk profiles**:
   - Industrial zones: High crime, blight, air quality
   - Park districts: Low across all factors
   - Downtown: High traffic, moderate crime
3. **Time-series data**:
   - Weekly crime snapshots
   - Daily air quality measurements
   - Weekly emergency response times
   - Weekly traffic speed data
4. **Historical snapshots** for trend analysis

**Area Risk Profiles**:
```python
AREA_RISK_PROFILES = {
    'DOWNTOWN': {
        'crime_base': 0.6,
        'air_quality_base': 0.6,
        'traffic_base': 0.7
    },
    'PARK_DISTRICT': {
        'crime_base': 0.2,
        'air_quality_base': 0.2,
        'heat_base': 0.2  # More trees, less heat
    },
    'INDUSTRIAL': {
        'crime_base': 0.7,
        'blight_base': 0.8,
        'air_quality_base': 0.9  # Factory pollution
    }
}
```

**Output**:
```
Generating 200 risk blocks...
Generating crime data for 30 days...
Generating air quality data for 30 days...
...
✓ Data generation complete!

SUMMARY
Total blocks: 200
Total factor measurements: 7,800
Total historical snapshots: 800

Risk category distribution:
  LOW: 42 (21.0%)
  MODERATE: 81 (40.5%)
  HIGH: 58 (29.0%)
  CRITICAL: 19 (9.5%)
```

---

## Performance Considerations

### Large-Scale Calculations

**Challenge**: Calculating risk for thousands of blocks with spatial smoothing.

**Optimizations**:

1. **Batch Processing**:
   ```python
   # Update in batches of 500
   await db.batch_upsert_risk_blocks(blocks)
   ```

2. **Spatial Indexing**:
   - PostgreSQL BTREE index on `(lat, lng)`
   - Enables fast bounding box queries
   - Critical for spatial smoothing neighbor lookup

3. **Caching**:
   - Cache configuration in memory (`@lru_cache`)
   - Avoid repeated database queries for config

4. **Incremental Updates**:
   ```python
   # Only recalculate blocks with new data
   recent_factors = await db.get_risk_factors(
       measurement_date__gte=last_update_time
   )
   ```

### Database Query Optimization

**Bounding Box Query** (O(n) → O(log n)):
```sql
-- Efficient with index
SELECT * FROM risk_blocks
WHERE lat >= 40.71 AND lat <= 40.72
  AND lng >= -74.01 AND lng <= -74.00;
```

**Category Filtering** (O(n) → O(log n)):
```sql
-- Efficient with index
SELECT * FROM risk_blocks
WHERE risk_category = 'critical'
ORDER BY composite_risk_index DESC;
```

### API Response Times

**Benchmarks** (200 blocks):

| Endpoint | Response Time | Notes |
|----------|--------------|-------|
| GET /blocks | ~50ms | With indexes |
| GET /blocks/bounds | ~30ms | Geographic query |
| POST /recalculate (single) | ~100ms | Without spatial smoothing |
| POST /recalculate (single) | ~250ms | With spatial smoothing |
| POST /recalculate-all | ~15s | 200 blocks, batched |

### Scaling Recommendations

**10,000+ blocks**:
- Use background job queue (Celery) for bulk recalculation
- Implement result pagination (limit=1000 per request)
- Consider materialized views for frequently accessed aggregates

**Real-time Updates**:
- Use database triggers to auto-update `last_calculated_at`
- Implement webhook notifications for risk category changes
- Cache high-traffic queries (Redis)

---

## Configuration Profiles

### Creating Custom Profiles

Example: **Public Safety Focus** (emphasize crime and emergency response)

```sql
INSERT INTO risk_config (
    config_name,
    crime_weight, blight_weight, emergency_response_weight,
    air_quality_weight, heat_exposure_weight, traffic_speed_weight
) VALUES (
    'public_safety_focus',
    0.35,  -- Increased from 0.25
    0.10,  -- Decreased from 0.15
    0.30,  -- Increased from 0.20
    0.10,  -- Decreased from 0.15
    0.05,  -- Decreased from 0.10
    0.10   -- Decreased from 0.15
);
```

Then use in API:
```http
POST /risk-index/recalculate
{
  "config_name": "public_safety_focus",
  ...
}
```

---

## Future Enhancements

1. **Machine Learning Integration**:
   - Predict future risk based on trends
   - Identify leading indicators of neighborhood decline

2. **Real-Time Data Sources**:
   - Live crime feeds from police APIs
   - Real-time air quality from sensors
   - Traffic speed from GPS probes

3. **Interactive Visualization**:
   - Heat map overlay on frontend map
   - Time-lapse showing risk evolution
   - Comparative analysis tools

4. **Automated Alerting**:
   - Notify city officials when block transitions to "critical"
   - Weekly risk summary emails
   - Threshold-based triggers

5. **Community Engagement**:
   - Allow residents to view their block's score
   - Provide improvement recommendations
   - Track intervention effectiveness

---

## References

- **AQI Categories**: EPA AirNow (https://www.airnow.gov/aqi/aqi-basics/)
- **Heat Island Effect**: EPA Urban Heat Islands (https://www.epa.gov/heatislands)
- **Traffic Speed Safety**: FHWA Speed Management (https://highways.dot.gov/safety/speed-management)
- **Spatial Smoothing**: Tobler's First Law of Geography

---

## Support

For questions or issues:
- Documentation: `/RISK_INDEX_DOCUMENTATION.md`
- Service code: `/backend/app/services/risk_index_service.py`
- API endpoints: `/backend/app/api/endpoints/risk_index.py`
- Database schema: `/database/schema_risk_index.sql`

---

**Last Updated**: 2025-11-15
**Version**: 1.0.0
