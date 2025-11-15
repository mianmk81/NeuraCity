# NeuraCity Database Schema

Visual documentation of the database structure, relationships, and design decisions.

## Overview

The NeuraCity database consists of 7 tables organized around three main functional areas:

1. **Issue Management**: Citizen-reported problems and their resolution
2. **City Intelligence**: Mood, traffic, and noise data for analytics
3. **Work Management**: Automated work orders and emergency responses

## Entity Relationship Diagram

```
┌─────────────────────┐
│      issues         │
│─────────────────────│
│ id (PK)            │
│ lat                │
│ lng                │
│ issue_type         │
│ description        │
│ image_url          │──────┐
│ severity           │      │
│ urgency            │      │
│ priority           │      │
│ action_type        │      │
│ status             │      │
│ created_at         │      │
│ updated_at         │      │
└─────────────────────┘      │
         │                   │
         │                   │
         ├───────────────────┼──────────┐
         │                   │          │
         │                   │          │
         ▼                   ▼          ▼
┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐
│ work_orders     │  │ emergency_queue  │  │                    │
│─────────────────│  │──────────────────│  │                    │
│ id (PK)        │  │ id (PK)         │  │                    │
│ issue_id (FK)  │  │ issue_id (FK)   │  │                    │
│ contractor_id  │  │ summary         │  │                    │
│ material_sugg. │  │ status          │  │                    │
│ status         │  │ created_at      │  │                    │
│ created_at     │  │ updated_at      │  │                    │
│ updated_at     │  └──────────────────┘  │                    │
└────────┬────────┘                        │                    │
         │                                 │                    │
         │                                 │                    │
         ▼                                 │                    │
┌─────────────────┐                       │                    │
│  contractors    │                       │                    │
│─────────────────│                       │                    │
│ id (PK)        │                       │                    │
│ name           │                       │                    │
│ specialty      │                       │                    │
│ contact_email  │                       │                    │
│ has_city_contr.│                       │                    │
│ created_at     │                       │                    │
└─────────────────┘                       │                    │
                                          │                    │
┌─────────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│    mood_areas       │    │  traffic_segments   │    │ noise_segments   │
│─────────────────────│    │─────────────────────│    │──────────────────│
│ id (PK)            │    │ id (PK)            │    │ id (PK)         │
│ area_id            │    │ segment_id         │    │ segment_id      │
│ lat                │    │ lat                │    │ lat             │
│ lng                │    │ lng                │    │ lng             │
│ mood_score         │    │ congestion         │    │ noise_db        │
│ post_count         │    │ ts                 │    │ ts              │
│ created_at         │    └─────────────────────┘    └──────────────────┘
└─────────────────────┘
```

## Table Details

### 1. issues

**Purpose**: Core table for citizen-reported infrastructure problems.

**Critical Constraints**:
- Image URL is **required** (mandatory visual evidence)
- Latitude/longitude are **required** (automatic GPS capture)
- Issue type must be: `accident`, `pothole`, `traffic_light`, or `other`
- Coordinates validated: lat ∈ [-90, 90], lng ∈ [-180, 180]
- Severity and urgency scores: [0, 1]
- Status workflow: `open` → `in_progress` → `resolved` → `closed`

**Indexes**:
```sql
idx_issues_location       -- B-tree on (lat, lng) for geospatial queries
idx_issues_type           -- B-tree on issue_type for filtering
idx_issues_status         -- B-tree on status for workflow queries
idx_issues_created_at     -- B-tree DESC on created_at for recent issues
idx_issues_priority       -- B-tree on priority for sorting
idx_issues_urgency        -- B-tree DESC on urgency for emergency triage
```

**Auto-Triggers**:
- `update_issues_updated_at` - Automatically updates `updated_at` on modification

**Example Record**:
```json
{
  "id": "a1b2c3d4-...",
  "lat": 40.7128,
  "lng": -74.0060,
  "issue_type": "pothole",
  "description": "Large pothole causing vehicle damage",
  "image_url": "https://storage.supabase.co/...",
  "severity": 0.75,
  "urgency": 0.80,
  "priority": "high",
  "action_type": "work_order",
  "status": "open",
  "created_at": "2025-11-14T10:30:00Z",
  "updated_at": "2025-11-14T10:30:00Z"
}
```

---

### 2. mood_areas

**Purpose**: Aggregated sentiment analysis results by geographic area.

**Key Concepts**:
- Each record represents aggregated mood from multiple synthetic social posts
- Mood score range: -1 (very negative) to +1 (very positive)
- Time-series data allows tracking mood changes over time
- Used to identify areas needing attention or experiencing issues

**Indexes**:
```sql
idx_mood_areas_area_id    -- B-tree on area_id for area-based queries
idx_mood_areas_location   -- B-tree on (lat, lng) for map visualization
idx_mood_areas_created_at -- B-tree DESC for time-series queries
idx_mood_areas_score      -- B-tree on mood_score for sentiment filtering
```

**Example Query Pattern**:
```sql
-- Get current average mood by area
SELECT area_id, AVG(mood_score) as avg_mood
FROM mood_areas
WHERE created_at >= NOW() - INTERVAL '1 hour'
GROUP BY area_id;
```

---

### 3. traffic_segments

**Purpose**: Real-time traffic congestion data for routing algorithms.

**Key Concepts**:
- Congestion level: 0 (free-flowing) to 1 (complete gridlock)
- Time-series data with high frequency (e.g., every 15 minutes)
- Used in routing cost calculations and urgency scoring
- Synthetic data follows rush hour patterns (7-9 AM, 5-7 PM peaks)

**Indexes**:
```sql
idx_traffic_segment_id    -- B-tree on segment_id for segment queries
idx_traffic_location      -- B-tree on (lat, lng) for geospatial routing
idx_traffic_ts            -- B-tree DESC for latest data retrieval
idx_traffic_congestion    -- B-tree DESC for hotspot identification
```

**Data Retention**: Consider purging data older than 30 days for performance.

---

### 4. noise_segments

**Purpose**: Noise level measurements for quiet walking route calculations.

**Key Concepts**:
- Noise measured in decibels (dB)
- Typical ranges:
  - 40-50 dB: Very quiet (parks, residential side streets)
  - 55-65 dB: Moderate (commercial streets)
  - 70-85 dB: Loud (highways, major intersections)
- Correlates with traffic congestion
- Used in quiet route penalty calculations

**Indexes**:
```sql
idx_noise_segment_id      -- B-tree on segment_id
idx_noise_location        -- B-tree on (lat, lng)
idx_noise_ts              -- B-tree DESC for recency
idx_noise_level           -- B-tree on noise_db for filtering
```

**Routing Formula**:
```
quiet_route_cost = time_cost + α * normalized_noise
where normalized_noise = (noise_db - 40) / 45
```

---

### 5. contractors

**Purpose**: Registry of approved contractors for work order assignments.

**Key Concepts**:
- Specialty-based matching for work orders
- `has_city_contract` flag for active/inactive contractors
- Email validation enforced at database level
- Reference data (relatively static)

**Common Specialties**:
- `pothole_repair`
- `asphalt_repair`
- `traffic_signals`
- `electrical`
- `general_construction`
- `emergency_repair`
- `landscaping`
- `drainage`
- `sidewalk_repair`

**Indexes**:
```sql
idx_contractors_specialty      -- B-tree on specialty for matching
idx_contractors_has_contract   -- Partial index WHERE has_city_contract = TRUE
```

**Example Matching Query**:
```sql
-- Find available contractors for pothole repair
SELECT * FROM contractors
WHERE specialty = 'pothole_repair'
  AND has_city_contract = TRUE
ORDER BY name;
```

---

### 6. work_orders

**Purpose**: AI-generated work orders linking issues to contractors.

**Relationships**:
- **issue_id** → `issues.id` (CASCADE DELETE)
  - If issue is deleted, work order is automatically deleted
- **contractor_id** → `contractors.id` (SET NULL)
  - If contractor is deleted, work order is preserved with NULL contractor_id

**Status Workflow**:
```
pending_review → approved → in_progress → completed
               ↘ rejected
```

**Key Concepts**:
- `material_suggestion` contains AI-generated recommendations from Gemini
- Admin approval required before work can begin
- Created automatically for `pothole` and `traffic_light` issues
- Preserved as historical record even after issue resolution

**Indexes**:
```sql
idx_work_orders_issue_id       -- B-tree on issue_id (foreign key)
idx_work_orders_contractor_id  -- B-tree on contractor_id (foreign key)
idx_work_orders_status         -- B-tree on status for workflow queries
idx_work_orders_created_at     -- B-tree DESC for recency
```

**Auto-Triggers**:
- `update_work_orders_updated_at` - Automatically updates `updated_at` on modification

---

### 7. emergency_queue

**Purpose**: AI-generated emergency summaries for accident reports.

**Relationships**:
- **issue_id** → `issues.id` (CASCADE DELETE)

**Status Workflow**:
```
pending → reviewed → dispatched → resolved
```

**Key Concepts**:
- Created automatically for `accident` type issues
- `summary` contains Gemini-generated dispatcher-ready text
- Includes severity assessment, location details, and recommended actions
- Admin review required before emergency dispatch
- No automatic 911 calls (safety feature)

**Indexes**:
```sql
idx_emergency_queue_issue_id   -- B-tree on issue_id (foreign key)
idx_emergency_queue_status     -- B-tree on status for queue management
idx_emergency_queue_created_at -- B-tree DESC for FIFO processing
```

**Auto-Triggers**:
- `update_emergency_queue_updated_at` - Automatically updates `updated_at` on modification

---

## Views

### active_issues_summary

**Purpose**: Aggregated statistics for active issues dashboard.

```sql
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
```

**Usage**: Quick dashboard overview without complex aggregation queries.

---

### pending_work_orders_details

**Purpose**: Denormalized view combining work orders with issue and contractor details.

```sql
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
```

**Usage**: Admin work order management interface.

---

### emergency_queue_details

**Purpose**: Emergency queue items with full issue context.

```sql
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
```

**Usage**: Emergency dispatcher dashboard with prioritized queue.

---

## Design Patterns

### 1. UUID Primary Keys

**Rationale**:
- Distributed system compatibility
- No sequential ID exposure
- Merge-friendly across environments
- Generated server-side via `gen_random_uuid()`

**Trade-offs**:
- Slightly larger index size vs. BIGINT
- Non-human-readable
- No inherent ordering (use `created_at` for chronology)

---

### 2. Timestamp Management

**Pattern**: All tables use `timestamptz` (timestamp with timezone).

**Auto-Update Trigger**:
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Applied to issues, work_orders, emergency_queue
```

**Benefits**:
- Automatic audit trail
- No application-side timestamp management
- Consistent timezone handling

---

### 3. Foreign Key Strategies

| Relationship | ON DELETE Strategy | Rationale |
|--------------|-------------------|-----------|
| `work_orders.issue_id → issues.id` | **CASCADE** | Work order meaningless without parent issue |
| `emergency_queue.issue_id → issues.id` | **CASCADE** | Emergency entry meaningless without parent issue |
| `work_orders.contractor_id → contractors.id` | **SET NULL** | Preserve work order history even if contractor removed |

---

### 4. Check Constraints for Data Validation

**Examples**:
```sql
-- Coordinate validation
CHECK (lat >= -90 AND lat <= 90)
CHECK (lng >= -180 AND lng <= 180)

-- Score normalization
CHECK (severity >= 0 AND severity <= 1)
CHECK (urgency >= 0 AND urgency <= 1)
CHECK (mood_score >= -1 AND mood_score <= 1)
CHECK (congestion >= 0 AND congestion <= 1)

-- Enum-like validation
CHECK (issue_type IN ('accident', 'pothole', 'traffic_light', 'other'))
CHECK (status IN ('open', 'in_progress', 'resolved', 'closed'))

-- Email validation
CHECK (contact_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
```

**Benefits**:
- Database-enforced data integrity
- Validation independent of application layer
- Clear error messages on constraint violations

---

### 5. Index Strategy

**Geospatial Queries**:
- B-tree indexes on `(lat, lng)` pairs
- Future consideration: PostGIS for complex spatial operations

**Time-Series Queries**:
- DESC indexes on timestamp columns for "latest data" queries
- Composite indexes like `(segment_id, ts DESC)` for per-segment time-series

**Workflow Queries**:
- Indexes on status columns for filtering active records
- Partial indexes on boolean flags (e.g., `WHERE has_city_contract = TRUE`)

**Foreign Keys**:
- Automatic indexes on all foreign key columns for join performance

---

## Data Flow

### Issue Reporting Flow

```
1. Citizen uploads image + GPS → Frontend
2. Frontend validates data → POST /issues
3. Backend inserts into `issues` table
4. Backend calculates severity/urgency scores
5. Backend determines action_type based on issue_type:
   - accident → Create entry in `emergency_queue`
   - pothole/traffic_light → Create entry in `work_orders`
   - other → No automatic action
6. AI (Gemini) generates:
   - Emergency summary (for accidents)
   - Material suggestions + contractor match (for work orders)
7. Admin reviews and approves actions
```

### Routing Flow

```
1. User requests route (origin, destination, type) → Frontend
2. Frontend → POST /plan
3. Backend fetches latest data:
   - `traffic_segments` for congestion
   - `noise_segments` for quiet routes
   - `issues` for hazards
4. Backend runs A* with custom cost function:
   - Drive: time + urgency_penalty
   - Eco: time + congestion_penalty
   - Quiet: time + noise_penalty
5. Backend returns route with metrics
```

### Mood Analysis Flow

```
1. Synthetic data generator creates social posts → Python script
2. Posts analyzed via HuggingFace sentiment model
3. Aggregated mood scores inserted into `mood_areas`
4. Frontend queries recent mood data → GET /mood
5. Map visualization shows mood by area
```

---

## Scalability Considerations

### Current Scale (Free Tier)

- **Rows**: Supabase free tier supports up to 500 MB database
- **Estimated capacity**:
  - ~100,000 issues
  - ~500,000 traffic records (with 30-day retention)
  - ~500,000 noise records (with 30-day retention)
  - ~50,000 mood data points

### Growth Strategy

**Phase 1** (Current): Single-region, monolithic tables
**Phase 2** (Growth): Partition time-series tables by date
```sql
-- Example partitioning
CREATE TABLE traffic_segments_2025_11 PARTITION OF traffic_segments
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

**Phase 3** (Scale): Consider time-series database for traffic/noise
- TimescaleDB extension on Postgres
- Separate analytics database

**Phase 4** (Global): Multi-region replication
- Regional read replicas
- Geo-sharding by city/area

---

## Performance Benchmarks

### Expected Query Performance (Free Tier)

| Query Type | Expected Time | Notes |
|------------|---------------|-------|
| Single issue by ID | < 5ms | Primary key lookup |
| Issues in bounding box | < 50ms | B-tree index on (lat, lng) |
| Latest traffic by segment | < 100ms | Index on (segment_id, ts DESC) |
| Mood aggregation | < 200ms | Aggregation over indexed data |
| Work orders with joins | < 150ms | Indexed foreign keys |

### Optimization Tips

1. **Always use LIMIT**: Especially for map queries
2. **Bounding box first**: Filter by lat/lng range before distance calculation
3. **Batch inserts**: Insert traffic/noise data in batches of 500-1000 rows
4. **Archive old data**: Implement retention policies for time-series tables
5. **Monitor slow queries**: Use Supabase query performance dashboard

---

## Security Model

### Current Implementation

**No Row Level Security (RLS)** - Suitable for development/testing only.

### Production Recommendations

Enable RLS on all tables:

```sql
-- Enable RLS
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Public can view issues"
ON issues FOR SELECT
TO anon, authenticated
USING (true);

-- Only authenticated users can create issues
CREATE POLICY "Authenticated can create issues"
ON issues FOR INSERT
TO authenticated
WITH CHECK (true);

-- Only admins can update status
CREATE POLICY "Admins can update issues"
ON issues FOR UPDATE
TO authenticated
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');
```

---

## Migration History

| Version | Date | Description | Breaking Changes |
|---------|------|-------------|------------------|
| 001 | 2025-11-14 | Initial schema creation | N/A (first version) |

---

## Future Enhancements

### Potential Schema Evolution

1. **User Authentication**
   - Add `users` table
   - Add `user_id` foreign key to `issues`
   - Track issue reporters

2. **Comments/Updates**
   - Add `issue_comments` table
   - Allow threaded discussions on issues

3. **Attachments**
   - Add `issue_attachments` table
   - Support multiple images per issue

4. **Analytics Tables**
   - Pre-aggregated statistics tables
   - Materialized views for dashboards

5. **Geospatial Extension**
   - Enable PostGIS
   - Add GEOGRAPHY columns
   - Use spatial indexes for complex queries

6. **Audit Logging**
   - Add `audit_log` table
   - Track all administrative actions

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase Database Guide](https://supabase.com/docs/guides/database)
- [PostGIS Documentation](https://postgis.net/docs/)
- [UUID Best Practices](https://www.postgresql.org/docs/current/datatype-uuid.html)

---

**Last Updated**: 2025-11-14
**Schema Version**: 001
**Maintainer**: NeuraCity Database Architecture Team
