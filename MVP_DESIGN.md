# MVP Design Document

## Overview
Server-based Slay the Spire 2 analytics platform where users can upload run history and view personalized statistics.

## MVP Scope

### Core Features
1. **Cross-platform Upload Client** (Windows + macOS)
2. **Run History Storage** (PostgreSQL)
3. **Batch Analytics Computation** (triggered manually/API)
4. **User Authentication** (simple JWT-based)
5. **Web Interface** with two views:
   - **My Stats**: User's personal analytics
   - **Global Stats**: Averaged across all users

### Explicitly OUT of Scope for MVP
- OAuth integration (use simple username/password)
- Real-time analytics updates
- Complex user management/admin panel
- Rate limiting
- Email notifications
- Advanced caching strategies

---

## Architecture

```
┌─────────────────┐
│  Upload Client  │ (Python script, cross-platform)
│  (Windows/Mac)  │
└────────┬────────┘
         │ HTTP POST /api/runs/upload
         ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  - /api/auth/login                  │
│  - /api/runs/upload                 │
│  - /api/analytics/compute (admin)   │
│  - /api/analytics/my-stats          │
│  - /api/analytics/global-stats      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│       PostgreSQL Database           │
│  - users                            │
│  - runs                             │
│  - analytics_cache                  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         React Web Frontend          │
│  - Login page                       │
│  - My Stats (character/mode/asc)    │
│  - Global Stats (same filters)      │
└─────────────────────────────────────┘
```

---

## Database Schema

### `users` table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE
);
```

### `runs` table
```sql
CREATE TABLE runs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    run_file_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA256 to prevent duplicates
    character VARCHAR(50) NOT NULL,
    ascension INTEGER NOT NULL,
    num_players INTEGER NOT NULL,
    game_version VARCHAR(20),
    victory BOOLEAN NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB NOT NULL,

    -- Indexes for fast filtering
    INDEX idx_character (character),
    INDEX idx_ascension (ascension),
    INDEX idx_num_players (num_players),
    INDEX idx_user_id (user_id)
);
```

### `analytics_cache` table
```sql
CREATE TABLE analytics_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,  -- NULL for global stats
    character VARCHAR(50) NOT NULL,
    mode VARCHAR(20) NOT NULL,  -- 'singleplayer', 'multiplayer', 'all'
    ascension VARCHAR(10) NOT NULL,  -- 'a10', 'a0-9', 'all'
    runs_included INTEGER NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pickrate_data JSONB NOT NULL,

    -- Unique constraint: one cache entry per user/character/mode/ascension combo
    UNIQUE (user_id, character, mode, ascension),
    INDEX idx_user_char (user_id, character)
);
```

---

## API Endpoints

### Authentication
```
POST /api/auth/register
Body: { "username": "alice", "password": "..." }
Response: { "user_id": 1, "username": "alice" }

POST /api/auth/login
Body: { "username": "alice", "password": "..." }
Response: { "access_token": "eyJ...", "token_type": "bearer" }
```

### Upload Runs
```
POST /api/runs/upload
Headers: Authorization: Bearer <token>
Body: { "run_data": {...} }  # Single run JSON
Response: {
    "id": 123,
    "status": "accepted",
    "duplicate": false,
    "character": "CHARACTER.REGENT",
    "ascension": 10
}
```

### Compute Analytics (Admin/Manual Trigger)
```
POST /api/analytics/compute
Headers: Authorization: Bearer <token>
Body: { "user_id": null }  # null = all users (global), or specific user_id
Response: {
    "status": "computing",
    "combinations": 35,
    "estimated_time": "60 seconds"
}
```

### Get User's Stats
```
GET /api/analytics/my-stats?character=regent&mode=singleplayer&ascension=a10
Headers: Authorization: Bearer <token>
Response: {
    "metadata": {
        "character": "CHARACTER.REGENT",
        "ascension_level": "A10",
        "multiplayer_filter": "singleplayer",
        "runs_processed": 42
    },
    "cards": { ... }  # Same format as current JSON
}
```

### Get Global Stats
```
GET /api/analytics/global-stats?character=regent&mode=singleplayer&ascension=a10
Response: {
    "metadata": {
        "character": "CHARACTER.REGENT",
        "ascension_level": "A10",
        "multiplayer_filter": "singleplayer",
        "runs_processed": 587,
        "users_included": 14
    },
    "cards": { ... }
}
```

---

## Upload Client (Cross-Platform)

**File: `upload_runs.py`**

```python
#!/usr/bin/env python3
"""
Cross-platform run history uploader for Windows and macOS.

Usage:
    python upload_runs.py --username alice --password secret123
    python upload_runs.py --username alice --password secret123 --server https://myserver.com
"""

import os
import sys
import json
import glob
import hashlib
import requests
from pathlib import Path

# Platform-specific paths
if sys.platform == "darwin":  # macOS
    BASE_PATH = Path.home() / "Library/Application Support/SlayTheSpire2"
elif sys.platform == "win32":  # Windows
    BASE_PATH = Path(os.getenv("APPDATA")) / "SlayTheSpire2"
else:
    print(f"Unsupported platform: {sys.platform}")
    sys.exit(1)

def find_run_files():
    """Find all .run files in the game's save directory."""
    pattern = str(BASE_PATH / "steam/*/profile*/saves/history/*.run")
    return glob.glob(pattern, recursive=True)

def compute_hash(run_data):
    """Compute SHA256 hash of run data to detect duplicates."""
    json_str = json.dumps(run_data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()

def login(server, username, password):
    """Authenticate and get access token."""
    response = requests.post(f"{server}/api/auth/login", json={
        "username": username,
        "password": password
    })
    response.raise_for_status()
    return response.json()["access_token"]

def upload_run(server, token, run_data):
    """Upload a single run to the server."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{server}/api/runs/upload",
                             headers=headers,
                             json={"run_data": run_data})
    return response.json()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Upload STS2 run history to server')
    parser.add_argument('--username', required=True, help='Your username')
    parser.add_argument('--password', required=True, help='Your password')
    parser.add_argument('--server', default='http://localhost:8000', help='Server URL')
    args = parser.parse_args()

    print("Finding run files...")
    run_files = find_run_files()
    print(f"Found {len(run_files)} run files")

    print("Logging in...")
    token = login(args.server, args.username, args.password)
    print("✓ Authenticated")

    uploaded = 0
    duplicates = 0
    errors = 0

    for run_file in run_files:
        try:
            with open(run_file, 'r') as f:
                run_data = json.load(f)

            result = upload_run(args.server, token, run_data)

            if result.get("duplicate"):
                duplicates += 1
            else:
                uploaded += 1
                print(f"✓ Uploaded: {result['character']} A{result['ascension']}")
        except Exception as e:
            errors += 1
            print(f"✗ Error uploading {run_file}: {e}")

    print("\n" + "="*60)
    print(f"Upload complete!")
    print(f"Uploaded: {uploaded}")
    print(f"Duplicates skipped: {duplicates}")
    print(f"Errors: {errors}")
    print("="*60)

if __name__ == "__main__":
    main()
```

---

## Analytics Computation Strategy

**Process:**
1. Admin triggers `/api/analytics/compute` (or runs nightly cron job)
2. Backend iterates through all 35 combinations (5 chars × 7 buckets)
3. For each combination:
   - **User-specific**: Query runs WHERE user_id = X AND filters
   - **Global**: Query runs WHERE filters (all users)
   - Run existing `CardPickRateAnalyzer` logic
   - Store result in `analytics_cache` table
4. Frontend always reads from cache (fast!)

**Code reuse:**
- Keep existing `card_pickrate_analysis.py` logic
- Refactor into a class that accepts run list instead of file paths
- Backend calls this class with database-queried runs

---

## Web Frontend Updates

**New features:**
1. **Login page** (`/login`)
2. **View toggle**: "My Stats" vs "Global Stats"
3. **Data fetching**: Replace `fetch('data/...')` with `fetch('/api/analytics/...')`
4. **Auth header**: Include JWT token in requests

**Modified state:**
```javascript
const [viewMode, setViewMode] = useState('my-stats');  // 'my-stats' or 'global-stats'
const [token, setToken] = useState(localStorage.getItem('token'));
```

---

## Deployment (MVP)

**Recommended: Railway.app or Render.com**

Both offer:
- Free PostgreSQL database (with limits)
- Easy Python app deployment
- HTTPS included
- ~$5-10/month for production

**Steps:**
1. Push code to GitHub
2. Connect Railway/Render to repo
3. Add PostgreSQL service
4. Set environment variables:
   - `DATABASE_URL`
   - `JWT_SECRET_KEY`
5. Deploy!

---

## MVP Checklist

### Backend
- [ ] FastAPI project structure
- [ ] Database models (SQLAlchemy)
- [ ] Auth endpoints (register, login)
- [ ] Upload endpoint with duplicate detection
- [ ] Analytics computation endpoint
- [ ] User stats endpoint
- [ ] Global stats endpoint

### Upload Client
- [ ] Cross-platform path detection
- [ ] Authentication
- [ ] Batch upload with progress
- [ ] Duplicate detection (client-side optional)

### Frontend
- [ ] Login page
- [ ] JWT token storage
- [ ] View mode toggle (My Stats / Global Stats)
- [ ] API integration (replace local file fetching)
- [ ] Auth header on requests

### Deployment
- [ ] Railway/Render setup
- [ ] PostgreSQL database provisioned
- [ ] Environment variables configured
- [ ] Initial user accounts created

---

## Timeline Estimate

- **Week 1**: Backend API + Database (8-12 hours)
- **Week 2**: Upload client + Analytics refactor (6-8 hours)
- **Week 3**: Frontend updates + Auth (6-8 hours)
- **Week 4**: Testing + Deployment (4-6 hours)

**Total: 24-34 hours**

---

## Next Steps

1. Set up FastAPI project structure
2. Create database models
3. Implement authentication
4. Build upload endpoint
5. Refactor analytics code for database
6. Update frontend
7. Create upload client
8. Deploy to Railway/Render
