# Railway Deployment Checklist

Use this checklist when deploying to Railway.

## Pre-Deployment

- [ ] All code committed to Git
- [ ] Pushed to GitHub repository
- [ ] `.env` file is **NOT** committed (it's in `.gitignore`)
- [ ] Tested locally with `python3 main.py`

## Railway Setup

### 1. Create Project
- [ ] Go to https://railway.app/new
- [ ] Click "Deploy from GitHub repo"
- [ ] Select your repository
- [ ] Railway detects Python project

### 2. Configure Root Directory
- [ ] Go to Settings → "Root Directory"
- [ ] Set to: `backend`
- [ ] Click "Update"

### 3. Add PostgreSQL Database
- [ ] Click "New" in project
- [ ] Select "Database" → "PostgreSQL"
- [ ] Wait for database to provision
- [ ] Verify `DATABASE_URL` is set in Variables

### 4. Set Environment Variables

Go to Settings → Variables, add these:

#### Required Variables
- [ ] `UPLOAD_ACCESS_CODE` - Your secret upload code
  ```bash
  # Example: spire_2024_secret_abc123
  ```

- [ ] `JWT_SECRET_KEY` - Generate with:
  ```bash
  openssl rand -base64 32
  ```

#### Optional (have defaults)
- [ ] `JWT_ALGORITHM` - Default: `HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` - Default: `10080` (7 days)

### 5. Deploy
- [ ] Click "Deploy" or push to GitHub
- [ ] Wait for deployment to complete
- [ ] Check logs for errors

### 6. Initialize Database
- [ ] Open Railway Shell (click service → "Shell" tab)
- [ ] Run:
  ```bash
  python create_admin.py --username admin --password YOUR_SECURE_PASSWORD
  ```

### 7. Test Deployment
- [ ] Get your Railway URL (e.g., `https://your-app.railway.app`)
- [ ] Test health endpoint:
  ```bash
  curl https://your-app.railway.app/health
  ```
- [ ] Should return: `{"status":"healthy"}`

### 8. Test API Docs
- [ ] Visit: `https://your-app.railway.app/docs`
- [ ] Verify Swagger UI loads
- [ ] Try test authentication endpoint

## Post-Deployment

### Test Upload Flow
- [ ] Run uploader locally:
  ```bash
  python3 sts2_uploader.py \
    --server https://your-app.railway.app \
    --access-code YOUR_CODE \
    --dry-run
  ```
- [ ] Test actual upload (remove `--dry-run`)
- [ ] Verify runs appear in database

### Share With Friends
- [ ] Share `sts2_uploader.py` script
- [ ] Share upload command:
  ```bash
  python3 sts2_uploader.py \
    --server https://your-app.railway.app \
    --access-code YOUR_SECRET_CODE
  ```
- [ ] **DO NOT** commit access code to public repo!

### Compute Analytics
- [ ] Login as admin to get token
- [ ] Trigger analytics computation:
  ```bash
  # Using test_api.py
  python3 test_api.py compute admin YOUR_ADMIN_PASSWORD
  ```

### Monitor
- [ ] Check Railway logs for errors
- [ ] Monitor resource usage
- [ ] Set up notifications (optional)

## Troubleshooting

### Deployment fails
- [ ] Check Railway logs
- [ ] Verify `requirements.txt` has all dependencies
- [ ] Ensure root directory is set to `backend`

### Database connection errors
- [ ] Verify PostgreSQL service is running
- [ ] Check `DATABASE_URL` is set
- [ ] Look for migration errors in logs

### "Invalid access code" errors
- [ ] Verify `UPLOAD_ACCESS_CODE` matches what friends are using
- [ ] Check for typos or extra spaces

### Port binding errors
- [ ] Ensure `Procfile` uses `$PORT`
- [ ] Check `start.sh` uses `${PORT:-8000}`

## Security Checklist

- [ ] Changed `JWT_SECRET_KEY` from default
- [ ] Set strong admin password
- [ ] `UPLOAD_ACCESS_CODE` is unique and secret
- [ ] `.env` file is gitignored
- [ ] Shared access code only with trusted friends
- [ ] Updated CORS if using separate frontend domain

## Cost Management

- [ ] Check Railway usage dashboard
- [ ] Hobby plan: $5/month should be sufficient
- [ ] Monitor database size
- [ ] Set up usage alerts (optional)

## Updating Production

When you make changes:

```bash
git add .
git commit -m "Your changes"
git push

# Railway auto-deploys!
```

## Rollback Plan

If something breaks:
1. Go to Railway dashboard
2. Click "Deployments"
3. Find last working deployment
4. Click "Redeploy"

## Support Resources

- [ ] Railway docs: https://docs.railway.app
- [ ] Railway Discord: https://discord.gg/railway
- [ ] Project issues: Your GitHub Issues page

## Done!

Once all items are checked:
- ✅ Your API is live
- ✅ Friends can upload runs
- ✅ Analytics are computable
- ✅ Ready to scale

**Your URLs:**
- API: `https://your-app.railway.app`
- Docs: `https://your-app.railway.app/docs`
- Health: `https://your-app.railway.app/health`
