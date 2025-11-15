# 🚀 NeuraCity - Getting Started Guide

This guide will help you set up and run the complete NeuraCity platform in **15 minutes**.

## 📋 Prerequisites

1. **Python 3.10+** - [Download here](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download here](https://nodejs.org/) (for frontend)
3. **Supabase Account** - [Sign up free](https://supabase.com/)
4. **Google Gemini API Key** - [Get free key](https://ai.google.dev/)

---

## 🗄️ Part 1: Database Setup (5 minutes)

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com/) and sign in
2. Click **"New Project"**
3. Fill in:
   - **Name**: NeuraCity
   - **Database Password**: (create a strong password)
   - **Region**: (choose closest to you)
4. Click **"Create new project"**
5. Wait 1-2 minutes for project to be ready

### Step 2: Get Your API Credentials

1. In your Supabase project, go to **Settings** → **API**
2. Copy these values (you'll need them soon):
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)
   - **service_role** key (another long string starting with `eyJ...`)

### Step 3: Create Database Schema

1. In Supabase, click **SQL Editor** (in left sidebar)
2. Click **"New Query"**
3. Open `database/schema.sql` on your computer
4. Copy the **entire contents** and paste into the SQL Editor
5. Click **"Run"** (or press Ctrl+Enter)
6. You should see: "Success. No rows returned"

### Step 4: Add Seed Data

1. Still in SQL Editor, click **"New Query"**
2. Open `database/seeds/001_contractors.sql`
3. Copy contents and paste, then **Run**
4. Repeat for `database/seeds/002_city_areas.sql`
5. Repeat for `database/seeds/003_initial_data.sql`

### Step 5: Configure Database Environment

```bash
cd database
cp .env.example .env
```

Edit `database/.env` and add your Supabase credentials:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here
```

### Step 6: Generate Synthetic Data (Optional)

```bash
cd database
pip install -r requirements.txt
python seeds/generate_data.py --days=7
```

This will create realistic traffic, noise, and mood data for testing.

**✅ Database setup complete!**

---

## 🔧 Part 2: Backend Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

On Windows, you might need:
```bash
python -m pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your credentials:

```env
# Supabase Configuration (from Part 1, Step 2)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration (leave as default)
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=True
```

**How to get Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

### Step 3: Test Integration

Run the integration test to verify everything is connected:

```bash
cd ..  # Go back to NeuraCity root
python test_integration.py
```

You should see all tests pass:
```
✅ PASS: Environment Variables
✅ PASS: Backend Imports
✅ PASS: Database Connection
✅ PASS: Database Tables
✅ PASS: Backend Services
✅ PASS: FastAPI Application

🎉 ALL TESTS PASSED!
```

If any tests fail, check the error messages and fix the issues.

### Step 4: Start Backend Server

**Option 1: Simple (Recommended)**
```bash
cd backend
python run.py
```

**Option 2: Using startup script**

Windows:
```bash
cd backend
startup.bat
```

Linux/Mac:
```bash
cd backend
chmod +x startup.sh
./startup.sh
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**✅ Backend is running!**

### Step 5: Test the API

Open your browser and go to: **http://localhost:8000/docs**

You should see the interactive API documentation (Swagger UI).

Try these endpoints:
- **GET /health** - Should return `{"status": "healthy"}`
- **GET /api/v1/mood** - Should return mood areas
- **GET /api/v1/traffic** - Should return traffic data

**✅ Backend setup complete!**

---

## 🎨 Part 3: Frontend Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

This will install React, Vite, TailwindCSS, Leaflet, and all dependencies.

### Step 2: Configure Environment

```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Step 3: Start Frontend

```bash
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 4: Open Application

Open your browser and go to: **http://localhost:5173**

You should see the NeuraCity homepage with four feature cards.

**✅ Frontend setup complete!**

---

## 🧪 Part 4: Test the Complete System

### Test 1: View City Data

1. Go to **http://localhost:5173/mood**
2. You should see a map with colored circles showing city mood
3. Click on circles to see mood scores

### Test 2: Report an Issue

1. Go to **http://localhost:5173/report**
2. Upload an image (any jpg/png file)
3. Click "Capture GPS Location" and allow browser permission
4. Select issue type (e.g., "Pothole")
5. Add optional description
6. Click "Submit Issue Report"
7. You should see severity, urgency, and priority scores

### Test 3: Plan a Route

1. Go to **http://localhost:5173/route**
2. Click on the map to set origin
3. Click again to set destination
4. Select route type (Drive/Eco/Quiet Walk)
5. Click "Plan Route"
6. You should see a route drawn on the map with metrics

### Test 4: Admin Panel

1. Go to **http://localhost:5173/admin**
2. Check "Emergency Queue" tab - should show accidents (if any)
3. Check "Work Orders" tab - should show work orders
4. Check "All Issues" tab - should show all reported issues

**✅ Complete system is working!**

---

## 📂 Project Structure

```
NeuraCity/
├── database/              # Database setup and scripts
│   ├── schema.sql        # Complete database schema
│   ├── setup.py          # Automated setup script
│   ├── verify.py         # Verification script
│   └── seeds/            # Seed data scripts
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   ├── run.py           # Start server
│   └── .env             # Your credentials (create this!)
├── frontend/             # React frontend
│   ├── src/
│   │   ├── pages/       # Page components
│   │   ├── components/  # Reusable components
│   │   └── lib/         # API client
│   └── .env             # Your API URL (create this!)
└── test_integration.py   # Integration test script
```

---

## 🔧 Common Issues & Solutions

### Issue: "Module not found" errors

**Solution:**
```bash
# For backend
cd backend
pip install -r requirements.txt

# For frontend
cd frontend
npm install
```

### Issue: "Supabase connection failed"

**Solution:**
1. Check that your `.env` file exists in `backend/`
2. Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
3. Make sure your Supabase project is active

### Issue: "Table does not exist"

**Solution:**
1. Go to Supabase SQL Editor
2. Run `database/schema.sql` again
3. Run seed files in order (001, 002, 003)

### Issue: "CORS error" in frontend

**Solution:**
1. Make sure backend is running on port 8000
2. Check `CORS_ORIGINS` in `backend/.env` includes `http://localhost:5173`
3. Restart backend server

### Issue: "Gemini API error"

**Solution:**
1. Verify your `GEMINI_API_KEY` in `backend/.env`
2. Check that the API key is active at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Make sure you have API quota available (free tier has limits)

---

## 🚀 Running in Production

### Backend Deployment

**Railway (Recommended):**
1. Push your code to GitHub
2. Go to [railway.app](https://railway.app/)
3. Create new project → Deploy from GitHub
4. Add environment variables from `.env`
5. Deploy!

**Render:**
1. Go to [render.com](https://render.com/)
2. New Web Service → Connect GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python run.py`
5. Add environment variables

### Frontend Deployment

**Vercel (Recommended):**
```bash
cd frontend
npm run build
npx vercel
```

**Netlify:**
```bash
cd frontend
npm run build
netlify deploy --prod
```

---

## 📖 Additional Resources

- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Database Schema**: See `database/SCHEMA.md`
- **Backend README**: See `backend/README.md`
- **Frontend README**: See `frontend/README.md`

---

## 🎉 You're All Set!

Your NeuraCity platform is now running with:
- ✅ Complete database with realistic data
- ✅ FastAPI backend with AI integration
- ✅ React frontend with interactive maps
- ✅ Full integration between all components

**Access Points:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🐛 Need Help?

If you encounter any issues:
1. Run `python test_integration.py` to diagnose problems
2. Check the error messages in terminal
3. Verify all `.env` files are configured correctly
4. Make sure all dependencies are installed

Happy building! 🏙️✨
