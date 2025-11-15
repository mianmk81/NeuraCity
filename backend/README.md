# NeuraCity Backend API

Complete, production-ready FastAPI backend for the NeuraCity intelligent smart city platform.

## Features

- **Issue Reporting**: Image-based citizen issue reporting with automatic GPS location
- **AI-Powered Analysis**: 
  - Emergency summaries using Google Gemini
  - Work order suggestions with material and contractor recommendations
  - Sentiment analysis for mood mapping using HuggingFace
- **Smart Routing**: Three route types (drive, eco, quiet_walk) with A* pathfinding
- **Admin Tools**: Emergency queue management and work order approval system
- **Real-time Data**: Traffic, noise, and mood area analytics

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Supabase account and project
- Google Gemini API key

### Setup

1. **Clone and navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your keys:
# - SUPABASE_URL
# - SUPABASE_KEY
# - SUPABASE_SERVICE_KEY
# - GEMINI_API_KEY
```

5. **Run the server**:
```bash
# Using run.py
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload --port 8000
```

6. **Access the API**:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Issues
- `POST /api/v1/issues` - Create new issue (requires image + GPS + type)
- `GET /api/v1/issues` - List issues with filters
- `GET /api/v1/issues/{id}` - Get single issue
- `PATCH /api/v1/issues/{id}` - Update issue
- `DELETE /api/v1/issues/{id}` - Delete issue

### Mood
- `GET /api/v1/mood` - Get mood areas with sentiment scores

### Traffic
- `GET /api/v1/traffic` - Get traffic segments with congestion data

### Noise
- `GET /api/v1/noise` - Get noise segments with dB levels

### Routing
- `POST /api/v1/plan` - Plan route (drive/eco/quiet_walk)

### Admin
- `GET /api/v1/admin/emergency` - Get emergency queue
- `PATCH /api/v1/admin/emergency/{id}` - Update emergency status
- `GET /api/v1/admin/work-orders` - Get work orders
- `POST /api/v1/admin/work-orders/{id}/approve` - Approve work order
- `PATCH /api/v1/admin/work-orders/{id}` - Update work order

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/       # API route handlers
│   │   │   ├── issues.py
│   │   │   ├── mood.py
│   │   │   ├── traffic.py
│   │   │   ├── noise.py
│   │   │   ├── routing.py
│   │   │   └── admin.py
│   │   └── schemas/         # Pydantic models
│   │       ├── issue.py
│   │       ├── mood.py
│   │       ├── traffic.py
│   │       ├── noise.py
│   │       ├── routing.py
│   │       └── admin.py
│   ├── core/               # Core configuration
│   │   ├── config.py
│   │   ├── database.py
│   │   └── dependencies.py
│   ├── services/           # Business logic
│   │   ├── supabase_service.py
│   │   ├── image_service.py
│   │   ├── scoring_service.py
│   │   ├── routing_service.py
│   │   ├── gemini_service.py
│   │   ├── mood_analysis.py
│   │   └── action_engine.py
│   ├── utils/              # Utilities
│   │   ├── validators.py
│   │   └── helpers.py
│   └── main.py             # FastAPI app
├── tests/                  # Test files
├── uploads/                # Uploaded images
├── requirements.txt
├── .env.example
├── run.py
└── README.md
```

## Environment Variables

See `.env.example` for all required and optional environment variables.

### Required
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_KEY` - Supabase service role key
- `GEMINI_API_KEY` - Google Gemini API key

### Optional
- `HUGGINGFACE_API_KEY` - HuggingFace API key (for remote inference)
- `BACKEND_HOST` - Server host (default: 0.0.0.0)
- `BACKEND_PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: False)
- `CORS_ORIGINS` - Allowed CORS origins

## Database Schema

The backend requires the following Supabase tables:

1. **issues** - Citizen-reported problems
2. **mood_areas** - Sentiment scores by area
3. **traffic_segments** - Traffic congestion data
4. **noise_segments** - Noise levels
5. **contractors** - Available contractors
6. **work_orders** - Infrastructure work orders
7. **emergency_queue** - Emergency summaries

See the main project README for complete schema definitions.

## AI Components

### Gemini AI
- **Emergency Summaries**: Generates dispatcher-ready summaries for accidents
- **Work Order Suggestions**: Recommends materials and contractor specialties

### HuggingFace Transformers
- **Sentiment Analysis**: Analyzes text sentiment for mood scoring
- **Model**: distilbert-base-uncased-finetuned-sst-2-english

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

## Development

### Running in Development Mode

```bash
python run.py
# or
uvicorn app.main:app --reload --port 8000
```

### Code Quality

The codebase follows:
- Type hints throughout
- Pydantic validation for all inputs
- Comprehensive error handling
- Structured logging
- Async/await patterns

## Deployment

### Environment Setup
1. Set `DEBUG=False` in production
2. Use strong, unique API keys
3. Configure proper CORS origins
4. Set up environment variables in your hosting platform

### Recommended Platforms
- **Railway** - Easy deployment with auto-scaling
- **Render** - Free tier available
- **AWS/GCP/Azure** - Full control

### Docker (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the backend directory and virtual environment is activated
2. **Database Connection**: Verify Supabase credentials in `.env`
3. **Gemini API Errors**: Check API key and quota
4. **Image Upload Failures**: Ensure `uploads/` directory exists and is writable

### Logs

Check logs for detailed error information. All services use structured logging.

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review error logs
- Ensure all environment variables are set correctly

## License

Open source - See main project LICENSE file.
