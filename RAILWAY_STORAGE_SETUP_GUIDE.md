# Railway Persistent Storage Setup Guide

## Critical: Manual Configuration Required

The CodeGraph backend requires **persistent storage** to function correctly in production. Railway uses ephemeral storage by default, which means all data is lost when the container restarts. This must be configured manually in the Railway dashboard.

## Step-by-Step Instructions

### 1. Access Railway Dashboard

1. Go to [railway.app](https://railway.app)
2. Log in to your account
3. Navigate to the CodeGraph project

### 2. Configure Persistent Storage

1. Click on the **backend** service
2. Click on the **"Volumes"** tab
3. Click **"New Volume"**
4. Configure the volume:
   - **Name**: `storage`
   - **Mount Path**: `/app/backend/storage`
   - **Size**: Select appropriate size (recommended: 1GB for initial deployment)
5. Click **"Create Volume"**

### 3. Redeploy the Service

1. After creating the volume, click **"Redeploy"** on the backend service
2. Wait for the deployment to complete
3. Verify the service is healthy

### 4. Verify Storage is Working

1. Upload a test repository through the Vercel frontend
2. Wait for indexing to complete
3. Trigger a Railway redeploy
4. Verify the repository still exists after redeploy

## Why This is Required

Railway containers restart periodically and after deployments. Without persistent storage:

- ✗ Uploaded ZIP files are lost
- ✗ Extracted repositories are lost
- ✗ SQLite database is lost
- ✗ Vector store data is lost
- ✗ All user data is lost

With persistent storage configured:

- ✓ Uploaded files persist across restarts
- ✓ Indexed data is preserved
- ✓ SQLite database survives deployments
- ✓ User data is retained
- ✓ Application works reliably

## Alternative Solutions

If Railway volumes are not available or sufficient:

### Option 1: Use Railway PostgreSQL

1. Create PostgreSQL service in Railway
2. Update `backend/app/core/config.py` to use PostgreSQL
3. Configure connection via `DATABASE_URL` environment variable
4. Run database migrations

### Option 2: Use Cloud Storage

1. Create AWS S3 bucket or DigitalOcean Spaces
2. Update backend to store files in cloud storage
3. Configure cloud storage credentials via environment variables
4. Keep only metadata in Railway storage

### Option 3: Use Railway Redis

1. Create Redis service in Railway
2. Use Redis for session/state management
3. Cache ephemeral data in Redis
4. Keep critical data in persistent storage

## Verification After Setup

After configuring persistent storage, run the production test:

```bash
cd backend
python production_test.py
```

Expected results:
- Upload succeeds
- Indexing completes to READY state
- API endpoints return 200
- Data persists across Railway restarts

## Troubleshooting

### Issue: Volume not accessible

**Solution**: Verify the mount path matches `/app/backend/storage` exactly

### Issue: Data still lost after restart

**Solution**: 
1. Check volume is properly attached
2. Verify volume has sufficient disk space
3. Check Railway logs for I/O errors

### Issue: Performance issues

**Solution**: 
1. Monitor volume I/O in Railway dashboard
2. Consider upgrading to higher-performance volume
3. Optimize database queries

## Monitoring

After setup, monitor:
- Volume disk usage in Railway dashboard
- Database file size
- Vector store size
- Upload frequency
- Container restart frequency

## Cost Considerations

Railway volumes have monthly costs based on size and I/O:
- 1GB volume: ~$5/month
- 10GB volume: ~$50/month
- Additional I/O charges may apply

Monitor usage to optimize costs.