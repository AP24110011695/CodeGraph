# Railway Deployment Guide

## Required Railway Environment Variables

Set these in your Railway service environment variables:

### Core Configuration
```
APP_ENV=production
FRONTEND_URL=https://code-graph-alpha.vercel.app
```

### Storage Configuration (Required for Persistence)
```
UPLOAD_DIR=/data/uploads
STORAGE_DIR=/data
CODEGRAPH_DB_PATH=/data/codegraph.db
VECTOR_STORAGE_PATH=/data/vectors
```

### Optional LLM Providers
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

### Safety
```
EXPOSE_ERROR_DETAILS=false
```

## Railway Deployment Steps

### 1. Create Railway Service
1. Go to Railway dashboard
2. Create new project
3. Select "Deploy from GitHub repo"
4. Choose the CodeGraph repository

### 2. Configure Environment Variables
Add the environment variables listed above in Railway's service settings.

### 3. Add Persistent Volume
1. Go to your Railway service
2. Add a volume named `data`
3. Mount path: `/data`
4. This ensures database and uploads persist across deployments

### 4. Deploy
Railway will automatically deploy using the Procfile:
```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 5. Get Railway URL
After deployment, Railway will provide a URL like:
```
https://codegraph-backend.railway.app
```

### 6. Update Vercel Environment Variables
In Vercel project settings, set:
```
VITE_API_URL=https://codegraph-backend.railway.app
```

## Verification

### Check Backend Health
Once deployed, test the health endpoint:
```bash
curl https://codegraph-backend.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0-rc.1",
  "environment": "production"
}
```

### Check CORS
Test that CORS is properly configured:
```bash
curl -H "Origin: https://code-graph-alpha.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://codegraph-backend.railway.app/upload
```

Should return CORS headers allowing the Vercel domain.

## Troubleshooting

### 404 Errors
- Verify Railway service is running
- Check Railway logs for startup errors
- Ensure Procfile is correct

### CORS Errors
- Verify FRONTEND_URL matches Vercel domain exactly
- Check Railway environment variables
- Ensure CORS middleware is properly configured

### Upload Failures
- Verify persistent volume is mounted
- Check storage directory permissions
- Review Railway logs for file system errors

### Database Issues
- Ensure CODEGRAPH_DB_PATH points to persistent volume
- Verify `/data` volume is properly mounted
- Check database file permissions