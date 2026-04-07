# Backend Setup Guide

Complete step-by-step guide to get the backend running.

## Prerequisites

- Python 3.8+
- PostgreSQL 12+

---

## Step 1: Install PostgreSQL

### macOS (Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15

# Add to PATH (add to ~/.zshrc or ~/.bashrc)
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Verify installation:
```bash
psql --version
```

---

## Step 2: Create Database

```bash
# Create database
createdb sts2_analytics

# Verify
psql -l | grep sts2_analytics
```

---

## Step 3: Install Python Dependencies

```bash
cd backend
python3 -m pip install -r requirements.txt
```

---

## Step 4: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env (use your favorite editor)
nano .env
```

Update these values:
```
DATABASE_URL=postgresql://YOUR_USERNAME@localhost:5432/sts2_analytics
JWT_SECRET_KEY=generate-a-random-secret-key-here
```

To get your PostgreSQL username:
```bash
whoami  # This is usually your username
```

To generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Step 5: Initialize Database

```bash
python3 init_db.py
```

Expected output:
```
Creating database tables...
✓ Database tables created successfully

Tables created:
  - users
  - runs
  - analytics_cache
```

---

## Step 6: Create Admin User

```bash
python3 create_admin.py --username admin --password yourpassword
```

---

## Step 7: Start the Server

```bash
python3 main.py
```

Or:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Step 8: Test the API

Open another terminal and test:

### 1. Health check:
```bash
curl http://localhost:8000/health
```

### 2. Register a test user:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 3. Login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

Save the `access_token` from the response!

### 4. View API Documentation:

Open in browser: **http://localhost:8000/docs**

---

## Troubleshooting

### "Connection refused" error

PostgreSQL is not running:
```bash
brew services start postgresql@15
```

### "password authentication failed"

Update DATABASE_URL in `.env` with correct credentials:
```
DATABASE_URL=postgresql://username:password@localhost:5432/sts2_analytics
```

### "database does not exist"

Create the database:
```bash
createdb sts2_analytics
```

### Module import errors

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

---

## Next Steps

Once the backend is running:

1. **Create upload client** - See `upload_runs.py` in parent directory
2. **Update frontend** - Modify React app to use API
3. **Test end-to-end** - Upload runs, compute analytics, view in web UI

See `MVP_DESIGN.md` for complete workflow.
