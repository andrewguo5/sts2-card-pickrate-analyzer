#!/usr/bin/env python3
"""
Create an admin user account.

Usage:
    python3 create_admin.py --username admin --password yourpassword
"""
import argparse
from database import SessionLocal
from models import User
from auth import get_password_hash


def create_admin_user(username: str, password: str):
    """Create an admin user."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"✗ User '{username}' already exists")
            return

        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            password_hash=hashed_password,
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print(f"✓ Admin user '{username}' created successfully")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create an admin user')
    parser.add_argument('--username', required=True, help='Admin username')
    parser.add_argument('--password', required=True, help='Admin password')
    args = parser.parse_args()

    create_admin_user(args.username, args.password)
