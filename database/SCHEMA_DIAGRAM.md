# NeuraCity Database Schema Diagram

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         NEURACITY DATABASE SCHEMA                        │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│      issues          │ ◄──────────────┐
├──────────────────────┤                │
│ id (PK)              │                │
│ lat                  │                │ Foreign Key
│ lng                  │                │ ON DELETE CASCADE
│ issue_type           │                │
│ description          │                │
│ image_url            │                │
│ severity             │       ┌────────┴────────────┐
│ urgency              │       │  emergency_queue    │
│ priority             │       ├─────────────────────┤
│ action_type          │       │ id (PK)             │
│ status               │       │ issue_id (FK)       │
│ created_at           │       │ summary             │
│ updated_at           │       │ status              │
└──────────────────────┘       │ created_at          │
         ▲                     │ updated_at          │
         │                     └─────────────────────┘
         │ Foreign Key
         │ ON DELETE CASCADE
         │
┌────────┴────────────┐
│   work_orders       │
├─────────────────────┤                ┌──────────────────────┐
│ id (PK)             │                │    contractors       │
│ issue_id (FK) ──────┘                ├──────────────────────┤
│ contractor_id (FK) ─────────────────►│ id (PK)              │
│ material_suggestion │                │ name                 │
│ status              │                │ specialty            │
│ created_at          │                │ contact_email        │
│ updated_at          │                │ has_city_contract    │
└─────────────────────┘                │ created_at           │
                                       │ updated_at           │
                                       └──────────────────────┘

┌──────────────────────┐               ┌──────────────────────┐
│    mood_areas        │               │  traffic_segments    │
├──────────────────────┤               ├──────────────────────┤
│ id (PK)              │               │ id (PK)              │
│ area_id              │               │ segment_id           │
│ lat                  │               │ lat                  │
│ lng                  │               │ lng                  │
│ mood_score           │               │ congestion           │
│ post_count           │               │ ts                   │
│ created_at           │               └──────────────────────┘
└──────────────────────┘

┌──────────────────────┐
│   noise_segments     │
├──────────────────────┤
│ id (PK)              │
│ segment_id           │
│ lat                  │
│ lng                  │
│ noise_db             │
│ ts                   │
└──────────────────────┘
```

## Table Details

### Core Tables

#### `issues` - Citizen Issue Reports
- **Purpose**: Stores all citizen-reported infrastructure problems
- **Required Fields**: lat, lng, issue_type, image_url
- **AI Fields**: severity, urgency, priority, action_type (calculated by backend)
- **Relationships**: Parent to work_orders and emergency_queue
- **Indexes**: Geospatial (lat/lng), status, urgency, created_at

#### `contractors` - City-Approved Contractors
- **Purpose**: Contractor database for work order matching
- **Key Field**: specialty (used for AI matching)
- **Relationships**: Referenced by work_orders
- **Indexes**: specialty, has_city_contract

#### `work_orders` - Infrastructure Work Orders
- **Purpose**: Auto-generated repair tasks for potholes, traffic lights, etc.
- **AI Field**: material_suggestion (Gemini-generated)
- **Relationships**: References issues (parent) and contractors
- **Cascade**: Deleted when parent issue is deleted
- **Indexes**: issue_id, contractor_id, status, created_at

#### `emergency_queue` - Accident Emergency Summaries
- **Purpose**: AI-generated summaries for accident reports
- **AI Field**: summary (Gemini-generated dispatcher-ready text)
- **Relationships**: References issues (parent)
- **Cascade**: Deleted when parent issue is deleted
- **Indexes**: issue_id, status, created_at

### Analytics Tables

#### `mood_areas` - City Mood Analysis
- **Purpose**: Aggregated sentiment data by geographic area
- **Time-Series**: New records created periodically with updated mood scores
- **Score Range**: -1 (very negative) to +1 (very positive)
- **Source**: Synthetic social posts analyzed via HuggingFace
- **Indexes**: area_id, geospatial (lat/lng), created_at

#### `traffic_segments` - Traffic Congestion Data
- **Purpose**: Real-time traffic conditions by road segment
- **Time-Series**: Updated frequently (every 5-15 minutes)
- **Congestion Range**: 0 (free flow) to 1 (gridlock)
- **Uses**: Routing algorithms, urgency scoring
- **Indexes**: segment_id, geospatial (lat/lng), ts

#### `noise_segments` - Road Noise Levels
- **Purpose**: Noise pollution measurements by road segment
- **Time-Series**: Updated with traffic data
- **Noise Range**: 30-100 dB (typically 40-90 dB)
- **Uses**: Quiet walking routes, quality-of-life metrics
- **Indexes**: segment_id, geospatial (lat/lng), ts, noise_db

## Data Flow

### Issue Reporting Flow
```
1. User uploads image + GPS → Frontend
2. Frontend → POST /issues → Backend (FastAPI)
3. Backend calculates severity/urgency
4. Backend inserts into issues table
5. IF issue_type == 'accident':
     - Backend calls Gemini API
     - Insert into emergency_queue
   ELSE IF issue_type IN ('pothole', 'traffic_light'):
     - Backend calls Gemini API
     - Match contractor by specialty
     - Insert into work_orders
```

### Routing Query Flow
```
1. User requests route → Frontend
2. Frontend → POST /plan → Backend
3. Backend queries:
   - issues (urgency, location)
   - traffic_segments (congestion)
   - noise_segments (noise_db)
4. Backend runs A* algorithm with custom cost function
5. Returns route + explanation
```

### Mood Analysis Flow
```
1. Cron job triggers mood analysis
2. Python script generates synthetic posts
3. HuggingFace analyzes sentiment
4. Aggregate scores by area
5. Insert into mood_areas table
6. Frontend displays on mood map
```

## Indexing Strategy

### Geospatial Queries
All location-based tables have `(lat, lng)` B-tree indexes for bounding box queries:
```sql
WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
```

### Time-Series Queries
Traffic and noise segments use descending `ts` indexes for latest-data queries:
```sql
ORDER BY ts DESC LIMIT 1
```

### Status Filtering
Admin queues use `status` indexes for filtering pending items:
```sql
WHERE status = 'pending'
```

### Composite Indexes
Frequently combined filters use composite indexes:
- `issues`: (status, urgency DESC)
- `work_orders`: (status, created_at DESC)
- `mood_areas`: (area_id, created_at DESC)
- `traffic_segments`: (segment_id, ts DESC)

## Constraints and Validation

### Check Constraints
- `issues.issue_type`: Must be 'accident', 'pothole', 'traffic_light', or 'other'
- `issues.severity`: 0 to 1
- `issues.urgency`: 0 to 1
- `issues.priority`: 'low', 'medium', 'high', or 'critical'
- `mood_areas.mood_score`: -1 to 1
- `traffic_segments.congestion`: 0 to 1
- `noise_segments.noise_db`: 0 to 120

### Foreign Key Constraints
- `work_orders.issue_id` → `issues.id` (CASCADE DELETE)
- `work_orders.contractor_id` → `contractors.id` (SET NULL)
- `emergency_queue.issue_id` → `issues.id` (CASCADE DELETE)

### Automatic Behaviors
- All timestamps auto-set to `now()` on insert
- `updated_at` auto-updates on row modification via triggers
- UUIDs auto-generated via `gen_random_uuid()`

## Scalability Considerations

### Current Design (Free Tier)
- **Storage**: ~500 MB limit on Supabase free tier
- **Rows**: Millions supported by PostgreSQL
- **Concurrency**: 60 simultaneous connections

### Estimated Data Growth
- **Issues**: ~100-1000 per day = 30K-300K per month
- **Traffic**: 25 segments × 288 samples/day = 7,200 rows/day = 216K/month
- **Noise**: Same as traffic = 216K/month
- **Mood**: 5 areas × 24 samples/day = 120 rows/day = 3.6K/month

### Optimization Strategies
1. **Partitioning**: Partition traffic/noise by month for time-series queries
2. **Aggregation**: Pre-aggregate older data, delete raw records
3. **Archival**: Move resolved issues older than 90 days to archive table
4. **Retention**: Delete traffic/noise data older than 30 days

## Security

### Row Level Security (RLS)
Enable RLS in Supabase for production:
```sql
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;
-- Add policies for authenticated users
```

### API Access
- **Anonymous Key**: Read-only access to public data
- **Service Role Key**: Full access (backend only, never expose to frontend)
- **User JWT**: Authenticated user access (future feature)

## Monitoring Queries

### Check Index Usage
```sql
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Check Table Sizes
```sql
SELECT tablename,
       pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.'||tablename) DESC;
```

### Check Active Connections
```sql
SELECT count(*) FROM pg_stat_activity;
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-14 | Initial schema design with 7 tables |
