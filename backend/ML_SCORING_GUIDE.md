# 🤖 ML-Based Scoring Guide for NeuraCity

This guide explains how to use **real ML models** instead of hardcoded rules for scoring issues.

---

## 📋 What We're Replacing

### Before (Hardcoded):
```python
# Simple dictionary lookup
severity = {"accident": 0.9, "pothole": 0.5}[issue_type]

# Simple if/else rules
if "injury" in description:
    severity += 0.15
```

### After (ML-Based):
```python
# AI analyzes context and predicts scores
severity = await calculate_severity_ml(
    issue_type=issue_type,
    description=description,
    image_available=True,
    location_context="near school"
)
```

---

## 🎯 Three Approaches

### **Option 1: Gemini AI (Recommended - Already Implemented)**
✅ **CURRENT DEFAULT** - Using `ml_scoring_service.py`

**Pros:**
- No training data needed
- Understands complex context
- Considers multiple factors simultaneously
- Easy to customize prompts
- Already integrated in your code

**Cons:**
- Requires internet connection
- API costs (free tier: 15 req/min)
- ~1-2 seconds per request

**Status:** ✅ **Already active in your code!**

---

### **Option 2: HuggingFace Zero-Shot (Local ML)**
Uses: `ml_scoring_huggingface.py`

**Pros:**
- Runs 100% locally (no API calls)
- No training data needed (uses zero-shot classification)
- Free, no rate limits
- Privacy-friendly

**Cons:**
- Less accurate than Gemini
- Slower (3-5 seconds per request)
- Large model download (~1.5GB)
- Less contextual understanding

**How to switch:**
```python
# In backend/app/api/endpoints/issues.py
# Change this:
from app.services.ml_scoring_service import (

# To this:
from app.services.ml_scoring_huggingface import (
    calculate_severity_ml_hf as calculate_severity_ml,
    calculate_urgency_ml_hf as calculate_urgency_ml,
    calculate_priority_ml_hf as calculate_priority_ml,
    determine_action_type_ml_hf as determine_action_type_ml
)
```

---

### **Option 3: Fine-Tuned Custom Models (Production-Grade)**
Uses: Your own trained models

**Pros:**
- **Most accurate** - trained on your city's data
- Fast (~100ms per request)
- Runs locally
- Learns your city's patterns

**Cons:**
- Requires collecting training data (1000+ labeled examples)
- Needs ML expertise to train
- Initial setup time

**When to use:** When you have real historical data and want the best accuracy

---

## 🚀 Quick Start

### Your Code is Already Using ML! (Option 1)

I've already switched your code to use **Gemini AI-based scoring**. Here's what changed:

**File:** `backend/app/api/endpoints/issues.py`

**Before:**
```python
from app.services.scoring_service import calculate_severity

severity = calculate_severity(issue_type, description)  # Hardcoded rules
```

**After (Current):**
```python
from app.services.ml_scoring_service import calculate_severity_ml

severity = await calculate_severity_ml(
    issue_type=issue_type,
    description=description,
    image_available=True
)  # AI predicts based on context!
```

---

## 🧪 Testing the ML Scoring

### Test 1: Severity Prediction

**Run the backend:**
```bash
cd backend
python run.py
```

**Submit an issue with different descriptions:**

**Test A - Minor pothole:**
```bash
curl -X POST http://localhost:8000/api/v1/issues \
  -F "lat=37.7749" \
  -F "lng=-122.4194" \
  -F "issue_type=pothole" \
  -F "description=Small pothole, barely noticeable" \
  -F "image=@test.jpg"
```
**Expected ML Severity:** ~0.3-0.4 (low)

**Test B - Dangerous pothole:**
```bash
curl -X POST http://localhost:8000/api/v1/issues \
  -F "lat=37.7749" \
  -F "lng=-122.4194" \
  -F "issue_type=pothole" \
  -F "description=Huge pothole causing vehicles to swerve dangerously, nearly caused accident" \
  -F "image=@test.jpg"
```
**Expected ML Severity:** ~0.7-0.8 (high)

**The ML model understands the severity from context!**

---

### Test 2: Urgency Based on Time

**Morning rush hour accident:**
```python
# ML considers: accident type + rush hour + description
# Result: urgency = 0.95+ (critical)
```

**Late night pothole:**
```python
# ML considers: pothole + low traffic time + no immediate danger
# Result: urgency = 0.3-0.4 (can wait)
```

---

## 📊 How Each ML Approach Works

### Option 1: Gemini AI (Current)

**Location:** `backend/app/services/ml_scoring_service.py`

**How it works:**
1. Builds detailed prompt with context
2. Sends to Gemini AI
3. AI analyzes like a human expert would
4. Returns JSON with score + reasoning

**Example Prompt:**
```
You are an expert city infrastructure analyst. Analyze this issue:

Issue Type: pothole
Description: Large hole in road, car damaged tire
Image Evidence: Yes
Location Context: Near school zone

Provide severity score 0.0-1.0...
```

**Gemini Response:**
```json
{
  "severity": 0.75,
  "reasoning": "Significant safety risk near school, already caused vehicle damage"
}
```

---

### Option 2: HuggingFace Zero-Shot

**Location:** `backend/app/services/ml_scoring_huggingface.py`

**How it works:**
1. Uses BART model (trained on natural language understanding)
2. Classifies text into severity categories
3. Maps categories to scores
4. All runs locally on CPU

**Example:**
```python
text = "accident: multiple vehicles, person injured"
labels = [
    "minor issue",
    "moderate issue", 
    "significant issue",
    "severe issue",
    "critical emergency"  # <- Model picks this (98% confidence)
]

# Maps to severity = 0.95
```

---

### Option 3: Custom Fine-Tuned Models

**Location:** Code included in `ml_scoring_huggingface.py` (comments at bottom)

**Steps to implement:**

#### 1. Collect Training Data
```python
# Export your historical data
import pandas as pd

data = pd.DataFrame({
    'issue_type': ['pothole', 'accident', ...],
    'description': ['Large hole in road', 'Car collision', ...],
    'severity_label': [0.6, 0.9, ...],  # Expert-labeled scores
    'urgency_label': [0.5, 0.95, ...],
    'action_label': ['work_order', 'emergency', ...]
})

# Need 1000-5000 labeled examples for good performance
data.to_csv('training_data.csv')
```

#### 2. Train the Model
```bash
# Install training dependencies
pip install datasets accelerate

# Run training script (provided in ml_scoring_huggingface.py comments)
python train_severity_model.py
```

#### 3. Use Trained Model
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained("./severity_model")
tokenizer = AutoTokenizer.from_pretrained("./severity_model")

# Make predictions
inputs = tokenizer("accident with injuries", return_tensors="pt")
outputs = model(**inputs)
severity = torch.sigmoid(outputs.logits).item()
```

---

## 🔄 Switching Between Approaches

### Currently Active: Gemini AI (Option 1)

**To switch to HuggingFace (Option 2):**

1. Update imports in `backend/app/api/endpoints/issues.py`:
```python
from app.services.ml_scoring_huggingface import (
    calculate_severity_ml_hf as calculate_severity_ml,
    calculate_urgency_ml_hf as calculate_urgency_ml,
    calculate_priority_ml_hf as calculate_priority_ml,
    determine_action_type_ml_hf as determine_action_type_ml
)
```

2. Restart backend:
```bash
cd backend
python run.py
```

3. First run will download models (~1.5GB) - takes 5-10 minutes

---

### To switch to Custom Models (Option 3):

1. Train your models (see guide in `ml_scoring_huggingface.py`)
2. Save models to `backend/models/severity_model/`
3. Update `ml_scoring_huggingface.py` to load custom models:
```python
@lru_cache(maxsize=1)
def get_severity_classifier():
    model = AutoModelForSequenceClassification.from_pretrained("./models/severity_model")
    tokenizer = AutoTokenizer.from_pretrained("./models/severity_model")
    # Use model instead of zero-shot classifier
```

---

## 📈 Performance Comparison

| Approach | Speed | Accuracy | Cost | Offline? |
|----------|-------|----------|------|----------|
| **Gemini AI** | 1-2s | ⭐⭐⭐⭐⭐ | Free tier | ❌ No |
| **HuggingFace Zero-Shot** | 3-5s | ⭐⭐⭐ | Free | ✅ Yes |
| **Custom Fine-Tuned** | 0.1s | ⭐⭐⭐⭐⭐ | Free | ✅ Yes |
| **Hardcoded Rules** | 0.001s | ⭐⭐ | Free | ✅ Yes |

---

## 🎓 Understanding the ML Predictions

### What makes ML better than hardcoded rules?

**Example: Pothole Report**

**Hardcoded approach:**
```python
severity = 0.5  # All potholes get same score
if "severe" in description:
    severity += 0.1  # Simple keyword matching
# Final: 0.6
```

**ML approach (Gemini):**
```python
# Input: "Small crack in road, barely visible"
# ML Output: severity = 0.25

# Input: "Massive pothole, swallowed entire tire, car now disabled"
# ML Output: severity = 0.85

# Input: "Pothole near school, kids walk near it every day"
# ML Output: severity = 0.70 (considers location + safety)
```

**ML understands:**
- Size and impact
- Location context (school = more dangerous)
- Consequences (car damaged = higher severity)
- Comparative language ("small" vs "massive")

---

## 🔍 Debugging ML Predictions

### View ML Reasoning

Check backend logs:
```bash
cd backend
python run.py

# You'll see:
INFO: ML Severity: 0.75 - Significant safety risk near school
INFO: ML Urgency: 0.65 - Should be addressed within hours given traffic
INFO: ML Action: work_order - Requires physical repair
```

### Test Different Scenarios

Create a test script `backend/test_ml_scoring.py`:
```python
import asyncio
from app.services.ml_scoring_service import calculate_severity_ml

async def test():
    # Test minor issue
    severity1 = await calculate_severity_ml(
        issue_type="pothole",
        description="Tiny crack, barely noticeable"
    )
    print(f"Minor pothole: {severity1}")
    
    # Test major issue
    severity2 = await calculate_severity_ml(
        issue_type="pothole",
        description="Massive hole, destroyed car tire, dangerous"
    )
    print(f"Major pothole: {severity2}")

asyncio.run(test())
```

Run:
```bash
cd backend
python test_ml_scoring.py
```

---

## 🛠️ Customizing ML Behavior

### Adjust Gemini Prompts

Edit `backend/app/services/ml_scoring_service.py`:

**Make it more conservative:**
```python
prompt = f"""You are a cautious infrastructure analyst. 
Be conservative with severity scores. 
Only rate as critical if there's immediate life-threatening danger.
...
"""
```

**Make it more sensitive:**
```python
prompt = f"""You are a proactive safety officer. 
Err on the side of caution.
Consider potential risks even if not explicitly stated.
...
"""
```

### Add New Context Factors

```python
async def calculate_severity_ml(
    issue_type: str,
    description: Optional[str] = None,
    image_available: bool = True,
    location_context: Optional[str] = None,
    weather: Optional[str] = None,  # NEW
    nearby_schools: bool = False,   # NEW
    previous_incidents: int = 0     # NEW
):
    prompt = f"""...
Weather Conditions: {weather}
Near Schools/Hospitals: {nearby_schools}
Previous Incidents at Location: {previous_incidents}
...
"""
```

---

## 📚 Next Steps

### For Development (Current State):
✅ **You're ready!** Gemini ML is active and working.

### For Production:
1. **Monitor Gemini usage** - Check API limits
2. **Collect feedback** - Compare ML scores vs expert opinions
3. **Consider training custom models** - When you have 1000+ labeled examples

### For Local/Offline Use:
1. Switch to HuggingFace approach (Option 2)
2. Accept slightly lower accuracy for offline capability

---

## ❓ FAQ

**Q: Will this slow down the API?**
A: Gemini adds 1-2 seconds. HuggingFace adds 3-5 seconds. Still acceptable for most use cases.

**Q: What if Gemini API is down?**
A: Code automatically falls back to hardcoded rules. System never breaks.

**Q: Can I use both approaches?**
A: Yes! Use Gemini as primary, HuggingFace as fallback:
```python
try:
    severity = await calculate_severity_ml(...)  # Gemini
except:
    severity = await calculate_severity_ml_hf(...)  # HuggingFace fallback
```

**Q: How do I know if ML is working?**
A: Check logs for "ML Severity: X.XX" messages. Compare scores for similar issues with different descriptions.

---

## 🎉 Summary

**You now have:**
- ✅ ML-based scoring (Gemini) already active
- ✅ Alternative approach (HuggingFace) ready to use
- ✅ Guide for training custom models
- ✅ Fallback to rules if ML fails

**The hardcoded rules are replaced with actual machine learning!** 🚀


