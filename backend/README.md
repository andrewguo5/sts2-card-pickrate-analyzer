# STS2 Analytics Backend

FastAPI backend for Slay the Spire 2 run history analytics.

## Features

- **User Authentication** (JWT-based)
- **Run Upload** with duplicate detection
- **Analytics Computation** with caching
- **User Stats** (personal analytics)
- **Global Stats** (aggregated across all users)

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL

Install PostgreSQL if you haven't already:

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Create database:**
```bash
createdb sts2_analytics
```

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and update:
```
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/sts2_analytics
JWT_SECRET_KEY=your-secret-key-here
```

### 4. Initialize Database

Create tables:
```bash
python3 init_db.py
```

Create an admin user:
```bash
python3 create_admin.py --username admin --password your_admin_password
```

### 5. Run the Server

```bash
python3 main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

API documentation: **http://localhost:8000/docs**

---

## API Endpoints

### Authentication

**Register:**
```bash
POST /api/auth/register
{
  "username": "alice",
  "password": "secret123"
}
```

**Login:**
```bash
POST /api/auth/login
{
  "username": "alice",
  "password": "secret123"
}
# Returns: { "access_token": "...", "token_type": "bearer" }
```

### Upload Runs

```bash
POST /api/runs/upload
Headers: Authorization: Bearer <token>
{
  "run_data": { ... }  # Run JSON from game
}
```

### Analytics

**Compute Analytics (Admin only):**
```bash
POST /api/analytics/compute
Headers: Authorization: Bearer <admin_token>
{
  "user_id": null  # null for global, or specific user_id
}
```

**Get My Stats:**
```bash
GET /api/analytics/my-stats?character=regent&mode=singleplayer&ascension=a10
Headers: Authorization: Bearer <token>
```

**Get Global Stats:**
```bash
GET /api/analytics/global-stats?character=regent&mode=singleplayer&ascension=a10
```

---

## Testing

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

Save the access_token from the response.

### 3. Upload a Run

```bash
# First, get a sample run file
cat ~/Library/Application\ Support/SlayTheSpire2/steam/*/profile*/saves/history/*.run | head -1 > sample_run.json

# Upload it
curl -X POST http://localhost:8000/api/runs/upload \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d @sample_run.json
```

### 4. Compute Analytics (as admin)

```bash
curl -X POST http://localhost:8000/api/analytics/compute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{"user_id": null}'
```

### 5. Get Stats

```bash
# My stats
curl http://localhost:8000/api/analytics/my-stats?character=regent&mode=singleplayer&ascension=a10 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Global stats
curl http://localhost:8000/api/analytics/global-stats?character=regent&mode=singleplayer&ascension=a10
```

---

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration settings
├── database.py            # Database connection
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── auth.py                # Authentication utilities
├── analytics_engine.py    # Analytics computation
├── routers/
│   ├── auth.py           # Auth endpoints
│   ├── runs.py           # Run upload endpoints
│   └── analytics.py      # Analytics endpoints
├── init_db.py            # Database initialization
├── create_admin.py       # Admin user creation
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## Database Schema

### users
- id (primary key)
- username (unique)
- password_hash
- created_at
- is_admin

### runs
- id (primary key)
- user_id (foreign key)
- run_file_hash (unique, for duplicate detection)
- character
- ascension
- num_players
- game_version
- victory
- uploaded_at
- raw_data (JSONB)

### analytics_cache
- id (primary key)
- user_id (foreign key, NULL for global)
- character
- mode
- ascension
- runs_included
- computed_at
- pickrate_data (JSONB)

---

## Deployment

See `MVP_DESIGN.md` in the parent directory for deployment instructions.

Recommended platforms:
- Railway.app
- Render.com
- DigitalOcean App Platform

All offer managed PostgreSQL and easy Python deployment.
