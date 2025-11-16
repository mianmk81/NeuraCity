@echo off
echo ========================================
echo NeuraCity Railway Deployment
echo ========================================
echo.

echo Step 1: Login to Railway (will open browser)
railway login
if %errorlevel% neq 0 (
    echo Login failed. Please try again.
    pause
    exit /b 1
)

echo.
echo Step 2: Initialize Railway project
railway init
if %errorlevel% neq 0 (
    echo Init failed. Project may already exist.
)

echo.
echo Step 3: Setting environment variables...
echo Please update the values in this script with your actual credentials!
echo.
echo Setting SUPABASE_URL...
railway variables set SUPABASE_URL=YOUR_SUPABASE_URL_HERE
echo Setting SUPABASE_KEY...
railway variables set SUPABASE_KEY=YOUR_SUPABASE_KEY_HERE
echo Setting SUPABASE_SERVICE_KEY...
railway variables set SUPABASE_SERVICE_KEY=YOUR_SUPABASE_SERVICE_KEY_HERE
echo Setting GEMINI_API_KEY...
railway variables set GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
echo Setting BACKEND_HOST...
railway variables set BACKEND_HOST=0.0.0.0
echo Setting BACKEND_PORT...
railway variables set BACKEND_PORT=8000
echo Setting DEBUG...
railway variables set DEBUG=False

echo.
echo Step 4: Deploying to Railway...
railway up

echo.
echo Step 5: Getting deployment URL...
railway domain

echo.
echo ========================================
echo Deployment complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy your Railway URL from above
echo 2. Update CORS_ORIGINS: railway variables set CORS_ORIGINS=https://your-url.railway.app
echo 3. Visit your app: railway open
echo.
pause

