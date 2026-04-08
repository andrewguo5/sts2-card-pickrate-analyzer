# File Guide

Quick reference for what each file does.

## 📖 Documentation (Read These First)

- `README.md` - Project overview and quick start
- `RAILWAY_CHECKLIST.md` - **Start here for deployment**
- `DEPLOYMENT.md` - Detailed deployment guide
- `UPLOADER_README.md` - Share with users
- `WORKFLOW.md` - Common workflows
- `MVP_DESIGN.md` - Technical architecture
- `FILE_GUIDE.md` - This file

## 🚀 Production Files (Deploy These)

### Backend (`backend/`)
- `main.py` - FastAPI application entry point
- `config.py` - Configuration from environment variables
- `database.py` - Database connection
- `models.py` - SQLAlchemy database models
- `schemas.py` - Pydantic request/response schemas
- `auth.py` - Authentication (JWT + access code)
- `analytics_engine.py` - Card pick rate computation with kernel smoothing
- `routers/auth.py` - Auth endpoints (register/login)
- `routers/runs.py` - Upload endpoints
- `routers/analytics.py` - Global and per-user analytics endpoints
- `routers/steam.py` - Steam Web API integration for usernames
- `init_db.py` - Initialize database tables
- `create_admin.py` - Create admin user

### Deployment Config
- `backend/Procfile` - Railway start command
- `backend/railway.json` - Railway configuration
- `backend/nixpacks.toml` - Build configuration
- `backend/start.sh` - Startup script
- `backend/requirements.txt` - Python dependencies
- `backend/.env.example` - Environment variable template

### Upload Client
- `sts2_uploader.py` - Standalone upload script
- `upload_runs.py` - Bulk upload utility for admins
- `mbgg_sts2_uploader/` - PyPI package (pip install mbgg-sts2-uploader)

### Frontend (`frontend/`)
- `index.html` - Main app entry point
- `server.py` - Simple HTTP server for Railway
- `styles.css` - All application styles
- `components/config.js` - API config and constants
- `components/ChartComponent.js` - Chart.js visualization
- `components/FilterBar.js` - Character/Mode/Ascension/User filters
- `components/MetadataBar.js` - Stats metadata display
- `components/CardList.js` - Searchable card sidebar
- `components/CardDetail.js` - Card stats and charts

## 📊 Data Directories (Gitignored)

- `run_history_data/` - Local run files for development

## 🔒 Secret Files (Never Commit)

- `backend/.env` - Contains: `DATABASE_URL`, `JWT_SECRET_KEY`, `UPLOAD_ACCESS_CODE`, `STEAM_API_KEY`

## 📝 Documentation

- `README_DEPLOY.md` - Alternate deploy guide
- `WORKFLOW.md` - Common development workflows

## What to Share

**With users:**
- PyPI package name: `mbgg-sts2-uploader`
- Or: `sts2_uploader.py` + `UPLOADER_README.md`
- Access code (privately!)

**For deployment:**
- Everything in `backend/` and `frontend/` (except `.env`)
- `RAILWAY_CHECKLIST.md`
- `DEPLOYMENT.md`

## What NOT to Commit

- `backend/.env` - Contains secrets
- `run_history_data/` - Large game files
- `dist/`, `build/`, `*.egg-info` - Python build artifacts
- `__pycache__/` - Python cache
- `node_modules/` - If using Node tools

## Local Development

**Run frontend locally:**
```bash
cd frontend
python3 -m http.server 3000
# Open http://localhost:3000
# Frontend auto-detects localhost and uses http://localhost:8000 for API
```

**Run backend locally:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```
