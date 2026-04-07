#!/usr/bin/env python3
"""
Initialize the database with tables.

Usage:
    python3 init_db.py
"""
from database import Base, engine
from models import User, Run, AnalyticsCache

def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")
    print("\nTables created:")
    print("  - users")
    print("  - runs")
    print("  - analytics_cache")

if __name__ == "__main__":
    init_database()
