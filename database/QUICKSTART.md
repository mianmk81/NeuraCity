# NeuraCity Database Quick Start Guide

Get your database up and running in 10 minutes.

## Prerequisites

- [ ] Supabase account created at [supabase.com](https://supabase.com)
- [ ] Supabase project created
- [ ] Python 3.8+ installed
- [ ] pip installed

## Step 1: Get Supabase Credentials (2 minutes)

1. Log into your Supabase project dashboard
2. Go to **Settings** → **API**
3. Copy the following:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)
   - **service_role key** (starts with `eyJ...`)

## Step 2: Configure Environment Variables (1 minute)

Create a `.env` file in the project root (`C:\Users\mianm\Downloads\NeuraCity\.env`):

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
```

**Security Note**: Never commit `.env` to version control!

## Step 3: Run Database Migration (2 minutes)

1. Open your Supabase project dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the entire contents of `database/migrations/001_initial_schema.sql`
5. Paste into the SQL Editor
6. Click **Run** (or press Ctrl+Enter)
7. You should see "Success. No rows returned"

**Verify**: Go to **Table Editor** and confirm you see 7 tables:
- issues
- mood_areas
- traffic_segments
- noise_segments
- contractors
- work_orders
- emergency_queue

## Step 4: Seed Initial Data (3 minutes)

Run each seed file in order in the Supabase SQL Editor:

### 4.1 Seed Contractors
1. Open `database/seeds/001_seed_contractors.sql`
2. Copy entire contents
3. Paste and Run in SQL Editor
4. Verify: `SELECT COUNT(*) FROM contractors;` → Should return 15

### 4.2 Seed City Areas
1. Open `database/seeds/002_seed_synthetic_areas.sql`
2. Copy entire contents
3. Paste and Run in SQL Editor
4. Verify: `SELECT * FROM mood_areas;` → Should return 5 rows

### 4.3 Seed Traffic and Noise Data
1. Open `database/seeds/003_seed_synthetic_data.sql`
2. Copy entire contents
3. Paste and Run in SQL Editor
4. Verify:
   - `SELECT COUNT(*) FROM traffic_segments;` → Should return 25+
   - `SELECT COUNT(*) FROM noise_segments;` → Should return 25+

## Step 5: Install Python Dependencies (1 minute)

```bash
cd C:\Users\mianm\Downloads\NeuraCity\database
pip install -r requirements.txt
```

This installs:
- `supabase` - Supabase Python client
- `Faker` - Synthetic data generation
- `python-dotenv` - Environment variable management

## Step 6: Test Database Connection (1 minute)

```bash
python test_connection.py
```

You should see:
```
✓ SUPABASE_URL: https://xxxxx.supabase.co
✓ SUPABASE_KEY: eyJ...
✓ Supabase client created
✓ issues: exists
✓ mood_areas: exists
✓ traffic_segments: exists
✓ noise_segments: exists
✓ contractors: exists
✓ work_orders: exists
✓ emergency_queue: exists
✓ Contractors: 15 rows
✓ Mood Areas: 5 rows
✓ Traffic Segments: 25+ rows
✓ Noise Segments: 25+ rows
✓ All tables exist and are accessible
```

## Step 7: Generate Synthetic Data (OPTIONAL - 2 minutes)

For time-series testing data:

```bash
cd database/seeds
python generate_synthetic_data.py
```

This generates:
- 350 mood records (7 days × 5 areas)
- 4,200 traffic records (7 days × 24 hours × 25 segments)
- 4,200 noise records (7 days × 24 hours × 25 segments)
- 20 sample issues

**Note**: This is optional for initial development. You can run it later when you need test data.

## Verification Checklist

After completing all steps, verify:

- [ ] All 7 tables exist in Supabase Table Editor
- [ ] Contractors table has 15 rows
- [ ] Mood areas table has 5 rows
- [ ] Traffic segments table has 25+ rows
- [ ] Noise segments table has 25+ rows
- [ ] `test_connection.py` passes all checks
- [ ] `.env` file configured with Supabase credentials

## Next Steps

### For Backend Developer
1. Set up FastAPI project structure
2. Install Supabase client: `pip install supabase`
3. Create database connection module
4. Implement `/issues` POST endpoint
5. Test inserting issues

**Example**:
```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Insert test issue
new_issue = supabase.table('issues').insert({
    'lat': 40.7580,
    'lng': -73.9855,
    'issue_type': 'pothole',
    'description': 'Test pothole',
    'image_url': 'https://example.com/test.jpg',
    'severity': 0.5,
    'urgency': 0.6,
    'priority': 'medium',
    'action_type': 'work_order'
}).execute()

print(f"Created issue: {new_issue.data[0]['id']}")
```

### For Frontend Developer
1. Set up React + Vite project
2. Install Supabase client: `npm install @supabase/supabase-js`
3. Create Supabase client configuration
4. Fetch issues for map display
5. Test displaying issues on Leaflet map

**Example**:
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

// Fetch issues
const { data: issues } = await supabase
  .from('issues')
  .select('*')
  .eq('status', 'open')

console.log(`Loaded ${issues.length} issues`)
```

## Troubleshooting

### "Table does not exist" error
- **Cause**: Migration not run or failed
- **Solution**: Re-run `001_initial_schema.sql` in Supabase SQL Editor

### "SUPABASE_URL not found" error
- **Cause**: `.env` file missing or not loaded
- **Solution**: Ensure `.env` exists in project root with correct values

### "Failed to create client" error
- **Cause**: Invalid credentials
- **Solution**: Double-check Supabase URL and keys are correct

### "supabase module not found" error
- **Cause**: Python dependencies not installed
- **Solution**: Run `pip install -r database/requirements.txt`

### Seed data already exists error
- **Cause**: Re-running seed scripts
- **Solution**: Seeds use `TRUNCATE` - they should work on re-run. If not, manually delete data first.

## Resources

- **Full Documentation**: `database/README.md` (comprehensive guide)
- **Schema Reference**: `database/SCHEMA_DIAGRAM.md` (visual diagrams)
- **Implementation Details**: `database/DATABASE_SUMMARY.md` (design decisions)
- **Supabase Docs**: https://supabase.com/docs
- **Support**: File issues in NeuraCity GitHub repository

## Quick Reference

### File Locations

```
C:\Users\mianm\Downloads\NeuraCity\
├── .env (CREATE THIS!)
└── database/
    ├── migrations/
    │   └── 001_initial_schema.sql (RUN FIRST)
    ├── seeds/
    │   ├── 001_seed_contractors.sql (RUN SECOND)
    │   ├── 002_seed_synthetic_areas.sql (RUN THIRD)
    │   ├── 003_seed_synthetic_data.sql (RUN FOURTH)
    │   └── generate_synthetic_data.py (OPTIONAL)
    └── test_connection.py (RUN TO VERIFY)
```

### Supabase Dashboard Quick Links

- **SQL Editor**: `https://supabase.com/dashboard/project/YOUR_PROJECT/sql`
- **Table Editor**: `https://supabase.com/dashboard/project/YOUR_PROJECT/editor`
- **API Settings**: `https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api`

### Essential SQL Queries

```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;

-- Count rows in each table
SELECT 'contractors' as table, COUNT(*) FROM contractors
UNION ALL SELECT 'mood_areas', COUNT(*) FROM mood_areas
UNION ALL SELECT 'traffic_segments', COUNT(*) FROM traffic_segments
UNION ALL SELECT 'noise_segments', COUNT(*) FROM noise_segments
UNION ALL SELECT 'issues', COUNT(*) FROM issues
UNION ALL SELECT 'work_orders', COUNT(*) FROM work_orders
UNION ALL SELECT 'emergency_queue', COUNT(*) FROM emergency_queue;

-- View sample data
SELECT * FROM contractors LIMIT 5;
SELECT * FROM mood_areas;
SELECT * FROM traffic_segments LIMIT 5;
```

---

**Time to Complete**: ~10 minutes
**Difficulty**: Beginner-friendly
**Prerequisites Met**: ✓ Ready for backend and frontend development
