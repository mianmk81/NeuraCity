# NeuraCity Database Documentation

This directory contains the complete database schema, migrations, and seed data for the NeuraCity smart city platform.

## Table of Contents

- [Overview](#overview)
- [Schema Design](#schema-design)
- [Setup Instructions](#setup-instructions)
- [Running Migrations](#running-migrations)
- [Seeding Data](#seeding-data)
- [Generating Synthetic Data](#generating-synthetic-data)
- [Connection Examples](#connection-examples)
- [Query Examples](#query-examples)
- [Performance Considerations](#performance-considerations)

## Overview

NeuraCity uses **PostgreSQL** via **Supabase** (free tier) as its primary database. The schema is designed to support:

- Citizen issue reporting with image evidence and GPS coordinates
- City mood analysis from synthetic social posts
- Traffic and noise awareness for intelligent routing
- Emergency queue management for accidents
- Automated work order generation for infrastructure issues

### Technology

- **Database**: PostgreSQL 15+ (via Supabase)
- **Features Used**: UUID, timestamptz, CHECK constraints, foreign keys, indexes
- **Access**: Supabase client libraries (Python, JavaScript)

## Schema Design

### Tables

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `issues` | Citizen-reported problems | Image required, GPS required, AI-scored severity/urgency |
| `mood_areas` | City emotional sentiment | Aggregated from synthetic posts, -1 to +1 scale |
| `traffic_segments` | Real-time traffic data | Congestion levels (0-1), time-series data |
| `noise_segments` | Road noise levels | dB measurements, correlated with traffic |
| `contractors` | City-approved contractors | Specialty-based matching for work orders |
| `work_orders` | Infrastructure repair tasks | AI-generated material suggestions |
| `emergency_queue` | Accident summaries | AI-generated dispatcher summaries |

### Entity Relationships

```
issues (1) ──→ (0..1) emergency_queue
       └────→ (0..*) work_orders (*.1) ──→ contractors
```

### Key Design Decisions

1. **UUID Primary Keys**: Using `gen_random_uuid()` for distributed system compatibility
2. **Timestamptz**: All timestamps use timezone-aware format for global compatibility
3. **Check Constraints**: Validation at database level for data integrity
4. **Geospatial Indexing**: B-tree indexes on (lat, lng) for location queries
5. **Foreign Key Cascades**:
   - `work_orders.issue_id` → CASCADE DELETE (cleanup orphaned work orders)
   - `work_orders.contractor_id` → SET NULL (preserve work order history)
6. **Automatic Timestamps**: Triggers update `updated_at` on row modifications

## Setup Instructions

### Prerequisites

1. **Supabase Account**: Create a free account at [supabase.com](https://supabase.com)
2. **Supabase Project**: Create a new project and note:
   - Project URL (e.g., `https://xxxxx.supabase.co`)
   - Anon/Public Key (for client access)
   - Service Role Key (for admin operations)

### Environment Variables

Create a `.env` file in the project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Optional: For synthetic data generation
SUPABASE_DB_PASSWORD=your_db_password
```

## Running Migrations

### Option 1: Supabase Dashboard (Recommended)

1. Log into your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Create a new query
4. Copy the contents of `database/migrations/001_initial_schema.sql`
5. Paste and click **Run**
6. Verify all tables were created in the **Table Editor**

### Option 2: Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref your-project-ref

# Run migration
supabase db push
```

### Option 3: Direct PostgreSQL Connection

```bash
# Connect to Supabase database
psql "postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres"

# Run migration
\i database/migrations/001_initial_schema.sql
```

### Verify Migration

After running the migration, verify table creation:

```sql
-- Check all tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Expected output:
-- contractors
-- emergency_queue
-- issues
-- mood_areas
-- noise_segments
-- traffic_segments
-- work_orders
```

## Seeding Data

After running migrations, populate the database with initial data:

### 1. Seed Contractors

Run `database/seeds/001_seed_contractors.sql` in the Supabase SQL Editor.

**Provides**: 15 contractors across 13 specialties (road repair, electrical, traffic engineering, etc.)

**Verify**:
```sql
SELECT specialty, COUNT(*) as count
FROM contractors
WHERE has_city_contract = true
GROUP BY specialty
ORDER BY specialty;
```

### 2. Seed City Areas

Run `database/seeds/002_seed_synthetic_areas.sql` in the Supabase SQL Editor.

**Provides**: 5 city areas (Midtown, Downtown, Campus, Park District, Residential Zone) with baseline mood scores

**Verify**:
```sql
SELECT area_id, lat, lng, mood_score
FROM mood_areas
ORDER BY mood_score DESC;
```

### 3. Seed Traffic and Noise Data

Run `database/seeds/003_seed_synthetic_data.sql` in the Supabase SQL Editor.

**Provides**: Initial traffic and noise measurements for major road segments in each area

**Verify**:
```sql
-- Traffic summary
SELECT
  SUBSTRING(segment_id FROM '^[^_]+') as area,
  COUNT(*) as segments,
  ROUND(AVG(congestion)::numeric, 2) as avg_congestion
FROM traffic_segments
GROUP BY SUBSTRING(segment_id FROM '^[^_]+')
ORDER BY avg_congestion DESC;

-- Noise summary
SELECT
  SUBSTRING(segment_id FROM '^[^_]+') as area,
  ROUND(AVG(noise_db)::numeric, 1) as avg_noise_db
FROM noise_segments
GROUP BY SUBSTRING(segment_id FROM '^[^_]+')
ORDER BY avg_noise_db DESC;
```

## Generating Synthetic Data

For realistic time-series data and testing, use the Python synthetic data generator:

### Installation

```bash
# Install dependencies
pip install faker supabase python-dotenv
```

### Usage

```bash
# Navigate to database seeds directory
cd database/seeds

# Run the generator
python generate_synthetic_data.py
```

### What It Generates

The script creates:

- **Mood Data**: 7 days × 5 areas × 10 posts/day = 350 mood records
- **Traffic Data**: 7 days × 24 hours × 25 segments = 4,200 traffic records
- **Noise Data**: 7 days × 24 hours × 25 segments = 4,200 noise records
- **Sample Issues**: 20 sample issues across all areas and types

### Features

1. **Rush Hour Patterns**: Traffic peaks at 7-9 AM and 5-7 PM
2. **Weekend Variation**: Reduced traffic on weekends
3. **Noise-Traffic Correlation**: Higher traffic = higher noise
4. **Mood Variance**: Area-specific sentiment patterns
5. **Realistic Issues**: Accident, pothole, traffic light, and other issues

### Customization

Edit the script to adjust:

```python
# In generate_synthetic_data.py

# Generate more/less data
mood_data = generate_mood_data(days=14, posts_per_day_per_area=20)  # 14 days, 20 posts/day
traffic_data = generate_traffic_data(days=14, samples_per_day=48)   # 14 days, hourly samples
issues_data = generate_sample_issues(count=50)                       # 50 sample issues
```

## Connection Examples

### Python (FastAPI Backend)

```python
from supabase import create_client, Client
import os

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Query issues
response = supabase.table('issues').select('*').eq('status', 'open').execute()
issues = response.data

# Insert new issue
new_issue = {
    'lat': 40.7580,
    'lng': -73.9855,
    'issue_type': 'pothole',
    'description': 'Large pothole on Main St',
    'image_url': 'https://example.com/image.jpg',
    'severity': 0.7,
    'urgency': 0.6,
    'priority': 'high',
    'action_type': 'work_order',
    'status': 'open'
}
response = supabase.table('issues').insert(new_issue).execute()
```

### JavaScript (React Frontend)

```javascript
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

// Fetch mood data
const { data: moodData, error } = await supabase
  .from('mood_areas')
  .select('*')
  .order('created_at', { ascending: false })
  .limit(5)

// Subscribe to real-time updates
const channel = supabase
  .channel('issues-changes')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'issues' },
    (payload) => console.log('New issue:', payload.new)
  )
  .subscribe()
```

## Query Examples

### Find Issues Near a Location

```sql
-- Find all open issues within ~1km of a location
-- (rough approximation: 0.01 degrees ≈ 1km)
SELECT
  id,
  issue_type,
  description,
  severity,
  urgency,
  status,
  created_at,
  -- Calculate approximate distance
  SQRT(POWER((lat - 40.7580), 2) + POWER((lng - (-73.9855)), 2)) as approx_distance
FROM issues
WHERE status = 'open'
  AND lat BETWEEN 40.7480 AND 40.7680
  AND lng BETWEEN -73.9955 AND -73.9755
ORDER BY approx_distance
LIMIT 10;
```

### Get Latest Traffic Data by Area

```sql
-- Get most recent traffic reading for each segment
SELECT DISTINCT ON (segment_id)
  segment_id,
  lat,
  lng,
  congestion,
  ts
FROM traffic_segments
ORDER BY segment_id, ts DESC;
```

### Calculate Average Mood by Area (Last 24 Hours)

```sql
SELECT
  area_id,
  COUNT(*) as record_count,
  ROUND(AVG(mood_score)::numeric, 3) as avg_mood,
  SUM(post_count) as total_posts
FROM mood_areas
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY area_id
ORDER BY avg_mood DESC;
```

### Find Contractors by Specialty

```sql
-- Find contractors for pothole repair
SELECT
  name,
  specialty,
  contact_email
FROM contractors
WHERE specialty IN ('pothole_repair', 'road_repair')
  AND has_city_contract = true
ORDER BY name;
```

### Pending Work Orders with Issue Details

```sql
SELECT
  wo.id as work_order_id,
  wo.status as wo_status,
  wo.material_suggestion,
  wo.created_at as wo_created,
  i.issue_type,
  i.description,
  i.lat,
  i.lng,
  i.severity,
  i.urgency,
  c.name as contractor_name,
  c.specialty
FROM work_orders wo
JOIN issues i ON wo.issue_id = i.id
LEFT JOIN contractors c ON wo.contractor_id = c.id
WHERE wo.status = 'pending_review'
ORDER BY wo.created_at DESC;
```

### Emergency Queue with Issue Context

```sql
SELECT
  eq.id as emergency_id,
  eq.summary,
  eq.status as eq_status,
  eq.created_at as reported_at,
  i.lat,
  i.lng,
  i.description,
  i.severity,
  i.urgency
FROM emergency_queue eq
JOIN issues i ON eq.issue_id = i.id
WHERE eq.status = 'pending'
ORDER BY eq.created_at ASC;
```

### Quiet Routes (Low Noise Segments)

```sql
-- Find quietest road segments (most recent data)
SELECT DISTINCT ON (segment_id)
  segment_id,
  lat,
  lng,
  noise_db,
  ts
FROM noise_segments
WHERE noise_db < 60  -- Less than 60 dB (moderate threshold)
ORDER BY segment_id, ts DESC, noise_db ASC;
```

## Performance Considerations

### Indexes

All critical query paths are indexed:

- **Geospatial queries**: `(lat, lng)` indexes on all location-based tables
- **Status filtering**: `status` indexes on `issues`, `work_orders`, `emergency_queue`
- **Time-series queries**: `created_at` and `ts` indexes with DESC ordering
- **Foreign keys**: Automatic indexes on all foreign key columns
- **Specialty matching**: `specialty` index on `contractors`

### Query Optimization Tips

1. **Use LIMIT**: Always limit result sets for map queries
2. **Use Bounding Boxes**: Filter by lat/lng range before distance calculations
3. **Index-Only Scans**: Select only indexed columns when possible
4. **DISTINCT ON**: Use for latest time-series data per segment
5. **Batch Inserts**: Insert traffic/noise data in batches (500-1000 rows)

### Monitoring

Check index usage:

```sql
-- Find unused indexes
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%_pkey'
ORDER BY tablename, indexname;
```

Check table sizes:

```sql
-- Show table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Data Retention

For production deployments, implement data retention policies:

```sql
-- Example: Delete traffic/noise data older than 30 days
DELETE FROM traffic_segments WHERE ts < NOW() - INTERVAL '30 days';
DELETE FROM noise_segments WHERE ts < NOW() - INTERVAL '30 days';

-- Example: Archive resolved issues older than 90 days
-- (Move to archive table, then delete)
DELETE FROM issues
WHERE status = 'resolved'
  AND updated_at < NOW() - INTERVAL '90 days';
```

Consider setting up a cron job or Supabase function to run retention policies automatically.

## Backup and Recovery

### Supabase Automatic Backups

Supabase provides automatic daily backups on paid plans. For free tier:

### Manual Backup

```bash
# Backup entire database
pg_dump "postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres" > backup.sql

# Restore from backup
psql "postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres" < backup.sql
```

### Export Specific Tables

```bash
# Export issues table as CSV
psql "postgresql://..." -c "\COPY issues TO 'issues_backup.csv' CSV HEADER"
```

## Troubleshooting

### Common Issues

**Problem**: Migration fails with permission error
**Solution**: Ensure you're using the service role key for DDL operations

**Problem**: Slow queries on location-based searches
**Solution**: Ensure lat/lng indexes exist and use bounding box filters

**Problem**: Foreign key constraint violations
**Solution**: Always insert parent records (issues, contractors) before child records (work_orders, emergency_queue)

**Problem**: Timestamp timezone confusion
**Solution**: Always use `timestamptz` and ISO format strings with timezone

### Getting Help

- **Supabase Docs**: https://supabase.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Supabase Discord**: https://discord.supabase.com
- **GitHub Issues**: File issues in the NeuraCity repository

## Schema Version History

| Version | Date | Description |
|---------|------|-------------|
| 001 | 2025-11-14 | Initial schema with all 7 tables, indexes, and triggers |

## License

This database schema is part of the NeuraCity project and is licensed under the MIT License.
