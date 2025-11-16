# Risk Index Quick Start Guide

## Setup (5 minutes)

### 1. Create Database Tables

Run the risk index schema in Supabase SQL Editor:

```bash
# Navigate to Supabase Dashboard -> SQL Editor
# Copy and paste contents of database/schema_risk_index.sql
# Execute
```

Or via command line:
```bash
cd database
psql $SUPABASE_URL -f schema_risk_index.sql
```

### 2. Generate Synthetic Data

```bash
cd database/seeds
python generate_risk_data.py --blocks=200 --days=30
```

This generates:
- 200 geographic blocks
- 7,800 risk factor measurements
- 800 historical snapshots

### 3. Start Backend

```bash
cd backend
python run.py
```

Backend will be available at `http://localhost:8000`

## Quick API Test

### Get All Risk Blocks

```bash
curl http://localhost:8000/api/v1/risk-index/blocks?limit=10
```

### Get High-Risk Blocks Only

```bash
curl http://localhost:8000/api/v1/risk-index/blocks?risk_category=high
```

### Get Statistics

```bash
curl http://localhost:8000/api/v1/risk-index/statistics
```

### Calculate Risk for New Block

```bash
curl -X POST http://localhost:8000/api/v1/risk-index/recalculate \
  -H "Content-Type: application/json" \
  -d '{
    "block_id": "BLK_TEST",
    "lat": 40.715,
    "lng": -74.005,
    "crime_data": {"incidents_per_month": 20, "severity_multiplier": 1.0},
    "blight_data": {"abandoned_buildings": 1, "vacant_lots": 2, "code_violations": 3},
    "emergency_data": {"avg_response_time_minutes": 7.5, "percentile_90_time_minutes": 10.0},
    "air_quality_data": {"aqi_value": 65},
    "heat_data": {"avg_temperature_celsius": 25, "max_temperature_celsius": 32, "tree_canopy_percent": 25, "impervious_surface_percent": 60},
    "traffic_data": {"avg_speed_mph": 30, "percentile_85_speed_mph": 38, "pedestrian_volume": 100, "road_type": "residential"},
    "save_to_database": true
  }'
```

## Interactive API Docs

Visit `http://localhost:8000/docs` to explore all endpoints interactively.

## Common Queries

### Find Critical Risk Blocks

```sql
SELECT block_id, lat, lng, composite_risk_index
FROM risk_blocks
WHERE risk_category = 'critical'
ORDER BY composite_risk_index DESC;
```

### Get Latest Crime Data

```sql
SELECT block_id, raw_value, normalized_score, measurement_date
FROM risk_factors
WHERE factor_type = 'crime'
ORDER BY measurement_date DESC
LIMIT 20;
```

### View Risk Trends

```sql
SELECT * FROM risk_trends
WHERE avg_risk > 0.5
ORDER BY avg_risk DESC;
```

## Updating Configuration

Change default weights in database:

```sql
UPDATE risk_config
SET crime_weight = 0.30,
    emergency_response_weight = 0.25
WHERE config_name = 'default';
```

Then recalculate all blocks:

```bash
curl -X POST http://localhost:8000/api/v1/risk-index/recalculate-all?config_name=default
```

## Troubleshooting

### "Table does not exist"
Run `database/schema_risk_index.sql` in Supabase

### "No data returned"
Run `python generate_risk_data.py` to create synthetic data

### "Import error: risk_index"
Restart backend after adding new files

## Next Steps

1. **Read Full Documentation**: `/RISK_INDEX_DOCUMENTATION.md`
2. **Customize Weights**: Create config profiles for different priorities
3. **Integrate Frontend**: Add risk overlay to map view
4. **Real Data**: Replace synthetic data with actual city data sources

## File Locations

- **Schema**: `C:\Users\mianm\Downloads\NeuraCity\database\schema_risk_index.sql`
- **Service**: `C:\Users\mianm\Downloads\NeuraCity\backend\app\services\risk_index_service.py`
- **API**: `C:\Users\mianm\Downloads\NeuraCity\backend\app\api\endpoints\risk_index.py`
- **Schemas**: `C:\Users\mianm\Downloads\NeuraCity\backend\app\api\schemas\risk_index.py`
- **Data Generator**: `C:\Users\mianm\Downloads\NeuraCity\database\seeds\generate_risk_data.py`
- **Documentation**: `C:\Users\mianm\Downloads\NeuraCity\RISK_INDEX_DOCUMENTATION.md`
