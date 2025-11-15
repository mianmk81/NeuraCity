# NeuraCity Project Context - November 14, 2025

## Summary
NeuraCity is an intelligent, human-centered smart city platform that enables citizens to report infrastructure issues using image evidence and automatic GPS location. The system uses AI to analyze city mood, traffic, noise, and infrastructure health to provide smart routing and automated support for city officials. The project needs to be built from scratch using a modern tech stack: React + Vite + TailwindCSS (frontend), FastAPI (backend), Supabase (database), and AI integrations (HuggingFace for mood analysis, Google Gemini for emergency summaries and work orders).

## Background

### Project Location
Working directory: `C:\Users\mianm\Downloads\NeuraCity`

### Project Type
Full-stack web application with AI components for smart city management.

### Key Constraints
- All data is synthetic (no real city data)
- All maps are 2D using Leaflet.js and OpenStreetMap tiles
- Must be fully free and open-source
- Must use Supabase free tier
- No automatic 911 calls (admin validation required)
- **Critical: Users MUST upload an image to report an issue**
- **Critical: Location MUST be taken automatically from device GPS**
- **Critical: User MUST select issue type (accident, pothole, traffic_light, other)**

### Unique Value Proposition
NeuraCity uniquely merges:
- Image-based reporting with automatic GPS location
- Emotion-aware city analytics (mood scoring)
- Noise-aware routing for quiet walking routes
- Infrastructure planning AI with contractor/material reasoning
- Emergency summarization for accidents
- Work order automation for potholes and traffic lights

## Technology Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Router** - Navigation
- **Leaflet.js** - 2D mapping
- **OpenStreetMap tiles** - Map tiles
- **Browser APIs** - Geolocation, File upload

### Backend
- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server
- **Supabase client** - Database client
- **Pydantic** - Data validation
- **transformers (HuggingFace)** - Mood/sentiment analysis
- **numpy/pandas** - Data processing
- **scikit-learn or A*** - Routing algorithms

### AI Components
- **Google Gemini API** - LLM for:
  - Emergency summaries (accidents)
  - Material suggestions (potholes/traffic lights)
  - Contractor specialty inference
- **HuggingFace Transformers** - Sentiment/emotion classification for mood analysis

### Database
- **Supabase (Postgres)** - Free tier

### Deployment Targets
- Frontend: Vercel or Netlify
- Backend: Render or Railway
- Database: Supabase hosted

## Database Schema

### Tables Required
1. **issues** - Citizen-reported problems with image, GPS, severity, urgency
2. **mood_areas** - Sentiment scores by city area
3. **traffic_segments** - Synthetic traffic congestion data
4. **noise_segments** - Synthetic noise levels (dB)
5. **contractors** - List of contractors with specialties
6. **work_orders** - Auto-generated work orders for infrastructure issues
7. **emergency_queue** - Emergency summaries for accidents

### Schema Details (from roadmap.md)
```sql
CREATE TABLE issues (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lat double precision NOT NULL,
  lng double precision NOT NULL,
  issue_type text NOT NULL,
  description text,
  image_url text NOT NULL,
  severity double precision,
  urgency double precision,
  priority text,
  action_type text,
  status text DEFAULT 'open',
  created_at timestamptz DEFAULT now()
);

CREATE TABLE mood_areas (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  area_id text,
  lat double precision,
  lng double precision,
  mood_score double precision,
  post_count integer,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE traffic_segments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  segment_id text,
  lat double precision,
  lng double precision,
  congestion double precision,
  ts timestamptz
);

CREATE TABLE noise_segments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  segment_id text,
  lat double precision,
  lng double precision,
  noise_db double precision,
  ts timestamptz
);

CREATE TABLE contractors (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text,
  specialty text,
  contact_email text,
  has_city_contract boolean DEFAULT true
);

CREATE TABLE work_orders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id uuid REFERENCES issues(id),
  contractor_id uuid REFERENCES contractors(id),
  material_suggestion text,
  status text DEFAULT 'pending_review',
  created_at timestamptz DEFAULT now()
);

CREATE TABLE emergency_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id uuid REFERENCES issues(id),
  summary text,
  status text DEFAULT 'pending',
  created_at timestamptz DEFAULT now()
);
```

## Core Features & Capabilities

### 1. Citizen Issue Reporting (MANDATORY: Image + GPS)
- **Required**: Upload an image (evidence)
- **Required**: Browser location access (automatic GPS)
- **Required**: Choose issue category:
  - `accident`
  - `pothole`
  - `traffic_light`
  - `other` → must specify text
- **Optional**: Short description

**Backend Processing**:
- Extract GPS coordinates from device
- Store uploaded image
- Apply severity & urgency scoring
- Create AI action based on issue type:
  - Accidents → Emergency summary (Gemini)
  - Potholes/Traffic lights → Work order suggestion (Gemini)

### 2. City Mood Analysis
- Synthetic local "social posts" created with Faker
- Sentiment/emotion classification using HuggingFace
- Mood stored per area (-1 = tense, +1 = positive)
- Displayed on 2D mood map with Leaflet

### 3. Traffic Awareness
- Synthetic congestion patterns per road segment
- Rush hour cycles
- Event-based spikes
- Used in urgency scoring + routing

### 4. Noise Awareness
- Noise (dB) assigned to each road segment:
  - 40-50 dB = quiet
  - 55-65 dB = moderate
  - 70-85 dB = loud
- Used in quiet walking routes

### 5. Smart Routing (3 Types)

**Driving Route**:
- Avoids high-urgency issues
- Avoids accident clusters
- Cost formula: `time_cost + 0.5 * urgency_penalty`

**Eco Route**:
- Prefers low-congestion segments
- Minimizes CO₂ score
- Cost formula: `time_cost + 0.8 * congestion`

**Quiet Walking Route**:
- Penalizes noisy segments
- Prefers quiet paths, parks, side streets
- Displays average noise level
- Cost formula: `time_cost + α * noise_norm`

All routes return:
- ETA
- Distance
- CO₂ or noise metric
- AI-generated explanation

### 6. AI-Powered Admin Support

**Emergency Queue** (for accidents):
- Gemini generates dispatcher-ready emergency summary
- Stored in `emergency_queue` table
- Admin can review and act

**Work Order System** (for potholes, traffic lights):
- Gemini suggests:
  - Materials needed
  - Required contractor specialty
- System selects contractor from Supabase
- Creates entry in `work_orders` table
- Admin must approve

## Backend API Endpoints

Required endpoints:
- `POST /issues` - Create new issue (requires image upload + GPS + type, triggers Gemini actions)
- `GET /issues` - List all issues
- `PATCH /issues/{id}` - Update issue status
- `GET /mood` - Get mood data by area
- `GET /noise` - Get noise data
- `GET /traffic` - Get traffic data
- `POST /plan` - Plan a route (drive/eco/quiet walk)
- `GET /admin/emergency` - Get emergency queue
- `GET /admin/work-orders` - Get work orders
- `POST /admin/work-orders/{id}/approve` - Approve work order

## Frontend Structure

```
src/
 ├─ pages/
 │   ├─ Home.jsx
 │   ├─ ReportIssue.jsx
 │   ├─ PlanRoute.jsx
 │   ├─ MoodMap.jsx
 │   ├─ Admin.jsx
 ├─ components/
 │   ├─ ImageUpload.jsx
 │   ├─ GPSCapture.jsx
 │   ├─ IssueForm.jsx
 │   ├─ Map2D.jsx
 │   ├─ RouteCard.jsx
 │   ├─ NoiseLegend.jsx
 │   ├─ MoodLegend.jsx
 │   ├─ WorkOrderCard.jsx
 └─ lib/
     ├─ api.js
     ├─ helpers.js
```

## Synthetic Data Requirements

### Synthetic Areas
- Midtown
- Downtown
- Campus
- Park District
- Residential Zone

Each with fixed lat/lng coordinates.

### Synthetic Posts (for mood)
Created via Faker library:
```
area_id, timestamp, text
MIDTOWN, 2025-01-01 09:00, "Terrible traffic this morning"
CAMPUS, 2025-01-01 10:00, "Amazing weather today!"
```

### Synthetic Traffic
- Rush hour formula
- Event-based random peaks

### Synthetic Noise
- 40-85 dB range
- Parks = quiet (40-50 dB)
- Highways = loud (70-85 dB)

## Map Layers (Leaflet)

1. Issue Pins (color-coded by type/severity)
2. Mood Circles (colored by sentiment)
3. Noise Heatmap (gradient by dB level)
4. Traffic Lines (colored by congestion)
5. Route Polyline (planned route)

## User Workflows

### Report Issue Workflow
1. User uploads an **image** (required)
2. Browser asks: **Allow location?** (required)
3. User selects issue type (required)
4. If `other` → user must type custom type
5. FastAPI processes:
   - Stores image URL
   - Saves GPS coordinates
   - Computes severity + urgency + priority
   - Creates emergency/work order tasks via Gemini
6. Confirmation screen shows severity/urgency

### Plan Trip Workflow
1. User picks origin/destination on map
2. Chooses route type: Drive / Eco drive / Quiet walk
3. System returns route with AI-generated explanation

### View Mood Map Workflow
1. User navigates to Mood Map page
2. Areas colored by emotional mood score

## Admin Workflows

### Emergency Queue Management
- View accident issues
- Review Gemini-generated 911 summary
- Button: "Review emergency"
- Update status

### Work Order Management
- View auto-generated work orders
- See contractor + materials suggested by Gemini
- Approve or reject work orders
- Track status

### Issue Management
- View all reported issues
- Update status (open/in_progress/resolved)
- Filter by type, severity, date

## Security & Safeguards

- No automatic 911 calls (admin validation required)
- Mandatory user image + GPS for evidence
- Admin validation required for all automated tasks
- Synthetic data only (no real city data)
- No personal data stored
- Safe AI usage (content filtering on user inputs)

## Current State

### Completed
- Comprehensive roadmap.md file created with full specifications
- Project directory exists at `C:\Users\mianm\Downloads\NeuraCity`

### In Progress
- **Nothing currently in progress** - Project is in planning phase

### Not Started
- Database schema setup in Supabase
- Backend API implementation
- AI component integration (HuggingFace, Gemini)
- Frontend React application
- Synthetic data generation
- Routing engine implementation
- Deployment configuration

## Next Steps

The project needs to be built in the following order to manage dependencies:

### Phase 1: Database Setup (FIRST)
- Set up Supabase project
- Create all 7 tables with proper schema
- Add sample contractors to contractors table
- Create indexes for performance (lat/lng queries)

### Phase 2: Backend + ML (PARALLEL)
- Set up FastAPI project structure
- Implement all API endpoints
- Integrate Supabase client
- Implement HuggingFace mood analysis
- Integrate Google Gemini API for:
  - Emergency summaries
  - Work order material/contractor suggestions
- Implement routing algorithms (A* with custom cost functions)
- Create synthetic data generation scripts

### Phase 3: Frontend (AFTER Backend API is ready)
- Set up React + Vite + TailwindCSS project
- Implement all pages (Home, ReportIssue, PlanRoute, MoodMap, Admin)
- Create reusable components (ImageUpload, GPSCapture, Map2D, etc.)
- Integrate Leaflet.js with OpenStreetMap
- Connect to backend API
- Implement all map layers
- Test all user and admin workflows

### Phase 4: Integration & Testing
- End-to-end testing of all features
- AI component validation
- Performance optimization
- Security testing

### Phase 5: Deployment
- Deploy frontend to Vercel/Netlify
- Deploy backend to Render/Railway
- Configure environment variables
- Set up CI/CD pipelines

## Key Decisions & Rationale

### Why Mandatory Image + GPS?
- Provides evidence and accountability
- Prevents spam/false reports
- Enables AI to analyze issue severity from visual evidence
- Ensures accurate location data for routing and contractor dispatch

### Why Synthetic Data?
- Avoids privacy concerns
- Enables complete control over testing scenarios
- No need for real city data partnerships
- Can demonstrate full feature set without legal/privacy barriers

### Why Gemini for Work Orders?
- Advanced reasoning capabilities for material/contractor matching
- Good at structured output generation
- Free tier available for development

### Why HuggingFace for Mood Analysis?
- Open-source models available
- Can run locally or use Inference API
- Specialized sentiment analysis models
- No API costs

### Why Supabase?
- Free tier with generous limits
- Built on Postgres (mature, reliable)
- Easy to use client libraries
- Real-time capabilities (future enhancement)
- Built-in authentication (future enhancement)

## Technical Challenges & Solutions

### Challenge: Image Upload Handling
**Solution**: Use browser File API, upload to Supabase Storage, store URL in issues table

### Challenge: GPS Accuracy
**Solution**: Use browser Geolocation API with high accuracy mode, show accuracy radius to user

### Challenge: Routing with Multiple Factors
**Solution**: Implement A* algorithm with custom cost functions based on route type

### Challenge: Real-time Mood Analysis
**Solution**: Batch process synthetic posts periodically, cache mood scores, update on schedule

### Challenge: Contractor Selection Logic
**Solution**: Use Gemini to infer specialty needed, then query Supabase for matching contractor

## Environment Variables Needed

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
HUGGINGFACE_API_KEY=your_hf_api_key_or_empty_for_local
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Files & Documentation

### Key Files
- **roadmap.md** - Complete project specification (located at `C:\Users\mianm\Downloads\NeuraCity\roadmap.md`)
- **context-neuracity-2025-11-14.md** - This context file

### Documentation to Create
- README.md - Project overview and setup instructions
- API.md - Backend API documentation
- DEPLOYMENT.md - Deployment guide
- CONTRIBUTING.md - Contribution guidelines

## Agent Coordination Strategy

### Recommended Agent Specializations

1. **database-architect**
   - Create Supabase project
   - Implement all table schemas
   - Set up indexes and constraints
   - Seed initial data (contractors, synthetic areas)
   - Document connection setup

2. **expert-backend-developer**
   - Set up FastAPI project structure
   - Implement all API endpoints
   - Integrate Supabase client
   - Implement routing algorithms
   - Create synthetic data generators
   - Write API tests

3. **ml-engineering-expert**
   - Integrate HuggingFace for mood analysis
   - Integrate Google Gemini API
   - Implement emergency summary generation
   - Implement work order suggestion logic
   - Optimize model performance
   - Handle API rate limits and errors

4. **frontend-expert**
   - Set up React + Vite + TailwindCSS
   - Implement all pages and components
   - Integrate Leaflet.js maps
   - Implement image upload + GPS capture
   - Connect to backend API
   - Implement responsive design
   - Test all user flows

### Dependency Order
1. **Database first** (blocks backend)
2. **Backend + ML in parallel** (ML components integrate into backend)
3. **Frontend last** (depends on working backend API)

### Communication Between Agents
- Each agent should document their work in their respective README files
- Backend agent should create API documentation for frontend agent
- Database agent should provide connection examples
- ML agent should document model endpoints and expected inputs/outputs

## Success Criteria

### Minimum Viable Product (MVP)
- [ ] User can report issue with image + GPS + type selection
- [ ] Issues are stored in Supabase with severity/urgency scores
- [ ] Accidents generate emergency summaries via Gemini
- [ ] Potholes/traffic lights generate work orders via Gemini
- [ ] Admin can view emergency queue and work orders
- [ ] Basic map shows issue locations
- [ ] At least one routing type works (drive route)

### Full Feature Set
- [ ] All three routing types work (drive, eco, quiet walk)
- [ ] Mood map displays synthetic sentiment data
- [ ] Noise and traffic layers display on map
- [ ] Synthetic data generation scripts work
- [ ] All admin workflows functional
- [ ] Responsive design works on mobile and desktop
- [ ] Deployed and accessible via public URL

## Notes for Coordinator Agent

- This is a greenfield project - no existing code to work with
- Project directory exists but is empty except for roadmap.md
- All agents will need to create their components from scratch
- Prioritize getting database setup first as it blocks other work
- Backend and ML work can proceed in parallel once database is ready
- Frontend should wait for stable backend API
- Use absolute file paths (Windows: `C:\Users\mianm\Downloads\NeuraCity\...`)
- Ensure all agents work within the NeuraCity directory
- Coordinate API contracts between backend and frontend agents
- Track progress and blockers across all agent work
- Ensure consistent code style and documentation across all components
