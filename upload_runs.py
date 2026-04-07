#!/usr/bin/env python3
"""
Cross-platform run history uploader for Windows and macOS.

Finds and uploads all .run files from Slay the Spire 2 save directory
to the analytics server.

Usage:
    python3 upload_runs.py --username alice --password secret123
    python3 upload_runs.py --username alice --password secret123 --server https://myserver.com
"""

import os
import sys
import json
import glob
import hashlib
import requests
from pathlib import Path
import argparse


# Platform-specific paths
if sys.platform == "darwin":  # macOS
    BASE_PATH = Path.home() / "Library/Application Support/SlayTheSpire2"
elif sys.platform == "win32":  # Windows
    appdata = os.getenv("APPDATA") or os.getenv("LOCALAPPDATA")
    if appdata:
        BASE_PATH = Path(appdata) / "SlayTheSpire2"
    else:
        print("Error: Could not find APPDATA directory")
        sys.exit(1)
else:
    print(f"Unsupported platform: {sys.platform}")
    sys.exit(1)


def find_run_files():
    """Find all .run files in the game's save directory."""
    if not BASE_PATH.exists():
        print(f"Error: Game directory not found at {BASE_PATH}")
        print("Please ensure Slay the Spire 2 is installed and you have played at least one game.")
        sys.exit(1)

    # Search for run files
    pattern = str(BASE_PATH / "steam/*/profile*/saves/history/*.run")
    run_files = glob.glob(pattern, recursive=True)

    return run_files


def compute_hash(run_data):
    """Compute SHA256 hash of run data to detect duplicates."""
    json_str = json.dumps(run_data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


def login(server, username, password):
    """Authenticate and get access token."""
    try:
        response = requests.post(
            f"{server}/api/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("✗ Authentication failed: Invalid username or password")
        else:
            print(f"✗ Login error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error: {e}")
        print(f"   Make sure the server is running at {server}")
        sys.exit(1)


def upload_run(server, token, run_data):
    """Upload a single run to the server."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{server}/api/runs/upload",
        headers=headers,
        json={"run_data": run_data},
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description='Upload STS2 run history to analytics server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 upload_runs.py --username alice --password secret123
  python3 upload_runs.py --username alice --password secret123 --server https://myserver.com
        """
    )
    parser.add_argument('--username', required=True, help='Your username')
    parser.add_argument('--password', required=True, help='Your password')
    parser.add_argument('--server', default='http://localhost:8000', help='Server URL (default: http://localhost:8000)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    print("=" * 70)
    print("STS2 RUN UPLOADER")
    print("=" * 70)
    print(f"Platform: {sys.platform}")
    print(f"Game directory: {BASE_PATH}")
    print(f"Server: {args.server}")
    print("-" * 70)

    print("\n[1/4] Finding run files...")
    run_files = find_run_files()
    print(f"      Found {len(run_files)} run files")

    if len(run_files) == 0:
        print("\n✗ No run files found.")
        print("  Have you played any games yet?")
        sys.exit(0)

    print("\n[2/4] Authenticating...")
    try:
        token = login(args.server, args.username, args.password)
        print("      ✓ Authenticated successfully")
    except Exception as e:
        print(f"      ✗ Authentication failed: {e}")
        sys.exit(1)

    print("\n[3/4] Uploading runs...")
    uploaded = 0
    duplicates = 0
    errors = 0

    for i, run_file in enumerate(run_files, 1):
        try:
            if args.verbose:
                print(f"      [{i}/{len(run_files)}] Processing {Path(run_file).name}...")

            with open(run_file, 'r', encoding='utf-8') as f:
                run_data = json.load(f)

            result = upload_run(args.server, token, run_data)

            if result.get("duplicate"):
                duplicates += 1
                if args.verbose:
                    print(f"          ⊙ Duplicate (already uploaded)")
            else:
                uploaded += 1
                char_name = result['character'].replace('CHARACTER.', '')
                asc = result['ascension']
                print(f"      ✓ [{i}/{len(run_files)}] Uploaded: {char_name} A{asc}")

        except json.JSONDecodeError:
            errors += 1
            print(f"      ✗ [{i}/{len(run_files)}] Invalid JSON: {Path(run_file).name}")
        except requests.exceptions.RequestException as e:
            errors += 1
            print(f"      ✗ [{i}/{len(run_files)}] Upload failed: {e}")
        except Exception as e:
            errors += 1
            print(f"      ✗ [{i}/{len(run_files)}] Error: {e}")

    print("\n[4/4] Summary")
    print("-" * 70)
    print(f"Total files processed: {len(run_files)}")
    print(f"Uploaded:              {uploaded}")
    print(f"Duplicates skipped:    {duplicates}")
    print(f"Errors:                {errors}")
    print("=" * 70)

    if uploaded > 0:
        print("\n✓ Upload complete!")
        print("\nNext steps:")
        print(f"  1. Compute analytics: POST {args.server}/api/analytics/compute")
        print(f"  2. View stats at your web interface")
    elif duplicates == len(run_files):
        print("\n✓ All runs already uploaded!")
    else:
        print("\n⚠ No new runs uploaded")


if __name__ == "__main__":
    main()
