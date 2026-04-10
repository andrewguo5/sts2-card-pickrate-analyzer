#!/usr/bin/env python3
"""
Admin CLI for STS2 Analytics Server

Provides convenient commands for cache management and analytics operations.
Requires admin credentials.
"""
import argparse
import getpass
import sys
import requests
from typing import Optional


DEFAULT_SERVER = "https://mbgg-api.up.railway.app"


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
    url = f"{server}/api/auth/login"
    data = {"username": username, "password": password}

    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()
    return response.json()['access_token']


def clear_cache(server: str, token: str, character: Optional[str] = None) -> dict:
    """
    Clear analytics cache.

    Args:
        server: Server URL
        token: Admin JWT token
        character: Optional character filter (e.g., 'regent')

    Returns:
        Response dict

    Raises:
        requests.exceptions.HTTPError: If request fails
    """
    url = f"{server}/api/analytics/cache/clear"
    if character:
        url += f"?character={character}"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def recompute_analytics(server: str, token: str) -> dict:
    """
    Trigger analytics recomputation.

    Args:
        server: Server URL
        token: Admin JWT token

    Returns:
        Response dict

    Raises:
        requests.exceptions.HTTPError: If request fails
    """
    url = f"{server}/api/analytics/compute"
    headers = {"Authorization": f"Bearer {token}"}
    data = {}  # Empty request triggers full recomputation

    response = requests.post(url, json=data, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description='Admin CLI for STS2 Analytics Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clear all analytics cache
  python3 admin_cli.py --clear-cache

  # Clear cache for specific character
  python3 admin_cli.py --clear-cache --character regent

  # Recompute all analytics
  python3 admin_cli.py --recompute-analytics

  # Use custom server
  python3 admin_cli.py --clear-cache --server http://localhost:8001
        """
    )

    parser.add_argument('--server', default=DEFAULT_SERVER,
                        help=f'Server URL (default: {DEFAULT_SERVER})')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear analytics cache')
    parser.add_argument('--recompute-analytics', action='store_true',
                        help='Recompute analytics cache')
    parser.add_argument('--character', default=None,
                        help='Character filter for cache operations (e.g., regent, ironclad)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    # Require at least one operation
    if not (args.clear_cache or args.recompute_analytics):
        parser.print_help()
        print("\n✗ Error: Please specify an operation (--clear-cache or --recompute-analytics)")
        sys.exit(1)

    print("=" * 70)
    print("STS2 ANALYTICS - ADMIN CLI")
    print("=" * 70)
    print(f"Server: {args.server}")
    print("-" * 70)

    # Get admin credentials
    print("\nAdmin authentication required:")
    username = input("  Username: ").strip()
    if not username:
        print("✗ Username required")
        sys.exit(1)

    password = getpass.getpass("  Password: ")
    if not password:
        print("✗ Password required")
        sys.exit(1)

    # Login
    print("\nAuthenticating...")
    try:
        token = login_admin(args.server, username, password)
        print("✓ Authentication successful")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("\n✗ Authentication failed: Invalid username or password")
        else:
            print(f"\n✗ Login failed: HTTP {e.response.status_code}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

    # Execute operations
    if args.clear_cache:
        print("\n" + "=" * 70)
        print("CLEARING CACHE")
        print("=" * 70)
        if args.character:
            print(f"Character: {args.character}")
        else:
            print("Scope: ALL characters")
        print()

        try:
            result = clear_cache(args.server, token, args.character)
            print(f"✓ {result['status']}")
            print(f"  Entries deleted: {result['entries_deleted']}")
            print(f"  Scope: {result['scope']}")
        except requests.exceptions.HTTPError as e:
            print(f"\n✗ Failed: HTTP {e.response.status_code}")
            if args.verbose and hasattr(e.response, 'text'):
                print(f"  {e.response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)

    if args.recompute_analytics:
        print("\n" + "=" * 70)
        print("RECOMPUTING ANALYTICS")
        print("=" * 70)
        print("⚠️  This may take several minutes...")
        print()

        try:
            result = recompute_analytics(args.server, token)
            print(f"✓ {result['status']}")
            print(f"  Combinations: {result.get('combinations', 'N/A')}")
            print(f"  Estimated time: {result.get('estimated_time', 'N/A')}")
        except requests.exceptions.HTTPError as e:
            print(f"\n✗ Failed: HTTP {e.response.status_code}")
            if args.verbose and hasattr(e.response, 'text'):
                print(f"  {e.response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
