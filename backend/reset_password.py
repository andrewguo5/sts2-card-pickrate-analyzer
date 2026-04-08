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


def reset_password(username: str, password: str):
    """Reset a user's password."""
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"✗ User '{username}' not found")
            return

        # Update password
        from auth import verify_password
        new_hash = get_password_hash(password)
        user.password_hash = new_hash
        db.commit()
        db.refresh(user)

        print(f"✓ Password reset for user '{username}'")

        # Verify the password was set correctly
        if verify_password(password, user.password_hash):
            print(f"✓ Password verification successful")
        else:
            print(f"✗ WARNING: Password verification failed after reset!")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reset user password')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='New password')
    args = parser.parse_args()

    reset_password(args.username, args.password)
