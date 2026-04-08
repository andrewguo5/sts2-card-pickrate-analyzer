"""
Steam Web API integration for username resolution.
"""
from typing import Optional
import requests
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from config import settings

router = APIRouter(prefix="/api/steam", tags=["steam"])

# In-memory cache for Steam usernames (steam_id -> username)
_username_cache = {}


class SteamUserInfo(BaseModel):
    """Steam user information."""
    steam_id: str
    username: str
    avatar_url: Optional[str] = None


def get_steam_username(steam_id: str) -> Optional[str]:
    """
    Fetch Steam username from Steam Web API.

    Args:
        steam_id: 64-bit Steam ID

    Returns:
        Username (personaname) or None if not found/error
    """
    # Check cache first
    if steam_id in _username_cache:
        return _username_cache[steam_id]

    # Get API key from settings
    api_key = getattr(settings, 'steam_api_key', None)
    if not api_key:
        # No API key configured, return None
        return None

    try:
        # Call Steam Web API
        url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        params = {
            'key': api_key,
            'steamids': steam_id
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        players = data.get('response', {}).get('players', [])

        if not players:
            return None

        player = players[0]
        username = player.get('personaname', steam_id)

        # Cache the result
        _username_cache[steam_id] = username

        return username

    except Exception as e:
        # On error, return None (will fallback to Steam ID)
        print(f"Error fetching Steam username for {steam_id}: {e}")
        return None


@router.get("/username/{steam_id}", response_model=SteamUserInfo)
def get_username(steam_id: str):
    """
    Get Steam username for a Steam ID.

    Args:
        steam_id: 64-bit Steam ID

    Returns:
        SteamUserInfo with username and avatar
    """
    username = get_steam_username(steam_id)

    if username is None:
        # Fallback to Steam ID if API fails
        username = steam_id

    return SteamUserInfo(
        steam_id=steam_id,
        username=username,
        avatar_url=None  # Could fetch from API if needed
    )


@router.get("/usernames", response_model=dict)
def get_usernames_batch(steam_ids: str):
    """
    Get Steam usernames for multiple Steam IDs (comma-separated).

    Query params:
        steam_ids: Comma-separated list of Steam IDs

    Returns:
        Dictionary mapping steam_id -> username
    """
    ids = [sid.strip() for sid in steam_ids.split(',') if sid.strip()]

    result = {}
    for steam_id in ids:
        username = get_steam_username(steam_id)
        result[steam_id] = username if username else steam_id

    return result
