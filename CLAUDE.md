# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

### Backend (FastAPI)
```bash
# Development
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                    # Start server on port 8000
# OR
python -m app.main              # Alternative startup
uvicorn app.main:app --reload   # With uvicorn directly

# Testing
pytest tests/ -v                 # Run all tests
pytest tests/test_issues.py -v  # Run specific test file
python test_integration.py       # Test DB + backend integration
```

### Frontend (React + Vite)
```bash
# Development
cd frontend
npm install
npm run dev          # Start dev server on port 5173
npm run build        # Production build
npm run preview      # Preview production build
```

### Database (Supabase)
```bash
# Setup
cd database
pip install -r requirements.txt
python setup.py                                      # Interactive setup wizard
python seeds/generate_data.py --days=7              # Generate base synthetic data
python seeds/generate_gamification_data.py --users=100 --days=30  # Generate gamification data
python seeds/generate_risk_data.py --blocks=200 --days=30         # Generate risk index data
python verify.py                                     # Verify database health
python reset.py                                      # Reset database (careful!)
```

### Verification
```bash
# From project root
python verify_codebase.py     # Verify all files present
python test_integration.py    # Test full integration
```

## Architecture Overview

### Three-Tier Architecture
```
Frontend (React) ←→ Backend (FastAPI) ←→ Database (Supabase)
                         ↓
                    AI Services (Gemini + HuggingFace)
```

### Data Flow: Issue Reporting
The core workflow demonstrates how all components interact:

1. **User submits issue** (image + GPS + type) via `frontend/src/pages/ReportIssue.jsx`
2. **Frontend API client** sends multipart/form-data to `POST /api/v1/issues`
3. **Issues endpoint** (`backend/app/api/endpoints/issues.py`) validates and processes:
   - `image_service.py` validates and saves image to `uploads/`
   - `scoring_service.py` calculates severity (0-1) and urgency (0-1) based on type, description, traffic, time
   - `scoring_service.py` derives priority (low/medium/high/critical) and action_type (emergency/work_order/monitor)
4. **Supabase service** inserts issue into `issues` table
5. **Action engine** (`services/action_engine.py`) automatically triggers:
   - If `action_type == "emergency"`: calls `gemini_service.py` to generate dispatcher summary → inserts into `emergency_queue` table
   - If `action_type == "work_order"`: calls `gemini_service.py` for material suggestions + contractor specialty → selects contractor from `contractors` table → inserts into `work_orders` table
6. **Response returns** to frontend with calculated scores

### Service Layer Pattern
All business logic lives in `backend/app/services/`:
- `supabase_service.py`: Database CRUD for all tables (wrapper around Supabase client)
- `image_service.py`: File upload validation, storage, deletion
- `scoring_service.py`: Severity/urgency calculation based on issue attributes and context
- `routing_service.py`: A* pathfinding with three cost functions (drive/eco/quiet_walk)
- `gemini_service.py`: Google Gemini API integration for summaries and suggestions
- `mood_analysis.py`: HuggingFace sentiment analysis (distilbert model)
- `action_engine.py`: Orchestrates AI actions based on issue type
- `gamification_service.py`: Point awards, rank calculation, leaderboard management
- `accident_history_service.py`: Historical accident aggregation and hotspot identification
- `risk_index_service.py`: Composite risk scoring from 7 factors (crime, blight, air quality, etc.)

### Frontend State Management
No Redux/Zustand - uses React hooks (useState, useEffect) with:
- `src/lib/api.js`: Centralized Axios client with 5-minute TTL caching (70% reduction in redundant calls)
- `src/lib/helpers.js`: Utility functions (color mapping, formatting, validation)
- Component-local state for UI interactions
- Props drilling for shared data (intentionally simple)
- React.lazy() code splitting for 40-60% faster initial load

### Database Schema (15 Tables)
All tables use UUID primary keys with `gen_random_uuid()`:

**Core Infrastructure** (7 tables):
1. **issues**: Core issue reports (lat, lng, issue_type, image_url, severity, urgency, priority, action_type, status, user_id)
2. **mood_areas**: Sentiment by city area (area_id, mood_score from -1 to +1, post_count)
3. **traffic_segments**: Road congestion (segment_id, congestion 0-1, timestamp)
4. **noise_segments**: Noise levels (segment_id, noise_db, timestamp)
5. **contractors**: Service providers (name, specialty, contact_email, has_city_contract)
6. **work_orders**: Repair tasks (issue_id FK, contractor_id FK, material_suggestion, status)
7. **emergency_queue**: Accident summaries (issue_id FK, summary from Gemini, status)

**Gamification System** (3 tables):
8. **users**: User profiles (username, email, total_points, rank: bronze/silver/gold/platinum/diamond)
9. **points_transactions**: Point award history (user_id FK, issue_id FK, points_earned, transaction_type)
10. **leaderboard**: Pre-calculated rankings for performance (user_id FK, position, total_points)

**Accident History** (1 table):
11. **accident_history**: Historical accidents with PostGIS spatial indexing (location GEOGRAPHY, severity, weather, time_of_day)

**Community Risk Index** (4 tables):
12. **block_risk_scores**: Per-block composite risk (block_id, overall_risk_score, crime_score, blight_score, air_quality_score, heat_score, traffic_score, wait_time_score, noise_score)
13. **risk_factors**: Individual factor data for risk calculation
14. **risk_history**: Historical risk snapshots for trend analysis
15. **risk_config**: Configurable weights for composite scoring

Key relationships:
- `work_orders.issue_id` → `issues.id` (CASCADE DELETE)
- `work_orders.contractor_id` → `contractors.id` (SET NULL)
- `emergency_queue.issue_id` → `issues.id` (CASCADE DELETE)
- `points_transactions.user_id` → `users.id` (CASCADE DELETE)
- `points_transactions.issue_id` → `issues.id` (SET NULL)
- `accident_history.issue_id` → `issues.id` (CASCADE DELETE)

**Indexes**: 53 total (28 new for spatial queries, gamification lookups, and risk filtering)

## Critical Integration Points

### Environment Variables
**Backend** requires (in `backend/.env`):
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-api-key
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Frontend** requires (in `frontend/.env`):
```
VITE_API_URL=http://localhost:8000/api/v1
```

### CORS Configuration
Backend CORS is configured in `app/main.py` to accept origins from `CORS_ORIGINS` env var. Default includes `localhost:5173` (Vite dev server). Update when deploying.

### Image Upload Flow
- Images POST to `/api/v1/issues` as multipart/form-data
- Saved to `backend/uploads/` directory (created on app startup)
- Served statically via `/uploads/{filename}` route
- Frontend displays via `<img src={issue.image_url} />`
- Max size: 10MB (configurable via `MAX_UPLOAD_SIZE`)

### AI Service Integration
Both AI services have graceful degradation:
- **Gemini**: If API key missing or call fails, returns fallback text ("AI service unavailable")
- **HuggingFace**: If model load fails, sentiment analysis returns 0.0 (neutral)
- Models are cached with `@lru_cache` to avoid reloading

### Routing Algorithm
`routing_service.py` implements A* pathfinding with three cost functions:
- **Drive**: `time_cost + 0.5 * urgency_penalty` (avoids high-urgency issues)
- **Eco**: `time_cost + 0.8 * congestion` (minimizes traffic)
- **Quiet Walk**: `time_cost + α * noise_norm` (prefers low-noise paths)

Cost is calculated per segment using nearby issues, traffic, and noise data fetched from Supabase.

### Gamification System
The gamification system incentivizes citizen participation through points and leaderboards:
- **Point awards**: Users earn points when reporting issues (50 base + bonus based on severity/urgency)
- **Rank progression**: bronze (0-499) → silver (500-1999) → gold (2000-4999) → platinum (5000-9999) → diamond (10000+)
- **Leaderboard**: Pre-calculated table refreshed via `refresh_leaderboard()` function for performance
- **Integration**: `POST /api/v1/issues` accepts optional `user_id` parameter to link reports to users
- **Caching**: Leaderboard cached for 60 seconds to handle high read traffic

### Accident History Tracking
Historical accident data enables pattern analysis and route safety scoring:
- **Spatial storage**: Uses PostGIS GEOGRAPHY type for efficient radius queries
- **Hotspot detection**: Groups accidents by location (3 decimal precision ~110m)
- **Temporal patterns**: Tracks time_of_day (morning/afternoon/evening/night) and weather_conditions
- **Frontend visualization**: Heatmap overlay on Analytics page with date range and severity filters
- **Performance**: GIST spatial index enables sub-50ms queries for `get_nearby_accidents(lat, lng, radius)`

### Community Risk Index
Composite risk scoring helps identify underserved areas and inform resource allocation:
- **7 Risk factors**: crime (25%), emergency response (20%), blight (15%), air quality (15%), traffic (15%), heat (10%), noise
- **Block-based aggregation**: City divided into ~1km blocks (0.01 degrees) for per-block risk scores
- **Configurable weights**: `risk_config` table allows adjusting factor weights per use case
- **Spatial smoothing**: Nearby blocks influence target block via exponential decay (500m radius)
- **Risk categories**: Low (0-0.29), Moderate (0.30-0.49), High (0.50-0.69), Critical (0.70-1.00)
- **Frontend visualization**: Color-coded map on `/risk` page with detailed breakdown panels

## Key Architectural Decisions

### Why No ORM?
Uses Supabase Python client directly instead of SQLAlchemy/Tortoise because:
- Supabase client provides type-safe queries
- Simpler dependency management
- Easier to map to PostgreSQL features (UUID, timestamptz)
- Frontend also uses Supabase client (could add direct access later)

### Why Synthetic Data?
All data (issues, mood, traffic, noise) is synthetic because:
- Privacy: no real citizen data
- Testing: reproducible scenarios
- Demo-ready: populate instantly with `generate_data.py`
- Controlled: predictable patterns (rush hour, area mood biases)

### Why Three Route Types?
Each represents a different user persona:
- **Drive**: Commuter prioritizing time + safety
- **Eco**: Environmentally conscious user
- **Quiet Walk**: Pedestrian seeking peaceful routes

### Frontend Design System
All styling in `src/index.css` and `src/styles/animations.css` using:
- CSS custom properties for theming
- Tailwind utility classes for components
- No CSS-in-JS library (keeps bundle small)
- Animations via pure CSS (better performance)

## Common Development Patterns

### Adding a New Endpoint
1. Create Pydantic schema in `backend/app/api/schemas/`
2. Add endpoint function in `backend/app/api/endpoints/`
3. Import and include router in `app/main.py`
4. Add service method in relevant `services/*.py` file
5. Add API function in `frontend/src/lib/api.js`
6. Use in React component

### Adding a New Database Table
1. Create migration SQL file in `database/migrations/` (numbered: 003_feature_name.sql)
2. Add CREATE TABLE with UUID primary key: `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
3. Add indexes, foreign keys, triggers, views as needed
4. Run migration in Supabase SQL Editor
5. Add seed data generator in `database/seeds/generate_<feature>_data.py`
6. Add CRUD methods to `backend/app/services/supabase_service.py`
7. Create Pydantic schema in `backend/app/api/schemas/`
8. Update `database/verify.py` to check new table
9. Document in `database/migrations/README_MIGRATION_XXX.md`

### AI Service Pattern
See `gemini_service.py` or `mood_analysis.py` for pattern:
- Initialize client/model at module level (outside functions)
- Cache with `@lru_cache` if expensive to load
- Async functions for API calls
- Graceful error handling with fallback responses
- Logging for debugging

## Important Constraints

### Issue Reporting Requirements
- Image upload is **mandatory** (enforced in frontend and backend)
- GPS coordinates are **mandatory** (browser geolocation)
- Issue type must be: `accident`, `pothole`, `traffic_light`, or `other`
- If type is `other`, description field becomes mandatory

These are not configurable - they're core to the "evidence-based reporting" design.

### No Automatic Emergency Calls
The system generates emergency summaries but does **not** automatically dispatch. Admin must review in `/admin` page. This is a safety feature to prevent false positives.

### Synthetic Data Boundaries
- GPS coordinates hardcoded to San Francisco area (37.7-37.8 lat, -122.5 to -122.3 lng)
- Rush hour: 7-9 AM and 5-7 PM with 50% congestion increase
- 8 city areas: Midtown, Downtown, Campus, Park District, Residential, Industrial, Waterfront, Arts District
- Mood biases per area (e.g., Park District +0.3 positive)

Changing these requires updating both `database/seeds/generate_data.py` and `database/seeds/002_city_areas.sql`.

## Testing Strategy

### Backend Tests
- `tests/conftest.py`: Shared fixtures (test client, mock DB)
- `tests/test_issues.py`: Issue endpoint tests
- `test_integration.py`: Full stack integration (requires real Supabase)

### Manual Testing Flows
1. **Issue Reporting**: Upload image → Capture GPS → Select type → Submit → Verify scores + points earned toast
2. **Route Planning**: Click map twice → Select route type → Plan → Verify polyline + metrics
3. **Admin Emergency**: Report accident → Check `/admin` Emergency Queue → Verify Gemini summary
4. **Admin Work Orders**: Report pothole → Check `/admin` Work Orders → Verify materials + contractor
5. **Gamification**: Report issues → Check `/leaderboard` → Verify rank and position
6. **Accident Heatmap**: Go to `/analytics` → Toggle "Show Accident Heatmap" → Filter by date/severity
7. **Risk Index**: Go to `/risk` → Click area → Verify detailed risk breakdown

### Verification Scripts
- `verify_codebase.py`: Checks all files exist and have content
- `database/verify.py`: Checks all 15 tables exist, validates data quality, verifies 7 views
- `test_integration.py`: Tests DB → Backend → Frontend connections

## Performance Considerations

### Backend Caching
**Function-level caching**:
- Settings: `@lru_cache` on `get_settings()`
- DB client: `@lru_cache` on `get_supabase_client()`
- AI models: `@lru_cache` on `get_sentiment_pipeline()`

**Response caching (TTL-based using cachetools)**:
- Leaderboard: 60 seconds TTL, 100 entry capacity
- Accident history: 5 minutes TTL, 500 entry capacity
- Risk index: 10 minutes TTL, 1000 entry capacity
- Performance: 90-95% response time reduction for cached queries

All caches persist for app lifetime. To clear, restart server.

### Frontend Optimization
- Code splitting: React.lazy() for all page components (main bundle reduced to 73KB gzipped)
- Image lazy loading: Native `loading="lazy"` on `<img>`
- API response caching: 5-minute in-memory cache with 50 entry limit (70% reduction in network calls)
- Map layers: Separate layer groups for efficient toggling
- Component memoization: React.memo on Map2D and heavy components
- Loading skeletons: Improved perceived performance during async operations
- Performance: 40-60% faster initial page load

### Database Indexes
53 indexes total for query performance:

**Base indexes** (25):
- (lat, lng) on all location tables for bounding box queries
- (status) on issues, work_orders, emergency_queue for filtering
- (created_at DESC) and (ts DESC) for time-series queries
- (segment_id, ts) composite for traffic/noise time lookups
- (specialty) on contractors for work order matching

**Gamification indexes** (8):
- username, email, total_points DESC, rank on users
- user_id, issue_id, transaction_type, created_at DESC on points_transactions
- user_id (unique), position, total_points on leaderboard

**Spatial indexes** (4 PostGIS GIST):
- accident_history location (GEOGRAPHY)
- block_risk_scores geometry (GEOGRAPHY)
- Coordinate pairs for efficient bounding box queries

**Risk filtering indexes** (6):
- block_id (unique), overall_risk_score, area_name, crime_score, traffic_score

**Performance**: Sub-50ms spatial queries on 100k+ records

## Deployment Notes

The codebase is deployment-ready but **not deployed**. When deploying:

1. **Backend**: Railway, Render, or any Python host
   - Set all env vars
   - Ensure `uploads/` directory is writable or use S3
   - Update `CORS_ORIGINS` to include production frontend URL

2. **Frontend**: Vercel, Netlify, or static host
   - Set `VITE_API_URL` to production backend URL
   - Build with `npm run build`
   - Serve `dist/` directory

3. **Database**: Already on Supabase (cloud-hosted)
   - Enable RLS (Row Level Security) for production
   - Rotate service_role key periodically
   - Set up backups

4. **API Keys**: Use secrets management (not committed to repo)

## Common Pitfalls

### "Module not found" errors
- Backend: Ensure virtual environment is activated
- Frontend: Run `npm install` after pulling changes
- Both: Check `requirements.txt` / `package.json` are up to date

### CORS errors in browser
- Check `CORS_ORIGINS` in backend `.env` includes frontend URL
- Restart backend after changing `.env`
- Verify frontend is making requests to correct backend URL

### "Table does not exist" errors
- Run `database/schema.sql` in Supabase SQL Editor
- Verify with `python database/verify.py`
- Check Supabase credentials in backend `.env`

### AI services not working
- Gemini: Verify `GEMINI_API_KEY` is valid at makersuite.google.com
- HuggingFace: First run downloads model (~500MB), may take time
- Both: Check backend logs for detailed error messages

### Images not displaying
- Check `backend/uploads/` directory exists and is writable
- Verify image was saved (check server logs)
- Ensure backend is serving static files (check `app/main.py` mounts `/uploads`)
- Frontend must request from correct URL: `{VITE_API_URL}/uploads/{filename}`
