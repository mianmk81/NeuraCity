# NeuraCity API - Quick Reference Guide

## Base URL
```
http://localhost:8000/api/v1
```

## New Endpoints Summary

### Gamification System

#### Create User
```http
POST /users
Content-Type: application/json

{
  "username": "citizen_123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": "https://example.com/avatar.jpg"
}

Response: 201 Created
{
  "id": "uuid",
  "username": "citizen_123",
  "email": "user@example.com",
  "total_points": 0,
  "rank": 0,
  "issues_reported": 0,
  "issues_verified": 0,
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Get User Profile
```http
GET /users/{user_id}

Response: 200 OK
{
  "id": "uuid",
  "username": "citizen_123",
  "total_points": 450,
  "rank": 12,
  "issues_reported": 15,
  "issues_verified": 8,
  ...
}
```

#### Get Leaderboard
```http
GET /users?page=1&page_size=10

Response: 200 OK
{
  "total": 150,
  "page": 1,
  "page_size": 10,
  "entries": [
    {
      "id": "uuid",
      "username": "top_citizen",
      "total_points": 1250,
      "rank": 1,
      ...
    }
  ]
}
```

#### Get Points History
```http
GET /users/{user_id}/points-history?limit=50

Response: 200 OK
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "points": 50,
    "action_type": "issue_reported",
    "issue_id": "uuid",
    "description": "Reported pothole issue",
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

#### Update User Profile
```http
PATCH /users/{user_id}
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "avatar_url": "https://example.com/new_avatar.jpg"
}

Response: 200 OK
```

---

### Accident History

#### Get Accident History
```http
GET /accidents/history?page=1&page_size=20&start_date=2025-01-01T00:00:00Z&min_lat=37.7&max_lat=37.8

Response: 200 OK
{
  "total": 42,
  "page": 1,
  "page_size": 20,
  "accidents": [
    {
      "id": "uuid",
      "lat": 40.7128,
      "lng": -74.0060,
      "severity": 0.85,
      "urgency": 0.9,
      "priority": "critical",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**Query Parameters:**
- `start_date` (optional): ISO 8601 datetime
- `end_date` (optional): ISO 8601 datetime
- `min_lat` (optional): -90 to 90
- `max_lat` (optional): -90 to 90
- `min_lng` (optional): -180 to 180
- `max_lng` (optional): -180 to 180
- `page` (default: 1)
- `page_size` (default: 20, max: 100)

#### Get Accident Hotspots
```http
GET /accidents/hotspots?min_accidents=2&limit=50

Response: 200 OK
{
  "total": 8,
  "hotspots": [
    {
      "lat": 40.713,
      "lng": -74.006,
      "accident_count": 5,
      "avg_severity": 0.75,
      "avg_urgency": 0.82,
      "last_accident_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

#### Get Accident Statistics
```http
GET /accidents/statistics?start_date=2025-01-01T00:00:00Z

Response: 200 OK
{
  "total_accidents": 42,
  "avg_severity": 0.68,
  "avg_urgency": 0.72,
  "critical_count": 8,
  "high_count": 15,
  "resolved_count": 20,
  "open_count": 22
}
```

#### Get Accident Trends
```http
GET /accidents/trends?days=30

Response: 200 OK
{
  "period_days": 30,
  "total_in_period": 42,
  "avg_per_day": 1.4,
  "daily_counts": [...],
  "trend_direction": "stable"
}
```

---

### Community Risk Index

#### Get Risk Index
```http
GET /risk-index?min_lat=37.7&max_lat=37.8&min_lng=-122.5&max_lng=-122.4&limit=100

Response: 200 OK
{
  "total": 125,
  "blocks": [
    {
      "block_id": "37.75_-122.45",
      "center_lat": 37.75,
      "center_lng": -122.45,
      "overall_risk": 0.72,
      "accident_count": 5,
      "pothole_count": 12
    }
  ]
}
```

**Query Parameters:**
- `min_lat` (required): Minimum latitude
- `max_lat` (required): Maximum latitude
- `min_lng` (required): Minimum longitude
- `max_lng` (required): Maximum longitude
- `min_risk` (optional): 0 to 1
- `limit` (default: 100, max: 500)

#### Get Risk Block Details
```http
GET /risk-index/37.75_-122.45

Response: 200 OK
{
  "block_id": "37.75_-122.45",
  "center_lat": 37.75,
  "center_lng": -122.45,
  "bounds_min_lat": 37.745,
  "bounds_min_lng": -122.455,
  "bounds_max_lat": 37.755,
  "bounds_max_lng": -122.445,
  "overall_risk": 0.72,
  "risk_breakdown": {
    "accident_risk": 0.85,
    "infrastructure_risk": 0.65,
    "traffic_risk": 0.70
  },
  "statistics": {
    "accident_count": 5,
    "pothole_count": 12,
    "traffic_light_count": 2,
    "avg_congestion": 0.68,
    "avg_noise_db": 72.5,
    "avg_severity": 0.63
  },
  "updated_at": "2025-01-15T10:30:00Z"
}
```

#### Calculate Risk for Area
```http
POST /risk-index/calculate?min_lat=37.7&max_lat=37.8&min_lng=-122.5&max_lng=-122.4&block_size=0.01

Response: 200 OK
{
  "blocks_updated": 125,
  "message": "Successfully recalculated risk for 125 blocks"
}
```

**Query Parameters:**
- `min_lat` (required): Minimum latitude
- `max_lat` (required): Maximum latitude
- `min_lng` (required): Minimum longitude
- `max_lng` (required): Maximum longitude
- `block_size` (default: 0.01 ~ 1km)

**Note:** Area must be <= 0.5 degrees (~55km) to prevent abuse.

#### Get High-Risk Areas
```http
GET /risk-index/high-risk-areas?min_risk=0.6&limit=50

Response: 200 OK
{
  "total": 15,
  "min_risk_threshold": 0.6,
  "high_risk_areas": [...]
}
```

---

### Modified Endpoints

#### Create Issue (with Gamification)
```http
POST /issues
Content-Type: multipart/form-data

lat: 40.7128
lng: -74.0060
issue_type: pothole
description: Large pothole on Main Street
image: <file>
user_id: uuid  [NEW - OPTIONAL]

Response: 201 Created
{
  "id": "uuid",
  "lat": 40.7128,
  "lng": -74.0060,
  "severity": 0.7,
  "urgency": 0.8,
  "priority": "high",
  "user_id": "uuid",
  ...
}
```

**New Behavior:**
- If `user_id` provided, points are automatically awarded
- Base points: 50 for issue_reported
- Bonus points based on severity/urgency
- Additional +10 for accident reports

---

## Point System

### Point Values
| Action | Points |
|--------|--------|
| Issue Reported | 50 + bonus |
| Issue Verified | 30 |
| Issue Resolved | 20 |
| Accident Bonus | +10 |

### Bonus Calculation
```
bonus = base_points * ((severity + urgency) / 2) * 0.5
```

Example:
- Pothole (severity: 0.7, urgency: 0.8)
- Base: 50 points
- Bonus: 50 * 0.75 * 0.5 = 18.75 points
- Total: 68 points

---

## Risk Score Formulas

### Accident Risk (0-1)
- 0 accidents: 0.0
- 1 accident: 0.3
- 2 accidents: 0.5
- 3-5 accidents: 0.7
- 6+ accidents: 0.9+

### Infrastructure Risk (0-1)
```
count_risk = min(0.7, log10(pothole_count + traffic_light_count + 1) / 2)
infrastructure_risk = count_risk * 0.6 + avg_severity * 0.4
```

### Traffic Risk (0-1)
```
traffic_risk = min(1.0, avg_congestion * 1.1)
```

### Overall Risk (0-1)
```
overall_risk = (accident_risk * 0.5) + (infrastructure_risk * 0.3) + (traffic_risk * 0.2)
```

---

## Caching Information

| Endpoint | Cache Duration | Notes |
|----------|----------------|-------|
| GET /users (leaderboard) | 60 seconds | Invalidated on user creation |
| GET /accidents/history | 5 minutes | Time-based expiration |
| GET /accidents/hotspots | 5 minutes | Time-based expiration |
| GET /risk-index | 10 minutes | Time-based expiration |
| GET /risk-index/{block_id} | 10 minutes | Time-based expiration |

**Cache Behavior:**
- First request: Fetches from database (~100-150ms)
- Subsequent requests: Returns cached data (~5-15ms)
- Automatic expiration based on TTL

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Username already exists"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Testing Examples (cURL)

### Create User
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "full_name": "Test User"
  }'
```

### Get Leaderboard
```bash
curl http://localhost:8000/api/v1/users?page=1&page_size=10
```

### Get Accident Hotspots
```bash
curl "http://localhost:8000/api/v1/accidents/hotspots?min_accidents=2&limit=50"
```

### Get Risk Index
```bash
curl "http://localhost:8000/api/v1/risk-index?min_lat=37.7&max_lat=37.8&min_lng=-122.5&max_lng=-122.4"
```

### Report Issue with Gamification
```bash
curl -X POST http://localhost:8000/api/v1/issues \
  -F "lat=40.7128" \
  -F "lng=-74.0060" \
  -F "issue_type=pothole" \
  -F "description=Large pothole" \
  -F "image=@/path/to/image.jpg" \
  -F "user_id=<user-uuid>"
```

---

## Rate Limiting (Not Implemented)

Currently no rate limiting is in place. For production deployment, consider:
- 100 requests/minute per IP for general endpoints
- 10 requests/minute per IP for compute-intensive endpoints (risk calculation)
- Higher limits for authenticated users

---

## Best Practices

1. **Always paginate** list endpoints to avoid large responses
2. **Use bounding boxes** instead of fetching all data
3. **Cache aggressively** on the client side
4. **Batch operations** when creating multiple users/issues
5. **Monitor cache hit rates** for performance tuning
6. **Set reasonable limits** on query parameters

---

## Support

For API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

For implementation details:
- See `IMPLEMENTATION_SUMMARY.md`
- See `CLAUDE.md` for project overview
