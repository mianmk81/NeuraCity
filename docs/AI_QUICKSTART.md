# NeuraCity AI Services - Quick Start Guide

## Get Started in 5 Minutes

This guide will help you test all AI services quickly without needing API keys or database setup.

## Prerequisites

```bash
cd C:\Users\mianm\Downloads\NeuraCity\backend
pip install -r requirements.txt
```

## Test 1: Generate Synthetic Data (30 seconds)

```bash
cd C:\Users\mianm\Downloads\NeuraCity
python scripts/generate_synthetic_posts.py --posts-per-area 20
```

**Output**: Creates `data/synthetic_posts.json` with 100 posts across 5 city areas.

---

## Test 2: Run AI Examples (2 minutes)

```bash
python scripts/example_ai_usage.py
```

This will demonstrate:
1. ✅ Mood analysis on sample posts
2. ✅ Emergency summary generation
3. ✅ Work order generation
4. ✅ Action engine workflow
5. ✅ Batch processing

**Expected Output**:
```
====================================================================
EXAMPLE 1: Mood Analysis
====================================================================

--- MIDTOWN ---

Individual Post Analysis:
  NEGATIVE (-0.85): Traffic is absolutely terrible in Midtown...
  POSITIVE (+0.92): Love the new coffee shop in Midtown!
  NEUTRAL  (+0.12): Just another day at the office...

Area Mood Summary:
  Mood Score: 0.123
  Post Count: 5
  Distribution:
    Positive: 2
    Neutral:  1
    Negative: 2
```

---

## Test 3: Run Unit Tests (1 minute)

```bash
cd backend
pytest tests/test_ai_services.py -v
```

**Expected**: 30+ tests pass, showing all services work correctly.

---

## Test 4: Quick Python Test

```python
# Test in Python REPL
import sys
sys.path.insert(0, 'C:/Users/mianm/Downloads/NeuraCity/backend')

from app.services import MoodAnalysisService

# Analyze sentiment
service = MoodAnalysisService()
print(service.analyze_post_sentiment("I love this city!"))  # ~0.95
print(service.analyze_post_sentiment("Traffic is horrible"))  # ~-0.85
```

---

## Test 5: Process Synthetic Posts

```python
import sys
import json
import asyncio
sys.path.insert(0, 'C:/Users/mianm/Downloads/NeuraCity/backend')

from app.services import MoodAnalysisService

async def test_mood():
    # Load synthetic posts
    with open('data/synthetic_posts.json') as f:
        posts_by_area = json.load(f)

    # Analyze each area
    service = MoodAnalysisService()

    for area_id, posts in posts_by_area.items():
        mood_data = await service.calculate_area_mood(area_id, posts)
        print(f"{area_id}: Mood={mood_data['mood_score']:.3f}, Posts={mood_data['post_count']}")

asyncio.run(test_mood())
```

**Expected Output**:
```
MIDTOWN: Mood=0.123, Posts=20
DOWNTOWN: Mood=0.089, Posts=20
CAMPUS: Mood=0.756, Posts=20
PARK_DISTRICT: Mood=0.812, Posts=20
RESIDENTIAL_ZONE: Mood=0.034, Posts=20
```

---

## Test 6: Emergency Summary Generation

```python
import sys
import asyncio
sys.path.insert(0, 'C:/Users/mianm/Downloads/NeuraCity/backend')

from app.services import GeminiService

async def test_emergency():
    service = GeminiService()  # No API key = template mode

    accident = {
        'id': 'test-123',
        'lat': 40.7589,
        'lng': -73.9851,
        'issue_type': 'accident',
        'description': 'Multi-car collision',
        'severity': 0.90,
        'created_at': '2025-11-14T10:00:00Z'
    }

    summary = await service.generate_emergency_summary(accident)
    print(summary)

asyncio.run(test_emergency())
```

**Expected Output**:
```
EMERGENCY ALERT - TRAFFIC ACCIDENT
Location: Coordinates 40.7589, -73.9851
Severity: CRITICAL (0.9/1.0)
Description: Multi-car collision
Recommended Response: Dispatch ambulance, fire rescue, and traffic control IMMEDIATELY
Additional Notes: Citizen-reported with photo evidence. GPS location confirmed.
Report Time: 2025-11-14T10:00:00Z
```

---

## Test 7: Work Order Generation

```python
import sys
import asyncio
sys.path.insert(0, 'C:/Users/mianm/Downloads/NeuraCity/backend')

from app.services import GeminiService

async def test_work_order():
    service = GeminiService()

    pothole = {
        'id': 'test-456',
        'issue_type': 'pothole',
        'severity': 0.75,
        'description': 'Large pothole on Main St',
        'lat': 40.7128,
        'lng': -74.0060
    }

    work_order = await service.generate_work_order_suggestion(pothole)
    print(f"Priority: {work_order['estimated_priority']}")
    print(f"Contractor: {work_order['contractor_specialty']}")
    print(f"Materials: {work_order['materials'][:100]}...")

asyncio.run(test_work_order())
```

**Expected Output**:
```
Priority: URGENT
Contractor: road_repair
Materials: Asphalt mix (hot), road cones (6-8), safety barriers, hand tamper or compactor, shovels, broom...
```

---

## Using with Gemini API Key

To test actual AI generation (not templates):

1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Set environment variable:
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

3. Run tests:
```python
from app.services import GeminiService
import os

service = GeminiService(api_key=os.getenv('GEMINI_API_KEY'))
# Now uses actual AI generation
```

---

## Common Issues

### "transformers not found"
```bash
pip install transformers torch sentencepiece
```

### "faker not found"
```bash
pip install faker
```

### Model download is slow
- First run downloads ~250MB model
- Subsequent runs use cached model
- To pre-download: `python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')"`

### Out of memory
- Uses CPU by default (slower but works)
- GPU requires CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu118`

---

## Next Steps

1. ✅ Generate synthetic posts
2. ✅ Test mood analysis
3. ✅ Test emergency summaries
4. ✅ Test work orders
5. ⏭️ Integrate with backend API
6. ⏭️ Set up Supabase database
7. ⏭️ Connect to frontend

See `backend/app/services/README.md` for full documentation.

---

## Performance Benchmarks

Run benchmark tests:

```bash
pytest backend/tests/test_ai_services.py::TestPerformance -v
```

**Expected Performance** (CPU):
- Mood analysis: 50-100ms per post (after model load)
- Batch 100 posts: < 30 seconds
- Emergency summary: 2-5 seconds (with API) or instant (template)
- Work order: 2-5 seconds (with API) or instant (template)

**With GPU** (if available):
- Mood analysis: 5-10ms per post
- Batch 100 posts: < 5 seconds

---

## Success Criteria

After running these tests, you should see:

- ✅ Synthetic posts generated successfully
- ✅ Mood scores calculated for all areas
- ✅ Emergency summaries created for accidents
- ✅ Work orders generated for infrastructure issues
- ✅ All tests passing
- ✅ No errors in output

If all green, the AI services are working correctly and ready for integration!

---

## Support

- Full docs: `backend/app/services/README.md`
- Examples: `scripts/example_ai_usage.py`
- Tests: `backend/tests/test_ai_services.py`
- Summary: `docs/AI_SERVICES_SUMMARY.md`
