# NeuraCity Backend - Quick Start Guide

## 5-Minute Setup

### 1. Prerequisites Check
- Python 3.10 or higher installed
- Supabase account created
- Gemini API key obtained

### 2. Setup Database (Supabase)

Go to your Supabase project and run this SQL:

```sql
-- Create all required tables
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

-- Add some sample contractors
INSERT INTO contractors (name, specialty, contact_email) VALUES
('City Road Repair Inc.', 'pothole_repair', 'contact@roadrepair.com'),
('ElectroCity Services', 'electrical', 'service@electrocity.com'),
('Signal Solutions', 'traffic_signal', 'info@signalsolutions.com'),
('General Contractors Co.', 'general_contractor', 'admin@generalco.com');
```

### 3. Configure Backend

```bash
# Navigate to backend directory
cd backend

# Copy environment template
cp .env.example .env

# Edit .env file and add your credentials:
# - SUPABASE_URL (from Supabase project settings)
# - SUPABASE_KEY (anon key from Supabase)
# - SUPABASE_SERVICE_KEY (service_role key from Supabase)
# - GEMINI_API_KEY (from Google AI Studio)
```

### 4. Install and Run

#### Windows:
```bash
# Double-click startup.bat
# OR run in terminal:
startup.bat
```

#### Linux/Mac:
```bash
chmod +x startup.sh
./startup.sh
```

#### Manual:
```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python run.py
```

### 5. Test the API

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Testing the Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Create an Issue (with image)
Use the interactive docs at `/docs` or:
```bash
curl -X POST "http://localhost:8000/api/v1/issues" \
  -H "Content-Type: multipart/form-data" \
  -F "lat=40.7128" \
  -F "lng=-74.0060" \
  -F "issue_type=pothole" \
  -F "description=Large pothole" \
  -F "image=@path/to/image.jpg"
```

### 3. Get Issues
```bash
curl http://localhost:8000/api/v1/issues
```

### 4. Plan a Route
```bash
curl -X POST "http://localhost:8000/api/v1/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "origin_lat": 40.7128,
    "origin_lng": -74.0060,
    "destination_lat": 40.7580,
    "destination_lng": -73.9855,
    "route_type": "drive"
  }'
```

## Common Issues

### Import Error: No module named 'app'
- Make sure you're in the `backend/` directory
- Virtual environment is activated

### Database Connection Error
- Check your Supabase credentials in `.env`
- Verify your Supabase project is active

### Gemini API Error
- Verify your API key in `.env`
- Check your API quota at Google AI Studio

### Port Already in Use
- Change `BACKEND_PORT` in `.env`
- Or kill the process using port 8000

## Next Steps

1. **Add Sample Data**: Use the Supabase dashboard to add sample mood_areas, traffic_segments, and noise_segments
2. **Test with Frontend**: Once frontend is ready, configure CORS_ORIGINS in `.env`
3. **Deploy**: See README.md for deployment instructions

## Documentation

- **Full README**: See `README.md`
- **API Documentation**: http://localhost:8000/docs
- **Project Roadmap**: See `../roadmap.md`
