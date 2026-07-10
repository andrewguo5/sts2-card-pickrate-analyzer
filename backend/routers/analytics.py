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
from card_coordinates import compute_all_card_coordinates

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Cache TTL: 24 hours
CACHE_TTL_HOURS = 24

# Trend delta window (personal stats only): compares the headline stat computed
# over all of a user's runs against a baseline computed over all runs EXCEPT the
# most recent RECENT_RUN_WINDOW. The delta surfaces how recent play has shifted
# each card's pick/win/skip rate.
RECENT_RUN_WINDOW = 10           # N: number of most-recent runs defining the "recent" window
MIN_RECENT_OFFERS_FOR_TREND = 3  # min recent offers before a pick/skip delta is shown
MIN_RECENT_PICKS_FOR_TREND = 3   # min recent picks before a win-rate delta is shown


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


def get_fresh_cached_analytics(
    db: Session,
    user_id: Optional[int],
    character: str,
    mode: str,
    ascension: str,
    version: str
) -> Optional[dict]:
    """Return fresh cached analytics for a bucket, or None to compute on demand.

    The cache only holds the unfiltered ("all" versions) bucket, so a specific
    version always misses and is computed live. Returns the cached pickrate_data
    dict when a fresh entry exists, else None.
    """
    if version != "all":
        return None

    cache_entry = db.query(AnalyticsCache).filter(
        AnalyticsCache.user_id.is_(None) if user_id is None else AnalyticsCache.user_id == user_id,
        AnalyticsCache.character == character,
        AnalyticsCache.mode == mode,
        AnalyticsCache.ascension == ascension
    ).first()

    if cache_entry and is_cache_fresh(cache_entry):
        return cache_entry.pickrate_data
    return None


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


def apply_version_filter(query, version: str):
    """Narrow a run query to a single game version, unless version is 'all'."""
    if version != "all":
        query = query.filter(Run.game_version == version)
    return query


def filter_runs(db: Session, user_id: Optional[int], character: str, mode: str, ascension: str, version: str = "all"):
    """
    Filter runs based on criteria.

    Args:
        db: Database session
        user_id: User ID (None for global stats)
        character: Character filter (e.g., "CHARACTER.REGENT")
        mode: Mode filter ("singleplayer", "multiplayer", "all")
        ascension: Ascension filter ("a10", "a0-9", "all")
        version: Game version filter (e.g., "v0.98.3"), or "all" for no filter

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

    # Game version filter
    query = apply_version_filter(query, version)

    # Order by upload sequence (Run.id) so index reflects recency: oldest first,
    # newest last. Keeps the "most recent N runs" slice deterministic for baseline
    # coordinate computation.
    runs = query.order_by(Run.id.asc()).all()
    # Decompress run data before returning
    return [decompress_run_data(run.raw_data) for run in runs]


def build_analytics_result(pickrate_data: dict, metadata: dict) -> dict:
    """Assemble the analytics response payload from computed pick-rate data.

    Centralizes which top-level analytics blocks are surfaced so every endpoint
    returns the same shape: cards, baseline skip data, and the bucket-wide
    baseline win rate.
    """
    return {
        "metadata": metadata,
        "cards": pickrate_data["cards"],
        "baseline_skip_data": pickrate_data.get("baseline_skip_data", {}),
        "baseline_winrate": pickrate_data.get("baseline_winrate", 0.0)
    }


def compute_and_cache_analytics(
    db: Session,
    user_id: Optional[int],
    character: str,
    mode: str,
    ascension: str,
    version: str = "all"
) -> dict:
    """
    Compute analytics and cache the result.

    Args:
        db: Database session
        user_id: User ID (None for global stats)
        character: Character filter
        mode: Mode filter
        ascension: Ascension filter
        version: Game version filter (e.g., "v0.98.3"), or "all" for no filter

    Returns:
        Analytics data dictionary
    """
    # Filter runs
    runs = filter_runs(db, user_id, character, mode, ascension, version)

    # Compute pick rates (with character filter to exclude cross-class cards)
    pickrate_data = compute_pickrates(runs, bandwidth=2, character=character)

    # Add metadata
    metadata = {
        "character": character,
        "ascension_level": ascension.upper().replace("A0-9", "A0-9"),
        "multiplayer_filter": mode,
        "game_version": version,
        "runs_processed": len(runs),
        "kernel_bandwidth": 2
    }

    result = build_analytics_result(pickrate_data, metadata)

    # The cache is keyed on (user_id, character, mode, ascension) only, so it can
    # store just the unfiltered ("all" versions) bucket. A specific version is a
    # live-compute path: never read from or written to the cache, or it would
    # collide with the unfiltered bucket's key.
    if version == "all":
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
    version: str = Query("all", description="Game version (e.g., 'v0.98.3'), or 'all'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's personal analytics.

    Query parameters:
        - character: Character short name (e.g., 'regent', 'ironclad')
        - mode: 'singleplayer', 'multiplayer', or 'all'
        - ascension: 'a10', 'a0-9', or 'all'
        - version: game version (e.g., 'v0.98.3'), or 'all' for no filter
    """
    # Convert short character name to full ID
    character_upper = character.upper()
    full_character = f"CHARACTER.{character_upper}"

    if full_character not in CHARACTERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid character: {character}"
        )

    # Check cache first (unfiltered bucket only; a specific version computes live)
    cached = get_fresh_cached_analytics(db, current_user.id, full_character, mode, ascension, version)
    if cached is not None:
        return enrich_with_metadata(cached)

    # Cache miss - compute on demand
    result = compute_and_cache_analytics(
        db,
        current_user.id,
        full_character,
        mode,
        ascension,
        version
    )

    return enrich_with_metadata(result)


@router.get("/global-stats", response_model=AnalyticsResponse)
def get_global_stats(
    character: str = Query(..., description="Character (e.g., 'regent', 'ironclad')"),
    mode: str = Query(..., description="Mode: singleplayer, multiplayer, all"),
    ascension: str = Query(..., description="Ascension: a10, a0-9, all"),
    version: str = Query("all", description="Game version (e.g., 'v0.98.3'), or 'all'"),
    db: Session = Depends(get_db)
):
    """
    Get global analytics (averaged across all users).

    Query parameters:
        - character: Character short name (e.g., 'regent', 'ironclad')
        - mode: 'singleplayer', 'multiplayer', or 'all'
        - ascension: 'a10', 'a0-9', or 'all'
        - version: game version (e.g., 'v0.98.3'), or 'all' for no filter
    """
    # Convert short character name to full ID
    character_upper = character.upper()
    full_character = f"CHARACTER.{character_upper}"

    if full_character not in CHARACTERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid character: {character}"
        )

    # Check cache first (user_id=None for global; unfiltered bucket only)
    cached = get_fresh_cached_analytics(db, None, full_character, mode, ascension, version)
    if cached is not None:
        return enrich_with_metadata(cached)

    # Cache miss - compute on demand
    result = compute_and_cache_analytics(
        db,
        None,  # None = global stats
        full_character,
        mode,
        ascension,
        version
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


@router.get("/distinct-versions")
def get_distinct_versions(db: Session = Depends(get_db)):
    """
    Get the distinct game versions present across all runs, newest first.

    Powers the patch filter. The frontend prepends an "All Patches" ('all')
    option; this endpoint returns only the concrete versions that have data.

    Returns:
        List of version strings (e.g., ["v0.98.3", "v0.98.2"]) sorted descending.
    """
    rows = db.query(Run.game_version).filter(
        Run.game_version.isnot(None)
    ).distinct().all()

    # rows are 1-tuples; sort descending so the newest patch leads the list.
    versions = sorted((row[0] for row in rows), reverse=True)
    return versions


@router.get("/users/filtered-counts")
def get_users_filtered_counts(
    character: str = Query(..., description="Character (e.g., 'regent', 'ironclad')"),
    mode: str = Query(..., description="Mode: singleplayer, multiplayer, all"),
    ascension: str = Query(..., description="Ascension: a10, a0-9, all"),
    version: str = Query("all", description="Game version (e.g., 'v0.98.3'), or 'all'"),
    db: Session = Depends(get_db)
):
    """
    Get run counts for all users filtered by character/mode/ascension/version.

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
    query = db.query(
        Run.steam_id,
        func.count(Run.id).label('filtered_count')
    ).filter(
        Run.steam_id.isnot(None),
        Run.character == full_character,
        Run.ascension.in_(ascension_levels),
        Run.num_players >= mode_criteria["min"],
        Run.num_players <= mode_criteria["max"]
    )
    query = apply_version_filter(query, version)
    results = query.group_by(Run.steam_id).all()

    # Return as dictionary for easy lookup
    return {
        row.steam_id: row.filtered_count
        for row in results
    }


def _overall_winrate(card: dict) -> tuple:
    """Return (win_rate, picked) for a card, computed as won/picked over all acts.

    Mirrors the frontend calculation in WinRateTab.js (winrate_data.overall).
    """
    overall = card.get("winrate_data", {}).get("overall", {})
    picked = overall.get("picked", 0)
    won = overall.get("won", 0)
    win_rate = won / picked if picked > 0 else 0.0
    return win_rate, picked


def _overall_skiprate(card: dict) -> float:
    """Return the overall skip rate for a card, summed across floors.

    Mirrors the frontend calculation in SkipRateTab.js (skip_data).
    """
    skip_data = card.get("skip_data", {})
    offered = sum(counts["offered"] for counts in skip_data.values())
    skipped = sum(counts["skipped"] for counts in skip_data.values())
    return skipped / offered if offered > 0 else 0.0


def _attach_trend_deltas(all_cards: dict, baseline_cards: Optional[dict]) -> None:
    """Inject recent-play trend deltas into each card's summary, in place.

    For every card, compares the headline stat (over all runs) against a baseline
    stat (over runs excluding the most recent RECENT_RUN_WINDOW). The delta is
    expressed in percentage points. A per-metric sufficiency flag guards against
    noise: it is only set when the recent window contributed enough samples, where
    the recent count is derived as (headline count - baseline count).

    When baseline_cards is None (too few total runs for a baseline), all deltas
    are 0.0 and all sufficiency flags are False.
    """
    has_baseline = baseline_cards is not None

    for card_id, card in all_cards.items():
        summary = card["summary"]

        if not has_baseline:
            summary["pickrate_delta_pp"] = 0.0
            summary["winrate_delta_pp"] = 0.0
            summary["skiprate_delta_pp"] = 0.0
            summary["pickrate_trend_ok"] = False
            summary["winrate_trend_ok"] = False
            summary["skiprate_trend_ok"] = False
            continue

        baseline = baseline_cards.get(card_id)

        # Headline stats (over all runs).
        pick_rate = summary["overall_pickrate"]
        win_rate, picked = _overall_winrate(card)
        skip_rate = _overall_skiprate(card)

        # Baseline stats (over old runs only); absent card => 0 rate, 0 counts.
        base_summary = baseline["summary"] if baseline else None
        base_pick_rate = base_summary["overall_pickrate"] if base_summary else 0.0
        base_offered = base_summary["total_offered"] if base_summary else 0
        base_win_rate, base_picked = _overall_winrate(baseline) if baseline else (0.0, 0)
        base_skip_rate = _overall_skiprate(baseline) if baseline else 0.0

        # Recent-window sample counts = headline - baseline.
        recent_offers = summary["total_offered"] - base_offered
        recent_picks = picked - base_picked

        offers_ok = recent_offers >= MIN_RECENT_OFFERS_FOR_TREND
        picks_ok = recent_picks >= MIN_RECENT_PICKS_FOR_TREND

        summary["pickrate_delta_pp"] = round((pick_rate - base_pick_rate) * 100, 1)
        summary["winrate_delta_pp"] = round((win_rate - base_win_rate) * 100, 1)
        summary["skiprate_delta_pp"] = round((skip_rate - base_skip_rate) * 100, 1)
        summary["pickrate_trend_ok"] = offers_ok
        summary["winrate_trend_ok"] = picks_ok
        summary["skiprate_trend_ok"] = offers_ok


@router.get("/user-stats", response_model=AnalyticsResponse)
def get_user_stats(
    steam_id: str = Query(..., description="Steam ID"),
    character: str = Query(..., description="Character (e.g., 'regent', 'ironclad')"),
    mode: str = Query(..., description="Mode: singleplayer, multiplayer, all"),
    ascension: str = Query(..., description="Ascension: a10, a0-9, all"),
    version: str = Query("all", description="Game version (e.g., 'v0.98.3'), or 'all'"),
    db: Session = Depends(get_db)
):
    """
    Get analytics for a specific user's Steam ID.

    Query parameters:
        - steam_id: 64-bit Steam ID
        - character: Character short name (e.g., 'regent', 'ironclad')
        - mode: 'singleplayer', 'multiplayer', or 'all'
        - ascension: 'a10', 'a0-9', or 'all'
        - version: game version (e.g., 'v0.98.3'), or 'all' for no filter
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
    runs = filter_runs_by_steam_id(db, steam_id, full_character, mode, ascension, version)

    # Compute pick rates (with character filter to exclude cross-class cards)
    pickrate_data = compute_pickrates(runs, bandwidth=2, character=full_character)

    # Attach recent-play trend deltas. runs is ordered oldest -> newest, so the
    # baseline is every run except the most recent RECENT_RUN_WINDOW. When there
    # aren't enough runs for a baseline, deltas fall back to the insufficient state.
    total = len(runs)
    if total > RECENT_RUN_WINDOW:
        old_runs = runs[:total - RECENT_RUN_WINDOW]
        baseline_data = compute_pickrates(old_runs, bandwidth=2, character=full_character)
        _attach_trend_deltas(pickrate_data["cards"], baseline_data["cards"])
    else:
        _attach_trend_deltas(pickrate_data["cards"], baseline_cards=None)

    # Add metadata
    metadata = {
        "character": full_character,
        "ascension_level": ascension.upper().replace("A0-9", "A0-9"),
        "multiplayer_filter": mode,
        "game_version": version,
        "runs_processed": len(runs),
        "kernel_bandwidth": 2,
        "steam_id": steam_id
    }

    result = build_analytics_result(pickrate_data, metadata)

    return enrich_with_metadata(result)


def filter_runs_by_steam_id(db: Session, steam_id: str, character: str, mode: str, ascension: str, version: str = "all"):
    """
    Filter runs by steam_id instead of user_id.

    Args:
        db: Database session
        steam_id: Steam ID to filter by
        character: Character filter
        mode: Mode filter
        ascension: Ascension filter
        version: Game version filter (e.g., "v0.98.3"), or "all" for no filter

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

    # Game version filter
    query = apply_version_filter(query, version)

    # Order by upload sequence (Run.id) so index reflects recency: oldest first,
    # newest last. This makes the "most recent N runs" slice deterministic.
    runs = query.order_by(Run.id.asc()).all()
    # Decompress run data before returning
    return [decompress_run_data(run.raw_data) for run in runs]


def build_coordinate_map(pickrate_data: dict) -> dict:
    """Compute card coordinates and keep only cards that carry full metadata.

    Cards without a name/type/rarity (colorless cards absent from Spire Codex)
    are dropped so the scatter plot never renders unlabeled points. Expects
    pickrate_data to already be metadata-enriched.
    """
    coordinates = compute_all_card_coordinates(pickrate_data)

    result = {}
    for card_id, coords in coordinates.items():
        card_summary = pickrate_data.get('cards', {}).get(card_id, {}).get('summary', {})

        # Skip cards without metadata (name/type/rarity missing => not in Spire Codex)
        if not card_summary.get('name'):
            continue
        if not card_summary.get('type') or not card_summary.get('rarity'):
            continue

        result[card_id] = {
            **coords,
            'name': card_summary.get('name'),
            'type': card_summary.get('type'),
            'rarity': card_summary.get('rarity'),
            'cost': card_summary.get('cost')
        }

    return result


def compute_baseline_coordinates(runs: list, character: str) -> dict:
    """Compute coordinates over all runs EXCEPT the most recent RECENT_RUN_WINDOW.

    These "baseline" positions let the frontend animate how the last N runs
    shifted each card's coordinates. `runs` must be ordered oldest -> newest.
    Returns {card_id: {x, y}} for cards present in the baseline; empty when there
    aren't enough runs to define a baseline window.
    """
    if len(runs) <= RECENT_RUN_WINDOW:
        return {}

    old_runs = runs[:len(runs) - RECENT_RUN_WINDOW]
    baseline_pickrates = compute_pickrates(old_runs, bandwidth=2, character=character)
    baseline_pickrates = enrich_with_metadata(baseline_pickrates)
    baseline_map = build_coordinate_map(baseline_pickrates)

    # Only the position is needed for the animation; drop the rest of the payload.
    return {card_id: {'x': coords['x'], 'y': coords['y']} for card_id, coords in baseline_map.items()}


@router.get("/card-coordinates")
def get_card_coordinates(
    character: str = Query(..., description="Character (e.g., 'regent', 'ironclad')"),
    mode: str = Query(..., description="Mode: singleplayer, multiplayer, all"),
    ascension: str = Query(..., description="Ascension: a10, a0-9, all"),
    version: str = Query("all", description="Game version (e.g., 'v0.98.3'), or 'all'"),
    steam_id: Optional[str] = Query(None, description="Optional Steam ID for user-specific data"),
    db: Session = Depends(get_db)
):
    """
    Get 2D coordinates for all cards in a given bucket.

    Each card is assigned (x, y) coordinates where:
    - x-axis (Pickability): How pickable/playable the card is (pick rate - skip rate)
    - y-axis (Conditional Power): How well the card performs given it was picked (win rate)

    Query parameters:
        - character: Character short name (e.g., 'regent', 'ironclad')
        - mode: 'singleplayer', 'multiplayer', or 'all'
        - ascension: 'a10', 'a0-9', or 'all'
        - steam_id: Optional Steam ID for user-specific data (omit for global stats)

    Returns:
        Dictionary mapping card_id -> coordinate data with metadata
    """
    # Convert short character name to full ID
    character_upper = character.upper()
    full_character = f"CHARACTER.{character_upper}"

    if full_character not in CHARACTERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid character: {character}"
        )

    # Fetch the bucket's runs (ordered oldest -> newest) so both current and
    # baseline coordinates come from the same, deterministically-ordered set.
    if steam_id:
        runs = filter_runs_by_steam_id(db, steam_id, full_character, mode, ascension, version)
    else:
        runs = filter_runs(db, None, full_character, mode, ascension, version)

    # Current coordinates: use the global cache when available (unauthenticated,
    # no steam_id); otherwise compute from the fetched runs.
    if steam_id:
        pickrate_data = compute_pickrates(runs, bandwidth=2, character=full_character)
        metadata = {
            "character": full_character,
            "ascension_level": ascension.upper().replace("A0-9", "A0-9"),
            "multiplayer_filter": mode,
            "game_version": version,
            "runs_processed": len(runs),
            "kernel_bandwidth": 2,
            "steam_id": steam_id
        }
        pickrate_data = build_analytics_result(pickrate_data, metadata)
    else:
        cached = get_fresh_cached_analytics(db, None, full_character, mode, ascension, version)
        if cached is not None:
            pickrate_data = cached
        else:
            pickrate_data = compute_and_cache_analytics(db, None, full_character, mode, ascension, version)

    # Enrich with metadata, then compute the current coordinate map.
    pickrate_data = enrich_with_metadata(pickrate_data)
    coordinates = build_coordinate_map(pickrate_data)

    # Baseline coordinates (all runs except the most recent N) drive the "recent
    # shift" animation on the scatter plot.
    baseline_coordinates = compute_baseline_coordinates(runs, full_character)

    return {
        'coordinates': coordinates,
        'baseline_coordinates': baseline_coordinates,
        'metadata': pickrate_data.get('metadata', {}),
        # Bucket-wide baseline win rate, surfaced so the scatter can draw a
        # reference line on its win-rate (Y) axis.
        'baseline_winrate': pickrate_data.get('baseline_winrate', 0.0)
    }
