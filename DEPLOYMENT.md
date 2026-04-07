# Deployment Guide - Railway

Complete guide to deploying the STS2 Analytics API to Railway.app

## Prerequisites

1. GitHub account
2. Railway account (sign up at https://railway.app)
3. Git repository pushed to GitHub

## Step 1: Push to GitHub

Make sure all your code is committed and pushed:

```bash
cd /Users/andrewguo5/mbSpireParser/Spire.mbgg

# Add all files
git add .

# Commit
git commit -m "Prepare for Railway deployment"

# Push to GitHub
git push origin main
```

## Step 2: Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository: `andrewguo5/sts2-card-pickrate-analyzer` (or whatever you named it)
4. Railway will detect the Python backend automatically

## Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically create a database and set `DATABASE_URL`

## Step 4: Configure Environment Variables

In Railway project settings → Variables, add these:

```bash
# REQUIRED - Generate a secure secret key
JWT_SECRET_KEY=<generate-with-openssl-rand-base64-32>

# REQUIRED - Set your upload access code
UPLOAD_ACCESS_CODE=<your-secret-upload-code>

# Optional - these have defaults
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

**Generate JWT secret:**
```bash
openssl rand -base64 32
```

**Important:** Don't use the development values in production!

## Step 5: Set Root Directory

Since your backend is in a subdirectory:

1. Go to Settings → "Root Directory"
2. Set to: `backend`
3. Click "Update"

## Step 6: Deploy

Railway will automatically deploy when you push to GitHub!

To trigger manual deployment:
1. Go to your project
2. Click "Deploy" button

## Step 7: Initialize Database

After first deployment, you need to create the admin user:

### Option A: Via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run command in production
railway run python create_admin.py --username admin --password <your-admin-password>
```

### Option B: Via Railway Shell

1. In Railway dashboard, click on your service
2. Click "Shell" tab
3. Run:
```bash
python create_admin.py --username admin --password <your-admin-password>
```

## Step 8: Update Frontend CORS (if deploying separately)

If serving the frontend from a different domain, update CORS in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Your URLs

After deployment, Railway will give you:

- **API URL**: `https://your-app.railway.app`
- **Database**: Automatically connected via `DATABASE_URL`

Test it:
```bash
curl https://your-app.railway.app/health
# Should return: {"status":"healthy"}
```

## Update Upload Script

Share this command with your friends:

```bash
python3 sts2_uploader.py \
  --server https://your-app.railway.app \
  --access-code YOUR_SECRET_CODE
```

## Monitoring

Railway provides:
- **Logs**: View in dashboard under "Deployments" → "View Logs"
- **Metrics**: CPU, Memory, Network usage
- **Database**: pgAdmin or connect via connection string

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Auto-set | PostgreSQL connection string | Provided by Railway |
| `JWT_SECRET_KEY` | Yes | Secret for JWT tokens | Generate with openssl |
| `UPLOAD_ACCESS_CODE` | Yes | Code for run uploads | `spire_2024_secret` |
| `JWT_ALGORITHM` | No | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token expiry | `10080` (7 days) |
| `PORT` | Auto-set | Server port | Provided by Railway |

## Troubleshooting

### "Address already in use"
Railway sets `PORT` automatically. Make sure you're using `$PORT` in the start command.

### Database connection errors
Make sure PostgreSQL service is running and `DATABASE_URL` is set.

### "Module not found"
Check that `requirements.txt` includes all dependencies.

### CORS errors from frontend
Update `allow_origins` in `main.py` to include your frontend domain.

## Cost Estimation

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month includes:
  - 500 hours of usage
  - $5 in resource credits
  - PostgreSQL database

This should be plenty for a small friend group!

## Updating Your Deployment

Railway auto-deploys on push to main:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push

# Railway automatically deploys!
```

## Rollback

If something breaks:
1. Go to Railway dashboard
2. Click "Deployments"
3. Find the working deployment
4. Click "Redeploy"

## Database Backups

Railway provides automatic backups for PostgreSQL. You can also manually backup:

```bash
# Get database URL from Railway
railway variables

# Backup locally
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

## Security Checklist

- [ ] Changed `JWT_SECRET_KEY` from default
- [ ] Set secure `UPLOAD_ACCESS_CODE`
- [ ] Updated CORS origins (if using separate frontend)
- [ ] Created admin account with strong password
- [ ] Don't commit `.env` file to git
- [ ] Share access code privately with friends only

## Next Steps

1. Test the deployed API
2. Share the uploader script + access code with friends
3. Set up analytics computation (can run manually or schedule)
4. Deploy frontend (optional - can serve from Railway static site or Vercel)

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- This project's GitHub Issues
