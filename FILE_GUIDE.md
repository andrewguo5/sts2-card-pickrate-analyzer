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
- `analytics_engine.py` - Card pick rate computation
- `routers/auth.py` - Auth endpoints (register/login)
- `routers/runs.py` - Upload endpoints
- `routers/analytics.py` - Analytics endpoints

### Deployment Config
- `backend/Procfile` - Railway start command
- `backend/railway.json` - Railway configuration
- `backend/nixpacks.toml` - Build configuration
- `backend/start.sh` - Startup script
- `backend/requirements.txt` - Python dependencies
- `backend/.env.example` - Environment variable template

### Upload Client
- `sts2_uploader.py` - **Share this with friends**

### Frontend
- `pickrate-viz/index.html` - Web visualization (React)

## 🛠️ Development/Testing Files

- `backend/init_db.py` - Initialize database tables
- `backend/create_admin.py` - Create admin user
- `backend/test_api.py` - Test API endpoints
- `card_pickrate_analysis.py` - Local analytics (legacy)
- `generate_all_analyses.py` - Batch analytics generation (legacy)
- `visualize_pickrates.py` - Terminal visualization (legacy)
- `analyze_runs.py` - Run statistics (legacy)
- `examine_run_structure.py` - Explore run file format (legacy)
- `upload_runs.py` - Old uploader (replaced by sts2_uploader.py)

## 📊 Data Directories (Gitignored)

- `run_history_data/` - Local run files for development
- `pickrate-viz/data/` - Generated analytics JSON files

## 🔒 Secret Files (Never Commit)

- `backend/.env` - **Contains secrets** (gitignored)

## 📝 Legacy Documentation

- `bandwidth_recommendations.md` - Kernel smoothing guide
- `README_DEPLOY.md` - Alternate deploy guide

## What to Share

**With users:**
- `sts2_uploader.py`
- `UPLOADER_README.md`
- Your server URL
- Your access code (privately!)

**For deployment:**
- Everything in `backend/` (except `.env`)
- `RAILWAY_CHECKLIST.md`
- `DEPLOYMENT.md`

## What NOT to Commit

- `backend/.env` - Contains secrets
- `run_history_data/` - Large game files
- `pickrate-viz/data/` - Generated files
- `__pycache__/` - Python cache
