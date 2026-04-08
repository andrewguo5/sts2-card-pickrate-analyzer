#!/usr/bin/env python3
"""
Debug user authentication.

Usage:
    python3 debug_user.py --username admin --password testpass
"""
import argparse
from database import SessionLocal
from models import User
from auth import get_password_hash, verify_password


def debug_user(username: str, password: str):
    """Debug user authentication."""
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"✗ User '{username}' not found in database")
            return

        print(f"✓ User found: {username}")
        print(f"  ID: {user.id}")
        print(f"  Is Admin: {user.is_admin}")
        print(f"  Password hash (first 50 chars): {user.password_hash[:50]}...")
        print(f"  Password hash length: {len(user.password_hash)}")

        # Test password verification
        print(f"\nTesting password verification...")
        try:
            is_valid = verify_password(password, user.password_hash)
            if is_valid:
                print(f"✓ Password is VALID")
            else:
                print(f"✗ Password is INVALID")
        except Exception as e:
            print(f"✗ Error during verification: {e}")

        # Generate new hash for comparison
        print(f"\nGenerating new hash for the same password...")
        new_hash = get_password_hash(password)
        print(f"  New hash (first 50 chars): {new_hash[:50]}...")
        print(f"  New hash length: {len(new_hash)}")

        # Test new hash verification
        is_valid_new = verify_password(password, new_hash)
        print(f"  New hash verification: {'✓ VALID' if is_valid_new else '✗ INVALID'}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Debug user authentication')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='Password to test')
    args = parser.parse_args()

    debug_user(args.username, args.password)
