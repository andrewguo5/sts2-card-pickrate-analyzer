#!/usr/bin/env python3
"""
Reset a user's password.

Usage:
    python3 reset_password.py --username admin --password newpassword
"""
import argparse
from database import SessionLocal
from models import User
from auth import get_password_hash


def reset_password(username: str, new_password: str):
    """Reset a user's password."""
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"✗ User '{username}' not found")
            return

        # Hash new password (will be stripped automatically by get_password_hash)
        new_hash = get_password_hash(new_password)

        # Update password
        user.password_hash = new_hash
        db.commit()

        print(f"✓ Password reset successful for user '{username}'")
        print(f"  New password: '{new_password.strip()}'")
        print(f"  Password length: {len(new_password.strip())}")
        print(f"  Hash: {new_hash}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reset a user password')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='New password')
    args = parser.parse_args()

    reset_password(args.username, args.password)
