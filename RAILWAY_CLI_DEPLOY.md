# Railway CLI Deployment Guide

## Prerequisites
✅ Railway CLI installed: `npm install -g @railway/cli`

## Step-by-Step CLI Deployment

### 1. Login to Railway
```bash
railway login
```
This will open your browser for authentication.

### 2. Initialize Railway Project
```bash
railway init
```
This will:
- Create a new Railway project (or link to existing)
- Generate `railway.toml` if needed
- Set up the project structure

### 3. Link to Existing Project (Optional)
If you already have a Railway project:
```bash
railway link
```
Then select your project from the list.

### 4. Set Environment Variables
Set all required environment variables:

```bash
# Supabase Configuration
railway variables set SUPABASE_URL=your_supabase_url
railway variables set SUPABASE_KEY=your_supabase_anon_key
railway variables set SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI API Keys
railway variables set GEMINI_API_KEY=your_gemini_api_key

# Server Configuration
railway variables set BACKEND_HOST=0.0.0.0
railway variables set BACKEND_PORT=8000
railway variables set DEBUG=False

# CORS (update after deployment with your Railway URL)
railway variables set CORS_ORIGINS=https://your-app.railway.app
```

Or set multiple at once:
```bash
railway variables set SUPABASE_URL=your_url SUPABASE_KEY=your_key SUPABASE_SERVICE_KEY=your_service_key GEMINI_API_KEY=your_key BACKEND_HOST=0.0.0.0 BACKEND_PORT=8000 DEBUG=False
```

### 5. Deploy
```bash
railway up
```

This will:
- Build your application
- Deploy to Railway
- Show deployment logs

### 6. Get Your Deployment URL
```bash
railway domain
```

Or check the Railway dashboard for your service URL.

### 7. Update CORS (After First Deployment)
Once you have your Railway URL:
```bash
railway variables set CORS_ORIGINS=https://your-actual-url.railway.app
```

### 8. View Logs
```bash
railway logs
```

### 9. Open in Browser
```bash
railway open
```

## Useful Commands

```bash
# Check status
railway status

# View environment variables
railway variables

# View logs (follow mode)
railway logs --follow

# Open service in browser
railway open

# Get service URL
railway domain

# Run commands in Railway environment
railway run python run.py

# Connect to database (if using Railway Postgres)
railway connect postgres
```

## Troubleshooting

### If deployment fails:
1. Check logs: `railway logs`
2. Verify environment variables: `railway variables`
3. Test locally: `railway run python run.py`
4. Check build: `railway up --detach` (runs in background)

### If frontend not loading:
1. Ensure frontend is built: `cd frontend && npm run build`
2. Check if `frontend/dist` exists
3. Verify `VITE_API_URL` is set correctly

### If API not working:
1. Check backend logs: `railway logs`
2. Verify all environment variables are set
3. Test health endpoint: `railway open` then visit `/health`

## Quick Deploy Script

Save this as `deploy-railway.sh`:

```bash
#!/bin/bash
echo "🚀 Deploying to Railway..."

# Login (if not already)
railway login

# Initialize (if not already)
railway init

# Set variables (update with your actual values)
railway variables set SUPABASE_URL=$SUPABASE_URL
railway variables set SUPABASE_KEY=$SUPABASE_KEY
railway variables set SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY
railway variables set GEMINI_API_KEY=$GEMINI_API_KEY
railway variables set BACKEND_HOST=0.0.0.0
railway variables set BACKEND_PORT=8000
railway variables set DEBUG=False

# Deploy
railway up

# Get URL
echo "✅ Deployment complete!"
railway domain
```

## Next Steps

After successful deployment:
1. Update `CORS_ORIGINS` with your Railway URL
2. Test all endpoints
3. Set up custom domain (optional)
4. Configure monitoring and alerts

