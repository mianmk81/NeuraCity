# Railway.app Deployment Guide for NeuraCity

This guide will help you deploy NeuraCity to Railway.app.

## Prerequisites

1. A Railway.app account (sign up at https://railway.app)
2. GitHub repository with your code
3. Supabase project with database configured
4. API keys:
   - Gemini API key (Google AI Studio)
   - Supabase URL and keys

## Deployment Steps

### 1. Connect Repository to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your NeuraCity repository
5. Railway will automatically detect the project structure

### 2. Configure Environment Variables

In Railway dashboard, go to your service → Variables tab and add:

#### Required Variables:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
GEMINI_API_KEY=your_gemini_api_key
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=False
```

#### Optional Variables:
```
HUGGINGFACE_API_KEY=your_huggingface_key (optional)
OPENROUTESERVICE_API_KEY=your_openrouteservice_key (optional)
CORS_ORIGINS=https://your-frontend-domain.railway.app,https://your-custom-domain.com
```

### 3. Configure Build Settings

Railway will automatically detect:
- **Backend**: Python project in `backend/` directory
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && python run.py`

### 4. Deploy Frontend (Separate Service)

For the frontend, you have two options:

#### Option A: Deploy as Static Site (Recommended)
1. Create a new service in Railway
2. Set root directory to `frontend/`
3. Build command: `npm install && npm run build`
4. Start command: `npx serve -s dist -l $PORT`
5. Add environment variable: `VITE_API_URL=https://your-backend-service.railway.app/api/v1`

#### Option B: Serve from Backend
The backend can serve the frontend static files. Update `backend/app/main.py` to mount the frontend dist folder.

### 5. Update Frontend API URL

Before building the frontend, set the API URL:

1. In Railway frontend service, add environment variable:
   ```
   VITE_API_URL=https://your-backend-service.railway.app/api/v1
   ```

2. Or update `frontend/src/lib/api.js` to use the Railway backend URL

### 6. Configure Ports

Railway automatically assigns a `PORT` environment variable. Update `backend/run.py` to use it:

```python
import os
port = int(os.environ.get("PORT", 8000))
```

### 7. Database Setup

Ensure your Supabase database is:
- Accessible from Railway (Supabase allows external connections)
- Has all migrations applied
- Has seed data if needed

### 8. File Uploads

For file uploads to work:
1. Create `uploads/` directory in backend
2. Consider using Supabase Storage for production instead of local files
3. Or use Railway's persistent volume for uploads

## Deployment Architecture

```
┌─────────────────┐
│  Railway App    │
│                 │
│  ┌───────────┐  │
│  │ Frontend  │  │  (Static site or separate service)
│  │ Service   │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │  Backend  │  │  (FastAPI service)
│  │  Service  │  │
│  └─────┬─────┘  │
│        │        │
└────────┼────────┘
         │
    ┌────▼────┐
    │ Supabase│
    │ Database│
    └─────────┘
```

## Troubleshooting

### Backend won't start
- Check logs in Railway dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` is correct
- Check Python version (Railway uses Python 3.11 by default)

### Frontend can't connect to backend
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Ensure backend service is running
- Check Railway service URLs

### Database connection issues
- Verify Supabase credentials
- Check Supabase project settings
- Ensure database is accessible from Railway IPs

### File uploads not working
- Check `uploads/` directory exists
- Verify file permissions
- Consider using Supabase Storage for production

## Custom Domain Setup

1. In Railway, go to your service → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update `CORS_ORIGINS` to include your custom domain

## Monitoring

- Check Railway dashboard for logs
- Monitor service health
- Set up alerts for service failures
- Monitor resource usage

## Cost Optimization

- Use Railway's free tier for development
- Optimize Docker images
- Use Supabase free tier for database
- Cache API responses where possible

## Next Steps

After deployment:
1. Test all endpoints
2. Verify frontend-backend communication
3. Test file uploads
4. Monitor logs for errors
5. Set up custom domain (optional)
6. Configure SSL (automatic with Railway)

