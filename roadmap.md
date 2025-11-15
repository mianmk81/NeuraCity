Understood — I will **rewrite the entire plan from scratch** with the updated rules:

### ✅ **User MUST upload an image to report an issue**

### ✅ **Location MUST be taken automatically from device GPS**

### ✅ **User MUST select the issue type**

### - `accident`

### - `pothole`

### - `traffic_light`

### - `other` (with text field to specify)

###


Here is the **full updated Markdown project plan**, ready to save as your `README.md`.

---

```markdown
# 🧠 NeuraCity – Intelligent, Human-Centered Smart City Platform

NeuraCity is a unified smart-city platform that enables citizens to report problems using **image + automatic GPS location**, while AI analyzes the city’s emotional mood, traffic, noise, and infrastructure health to provide smarter, safer, calmer routes and support city officials with automated summaries, work orders, and insights.

All data is synthetic, all maps are 2D, and the entire system runs on **React + FastAPI + Supabase + Gemini**, fully free and open-source.

---

# 📌 Table of Contents

1. [System Vision](#system-vision)  
2. [Core Capabilities](#core-capabilities)  
3. [Key Differentiators](#key-differentiators)  
4. [Technology Stack](#technology-stack)  
5. [High-Level Architecture](#high-level-architecture)  
6. [Database Schema (Supabase)](#database-schema-supabase)  
7. [Synthetic Data Specification](#synthetic-data-specification)  
8. [AI Components](#ai-components)  
9. [Routing Engine](#routing-engine)  
10. [Backend Services](#backend-services)  
11. [Frontend Structure](#frontend-structure)  
12. [User Workflows](#user-workflows)  
13. [Admin Workflows](#admin-workflows)  
14. [Map Layers](#map-layers)  
15. [Automatic Action Engine](#automatic-action-engine)  
16. [Security & Safeguards](#security--safeguards)  

---

# 🧭 System Vision

NeuraCity treats the city as a **living organism** whose infrastructure, mood, noise, and traffic patterns can be sensed, analyzed, and improved through AI-powered insights. Citizens report issues through **image evidence + GPS**, and the system enhances the report, scores urgency, and assists city officials with automated summaries, suggestions, and routing intelligence.

The platform equally supports **citizens, administrators, and urban AI analytics**.

---

# ✨ Core Capabilities

## 1. Citizen Issue Reporting (Image + GPS Required)
A citizen reports an issue through:

- Required: **Upload an image**
- Required: **Allow browser location access**
- Required: **Choose issue category**
  - `accident`
  - `pothole`
  - `traffic_light`
  - `other` → must specify text
- Optional: short description

The backend:

- Extracts GPS coordinates from device
- Stores the uploaded image
- Applies severity & urgency scoring
- Creates a structured “AI action” depending on issue type  
  (emergency summary OR work-order suggestion)

---

## 2. City Mood Analysis (Synthetic)
- Synthetic local “social posts”
- Sentiment/emotion classification using HuggingFace
- Mood stored per area (−1 = tense, +1 = positive)
- Displayed on 2D mood map (Leaflet)

---

## 3. Traffic Awareness (Synthetic)
City road segments include:

- Synthetic congestion patterns  
- Rush hour cycles  
- Event-based spikes  

Used in urgency scoring + routing.

---

## 4. Noise Awareness (Synthetic)
Noise (dB) assigned to each road segment:

- 40–50 = quiet  
- 55–65 = moderate  
- 70–85 = loud  

Used in quiet walking routes.

---

## 5. Smart Routing (Drive / Eco / Quiet Walk)
### **Driving Route**
- Avoids high-urgency issues  
- Avoids accident clusters  

### **Eco Route**
- Prefers low-congestion segments  
- Minimizes CO₂ score  

### **Quiet Walking Route**
- Penalizes noisy segments  
- Prefers quiet paths, parks, side streets  
- Displays average noise level  

All routes return:

- ETA  
- Distance  
- CO₂ or noise  
- AI-generated explanation  

---

## 6. AI-Powered Admin Support
### Emergency Queue  
For **accidents**:
- Gemini generates dispatcher-ready emergency summary  
- Stored in `emergency_queue`  
- Admin can review and act  

### Work Order System  
For potholes, traffic lights, and infrastructure:
- Gemini suggests:
  - Materials
  - Required contractor specialty
- System selects contractor from Supabase
- Creates `work_orders`

Admin must approve.

---

# 🧬 Key Differentiators

NeuraCity uniquely merges:

- Image-based reporting  
- Automatic GPS location  
- Emotion-aware city analytics  
- Noise-aware routing  
- Infrastructure planning AI  
- Contractor/material reasoning  
- Emergency summarization  
- Open-source and cost-free stack  

This system **does not exist anywhere** — it’s an entirely new category of “Urban Emotional + Infrastructure AI.”

---

# 🧰 Technology Stack

## Frontend
- React 18  
- Vite  
- TailwindCSS  
- React Router  
- Leaflet.js  
- OpenStreetMap tiles  
- Browser APIs:
  - Geolocation  
  - File upload  

## Backend
- FastAPI  
- Uvicorn  
- Supabase (Postgres) client  
- Pydantic  
- transformers (HuggingFace)  
- numpy / pandas  
- scikit-learn or A* for routing  

## AI
- Google Gemini API  
  - Emergency summaries  
  - Material suggestions  
  - Contractor specialty inference  

## Database
- Supabase Postgres (free tier)

## Deployment
- Frontend → Vercel / Netlify  
- Backend → Render / Railway  
- Database → Supabase hosted  

---

# 🏛 High-Level Architecture

```

```
            ┌──────────────────────────────┐
            │        React Frontend        │
            │  (User + Admin Interfaces)   │
            └──────────────┬───────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │       FastAPI        │
                │  Issues | Mood | AI  │
                │  Noise | Routing     │
                └───────────┬─────────┘
                            │
 ┌──────────────────────────┼──────────────────────────┐
 ▼                          ▼                          ▼
```

┌──────────────┐      ┌──────────────────────┐    ┌────────────────────┐
│ Supabase DB  │<---->│ Gemini (LLM Reasoner)│    │ Synthetic Data Jobs │
└──────────────┘      └──────────────────────┘    └────────────────────┘

````

---

# 🗄 Database Schema (Supabase)

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
````

---

# 🧪 Synthetic Data Specification

## 1. Synthetic Areas

* Midtown
* Downtown
* Campus
* Park District
* Residential Zone

Each with fixed lat/lng.

## 2. Synthetic Posts (for mood)

Created via Faker:

```
area_id, timestamp, text
MIDTOWN, 2025-01-01 09:00, "Terrible traffic this morning"
CAMPUS, 2025-01-01 10:00, "Amazing weather today!"
```

## 3. Synthetic Traffic

* Rush hour formula
* Event-based random peaks

## 4. Synthetic Noise

* 40–85 dB
* Parks = quiet
* Highways = loud

---

# 🤖 AI Components

### 1. Mood Engine (HuggingFace)

* Classifies each synthetic post
* Aggregates sentiment → mood score

### 2. Gemini AI Reasoning

**For accidents:**

* Creates a dispatcher-friendly emergency summary

**For potholes & traffic lights:**

* Suggests:

  * Materials
  * Required contractor specialty
* System selects contractor → creates work order

---

# 🧭 Routing Engine

## 1. Driving Route

Cost:

```
time_cost + 0.5 * urgency_penalty
```

## 2. Eco Route

Cost:

```
time_cost + 0.8 * congestion
```

## 3. Quiet Walking Route

Cost:

```
time_cost + α * noise_norm
```

Where `noise_norm` is normalized dB (0–1).

Outputs:

* ETA
* Distance
* CO₂ or noise score
* Explanation

---

# ⚙ Backend Services

Endpoints:

* `POST /issues`

  * Requires: image upload + GPS + type
  * Triggers Gemini actions

* `GET /issues`

* `PATCH /issues/{id}`

* `GET /mood`

* `GET /noise`

* `GET /traffic`

* `POST /plan`

* `GET /admin/emergency`

* `GET /admin/work-orders`

* `POST /admin/work-orders/{id}/approve`

---

# 🎨 Frontend Structure

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

---

# 👥 User Workflows

## 1. Report Issue (Image + GPS Required)

1. User uploads an **image**
2. Browser asks: **Allow location?**
3. User selects issue type
4. If `other` → user must type their custom type
5. FastAPI:

   * Stores image URL
   * Saves GPS coordinates
   * Computes severity + urgency + priority
   * Creates emergency/work order tasks
6. Confirmation screen shows severity/urgency

---

## 2. Plan Trip

* User picks origin/destination
* Chooses:

  * Drive
  * Eco drive
  * Quiet walk
* System returns route with explanation

---

## 3. View Mood Map

* Areas colored by emotional mood

---

# 🏛 Admin Workflows

## Emergency Queue

* Accident issues appear here
* Shows Gemini-generated 911 summary
* Button: "Review emergency"

## Work Orders

* Potholes & traffic lights create auto suggestions
* Contractor + materials displayed
* Admin approves

## Issue Management

* View issue list
* Update status

---

# 🗺 Map Layers

1. Issue Pins
2. Mood Circles
3. Noise Heatmap
4. Traffic Lines
5. Route Polyline

---

# 🤝 Automatic Action Engine

### Accidents

* Gemini generates:

  * Summary
  * Severity notes
  * Quick dispatcher script

### Potholes / Traffic Lights

* Gemini generates:

  * Material list
  * Contractor specialty
* Work order created in Supabase

Admin makes final approval.

---

# 🔒 Security & Safeguards

* No automatic 911 calls
* Mandatory user image + GPS for evidence
* Admin validation required for tasks
* Synthetic data only
* No personal data stored


