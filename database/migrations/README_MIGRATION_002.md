# Migration 002: Gamification, Accident History, and Community Risk Index

## Overview

This migration extends the NeuraCity database with three major feature sets designed to enhance civic engagement, track accident patterns, and assess community risk across geographic areas.

## New Features

### 1. Gamification System

**Purpose**: Incentivize citizen participation through points, ranks, and leaderboards.

#### Tables Created

**users**
- Primary table for gamification user accounts
- Tracks total points, rank progression, and profile information
- Ranks: bronze (0-499), silver (500-1999), gold (2000-4999), platinum (5000-9999), diamond (10000+)
- Auto-updates rank based on total_points via trigger

**points_transactions**
- Individual point-earning events with detailed tracking
- Links to users and optionally to issues
- Transaction types:
  - `issue_report`: 10-25 points (reporting new issue)
  - `issue_verified`: 15-30 points (validating existing issue)
  - `issue_resolved`: 30-50 points (issue marked resolved)
  - `community_vote`: 2-5 points (voting on issues)
  - `helpful_description`: 5-15 points (quality descriptions)
  - `photo_quality`: 10-20 points (high-quality evidence)
  - `repeat_reporter`: 25-40 points (consistent participation)
  - `first_in_area`: 50-75 points (first reporter in area)
  - `streak_bonus`: 100-200 points (daily/weekly streaks)

**leaderboard**
- Pre-calculated rankings for performance optimization
- Updated via `refresh_leaderboard()` function
- Includes position, activity stats, and cached user data

#### Views Created

**top_users_leaderboard**
- Real-time rankings with detailed activity metrics
- Shows issues reported, verified, and last activity
- Ordered by total_points DESC

**user_activity_summary**
- Per-user engagement metrics
- Tracks points earned in last 7 and 30 days
- Useful for identifying active vs. inactive users

#### Triggers

- **Auto-rank calculation**: Updates user rank when total_points changes
- **Auto-point addition**: Automatically adds transaction points to user total
- **Auto-timestamp updates**: Maintains updated_at on user records

---

### 2. Accident History Tracking

**Purpose**: Build historical accident database for pattern analysis, hotspot identification, and predictive safety modeling.

#### Tables Created

**accident_history**
- Historical accident records with spatial indexing
- Uses PostGIS GEOGRAPHY type for efficient spatial queries
- Captures severity, timing, weather, and area context
- Auto-populates location geometry from lat/lng via trigger

**Key Columns**:
- `location`: PostGIS geography point (EPSG:4326)
- `severity`, `urgency`: Copied from original issue
- `weather_conditions`: Weather at time of accident
- `time_of_day`: morning, afternoon, evening, night
- `occurred_at`: Actual accident timestamp (not report time)

#### Views Created

**accident_hotspots**
- Areas with 3+ accidents in last 90 days
- Aggregates by area_name with avg severity/urgency
- Shows temporal range (first to most recent)
- Ordered by accident_count DESC

#### Spatial Functions

**get_nearby_accidents(lat, lng, radius_meters)**
```sql
-- Find all accidents within 500m of a location
SELECT * FROM get_nearby_accidents(40.7128, -74.0060, 500);
```
- Returns accidents within specified radius
- Includes distance_meters for each result
- Ordered by proximity (nearest first)
- Uses PostGIS ST_DWithin for performance

**Example Use Cases**:
- Route safety scoring (avoid accident-prone areas)
- Real-time alerts when near accident hotspots
- Insurance risk assessment
- Urban planning and traffic calming initiatives

---

### 3. Community Risk Index

**Purpose**: Provide comprehensive risk assessment across city blocks for equity analysis, resource allocation, and community health tracking.

#### Tables Created

**block_risk_scores**
- Geographic blocks with multi-dimensional risk scores
- Overall score weighted from 7 component scores
- Uses PostGIS for spatial queries
- Auto-populates geometry from lat/lng via trigger

**Risk Components** (all 0-1 scale, higher = worse):
- `crime_score` (25% weight): Crime incident density
- `traffic_score` (20% weight): Traffic danger/congestion
- `blight_score` (15% weight): Property neglect indicators
- `noise_score` (12% weight): Noise pollution levels
- `air_quality_score` (12% weight): Air pollution (PM2.5, etc.)
- `heat_score` (8% weight): Urban heat island effect
- `wait_time_score` (8% weight): Service response delays

**Overall Risk Calculation**:
```
overall_risk_score =
    crime_score * 0.25 +
    traffic_score * 0.20 +
    blight_score * 0.15 +
    noise_score * 0.12 +
    air_quality_score * 0.12 +
    heat_score * 0.08 +
    wait_time_score * 0.08
```

#### Views Created

**high_risk_blocks**
- Blocks with overall_risk_score >= 0.7
- Sorted by risk score and accident count
- Includes all component scores for detailed analysis

#### Spatial Functions

**get_location_risk_score(lat, lng)**
```sql
-- Get risk score for a specific location
SELECT * FROM get_location_risk_score(40.7128, -74.0060);
```
- Returns nearest block's risk score
- Includes distance to block center
- Useful for real-time risk lookups

**Example Use Cases**:
- Equity dashboards (identify underserved areas)
- Resource allocation prioritization
- Route planning (avoid high-risk blocks)
- Community health interventions
- Environmental justice analysis

---

## Database Schema Summary

### Tables Added (5 total)

| Table | Rows (typical) | Primary Purpose |
|-------|----------------|-----------------|
| `users` | 100-10,000 | User accounts |
| `points_transactions` | 1,000-1,000,000 | Point history |
| `leaderboard` | Same as users | Cached rankings |
| `accident_history` | 100-100,000 | Accident records |
| `block_risk_scores` | 100-10,000 | Block risk data |

### Indexes Added (28 total)

**Performance-critical spatial indexes**:
- `idx_accident_history_location` (GIST on geography)
- `idx_block_risk_scores_geometry` (GIST on geography)
- `idx_accident_history_coords` (B-tree on lat, lng)
- `idx_block_risk_scores_coords` (B-tree on lat, lng)

**Query optimization indexes**:
- User lookups: username, email, total_points, rank
- Transaction filtering: user_id, transaction_type, created_at
- Leaderboard: position, total_points, rank
- Accident analysis: occurred_at, severity, area_name, time_of_day
- Risk filtering: block_id, overall_risk_score, area_name

### Foreign Key Relationships

```
users (id) <--  points_transactions (user_id) [CASCADE DELETE]
          <--  leaderboard (user_id) [CASCADE DELETE]

issues (id) <-- points_transactions (issue_id) [SET NULL]
           <-- accident_history (issue_id) [CASCADE DELETE]
```

### Triggers Added (5 total)

1. `update_users_updated_at`: Auto-update timestamp on user changes
2. `trigger_update_user_rank`: Auto-calculate rank from total_points
3. `trigger_add_points_to_user`: Add transaction points to user total
4. `trigger_set_accident_location`: Auto-populate PostGIS location
5. `trigger_set_block_geometry`: Auto-populate PostGIS geometry

---

## Installation Instructions

### Step 1: Run Migration SQL

**Option A: Supabase Dashboard**
1. Go to SQL Editor in Supabase dashboard
2. Paste contents of `002_gamification_accident_risk.sql`
3. Click "Run"
4. Verify completion message appears

**Option B: psql command line**
```bash
psql -h db.xxxxx.supabase.co -U postgres -d postgres -f 002_gamification_accident_risk.sql
```

### Step 2: Verify Tables Created

```bash
cd database
python verify.py --detailed
```

Expected output:
```
Database Verification
=====================
12/12 tables exist
12/12 structures valid
7 views accessible
```

### Step 3: Generate Seed Data

```bash
cd database/seeds
python generate_gamification_data.py --users=100 --days=30 --blocks=200
```

This generates:
- 100 users across all rank levels
- ~2,000 points transactions
- ~60-240 accident records (2-8 per day)
- 200 city block risk scores

**Advanced options**:
```bash
# Large dataset for production-like testing
python generate_gamification_data.py --users=1000 --days=365 --blocks=1000

# Minimal dataset for quick testing
python generate_gamification_data.py --users=10 --days=7 --blocks=50
```

### Step 4: Test Spatial Functions

```sql
-- Test nearby accidents function
SELECT * FROM get_nearby_accidents(40.7128, -74.0060, 1000);

-- Test location risk lookup
SELECT * FROM get_location_risk_score(40.7589, -73.9851);

-- Refresh leaderboard
SELECT refresh_leaderboard();
```

---

## Query Examples

### Gamification Queries

**Top 10 Users**
```sql
SELECT username, total_points, rank, position
FROM top_users_leaderboard
LIMIT 10;
```

**User Point History**
```sql
SELECT
    pt.created_at,
    pt.transaction_type,
    pt.points_earned,
    pt.description,
    i.issue_type
FROM points_transactions pt
LEFT JOIN issues i ON pt.issue_id = i.id
WHERE pt.user_id = 'user-uuid-here'
ORDER BY pt.created_at DESC;
```

**Users Who Joined This Month**
```sql
SELECT username, total_points, rank
FROM users
WHERE created_at >= DATE_TRUNC('month', NOW())
ORDER BY total_points DESC;
```

### Accident Analysis Queries

**Recent Accidents in Downtown**
```sql
SELECT
    occurred_at,
    severity,
    weather_conditions,
    time_of_day
FROM accident_history
WHERE area_name = 'DOWNTOWN'
    AND occurred_at >= NOW() - INTERVAL '7 days'
ORDER BY occurred_at DESC;
```

**Accidents Within 1km of Location**
```sql
SELECT
    id,
    lat,
    lng,
    severity,
    distance_meters
FROM get_nearby_accidents(40.7128, -74.0060, 1000)
WHERE occurred_at >= NOW() - INTERVAL '30 days';
```

**Accident Patterns by Time of Day**
```sql
SELECT
    time_of_day,
    COUNT(*) as accident_count,
    AVG(severity) as avg_severity,
    COUNT(*) FILTER (WHERE weather_conditions IN ('rainy', 'snowy', 'foggy')) as bad_weather_count
FROM accident_history
GROUP BY time_of_day
ORDER BY accident_count DESC;
```

### Risk Index Queries

**Highest Risk Blocks in Industrial Area**
```sql
SELECT
    block_id,
    overall_risk_score,
    crime_score,
    traffic_score,
    accident_count
FROM block_risk_scores
WHERE area_name = 'INDUSTRIAL'
ORDER BY overall_risk_score DESC
LIMIT 10;
```

**Environmental Health Analysis**
```sql
SELECT
    area_name,
    AVG(air_quality_score) as avg_air_quality,
    AVG(noise_score) as avg_noise,
    AVG(heat_score) as avg_heat,
    COUNT(*) as block_count
FROM block_risk_scores
GROUP BY area_name
ORDER BY avg_air_quality DESC;
```

**Blocks Needing Intervention**
```sql
SELECT
    block_id,
    lat,
    lng,
    overall_risk_score,
    crime_score,
    blight_score,
    issue_count
FROM high_risk_blocks
WHERE issue_count > 10
ORDER BY overall_risk_score DESC;
```

---

## Performance Considerations

### Spatial Query Optimization

PostGIS geography queries are optimized with GIST indexes. For best performance:

1. **Use geography functions**: `ST_DWithin`, `ST_Distance`
2. **Specify radius limits**: Don't query city-wide without bounds
3. **Filter by timestamp**: Limit historical queries to relevant timeframes

**Good**:
```sql
SELECT * FROM get_nearby_accidents(40.7128, -74.0060, 500)
WHERE occurred_at >= NOW() - INTERVAL '90 days';
```

**Bad**:
```sql
-- Scans entire table
SELECT * FROM accident_history
WHERE ST_Distance(location, ST_MakePoint(-74.0060, 40.7128)::geography) < 500;
```

### Leaderboard Refresh Strategy

The `leaderboard` table is a performance optimization for read-heavy workloads.

**Refresh frequency recommendations**:
- **Real-time app**: Refresh every 5-15 minutes via cron
- **Daily digest**: Refresh once per day at low-traffic hour
- **Manual**: Call `refresh_leaderboard()` after bulk imports

**Setup automated refresh** (Supabase):
```sql
-- Create cron job to refresh every 10 minutes
SELECT cron.schedule(
    'refresh-leaderboard',
    '*/10 * * * *',
    'SELECT refresh_leaderboard();'
);
```

### Index Maintenance

Monitor index usage and bloat:
```sql
-- Check index sizes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## Integration with Existing Services

### Backend Service Extensions

**Recommended new services** (to be created):

**C:\Users\mianm\Downloads\NeuraCity\backend\app\services\gamification_service.py**
- `award_points(user_id, transaction_type, points, issue_id=None)`
- `get_user_rank(user_id)`
- `get_leaderboard(limit=10, offset=0)`

**C:\Users\mianm\Downloads\NeuraCity\backend\app\services\accident_service.py**
- `record_accident(issue_id, lat, lng, severity, occurred_at)`
- `get_nearby_accidents(lat, lng, radius_meters)`
- `get_accident_hotspots(days=90, min_count=3)`

**C:\Users\mianm\Downloads\NeuraCity\backend\app\services\risk_service.py**
- `get_location_risk(lat, lng)`
- `get_high_risk_blocks(min_score=0.7)`
- `calculate_route_risk(waypoints)`

### Frontend Integration Examples

**Leaderboard Component** (`frontend/src/pages/Leaderboard.jsx`):
```javascript
const response = await api.get('/leaderboard?limit=50');
// Display top_users_leaderboard data
```

**Accident Map Layer** (`frontend/src/pages/Map.jsx`):
```javascript
const accidents = await api.get(`/accidents/nearby?lat=${lat}&lng=${lng}&radius=1000`);
// Render accident markers with severity-based colors
```

**Risk Heatmap** (`frontend/src/pages/RiskMap.jsx`):
```javascript
const riskBlocks = await api.get('/risk-scores?area=DOWNTOWN');
// Render choropleth map colored by overall_risk_score
```

---

## Data Privacy & Security

### PII Considerations

**users table**: Contains email addresses (PII)
- Enable Row Level Security (RLS) in production
- Hash/encrypt emails at application layer if needed
- Implement GDPR-compliant deletion (`DELETE CASCADE`)

**Recommended RLS policy**:
```sql
-- Users can only see their own data
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_select_own
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY user_update_own
    ON users FOR UPDATE
    USING (auth.uid() = id);
```

### Spatial Data Security

**accident_history**: May reveal sensitive locations
- Consider anonymizing exact coordinates (snap to grid)
- Aggregate to area level for public APIs
- Restrict detailed queries to authenticated users

---

## Rollback Instructions

If you need to revert this migration:

```sql
-- Drop functions
DROP FUNCTION IF EXISTS get_nearby_accidents(DOUBLE PRECISION, DOUBLE PRECISION, INTEGER);
DROP FUNCTION IF EXISTS get_location_risk_score(DOUBLE PRECISION, DOUBLE PRECISION);
DROP FUNCTION IF EXISTS refresh_leaderboard();
DROP FUNCTION IF EXISTS update_user_rank();
DROP FUNCTION IF EXISTS add_points_to_user();
DROP FUNCTION IF EXISTS set_accident_location();
DROP FUNCTION IF EXISTS set_block_geometry();

-- Drop views
DROP VIEW IF EXISTS top_users_leaderboard;
DROP VIEW IF EXISTS accident_hotspots;
DROP VIEW IF EXISTS high_risk_blocks;
DROP VIEW IF EXISTS user_activity_summary;

-- Drop tables (order matters due to foreign keys)
DROP TABLE IF EXISTS points_transactions CASCADE;
DROP TABLE IF EXISTS leaderboard CASCADE;
DROP TABLE IF EXISTS accident_history CASCADE;
DROP TABLE IF EXISTS block_risk_scores CASCADE;
DROP TABLE IF EXISTS users CASCADE;
```

---

## Future Enhancements

### Planned Improvements

1. **Gamification**:
   - Badges/achievements system
   - Team/group leaderboards
   - Seasonal competitions
   - Point redemption store

2. **Accident Analysis**:
   - ML-based accident prediction
   - Real-time accident alerts
   - Integration with traffic data
   - Weather correlation analysis

3. **Risk Index**:
   - Real-time risk updates
   - Predictive risk modeling
   - Equity scoring algorithms
   - Community feedback integration

### Schema Evolution

Future migrations might add:
- `badges` and `user_badges` tables
- `accident_predictions` table
- `risk_interventions` tracking table
- `community_feedback` for risk validation

---

## Support & Troubleshooting

### Common Issues

**PostGIS extension not found**:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```
Ensure PostGIS is installed on your PostgreSQL server.

**Leaderboard out of sync**:
```sql
SELECT refresh_leaderboard();
```

**Geometry not populating**:
Check that triggers are enabled:
```sql
SELECT tgname, tgenabled
FROM pg_trigger
WHERE tgname LIKE '%location%' OR tgname LIKE '%geometry%';
```

**Slow spatial queries**:
Verify GIST indexes exist:
```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('accident_history', 'block_risk_scores');
```

### Contact

For questions or issues with this migration:
- Check database logs for detailed error messages
- Verify all prerequisites (PostGIS, extensions) are installed
- Run `python verify.py --detailed` for comprehensive diagnostics

---

## Changelog

**Version 002 (2025-11-15)**:
- Initial release
- Added gamification system (3 tables)
- Added accident history tracking (1 table)
- Added community risk index (1 table)
- Created 4 views and 3 spatial query functions
- Implemented 5 automated triggers
