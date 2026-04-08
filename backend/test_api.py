#!/usr/bin/env python3
"""
Convenient test script for the STS2 Analytics API.

Usage:
    python3 test_api.py register <username> <password>
    python3 test_api.py login <username> <password>
    python3 test_api.py upload <username> <password> [--count N]
    python3 test_api.py compute <admin_username> <admin_password> [--user-id ID]
    python3 test_api.py stats <username> <password> --character regent [--mode singleplayer] [--ascension a10]
    python3 test_api.py global --character regent [--mode singleplayer] [--ascension a10]
"""

import sys
import json
import glob
import os
import requests
import argparse

BASE_URL = os.getenv("API_URL", "http://localhost:8001")


def register(username, password):
    """Register a new user."""
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "password": password
    })
    if response.status_code == 201:
        data = response.json()
        print(f"✓ User registered: {data['username']} (ID: {data['id']})")
    else:
        print(f"✗ Registration failed: {response.json().get('detail', 'Unknown error')}")


def login(username, password):
    """Login and get token."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✓ Login successful")
        print(f"Token: {token}")
        return token
    else:
        print(f"✗ Login failed: {response.json().get('detail', 'Unknown error')}")
        return None


def upload_runs(username, password, count=5):
    """Upload run files."""
    # Login first
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": password
    })
    token = response.json()['access_token']

    # Find run files
    run_files = glob.glob('../run_history_data/profile*/*.run')
    if not run_files:
        print("✗ No run files found in ../run_history_data/")
        return

    print(f"Found {len(run_files)} run files, uploading {min(count, len(run_files))}...")

    headers = {'Authorization': f'Bearer {token}'}
    uploaded = 0
    duplicates = 0
    errors = 0

    for run_file in run_files[:count]:
        try:
            with open(run_file, 'r') as f:
                run_data = json.load(f)

            response = requests.post(f"{BASE_URL}/api/runs/upload",
                                    headers=headers,
                                    json={'run_data': run_data})
            result = response.json()

            if result.get('duplicate'):
                duplicates += 1
                print(f"  ⊙ Duplicate: {result['character']} A{result['ascension']}")
            else:
                uploaded += 1
                print(f"  ✓ Uploaded: {result['character']} A{result['ascension']} (ID: {result['id']})")
        except Exception as e:
            errors += 1
            print(f"  ✗ Error: {e}")

    print(f"\nSummary: {uploaded} uploaded, {duplicates} duplicates, {errors} errors")


def compute_analytics(username, password, user_id=None):
    """Trigger analytics computation (admin only)."""
    # Login first
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": password
    })

    if response.status_code != 200:
        print(f"✗ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return

    token = response.json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    print(f"Computing analytics for {'all users' if user_id is None else f'user {user_id}'}...")

    response = requests.post(f"{BASE_URL}/api/analytics/compute",
                            headers=headers,
                            json={'user_id': user_id})

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Analytics computed")
        print(f"  Combinations: {result['combinations']}")
        print(f"  Estimated time: {result['estimated_time']}")
    else:
        print(f"✗ Computation failed: {response.json().get('detail', 'Unknown error')}")


def get_my_stats(username, password, character, mode='singleplayer', ascension='a10'):
    """Get user's personal stats."""
    # Login first
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": password
    })
    token = response.json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(
        f"{BASE_URL}/api/analytics/my-stats",
        headers=headers,
        params={'character': character, 'mode': mode, 'ascension': ascension}
    )

    if response.status_code == 200:
        data = response.json()
        metadata = data['metadata']
        print(f"✓ Stats retrieved for {username}")
        print(f"  Character: {metadata['character']}")
        print(f"  Mode: {metadata['multiplayer_filter']}")
        print(f"  Ascension: {metadata['ascension_level']}")
        print(f"  Runs: {metadata['runs_processed']}")
        print(f"  Cards analyzed: {len(data['cards'])}")
    else:
        print(f"✗ Failed: {response.json().get('detail', 'Unknown error')}")


def get_global_stats(character, mode='singleplayer', ascension='a10'):
    """Get global stats (no auth needed)."""
    response = requests.get(
        f"{BASE_URL}/api/analytics/global-stats",
        params={'character': character, 'mode': mode, 'ascension': ascension}
    )

    if response.status_code == 200:
        data = response.json()
        metadata = data['metadata']
        print(f"✓ Global stats retrieved")
        print(f"  Character: {metadata['character']}")
        print(f"  Mode: {metadata['multiplayer_filter']}")
        print(f"  Ascension: {metadata['ascension_level']}")
        print(f"  Runs: {metadata['runs_processed']}")
        print(f"  Cards analyzed: {len(data['cards'])}")
    else:
        print(f"✗ Failed: {response.json().get('detail', 'Unknown error')}")


def main():
    parser = argparse.ArgumentParser(description='Test STS2 Analytics API')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Register
    register_parser = subparsers.add_parser('register', help='Register a new user')
    register_parser.add_argument('username')
    register_parser.add_argument('password')

    # Login
    login_parser = subparsers.add_parser('login', help='Login and get token')
    login_parser.add_argument('username')
    login_parser.add_argument('password')

    # Upload
    upload_parser = subparsers.add_parser('upload', help='Upload run files')
    upload_parser.add_argument('username')
    upload_parser.add_argument('password')
    upload_parser.add_argument('--count', type=int, default=5, help='Number of runs to upload')

    # Compute
    compute_parser = subparsers.add_parser('compute', help='Compute analytics (admin only)')
    compute_parser.add_argument('username')
    compute_parser.add_argument('password')
    compute_parser.add_argument('--user-id', type=int, default=None, help='User ID (None for global)')

    # My stats
    stats_parser = subparsers.add_parser('stats', help='Get my stats')
    stats_parser.add_argument('username')
    stats_parser.add_argument('password')
    stats_parser.add_argument('--character', required=True)
    stats_parser.add_argument('--mode', default='singleplayer')
    stats_parser.add_argument('--ascension', default='a10')

    # Global stats
    global_parser = subparsers.add_parser('global', help='Get global stats')
    global_parser.add_argument('--character', required=True)
    global_parser.add_argument('--mode', default='singleplayer')
    global_parser.add_argument('--ascension', default='a10')

    args = parser.parse_args()

    if args.command == 'register':
        register(args.username, args.password)
    elif args.command == 'login':
        login(args.username, args.password)
    elif args.command == 'upload':
        upload_runs(args.username, args.password, args.count)
    elif args.command == 'compute':
        compute_analytics(args.username, args.password, args.user_id)
    elif args.command == 'stats':
        get_my_stats(args.username, args.password, args.character, args.mode, args.ascension)
    elif args.command == 'global':
        get_global_stats(args.character, args.mode, args.ascension)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
