# Vercel Environment Variables Setup

## Required Environment Variable

The Vercel deployment requires this environment variable to be set:

### VITE_API_URL
- **Variable Name**: `VITE_API_URL`
- **Value**: `https://codegraph-production-d523.up.railway.app`
- **Purpose**: Points the frontend to the Railway backend API

## How to Set in Vercel

### Method 1: Vercel Dashboard
1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Click **Add New**
4. Enter:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://codegraph-production-d523.up.railway.app`
   - **Environment**: Select **Production** (and optionally Preview/Development)
5. Click **Save**
6. **Redeploy** your Vercel application

### Method 2: Vercel CLI
```bash
vercel env add VITE_API_URL production
# When prompted, enter: https://codegraph-production-d523.up.railway.app
vercel --prod
```

## Verification

After setting the environment variable and redeploying:

1. Open your Vercel application
2. Open browser DevTools
3. Go to Network tab
4. Attempt an upload
5. Verify the request goes to `https://codegraph-production-d523.up.railway.app/upload`
6. Check that the request succeeds (should not be 404)

## Troubleshooting

### Upload Still Fails with 404
- Verify `VITE_API_URL` is set in Production environment
- Check the value is exactly: `https://codegraph-production-d523.up.railway.app`
- Ensure Vercel has been redeployed after setting the variable
- Clear browser cache and try again

### Request Goes to Wrong Domain
- Check that the frontend is using `import.meta.env.VITE_API_URL`
- Verify the environment variable is accessible in the browser console:
  ```javascript
  console.log(import.meta.env.VITE_API_URL)
  ```
- Should output: `https://codegraph-production-d523.up.railway.app`

### CORS Errors
- Verify Railway backend has `FRONTEND_URL=https://code-graph-alpha.vercel.app`
- Check Railway environment variables
- Ensure Railway has been redeployed with correct CORS settings