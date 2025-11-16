# Railway CLI Deployment - Step by Step

## ✅ Prerequisites Complete
- Railway CLI installed: `npm install -g @railway/cli` ✅
- Node.js and npm available ✅

## 🚀 Deployment Steps

### Step 1: Login to Railway
**Run this command manually (requires browser):**
```bash
railway login
```
This will open your browser for authentication. Complete the login there.

### Step 2: Initialize Project
```bash
railway init
```
Choose:
- **Create new project** (if first time)
- **Link existing project** (if you already have one on Railway)

### Step 3: Set Environment Variables

**Option A: Set them one by one (recommended for first time):**
```bash
railway variables --set "SUPABASE_URL=your_supabase_url"
railway variables --set "SUPABASE_KEY=your_supabase_anon_key"
railway variables --set "SUPABASE_SERVICE_KEY=your_supabase_service_key"
railway variables --set "GEMINI_API_KEY=your_gemini_api_key"
railway variables --set "BACKEND_HOST=0.0.0.0"
railway variables --set "BACKEND_PORT=8000"
railway variables --set "DEBUG=False"
```

**Option B: Set multiple at once:**
```bash
railway variables --set "SUPABASE_URL=your_url" --set "SUPABASE_KEY=your_key" --set "SUPABASE_SERVICE_KEY=your_service_key" --set "GEMINI_API_KEY=your_key" --set "BACKEND_HOST=0.0.0.0" --set "BACKEND_PORT=8000" --set "DEBUG=False"
```

**⚠️ Important:** You need a service linked first! If you get "No service linked", either:
1. Run `railway add` and select "Empty Service"
2. Or open Railway dashboard: `railway open` and create a service there

### Step 4: Deploy
```bash
railway up
```
This will build and deploy your application. Watch the logs!

### Step 5: Get Your URL
```bash
railway domain
```
Copy this URL - you'll need it for CORS.

### Step 6: Update CORS (After Deployment)
```bash
railway variables set CORS_ORIGINS=https://your-actual-url.railway.app
```
Replace `your-actual-url.railway.app` with the URL from Step 5.

### Step 7: Open Your App
```bash
railway open
```

## 📋 Quick Command Reference

```bash
# Check if logged in
railway whoami

# View all variables
railway variables

# View logs
railway logs

# Follow logs (real-time)
railway logs --follow

# Check deployment status
railway status

# Open in browser
railway open

# Get service URL
railway domain
```

## 🔧 Troubleshooting

### "Unauthorized" error
Run `railway login` again.

### Variables not set
Check with `railway variables` and set missing ones.

### Build fails
Check logs: `railway logs` and verify `requirements.txt` is correct.

### Frontend not loading
1. Build frontend: `cd frontend && npm run build`
2. Ensure `frontend/dist` exists
3. Check if backend is serving static files

## 📝 Example Full Deployment

```bash
# 1. Login
railway login

# 2. Initialize
railway init

# 3. Set variables (UPDATE WITH YOUR VALUES!)
railway variables set SUPABASE_URL=https://xxxxx.supabase.co
railway variables set SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
railway variables set SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
railway variables set GEMINI_API_KEY=AIzaSy...
railway variables set BACKEND_HOST=0.0.0.0
railway variables set BACKEND_PORT=8000
railway variables set DEBUG=False

# 4. Deploy
railway up

# 5. Get URL
railway domain

# 6. Update CORS (use URL from step 5)
railway variables set CORS_ORIGINS=https://your-app.railway.app

# 7. Open
railway open
```

## 🎯 Ready to Deploy?

Run these commands in order. The first one (`railway login`) will require you to interact with your browser.

