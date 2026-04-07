#!/bin/bash
# Railway startup script

set -e

echo "Initializing database tables..."
python init_db.py || echo "Tables may already exist, continuing..."

echo "Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
