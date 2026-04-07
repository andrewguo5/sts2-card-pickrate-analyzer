# STS2 Analytics - Quick Deploy Guide

🎮 **Slay the Spire 2 Card Pick Rate Analytics Platform**

## What This Does

- Friends upload their STS2 run history
- Backend stores runs in PostgreSQL
- Analytics computed on-demand
- View card pick rates by character/ascension/mode

## Deploy to Railway (5 minutes)

### 1. Click Deploy Button

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### 2. Add PostgreSQL

In Railway dashboard:
- Click "New" → "Database" → "PostgreSQL"

### 3. Set Environment Variables

In Settings → Variables:
```bash
UPLOAD_ACCESS_CODE=your_secret_code_here
JWT_SECRET_KEY=<run: openssl rand -base64 32>
```

### 4. Set Root Directory

In Settings → "Root Directory":
```
backend
```

### 5. Deploy!

Railway auto-deploys. You'll get a URL like:
```
https://your-app.railway.app
```

## Share With Friends

Give friends two things:

1. **The uploader script**: `sts2_uploader.py`
2. **Your access code**: (the one you set in Railway)

They run:
```bash
python3 sts2_uploader.py --server https://your-app.railway.app --access-code YOUR_CODE
```

## Files

- `backend/` - FastAPI API server
- `sts2_uploader.py` - Upload client for users
- `pickrate-viz/` - Web visualization (optional)
- `DEPLOYMENT.md` - Detailed deployment guide
- `UPLOADER_README.md` - User guide for uploader

## Local Development

```bash
# Setup database
createdb sts2_analytics

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Initialize database
python init_db.py
python create_admin.py --username admin --password admin123

# Run server
python main.py
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/runs/check-hashes` - Check which runs exist
- `POST /api/runs/simple-upload` - Upload runs
- `POST /api/analytics/compute` - Compute analytics (admin)
- `GET /api/analytics/global-stats` - Get global stats

## Architecture

```
Users → sts2_uploader.py → FastAPI Backend → PostgreSQL
                                ↓
                        Analytics Engine
                                ↓
                        Web Visualization
```

## Cost

Railway Hobby plan: **$5/month**
- Includes PostgreSQL
- More than enough for small friend groups

## Support

- See `DEPLOYMENT.md` for detailed guide
- See `UPLOADER_README.md` for user instructions
- Railway docs: https://docs.railway.app
