# Railway Quick Start Guide

## 🚀 Deploy in 5 Minutes

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Create Railway Project
1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your NeuraCity repository

### Step 3: Configure Environment Variables
In Railway dashboard → Your Service → Variables, add:

**Required:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `SUPABASE_SERVICE_KEY` - Your Supabase service key
- `GEMINI_API_KEY` - Your Google Gemini API key
- `BACKEND_HOST=0.0.0.0`
- `BACKEND_PORT=8000`
- `DEBUG=False`

**After deployment, update:**
- `CORS_ORIGINS` - Add your Railway app URL (e.g., `https://your-app.railway.app`)

### Step 4: Deploy
Railway will automatically:
1. Detect Python backend
2. Install dependencies from `backend/requirements.txt`
3. Run `python run.py` to start the server

### Step 5: Get Your URL
Railway provides a URL like: `https://your-app.railway.app`

Update `CORS_ORIGINS` with this URL and redeploy.

## 📝 Two-Service Setup (Recommended)

For better separation, deploy frontend and backend separately:

### Backend Service
- Root: `backend/`
- Build: `pip install -r requirements.txt`
- Start: `python run.py`

### Frontend Service
- Root: `frontend/`
- Build: `npm install && npm run build`
- Start: `npx serve -s dist -l $PORT`
- Env: `VITE_API_URL=https://your-backend.railway.app/api/v1`

## 🔧 Troubleshooting

**Backend won't start?**
- Check logs in Railway dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` is correct

**Frontend can't connect?**
- Set `VITE_API_URL` environment variable
- Update `CORS_ORIGINS` in backend
- Check Railway service URLs

## 📚 Full Documentation
See `RAILWAY_DEPLOYMENT.md` for detailed instructions.

