# NeuraCity Backend API Documentation

## Overview

The NeuraCity backend is a complete FastAPI application providing intelligent city management capabilities with AI-powered issue reporting, routing, and administrative functions.

**Base URL:** `http://localhost:8000`
**API Version:** v1
**API Prefix:** `/api/v1`

## Table of Contents

1. [Authentication](#authentication)
2. [Issue Management](#issue-management)
3. [City Data](#city-data)
4. [Routing](#routing)
5. [Admin Functions](#admin-functions)
6. [Error Handling](#error-handling)

---

## Authentication

Currently, the API does not require authentication (MVP phase). Future versions will implement JWT-based authentication for admin endpoints.

---

## Issue Management

### POST /api/v1/issues
**Report a new infrastructure issue**

**Request:** `multipart/form-data`

**Required Fields:**
- `image` (file): Image evidence (REQUIRED)
- `lat` (float): Latitude coordinate (REQUIRED, -90 to 90)
- `lng` (float): Longitude coordinate (REQUIRED, -180 to 180)
- `issue_type` (string): Type of issue (REQUIRED)
  - Values: `accident`, `pothole`, `traffic_light`, `other`

**Optional Fields:**
- `description` (string): Issue description (REQUIRED for `other` type, optional otherwise, max 1000 chars)

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "lat": 40.7128,
  "lng": -74.0060,
  "issue_type": "pothole",
  "description": "Large pothole on Main Street",
  "image_url": "/uploads/issue_20250114_103000_abc123.jpg",
  "severity": 0.65,
  "urgency": 0.72,
  "priority": "high",
  "action_type": "work_order",
  "status": "open",
  "created_at": "2025-01-14T10:30:00Z"
}
```

**Automatic Actions:**
- **Accidents:** Triggers emergency summary generation (Gemini AI)
- **Potholes/Traffic Lights:** Triggers work order creation (Gemini AI)

---

### GET /api/v1/issues
**List all issues with pagination and filters**

**Query Parameters:**
- `skip` (int, default: 0): Pagination offset
- `limit` (int, default: 100, max: 1000): Number of items per page
- `issue_type` (string): Filter by issue type
- `status_filter` (string): Filter by status (`open`, `in_progress`, `resolved`, `closed`)
- `min_severity` (float): Minimum severity score (0-1)
- `max_severity` (float): Maximum severity score (0-1)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "...",
      "lat": 40.7128,
      "lng": -74.0060,
      "issue_type": "pothole",
      "description": "Large pothole",
      "image_url": "/uploads/...",
      "severity": 0.65,
      "urgency": 0.72,
      "priority": "high",
      "action_type": "work_order",
      "status": "open",
      "created_at": "2025-01-14T10:30:00Z"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 100
}
```

---

### GET /api/v1/issues/{issue_id}
**Get a specific issue by ID**

**Response:** `200 OK` (same structure as single issue)

**Errors:**
- `404 Not Found`: Issue not found

---

### PATCH /api/v1/issues/{issue_id}
**Update an issue's status or description**

**Request Body:**
```json
{
  "status": "in_progress",
  "description": "Updated description"
}
```

**Response:** `200 OK` (updated issue object)

---

### DELETE /api/v1/issues/{issue_id}
**Delete an issue (admin only)**

**Response:** `204 No Content`

---

## City Data

### GET /api/v1/mood
**Get mood sentiment data for all city areas**

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "area_id": "MIDTOWN",
      "lat": 40.7549,
      "lng": -73.9840,
      "mood_score": 0.35,
      "post_count": 45,
      "created_at": "2025-01-14T10:00:00Z"
    }
  ],
  "total": 5
}
```

**Mood Score Range:**
- `-1.0`: Very tense/negative
- `0.0`: Neutral
- `+1.0`: Very positive

---

### GET /api/v1/traffic
**Get traffic congestion data for all road segments**

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "segment_id": "SEG_001",
      "lat": 40.7580,
      "lng": -73.9855,
      "congestion": 0.75,
      "ts": "2025-01-14T10:30:00Z"
    }
  ],
  "total": 120
}
```

**Congestion Levels:**
- `0.0 - 0.3`: Low
- `0.3 - 0.7`: Moderate
- `0.7 - 1.0`: High

---

### GET /api/v1/noise
**Get noise level data for all road segments**

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "segment_id": "SEG_001",
      "lat": 40.7580,
      "lng": -73.9855,
      "noise_db": 65.5,
      "ts": "2025-01-14T10:30:00Z"
    }
  ],
  "total": 120
}
```

**Noise Levels:**
- `40-50 dB`: Quiet (parks, residential)
- `55-65 dB`: Moderate (side streets)
- `70-85 dB`: Loud (main roads, highways)
- `85+ dB`: Very loud

---

## Routing

### POST /api/v1/routing/plan
**Plan an optimized route between two points**

**Request Body:**
```json
{
  "origin": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "destination": {
    "lat": 40.7580,
    "lng": -73.9855
  },
  "route_type": "drive"
}
```

**Route Types:**
- `drive`: Fastest route, avoids accidents and high-urgency issues
- `eco`: Eco-friendly route, minimizes CO2 by avoiding congestion
- `quiet_walk`: Quiet walking route, minimizes noise exposure

**Response:** `200 OK`
```json
{
  "route_type": "drive",
  "origin": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "destination": {
    "lat": 40.7580,
    "lng": -73.9855
  },
  "path": [
    {"lat": 40.7128, "lng": -74.0060},
    {"lat": 40.7350, "lng": -73.9950},
    {"lat": 40.7580, "lng": -73.9855}
  ],
  "segments": [],
  "metrics": {
    "total_distance": 5280.0,
    "total_duration": 900.0,
    "eta_minutes": 15,
    "co2_estimate": 0.95,
    "avg_noise_db": null,
    "avg_congestion": 0.35
  },
  "ai_explanation": "This route avoids the accident on Main St and takes a slightly longer but faster path through Broadway."
}
```

**Errors:**
- `400 Bad Request`: Invalid coordinates
- `404 Not Found`: No route found between points

---

## Admin Functions

### GET /api/v1/admin/emergency
**Get emergency queue entries for accident reports**

**Query Parameters:**
- `status_filter` (string): Filter by status (`pending`, `reviewed`, `dispatched`, `resolved`)
- `skip` (int, default: 0): Pagination offset
- `limit` (int, default: 100): Items per page

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "issue_id": "550e8400-e29b-41d4-a716-446655440000",
      "summary": "Vehicle accident at intersection of Main St and 5th Ave. Multiple vehicles involved. Request immediate police and ambulance dispatch. Cross-streets: Main St & 5th Ave. Time: 10:30 AM.",
      "status": "pending",
      "created_at": "2025-01-14T10:30:00Z"
    }
  ],
  "total": 3
}
```

---

### PATCH /api/v1/admin/emergency/{entry_id}
**Update emergency queue entry status**

**Request Body:**
```json
{
  "status": "dispatched"
}
```

**Response:** `200 OK` (updated entry)

---

### GET /api/v1/admin/work-orders
**Get work orders for infrastructure issues**

**Query Parameters:**
- `status_filter` (string): Filter by status (`pending_review`, `approved`, `in_progress`, `completed`, `rejected`)
- `skip` (int, default: 0): Pagination offset
- `limit` (int, default: 100): Items per page

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440011",
      "issue_id": "550e8400-e29b-41d4-a716-446655440001",
      "material_suggestion": "Required materials: 2 bags asphalt mix (50 lbs each), 1 bucket cold patch asphalt, hand tamper. Contractor specialty: pothole_repair. Estimated time: 2-3 hours.",
      "contractor_id": "550e8400-e29b-41d4-a716-446655440020",
      "contractor_name": "City Road Repair Inc",
      "contractor_email": "repairs@cityroadrepair.com",
      "status": "pending_review",
      "created_at": "2025-01-14T10:30:00Z"
    }
  ],
  "total": 8
}
```

---

### POST /api/v1/admin/work-orders/{work_order_id}/approve
**Approve or reject a work order**

**Request Body:**
```json
{
  "approved": true,
  "notes": "Approved for immediate repair"
}
```

**Response:** `200 OK` (updated work order)

---

### PATCH /api/v1/admin/work-orders/{work_order_id}
**Update work order status or contractor**

**Request Body:**
```json
{
  "status": "in_progress",
  "contractor_id": "550e8400-e29b-41d4-a716-446655440021"
}
```

**Response:** `200 OK` (updated work order)

---

## Error Handling

All errors follow the FastAPI standard error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `204 No Content`: Resource deleted successfully
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `413 Request Entity Too Large`: File too large (max 10MB)
- `500 Internal Server Error`: Server error

---

## Testing the API

### Using curl

**Report an issue:**
```bash
curl -X POST http://localhost:8000/api/v1/issues \
  -F "image=@/path/to/image.jpg" \
  -F "lat=40.7128" \
  -F "lng=-74.0060" \
  -F "issue_type=pothole" \
  -F "description=Large pothole on Main Street"
```

**List issues:**
```bash
curl http://localhost:8000/api/v1/issues?limit=10
```

**Plan a route:**
```bash
curl -X POST http://localhost:8000/api/v1/routing/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 40.7128, "lng": -74.0060},
    "destination": {"lat": 40.7580, "lng": -73.9855},
    "route_type": "drive"
  }'
```

### Using the Interactive API Docs

Visit `http://localhost:8000/docs` for the automatically generated Swagger UI documentation, where you can test all endpoints interactively.

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd C:\Users\mianm\Downloads\NeuraCity\backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

GEMINI_API_KEY=your-gemini-api-key

BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
DEBUG=True

CORS_ORIGINS=http://localhost:5173,http://localhost:3000

MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=./uploads
```

### 3. Run the Server

```bash
# Development mode with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Installation

Check the health endpoint:
```bash
curl http://localhost:8000/health
```

---

## Important Notes

1. **Image Upload Required**: All issue reports MUST include an image file
2. **GPS Coordinates Required**: Latitude and longitude are mandatory for all issues
3. **Issue Type Required**: Must be one of: accident, pothole, traffic_light, other
4. **Description Required for 'Other'**: If issue_type is 'other', description is mandatory
5. **File Size Limit**: Maximum upload size is 10MB
6. **Allowed Image Formats**: jpg, jpeg, png, gif, webp
7. **CORS**: Configured for localhost:5173 (frontend) by default

---

## Integration with Frontend

The backend is designed to work seamlessly with the React frontend:

- **Image URLs**: Served at `/uploads/{filename}`
- **CORS**: Pre-configured for localhost:5173
- **Error Messages**: User-friendly validation messages
- **Response Format**: Consistent JSON structure across all endpoints

---

## AI Services Integration

The backend integrates with:

1. **Google Gemini API**: Emergency summaries and work order suggestions
2. **HuggingFace Transformers**: Mood/sentiment analysis (existing services)

These services are automatically triggered when creating issues with appropriate types.

---

## Database Schema

The backend expects the following Supabase tables:
- `issues`
- `mood_areas`
- `traffic_segments`
- `noise_segments`
- `contractors`
- `work_orders`
- `emergency_queue`

Refer to the main project documentation for schema details.
