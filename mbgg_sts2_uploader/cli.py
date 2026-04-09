#!/usr/bin/env python3
"""
STS2 Run Uploader

Automatically finds, hashes, and uploads Slay the Spire 2 run files to the analytics server.
Only uploads runs that don't already exist on the server.

Usage:
    # Upload runs (uses production server by default)
    python3 sts2_uploader.py --access-code YOUR_SECRET_CODE
    python3 sts2_uploader.py  # Prompts for access code

    # Delete your data from the server (ADMIN ONLY)
    python3 sts2_uploader.py --delete-my-data
    # This will prompt for admin username/password
"""

import os
import sys
import json
import glob
import hashlib
import requests
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


# Platform-specific paths
if sys.platform == "darwin":  # macOS
    BASE_PATH = Path.home() / "Library/Application Support/SlayTheSpire2"
elif sys.platform == "win32":  # Windows
    appdata = os.getenv("APPDATA") or os.getenv("LOCALAPPDATA")
    if appdata:
        BASE_PATH = Path(appdata) / "SlayTheSpire2"
    else:
        print("✗ Error: Could not find APPDATA directory")
        sys.exit(1)
else:
    print(f"✗ Unsupported platform: {sys.platform}")
    sys.exit(1)


def extract_steam_id() -> Optional[str]:
    """
    Extract Steam ID from the game directory structure.

    Returns:
        Steam ID as string, or None if not found
    """
    steam_dir = BASE_PATH / "steam"
    if not steam_dir.exists():
        return None

    # Look for directory with numeric name (Steam ID)
    for item in steam_dir.iterdir():
        if item.is_dir() and item.name.isdigit():
            return item.name

    return None


def find_run_files() -> List[Path]:
    """
    Find all .run files in the game's save directory.

    Returns:
        List of Path objects to .run files
    """
    if not BASE_PATH.exists():
        print(f"✗ Game directory not found: {BASE_PATH}")
        print("  Please ensure Slay the Spire 2 is installed and you have played at least one game.")
        sys.exit(1)

    # Search for run files
    pattern = str(BASE_PATH / "steam/*/profile*/saves/history/*.run")
    run_files = [Path(p) for p in glob.glob(pattern, recursive=True)]

    return run_files


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA256 hash of a run file's JSON content.

    Args:
        file_path: Path to .run file

    Returns:
        SHA256 hash as hex string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        run_data = json.load(f)

    json_str = json.dumps(run_data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


def check_missing_hashes(server: str, access_code: str, hashes: List[str]) -> List[str]:
    """
    Check which hashes are not yet uploaded to the server.

    Args:
        server: Server URL
        access_code: Upload access code
        hashes: List of SHA256 hashes

    Returns:
        List of missing hashes that need to be uploaded
    """
    try:
        response = requests.post(
            f"{server}/api/runs/check-hashes",
            headers={'X-Access-Code': access_code},
            json={'hashes': hashes},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result['missing_hashes']
    except requests.exceptions.RequestException as e:
        print(f"✗ Error checking hashes: {e}")
        sys.exit(1)


def login_admin(server: str, username: str, password: str) -> str:
    """
    Login as admin and get JWT token.

    Args:
        server: Server URL
        username: Admin username
        password: Admin password

    Returns:
        JWT access token

    Raises:
        requests.exceptions.HTTPError: If login fails
    """
    url = f"{server}/api/auth/token"
    data = {"username": username, "password": password}

    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()
    return response.json()['access_token']


def delete_my_data(server: str, admin_token: str, steam_id: str) -> dict:
    """
    Delete all runs for a Steam ID from the server.

    IMPORTANT: Requires admin authentication.

    Args:
        server: Server URL
        admin_token: Admin JWT token
        steam_id: Steam ID to delete data for

    Returns:
        Response dict with deletion details

    Raises:
        requests.exceptions.HTTPError: If request fails
    """
    url = f"{server}/api/runs/delete-my-data"
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"steam_id": steam_id}

    response = requests.post(url, json=data, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def upload_run(server: str, access_code: str, steam_id: str, run_file: Path) -> dict:
    """
    Upload a single run file to the server.

    Args:
        server: Server URL
        access_code: Upload access code
        steam_id: Steam ID
        run_file: Path to .run file

    Returns:
        Response JSON from server
    """
    with open(run_file, 'r', encoding='utf-8') as f:
        run_data = json.load(f)

    response = requests.post(
        f"{server}/api/runs/simple-upload",
        headers={'X-Access-Code': access_code},
        json={
            'steam_id': steam_id,
            'run_data': run_data
        },
        timeout=60
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description='Upload STS2 run history to analytics server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload to production server (prompts for access code)
  python3 sts2_uploader.py

  # Upload with access code (no prompt)
  python3 sts2_uploader.py --access-code mycode123

  # Dry run (show what would be uploaded without uploading)
  python3 sts2_uploader.py --dry-run

  # Use custom server
  python3 sts2_uploader.py --server http://localhost:8001
        """
    )
    parser.add_argument('--server', default='https://mbgg-api.up.railway.app',
                        help='Server URL (default: https://mbgg-api.up.railway.app)')
    parser.add_argument('--access-code', default=None,
                        help='Upload access code (will prompt if not provided)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be uploaded without actually uploading')
    parser.add_argument('--delete-my-data', action='store_true',
                        help='DELETE all your run data from the server (requires confirmation)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    print("=" * 70)
    print("STS2 RUN UPLOADER")
    print("=" * 70)
    print(f"Platform:       {sys.platform}")
    print(f"Game directory: {BASE_PATH}")
    print(f"Server:         {args.server}")
    print("-" * 70)

    # Extract Steam ID
    print("\n[1/5] Detecting Steam ID...")
    steam_id = extract_steam_id()
    if not steam_id:
        print("✗ Could not find Steam ID in game directory")
        sys.exit(1)
    print(f"      ✓ Steam ID: {steam_id}")

    # Handle data deletion if requested
    if args.delete_my_data:
        print("\n" + "=" * 70)
        print("⚠️  DATA DELETION WARNING")
        print("=" * 70)
        print(f"This will DELETE all run data for Steam ID: {steam_id}")
        print("This action CANNOT be undone!")
        print("This operation requires ADMIN credentials.")
        print("=" * 70)

        confirmation = input("\nType 'DELETE' to confirm deletion: ").strip()
        if confirmation != "DELETE":
            print("✗ Deletion cancelled")
            sys.exit(0)

        # Get admin credentials
        print("\nAdmin authentication required:")
        admin_username = input("  Admin username: ").strip()
        if not admin_username:
            print("✗ Username required")
            sys.exit(1)

        import getpass
        admin_password = getpass.getpass("  Admin password: ")
        if not admin_password:
            print("✗ Password required")
            sys.exit(1)

        # Login as admin
        print("\nAuthenticating...")
        try:
            admin_token = login_admin(args.server, admin_username, admin_password)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("\n✗ Authentication failed: Invalid username or password")
            else:
                print(f"\n✗ Login failed: HTTP {e.response.status_code}")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)

        # Perform deletion
        print("Deleting data...")
        try:
            result = delete_my_data(args.server, admin_token, steam_id)
            print(f"\n✓ {result['message']}")
            print(f"  Runs deleted: {result['runs_deleted']}")
            sys.exit(0)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print("\n✗ Access denied: Admin privileges required")
            else:
                print(f"\n✗ Deletion failed: HTTP {e.response.status_code}")
                if args.verbose:
                    print(f"  {e.response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)

    # Find run files
    print("\n[2/5] Finding run files...")
    run_files = find_run_files()
    if not run_files:
        print("✗ No run files found")
        print("  Have you played any games yet?")
        sys.exit(0)
    print(f"      ✓ Found {len(run_files)} run files")

    # Compute hashes
    print("\n[3/5] Computing file hashes...")
    file_hash_map = {}  # hash -> file_path
    for run_file in run_files:
        try:
            file_hash = compute_file_hash(run_file)
            file_hash_map[file_hash] = run_file
        except Exception as e:
            if args.verbose:
                print(f"      ✗ Error hashing {run_file.name}: {e}")

    print(f"      ✓ Computed {len(file_hash_map)} hashes")

    if args.dry_run:
        print("\n✓ Dry run complete!")
        print(f"  Would check {len(file_hash_map)} runs for upload")
        sys.exit(0)

    # Get access code
    if not args.access_code:
        args.access_code = input("\nEnter upload access code: ").strip()
        if not args.access_code:
            print("✗ Access code required")
            sys.exit(1)

    # Check which runs are missing on server
    print("\n[4/5] Checking server for existing runs...")
    all_hashes = list(file_hash_map.keys())
    missing_hashes = check_missing_hashes(args.server, args.access_code, all_hashes)

    already_uploaded = len(all_hashes) - len(missing_hashes)
    print(f"      ✓ {already_uploaded} already uploaded")
    print(f"      ✓ {len(missing_hashes)} need to be uploaded")

    if not missing_hashes:
        print("\n✓ All runs are already uploaded!")
        sys.exit(0)

    # Upload missing runs
    print(f"\n[5/5] Uploading {len(missing_hashes)} runs...")
    uploaded = 0
    errors = 0

    for i, file_hash in enumerate(missing_hashes, 1):
        run_file = file_hash_map[file_hash]
        try:
            result = upload_run(args.server, args.access_code, steam_id, run_file)
            uploaded += 1
            char_name = result['character'].replace('CHARACTER.', '')
            asc = result['ascension']
            print(f"      [{i}/{len(missing_hashes)}] ✓ {char_name} A{asc}")
        except requests.exceptions.HTTPError as e:
            errors += 1
            if e.response.status_code == 403:
                print(f"\n✗ Access denied: Invalid access code")
                sys.exit(1)
            else:
                print(f"      [{i}/{len(missing_hashes)}] ✗ HTTP {e.response.status_code}")
        except Exception as e:
            errors += 1
            if args.verbose:
                print(f"      [{i}/{len(missing_hashes)}] ✗ {e}")

    # Summary
    print("\n" + "=" * 70)
    print("UPLOAD COMPLETE")
    print("=" * 70)
    print(f"Total runs found:      {len(run_files)}")
    print(f"Already on server:     {already_uploaded}")
    print(f"Newly uploaded:        {uploaded}")
    print(f"Errors:                {errors}")
    print("=" * 70)

    if uploaded > 0:
        print("\n✓ Upload successful!")
        print(f"  View stats at: {args.server.replace(':8001', ':8000')}")


if __name__ == "__main__":
    main()
