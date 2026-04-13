"""
Analytics computation and retrieval routes.
"""
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from auth import get_current_user, get_current_admin_user
from compression import decompress_run_data
from database import get_db
from models import User, Run, AnalyticsCache
from schemas import AnalyticsComputeRequest, AnalyticsComputeResponse, AnalyticsResponse
from analytics_engine import compute_pickrates
from card_metadata import get_card_metadata

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Cache TTL: 24 hours
CACHE_TTL_HOURS = 24


# Character mapping
CHARACTERS = [
    "CHARACTER.IRONCLAD",
    "CHARACTER.SILENT",
    "CHARACTER.REGENT",
    "CHARACTER.NECROBINDER",
    "CHARACTER.DEFECT"
]

# Bucket definitions
BUCKETS = [
    {"mode": "singleplayer", "ascension": "a10"},
    {"mode": "singleplayer", "ascension": "a0-9"},
    {"mode": "multiplayer", "ascension": "a10"},
    {"mode": "multiplayer", "ascension": "a0-9"},
    {"mode": "singleplayer", "ascension": "all"},
    {"mode": "multiplayer", "ascension": "all"},
    {"mode": "all", "ascension": "all"},
]


def is_cache_fresh(cache_entry: AnalyticsCache) -> bool:
    """
    Check if a cache entry is still fresh (within TTL).

    Args:
        cache_entry: AnalyticsCache database entry

    Returns:
        True if cache is fresh, False if stale
    """
    if not cache_entry or not cache_entry.computed_at:
        return False

    ttl = timedelta(hours=CACHE_TTL_HOURS)
    age = datetime.utcnow() - cache_entry.computed_at.replace(tzinfo=None)
    return age < ttl


def enrich_with_metadata(analytics_data: dict) -> dict:
    """
    Enrich analytics data with card metadata from Spire Codex.

    Adds name, type, rarity to each card's data.
    """
    import logging
    logger = logging.getLogger(__name__)

    enriched = analytics_data.copy()
    missing_metadata = []

    for card_id, card_data in enriched.get("cards", {}).items():
        metadata = get_card_metadata(card_id)
        if metadata:
            # Add metadata fields to the card's summary
            if "summary" in card_data:
                card_data["summary"]["name"] = metadata["name"]
                card_data["summary"]["type"] = metadata["type"]
                card_data["summary"]["rarity"] = metadata["rarity"]
                card_data["summary"]["cost"] = metadata["cost"]
        else:
            missing_metadata.append(card_id)

    if missing_metadata:
        logger.warning(f"Missing metadata for {len(missing_metadata)} cards: {missing_metadata[:10]}")

    return enriched


def parse_ascension_filter(ascension: str):
    """Parse ascension filter into list of ascension levels."""
    if ascension == "a10":
        return [10]
    elif ascension == "a0-9":
        return list(range(0, 10))
    elif ascension == "all":
        return list(range(0, 11))
    else:
        raise ValueError(f"Invalid ascension filter: {ascension}")


def parse_mode_filter(mode: str):
    """Parse mode filter into player count criteria."""
    if mode == "singleplayer":
        return {"min": 1, "max": 1}
    elif mode == "multiplayer":
        return {"min": 2, "max": 99}
    elif mode == "all":
        return {"min": 1, "max": 99}
    else:
        raise ValueError(f"Invalid mode filter: {mode}")


def filter_runs(db: Session, user_id: Optional[int], character: str, mode: str, ascension: str):
    """
    Filter runs based on criteria.

    Args:
        db: Database session
        user_id: User ID (None for global stats)
        character: Character filter (e.g., "CHARACTER.REGENT")
        mode: Mode filter ("singleplayer", "multiplayer", "all")
        ascension: Ascension filter ("a10", "a0-9", "all")

    Returns:
        List of run raw_data dictionaries
    """
    query = db.query(Run)

    # User filter
    if user_id is not None:
        query = query.filter(Run.user_id == user_id)

    # Character filter
    query = query.filter(Run.character == character)

    # Ascension filter
    ascension_levels = parse_ascension_filter(ascension)
    query = query.filter(Run.ascension.in_(ascension_levels))

    # Mode filter (player count)
    mode_criteria = parse_mode_filter(mode)
    query = query.filter(
        Run.num_players >= mode_criteria["min"],
        Run.num_players <= mode_criteria["max"]
    )

    runs = query.all()
    # Decompress run data before returning
    return [decompress_run_data(run.raw_data) for run in runs]


def compute_and_cache_analytics(
    db: Session,
    user_id: Optional[int],
    character: str,
    mode: str,
    ascension: str
) -> dict:
    """
    Compute analytics and cache the result.

    Args:
        db: Database session
        user_id: User ID (None for global stats)
        character: Character filter
        mode: Mode filter
        ascension: Ascension filter

    Returns:
        Analytics data dictionary
    """
    # Filter runs
    runs = filter_runs(db, user_id, character, mode, ascension)

    # Compute pick rates (with character filter to exclude cross-class cards)
    pickrate_data = compute_pickrates(runs, bandwidth=2, character=character)

    # Add metadata
    metadata = {
        "character": character,
        "ascension_level": ascension.upper().replace("A0-9", "A0-9"),
        "multiplayer_filter": mode,
        "runs_processed": len(runs),
        "kernel_bandwidth": 2
    }

    result = {
        "metadata": metadata,
        "cards": pickrate_data["cards"]
    }

    # Cache the result
    # Delete old cache entry if exists
    db.query(AnalyticsCache).filter(
        AnalyticsCache.user_id == user_id,
        AnalyticsCache.character == character,
        AnalyticsCache.mode == mode,
        AnalyticsCache.ascension == ascension
    ).delete()

    # Create new cache entry
    cache_entry = AnalyticsCache(
        user_id=user_id,
        character=character,
        mode=mode,
        ascension=ascension,
        runs_included=len(runs),
        pickrate_data=result
    )
    db.add(cache_entry)
    db.commit()

    return result


@router.post("/compute", response_model=AnalyticsComputeResponse)
def compute_analytics(
    request: AnalyticsComputeRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Compute analytics for all character/mode/ascension combinations.
    Admin only.

    Args:
        request: Contains optional user_id (None for global stats)
    """
    user_id = request.user_id

    # Validate user_id if provided
    if user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )

    # Compute all combinations
    total_combinations = len(CHARACTERS) * len(BUCKETS)

    for character in CHARACTERS:
        for bucket in BUCKETS:
            compute_and_cache_analytics(
                db,
                user_id,
                character,
                bucket["mode"],
                bucket["ascension"]
            )

    return AnalyticsComputeResponse(
        status="completed",
        combinations=total_combinations,
        estimated_time=f"{total_combinations * 2} seconds"
    )


@router.get("/my-stats", response_model=AnalyticsResponse)
def get_my_stats(
    character: str = Query(..., description="Character (e.g., 'regent', 'ironclad')"),
    mode: str = Query(..., description="Mode: singleplayer, multiplayer, all"),
    ascension: str = Query(..., description="Ascension: a10, a0-9, all"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's personal analytics.

    Query parameters:
        - character: Character short name (e.g., 'regent', 'ironclad')
        - mode: 'singleplayer', 'multiplayer', or 'all'
        - ascension: 'a10', 'a0-9', or 'all'
    """
    # Convert short character name to full ID
    character_upper = character.upper()
    full_character = f"CHARACTER.{character_upper}"

    if full_character not in CHARACTERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid character: {character}"
        )

    # Check cache first
    cache_entry = db.query(AnalyticsCache).filter(
        AnalyticsCache.user_id == current_user.id,
        AnalyticsCache.character == full_character,
        AnalyticsCache.mode == mode,
        AnalyticsCache.ascension == ascension
    ).first()

    # Return cached data if fresh
    if cache_entry and is_cache_fresh(cache_entry):
        return enrich_with_metadata(cache_entry.pickrate_data)

    # Cache miss - compute on demand
    result = compute_and_cache_analytics(
        db,
        current_user.id,
        full_character,
        mode,
        ascension
    )

    return enrich_with_metadata(result)


@router.get("/global-stats", response_model=AnalyticsResponse)
def get_global_stats(
    character: str = Query(..., description="Character (e.g., 'regent', 'ironclad')"),
    mode: str = Query(..., description="Mode: singleplayer, multiplayer, all"),
    ascension: str = Query(..., description="Ascension: a10, a0-9, all"),
    db: Session = Depends(get_db)
):
    """
    Get global analytics (averaged across all users).

    Query parameters:
        - character: Character short name (e.g., 'regent', 'ironclad')
        - mode: 'singleplayer', 'multiplayer', or 'all'
        - ascension: 'a10', 'a0-9', or 'all'
    """
    # Convert short character name to full ID
    character_upper = character.upper()
    full_character = f"CHARACTER.{character_upper}"

    if full_character not in CHARACTERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid character: {character}"
        )

    # Check cache first (user_id=None for global)
    cache_entry = db.query(AnalyticsCache).filter(
        AnalyticsCache.user_id.is_(None),
        AnalyticsCache.character == full_character,
        AnalyticsCache.mode == mode,
        AnalyticsCache.ascension == ascension
    ).first()

    # Return cached data if fresh
    if cache_entry and is_cache_fresh(cache_entry):
        return enrich_with_metadata(cache_entry.pickrate_data)

    # Cache miss - compute on demand
    result = compute_and_cache_analytics(
        db,
        None,  # None = global stats
        full_character,
        mode,
        ascension
    )

    return enrich_with_metadata(result)


@router.delete("/cache/clear")
def clear_cache(
    character: Optional[str] = Query(None, description="Clear cache for specific character only"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Clear analytics cache (admin only).

    Query parameters:
        - character: Optional character filter (e.g., 'regent'). If not provided, clears ALL cache.

    Returns:
        Number of cache entries deleted
    """
    query = db.query(AnalyticsCache)

    if character:
        # Clear cache for specific character
        character_upper = character.upper()
        full_character = f"CHARACTER.{character_upper}"

        if full_character not in CHARACTERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid character: {character}"
            )

        query = query.filter(AnalyticsCache.character == full_character)

    # Count before deleting
    count = query.count()

    # Delete cache entries
    query.delete()
    db.commit()

    return {
        "status": "success",
        "entries_deleted": count,
        "scope": f"character={character}" if character else "all characters"
    }


@router.get("/users")
def get_users_list(db: Session = Depends(get_db)):
    """
    Get list of all Steam IDs that have uploaded runs.

    Returns:
        List of objects with steam_id and run_count, sorted by run_count descending
    """
    from sqlalchemy import func

    # Query for unique steam_ids with run counts
    results = db.query(
        Run.steam_id,
        func.count(Run.id).label('run_count')
    ).filter(
        Run.steam_id.isnot(None)
    ).group_by(
        Run.steam_id
    ).order_by(
        func.count(Run.id).desc()
    ).all()

    return [
        {"steam_id": row.steam_id, "run_count": row.run_count}
        for row in results
    ]


@router.get("/users/filtered-counts")
def get_users_filtered_counts(
    character: str = Query(..., description="Character (e.g., 'regent', 'ironclad')"),
    mode: str = Query(..., description="Mode: singleplayer, multiplayer, all"),
    ascension: str = Query(..., description="Ascension: a10, a0-9, all"),
    db: Session = Depends(get_db)
):
    """
    Get run counts for all users filtered by character/mode/ascension.

    Returns:
        Dictionary mapping steam_id to filtered run count
    """
    from sqlalchemy import func

    # Convert short character name to full ID
    character_upper = character.upper()
    full_character = f"CHARACTER.{character_upper}"

    if full_character not in CHARACTERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid character: {character}"
        )

    # Parse filters
    ascension_levels = parse_ascension_filter(ascension)
    mode_criteria = parse_mode_filter(mode)

    # Query for filtered run counts per user
    results = db.query(
        Run.steam_id,
        func.count(Run.id).label('filtered_count')
    ).filter(
        Run.steam_id.isnot(None),
        Run.character == full_character,
        Run.ascension.in_(ascension_levels),
        Run.num_players >= mode_criteria["min"],
        Run.num_players <= mode_criteria["max"]
    ).group_by(
        Run.steam_id
    ).all()

    # Return as dictionary for easy lookup
    return {
        row.steam_id: row.filtered_count
        for row in results
    }


@router.get("/user-stats", response_model=AnalyticsResponse)
def get_user_stats(
    steam_id: str = Query(..., description="Steam ID"),
    character: str = Query(..., description="Character (e.g., 'regent', 'ironclad')"),
    mode: str = Query(..., description="Mode: singleplayer, multiplayer, all"),
    ascension: str = Query(..., description="Ascension: a10, a0-9, all"),
    db: Session = Depends(get_db)
):
    """
    Get analytics for a specific user's Steam ID.

    Query parameters:
        - steam_id: 64-bit Steam ID
        - character: Character short name (e.g., 'regent', 'ironclad')
        - mode: 'singleplayer', 'multiplayer', or 'all'
        - ascension: 'a10', 'a0-9', or 'all'
    """
    # Convert short character name to full ID
    character_upper = character.upper()
    full_character = f"CHARACTER.{character_upper}"

    if full_character not in CHARACTERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid character: {character}"
        )

    # Filter runs by steam_id
    runs = filter_runs_by_steam_id(db, steam_id, full_character, mode, ascension)

    # Compute pick rates (with character filter to exclude cross-class cards)
    pickrate_data = compute_pickrates(runs, bandwidth=2, character=full_character)

    # Add metadata
    metadata = {
        "character": full_character,
        "ascension_level": ascension.upper().replace("A0-9", "A0-9"),
        "multiplayer_filter": mode,
        "runs_processed": len(runs),
        "kernel_bandwidth": 2,
        "steam_id": steam_id
    }

    result = {
        "metadata": metadata,
        "cards": pickrate_data["cards"]
    }

    return enrich_with_metadata(result)


def filter_runs_by_steam_id(db: Session, steam_id: str, character: str, mode: str, ascension: str):
    """
    Filter runs by steam_id instead of user_id.

    Args:
        db: Database session
        steam_id: Steam ID to filter by
        character: Character filter
        mode: Mode filter
        ascension: Ascension filter

    Returns:
        List of run raw_data dictionaries
    """
    query = db.query(Run)

    # Steam ID filter
    query = query.filter(Run.steam_id == steam_id)

    # Character filter
    query = query.filter(Run.character == character)

    # Ascension filter
    ascension_levels = parse_ascension_filter(ascension)
    query = query.filter(Run.ascension.in_(ascension_levels))

    # Mode filter (player count)
    mode_criteria = parse_mode_filter(mode)
    query = query.filter(
        Run.num_players >= mode_criteria["min"],
        Run.num_players <= mode_criteria["max"]
    )

    runs = query.all()
    # Decompress run data before returning
    return [decompress_run_data(run.raw_data) for run in runs]
