# Workflow Guide

## User Workflow (Uploading Runs)

```bash
# 1. Install dependencies
pip install requests

# 2. Upload runs to server
python3 sts2_uploader.py --server https://your-app.railway.app --access-code YOUR_CODE

# 3. View stats
# Visit the web interface at your server URL
```

The uploader automatically:
- Finds run files on your system
- Detects your Steam ID
- Only uploads runs that don't already exist
- Shows progress

## Admin Workflow (Managing Server)

### Initial Setup
```bash
# Deploy to Railway (see RAILWAY_CHECKLIST.md)
# Set environment variables
# Initialize database and create admin user
```

### Computing Analytics
```bash
# After users upload runs, compute analytics:
python3 test_api.py compute admin YOUR_ADMIN_PASSWORD --user-id null

# Or for specific user:
python3 test_api.py compute admin YOUR_ADMIN_PASSWORD --user-id 2
```

### Viewing Stats
```bash
# Global stats (no auth required)
curl https://your-app.railway.app/api/analytics/global-stats?character=regent&mode=singleplayer&ascension=a10

# API docs
https://your-app.railway.app/docs
```

## Local Development Workflow

```bash
# 1. Start PostgreSQL
brew services start postgresql@15

# 2. Create database
createdb sts2_analytics

# 3. Configure backend
cd backend
cp .env.example .env
# Edit .env

# 4. Initialize database
python3 init_db.py
python3 create_admin.py --username admin --password admin123

# 5. Start backend
python3 main.py  # Runs on port 8001

# 6. (In another terminal) Test upload
cd ..
python3 sts2_uploader.py --access-code spire_upload_2026_secret

# 7. Compute analytics
python3 backend/test_api.py compute admin admin123

# 8. Serve frontend
cd pickrate-viz
python3 -m http.server 8000
# Visit http://localhost:8000
```

## Data Flow

```
1. User plays STS2 → Run saved to ~/.../history/*.run
2. User runs sts2_uploader.py
3. Uploader checks which runs are new
4. Uploader uploads new runs → PostgreSQL
5. Admin triggers analytics computation
6. Analytics stored in analytics_cache table
7. Users view stats on web interface
```

## File Locations

**Game saves (macOS):**
```
~/Library/Application Support/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run
```

**Game saves (Windows):**
```
%APPDATA%/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run
```

**Local run data (for development):**
```
run_history_data/  # Gitignored
```

## Common Tasks

### Generate all analytics
```bash
# All characters × all buckets (35 combinations)
python3 generate_all_analyses.py
```

### Test specific character
```bash
python3 card_pickrate_analysis.py \
  --character CHARACTER.REGENT \
  --ascension A10 \
  --multiplayer singleplayer \
  --output test_output.json
```

### View terminal visualization
```bash
python3 visualize_pickrates.py --card BEGONE
```
