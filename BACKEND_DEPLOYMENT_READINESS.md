# Backend Railway Deployment Readiness

## Summary of Changes

The backend has been prepared for Railway deployment with the following critical fixes:

### 1. Production HOST Configuration
- **File**: `backend/app/core/config.py`
- **Change**: Added `model_validator` to automatically set HOST to `0.0.0.0` when `APP_ENV=production`
- **Impact**: Backend will now bind to all interfaces in production instead of localhost

### 2. CORS Middleware
- **File**: `backend/app/main.py`
- **Change**: Added CORSMiddleware with configurable `FRONTEND_URL` environment variable
- **Impact**: Frontend can communicate with backend in production; allows all origins in development

### 3. Railway PORT Configuration
- **File**: `backend/app/core/config.py`
- **Change**: PORT now defaults to Railway's `$PORT` environment variable
- **Impact**: Backend will use Railway's assigned port automatically

### 4. Configurable Storage Paths
- **Files**: Multiple files updated to use environment variables
- **Changes**:
  - `UPLOAD_DIR`, `STORAGE_DIR`, `CODEGRAPH_DB_PATH`, `VECTOR_STORAGE_PATH` added to config
  - Updated `app/core/paths.py` with helper functions
  - Updated all API endpoints to use configurable paths
- **Impact**: Storage paths can be configured for Railway's persistent volumes

### 5. Deployment Configuration Files
- **New Files**:
  - `Procfile` - Railway startup command
  - `railway.json` - Railway deployment configuration with health checks
  - `backend/Procfile` - Backend-specific Procfile

### 6. Environment Variables
- **File**: `backend/.env.example`
- **Changes**: Added production-ready environment variable documentation

## Required Environment Variables for Railway

### Required for Production
```bash
APP_ENV=production
FRONTEND_URL=https://your-frontend.vercel.app
CODEGRAPH_DB_PATH=/data/codegraph.db
VECTOR_STORAGE_PATH=/data/vectors
```

### Optional but Recommended
```bash
UPLOAD_DIR=/data/uploads
STORAGE_DIR=/data
```

### Optional LLM Providers
```bash
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

### Always Set to False in Production
```bash
EXPOSE_ERROR_DETAILS=false
```

## Startup Command

### Railway (Automatic via Procfile)
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Local Production Testing
```bash
cd backend
export APP_ENV=production
export PORT=8000
export FRONTEND_URL=http://localhost:5173
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Local Development
```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Health Endpoint

### Endpoint
```
GET /health
```

### Response
```json
{
  "status": "healthy",
  "version": "1.0.0-rc.1",
  "environment": "production"
}
```

### Railway Configuration
- **Health Check Path**: `/health`
- **Health Check Timeout**: 100 seconds
- **Restart Policy**: ON_FAILURE (max 10 retries)

## Local Production Verification

### Step 1: Set Production Environment
```bash
cd backend
export APP_ENV=production
export PORT=8000
export FRONTEND_URL=http://localhost:5173
export CODEGRAPH_DB_PATH=/tmp/codegraph.db
export VECTOR_STORAGE_PATH=/tmp/vectors
```

### Step 2: Start Backend
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 3: Verify Health Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0-rc.1",
  "environment": "production"
}
```

### Step 4: Verify CORS Configuration
```bash
curl -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: POST" -X OPTIONS http://localhost:8000/upload
```

Expected headers should include:
```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### Step 5: Verify Root Endpoint
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "name": "CodeGraph",
  "version": "1.0.0-rc.1",
  "status": "running",
  "release": "RC-1"
}
```

### Step 6: Verify API Documentation
```bash
curl http://localhost:8000/docs
```

Should return HTML page with Swagger UI.

## Railway Deployment Steps

### Step 1: Create Railway Project
1. Go to Railway dashboard
2. Create new project
3. Select "Deploy from GitHub repo"

### Step 2: Configure Environment Variables
Set the following in Railway environment variables:
```
APP_ENV=production
FRONTEND_URL=https://your-frontend.vercel.app
CODEGRAPH_DB_PATH=/data/codegraph.db
VECTOR_STORAGE_PATH=/data/vectors
EXPOSE_ERROR_DETAILS=false
```

### Step 3: Add Persistent Volume
1. Go to your Railway service
2. Add a volume named `data`
3. Mount path: `/data`

### Step 4: Deploy
Railway will automatically deploy using the Procfile and railway.json configuration.

### Step 5: Verify Deployment
1. Check Railway logs for successful startup
2. Visit the health endpoint: `https://your-backend-url.railway.app/health`
3. Check that CORS is properly configured

## Modified Files

### Configuration
- `backend/app/core/config.py` - Added production HOST logic, CORS config, storage paths
- `backend/.env.example` - Added production environment variables

### Main Application
- `backend/app/main.py` - Added CORS middleware

### Path Management
- `backend/app/core/paths.py` - Added helper functions for configurable paths

### Services
- `backend/app/services/upload_service.py` - Configurable upload directory
- `backend/app/services/extraction_service.py` - Configurable storage paths
- `backend/app/rag/vector_store.py` - Configurable vector storage
- `backend/storage/database.py` - Configurable database path

### API Endpoints (40+ files updated)
All API endpoints updated to use configurable paths via `app/core/paths.py` helpers:
- `backend/app/api/architecture.py`
- `backend/app/api/security.py`
- `backend/app/api/chat.py`
- `backend/app/api/search.py`
- `backend/app/api/repositories.py`
- `backend/app/api/solid.py`
- `backend/app/api/review.py`
- `backend/app/api/pull_request_review.py`
- `backend/app/api/microservices.py`
- `backend/app/api/license.py`
- `backend/app/api/design_patterns.py`
- `backend/app/api/dependency_health.py`
- `backend/app/api/database_schema.py`
- `backend/app/api/code_generation.py`
- `backend/app/api/bug_localization.py`
- `backend/app/api/architecture_report.py`
- `backend/app/api/architecture_recommendation.py`
- `backend/app/api/architecture_drift.py`
- `backend/app/api/api_flow.py`
- `backend/app/api/uml.py`
- `backend/app/api/apidocs.py`
- `backend/app/api/scanner.py`
- `backend/app/api/parser.py`
- `backend/app/api/framework.py`
- `backend/app/api/explain.py`
- `backend/app/api/diagrams.py`
- `backend/app/api/dependency_graph.py`
- `backend/app/api/readme.py`
- `backend/app/api/indexing.py`

### Jobs & Workers
- `backend/app/jobs/task_registry.py`
- `backend/app/jobs/job_manager.py`
- `backend/app/workers/task_executor.py`
- `backend/app/cicd/cicd_engine.py`

### Deployment Files
- `Procfile` (new)
- `backend/Procfile` (new)
- `railway.json` (new)

## Railway-Specific Notes

### Persistent Storage
Railway's filesystem is ephemeral. You must add a persistent volume for:
- SQLite database (`/data/codegraph.db`)
- Uploaded files (`/data/uploads`)
- Extracted repositories (`/data/extracted`)
- Vector store metadata (`/data/vectors`)

### Database Persistence
Without a persistent volume, the SQLite database will be lost on redeployment. Configure:
```bash
CODEGRAPH_DB_PATH=/data/codegraph.db
```

### CORS Configuration
In production, set `FRONTEND_URL` to your Vercel frontend URL:
```bash
FRONTEND_URL=https://your-frontend.vercel.app
```

### Port Configuration
Railway automatically sets the `PORT` environment variable. The Procfile uses `$PORT` to bind to the correct port.

## Remaining Concerns (Not Addressed)

These are outside the scope of deployment blocker fixes:
- No authentication/authorization
- No rate limiting
- No caching layer
- No SSL/TLS configuration (handled by Railway)
- No backup strategy for SQLite database
- No monitoring/alerting
- No log aggregation

## Testing Checklist

Before deploying to Railway:
- [ ] Run local production verification steps
- [ ] Test health endpoint returns correct response
- [ ] Test CORS headers are properly set
- [ ] Test file upload functionality
- [ ] Test API endpoints are accessible
- [ ] Verify storage paths are configurable
- [ ] Test with production environment variables
- [ ] Verify HOST binds to 0.0.0.0 in production mode