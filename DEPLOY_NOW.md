# Quick Deploy Commands (Corrected Syntax)

## Current Status
- ✅ Railway CLI installed
- ✅ Logged in
- ✅ Project "NeuraCity" exists
- ❌ No service linked yet

## Step 1: Create/Link Service

**Option A: Via CLI (Interactive)**
```bash
railway add
# Select "Empty Service"
```

**Option B: Via Dashboard**
```bash
railway open
# Then create a new service in the dashboard
```

## Step 2: Set Environment Variables

Once service is linked, run these (UPDATE WITH YOUR VALUES):

```bash
railway variables --set "SUPABASE_URL=https://ramopptlasptqsfqikqj.supabase.co"
railway variables --set "SUPABASE_KEY=YOUR_SUPABASE_KEY"
railway variables --set "SUPABASE_SERVICE_KEY=YOUR_SERVICE_KEY"
railway variables --set "GEMINI_API_KEY=YOUR_GEMINI_KEY"
railway variables --set "BACKEND_HOST=0.0.0.0"
railway variables --set "BACKEND_PORT=8000"
railway variables --set "DEBUG=False"
```

## Step 3: Deploy

```bash
railway up
```

## Step 4: Get URL and Update CORS

```bash
railway domain
# Copy the URL, then:
railway variables --set "CORS_ORIGINS=https://your-actual-url.railway.app"
```

## Step 5: Open App

```bash
railway open
```

---

## Quick Fix: Create Service via Dashboard

The easiest way right now:
1. Run: `railway open`
2. In the dashboard, click "New Service" or "Add Service"
3. Select "Empty Service" or "GitHub Repo"
4. Then come back and run the variable commands above

