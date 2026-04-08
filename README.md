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
pip install mbgg-sts2-uploader
mbgg-sts2-uploader --access-code YOUR_CODE
```

Or manually:
```bash
pip install requests
python3 sts2_uploader.py --server https://mbgg-api.up.railway.app --access-code YOUR_CODE
```

See `UPLOADER_README.md` for details.

### For Admins (Deploying)

**Deploy to Railway:**
1. Follow `RAILWAY_CHECKLIST.md`
2. Set `UPLOAD_ACCESS_CODE`, `JWT_SECRET_KEY`, and `STEAM_API_KEY` in Railway
3. Publish uploader to PyPI or share `sts2_uploader.py` + access code

See `DEPLOYMENT.md` for complete guide.

### Local Development

**Backend:**
```bash
# Setup database
createdb sts2_analytics

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with: DATABASE_URL, JWT_SECRET_KEY, UPLOAD_ACCESS_CODE, STEAM_API_KEY

# Initialize database
python init_db.py
python create_admin.py --username admin --password admin123

# Run backend
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
# Option 1: Simple HTTP server
cd frontend
python3 -m http.server 3000

# Option 2: Using the provided server
cd frontend
python3 server.py

# Frontend will auto-detect localhost and connect to http://localhost:8000
# Open http://localhost:3000 (or http://localhost:8000 if using server.py)
```

## Architecture

```
Users → sts2_uploader.py → FastAPI Backend → PostgreSQL
                                ↓
                        Analytics Engine
                                ↓
                        Web Visualization
```

## Project Structure

- `backend/` - FastAPI server and analytics engine
- `frontend/` - React-based web UI (modular components)
- `mbgg_sts2_uploader/` - PyPI package for uploading runs
- `sts2_uploader.py` - Standalone upload script
- `upload_runs.py` - Bulk upload utility for admins

## API Endpoints

**Public:**
- `POST /api/runs/check-hashes` - Check which runs exist
- `POST /api/runs/simple-upload` - Upload runs (requires access code)
- `GET /api/analytics/global-stats` - Get global pick rates by character/mode/ascension
- `GET /api/analytics/user-stats` - Get per-user pick rates
- `GET /api/analytics/users` - List all users with run counts
- `GET /api/steam/username/{steam_id}` - Get Steam username
- `GET /api/steam/usernames` - Batch fetch Steam usernames

**Admin (JWT required):**
- `POST /api/analytics/compute` - Compute analytics for all filter combinations
- `POST /api/auth/token` - Get JWT token

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
