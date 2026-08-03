# Railway Deployment Guide

## Current Deployment Status

The backend is already deployed on Railway at:
```
https://codegraph-production-d523.up.railway.app
```

## Required Railway Environment Variables

The following are configured in `railway.json` and `nixpacks.toml`:

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

## Railway Configuration Files

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  },
  "variables": {
    "APP_ENV": "production",
    "FRONTEND_URL": "https://code-graph-alpha.vercel.app"
  }
}
```

### nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python312"]

[phases.build]
cmds = [
  "cd backend",
  "python -m venv .venv",
  ".venv/bin/pip install --upgrade pip",
  ".venv/bin/pip install -r requirements.txt"
]

[start]
cmd = "cd backend && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT"

[variables]
APP_ENV = "production"
FRONTEND_URL = "https://code-graph-alpha.vercel.app"
```

### Procfile
```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Verification

### Check Backend Health
Test the health endpoint:
```bash
curl https://codegraph-production-d523.up.railway.app/health
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
     https://codegraph-production-d523.up.railway.app/upload
```

Should return CORS headers allowing the Vercel domain.

## Troubleshooting

### Environment Shows "development"
- Ensure `APP_ENV=production` is set in Railway environment variables
- Check railway.json variables section
- Verify nixpacks.toml variables section
- Redeploy Railway service after changes

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