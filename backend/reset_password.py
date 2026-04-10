#!/usr/bin/env python3
"""
Reset a user's password.

Usage:
    python3 reset_password.py --username admin --password newpassword
"""
import argparse
from database import SessionLocal, engine
from models import User
from auth import get_password_hash


def reset_password(username: str, new_password: str):
    """Reset a user's password."""
    # Show which database we're connecting to
    db_url = str(engine.url)
    # Mask password in URL for security
    if '@' in db_url:
        parts = db_url.split('@')
        if ':' in parts[0]:
            user_pass = parts[0].split(':')
            masked_url = f"{user_pass[0]}:****@{parts[1]}"
        else:
            masked_url = db_url
    else:
        masked_url = db_url

    print(f"Database: {masked_url}")
    print()

    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"✗ User '{username}' not found")
            print(f"  Checked database: {masked_url}")
            return

        print(f"Found user: {username}")
        print(f"  User ID: {user.id}")
        print(f"  Is admin: {user.is_admin}")
        print(f"  Old hash (first 20 chars): {user.password_hash[:20]}...")
        print()

        # Hash new password (will be stripped automatically by get_password_hash)
        new_hash = get_password_hash(new_password)
        print(f"Generated new hash: {new_hash[:20]}...")
        print()

        # Update password
        old_hash = user.password_hash
        user.password_hash = new_hash
        db.commit()
        db.refresh(user)

        # Verify the update
        print(f"✓ Password reset successful for user '{username}'")
        print(f"  New password: '{new_password.strip()}'")
        print(f"  Password length: {len(new_password.strip())}")
        print(f"  Old hash: {old_hash[:20]}...")
        print(f"  New hash: {new_hash[:20]}...")
        print()

        # Double-check by querying again
        db.expire_all()
        verify_user = db.query(User).filter(User.username == username).first()
        if verify_user.password_hash == new_hash:
            print(f"✓ Verified: Password hash updated in database")
        else:
            print(f"✗ WARNING: Password hash does not match after commit!")
            print(f"    Expected: {new_hash[:20]}...")
            print(f"    Got: {verify_user.password_hash[:20]}...")

    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reset a user password')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='New password')
    args = parser.parse_args()

    reset_password(args.username, args.password)
