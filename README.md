# Slay the Spire 2 Analytics

Card pick rate analytics platform for Slay the Spire 2.

## What It Does

- **Upload**: Users run `sts2_uploader.py` to upload their run history
- **Store**: FastAPI backend stores runs in PostgreSQL
- **Analyze**: Compute card pick rates by character/ascension/mode
- **Visualize**: View pick rates on interactive web interface

## Quick Start

### For Users (Uploading Runs)

```bash
pip install requests
python3 sts2_uploader.py --server YOUR_SERVER_URL --access-code YOUR_CODE
```

See `UPLOADER_README.md` for details.

### For Admins (Deploying)

**Deploy to Railway:**
1. Follow `RAILWAY_CHECKLIST.md`
2. Set `UPLOAD_ACCESS_CODE` and `JWT_SECRET_KEY` in Railway
3. Share `sts2_uploader.py` + access code with friends

See `DEPLOYMENT.md` for complete guide.

### Local Development

```bash
# Setup
createdb sts2_analytics
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings

# Initialize
python init_db.py
python create_admin.py --username admin --password admin123

# Run
python main.py  # Backend on port 8001
# Serve pickrate-viz/index.html for frontend
```

## Architecture

```
Users → sts2_uploader.py → FastAPI Backend → PostgreSQL
                                ↓
                        Analytics Engine
                                ↓
                        Web Visualization
```

## Files

- `backend/` - FastAPI server
- `sts2_uploader.py` - Upload client (share with friends)
- `pickrate-viz/` - Web UI
- `card_pickrate_analysis.py` - Analytics computation logic
- `run_history_data/` - Local run data (gitignored)

## API Endpoints

- `POST /api/runs/check-hashes` - Check which runs exist
- `POST /api/runs/simple-upload` - Upload runs (requires access code)
- `POST /api/analytics/compute` - Compute analytics (admin)
- `GET /api/analytics/global-stats` - Get global pick rates

## Documentation

- `DEPLOYMENT.md` - Deploy to Railway
- `RAILWAY_CHECKLIST.md` - Deployment checklist
- `UPLOADER_README.md` - User guide
- `MVP_DESIGN.md` - Technical architecture

## Run Data Location

**macOS:** `~/Library/Application Support/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run`

**Windows:** `%APPDATA%/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run`

## Security

- Upload access code configured via environment variable
- Steam ID used for user identification
- JWT authentication available for future features
- `.env` files gitignored

## Cost

Railway Hobby: $5/month (includes PostgreSQL)
