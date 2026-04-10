"""
Run upload routes.
"""
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user, verify_access_code
from compression import compress_run_data
from database import get_db
from models import User, Run, AnalyticsCache
from schemas import RunUpload, RunUploadResponse
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/runs", tags=["runs"])


def invalidate_affected_cache(db: Session, character: str, ascension: int, num_players: int, user_id: Optional[int] = None):
    """
    Invalidate cache entries affected by a new run upload.

    Deletes cache entries for:
    - Exact match: specific character, mode, ascension
    - Broader aggregations: 'all' ascensions, 'all' modes
    - Both user-specific and global stats

    Args:
        db: Database session
        character: Character ID (e.g., "CHARACTER.REGENT")
        ascension: Ascension level (0-10)
        num_players: Number of players in run
        user_id: User ID (for user-specific stats)
    """
    # Determine mode based on num_players
    if num_players == 1:
        specific_mode = "singleplayer"
    else:
        specific_mode = "multiplayer"

    # Determine ascension bucket
    if ascension == 10:
        specific_ascension = "a10"
    else:
        specific_ascension = "a0-9"

    # All combinations that need invalidation
    invalidation_targets = [
        # Specific combinations
        (specific_mode, specific_ascension),
        (specific_mode, "all"),  # All ascensions for this mode
        ("all", specific_ascension),  # All modes for this ascension
        ("all", "all"),  # All modes, all ascensions
    ]

    # Invalidate for both user-specific and global stats
    for mode, asc in invalidation_targets:
        # Delete user-specific cache
        if user_id:
            db.query(AnalyticsCache).filter(
                AnalyticsCache.user_id == user_id,
                AnalyticsCache.character == character,
                AnalyticsCache.mode == mode,
                AnalyticsCache.ascension == asc
            ).delete()

        # Delete global cache
        db.query(AnalyticsCache).filter(
            AnalyticsCache.user_id.is_(None),
            AnalyticsCache.character == character,
            AnalyticsCache.mode == mode,
            AnalyticsCache.ascension == asc
        ).delete()

    db.commit()


class CheckHashesRequest(BaseModel):
    """Request to check which run hashes exist on server."""
    hashes: List[str]


class CheckHashesResponse(BaseModel):
    """Response with list of hashes that are missing (not yet uploaded)."""
    missing_hashes: List[str]
    total_checked: int
    already_uploaded: int


def compute_run_hash(run_data: dict) -> str:
    """Compute SHA256 hash of run data to detect duplicates."""
    json_str = json.dumps(run_data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


def extract_run_metadata(run_data: dict) -> dict:
    """
    Extract key metadata from run data.

    Returns:
        dict with keys: character, ascension, num_players, game_version, victory
    """
    character = run_data.get('players', [{}])[0].get('character', 'UNKNOWN')
    ascension = run_data.get('ascension', 0)
    num_players = len(run_data.get('players', []))
    game_version = run_data.get('build_id', None)
    victory = run_data.get('victory', False)

    return {
        'character': character,
        'ascension': ascension,
        'num_players': num_players,
        'game_version': game_version,
        'victory': victory
    }


@router.post("/upload", response_model=RunUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_run(
    upload_data: RunUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a single run file.

    Detects duplicates using SHA256 hash and returns appropriate status.
    """
    run_data = upload_data.run_data

    # Compute hash for duplicate detection
    run_hash = compute_run_hash(run_data)

    # Check if this run already exists
    existing_run = db.query(Run).filter(Run.run_file_hash == run_hash).first()
    if existing_run:
        # Run already uploaded (possibly by this user or another user)
        metadata = extract_run_metadata(run_data)
        return RunUploadResponse(
            id=existing_run.id,
            status="duplicate",
            duplicate=True,
            character=metadata['character'],
            ascension=metadata['ascension']
        )

    # Extract metadata
    metadata = extract_run_metadata(run_data)

    # Compress run data for storage
    compressed_data = compress_run_data(run_data)

    # Create new run record
    new_run = Run(
        user_id=current_user.id,
        run_file_hash=run_hash,
        character=metadata['character'],
        ascension=metadata['ascension'],
        num_players=metadata['num_players'],
        game_version=metadata['game_version'],
        victory=metadata['victory'],
        raw_data=compressed_data  # Store compressed
    )

    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    # Invalidate affected cache entries
    invalidate_affected_cache(
        db,
        character=metadata['character'],
        ascension=metadata['ascension'],
        num_players=metadata['num_players'],
        user_id=current_user.id
    )

    return RunUploadResponse(
        id=new_run.id,
        status="accepted",
        duplicate=False,
        character=new_run.character,
        ascension=new_run.ascension
    )


# ============================================================================
# NEW ACCESS-CODE BASED ENDPOINTS (for simplified upload workflow)
# ============================================================================

class SimpleRunUpload(BaseModel):
    """Simplified run upload with Steam ID."""
    steam_id: str
    run_data: dict


@router.post("/check-hashes", response_model=CheckHashesResponse)
def check_hashes(
    request: CheckHashesRequest,
    access_code_valid: bool = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """
    Check which run hashes are already uploaded to the server.

    This allows the upload client to only upload runs that don't already exist,
    saving bandwidth and time.

    Requires X-Access-Code header.
    """
    existing_hashes = db.query(Run.run_file_hash).filter(
        Run.run_file_hash.in_(request.hashes)
    ).all()

    existing_hash_set = {h[0] for h in existing_hashes}
    missing_hashes = [h for h in request.hashes if h not in existing_hash_set]

    return CheckHashesResponse(
        missing_hashes=missing_hashes,
        total_checked=len(request.hashes),
        already_uploaded=len(existing_hash_set)
    )


@router.post("/simple-upload", response_model=RunUploadResponse, status_code=status.HTTP_201_CREATED)
def simple_upload(
    upload_data: SimpleRunUpload,
    access_code_valid: bool = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """
    Simplified upload endpoint using access code instead of JWT.

    Associates runs with Steam ID instead of user account.
    Requires X-Access-Code header.
    """
    run_data = upload_data.run_data
    steam_id = upload_data.steam_id

    # Compute hash for duplicate detection
    run_hash = compute_run_hash(run_data)

    # Check if this run already exists
    existing_run = db.query(Run).filter(Run.run_file_hash == run_hash).first()
    if existing_run:
        metadata = extract_run_metadata(run_data)
        return RunUploadResponse(
            id=existing_run.id,
            status="duplicate",
            duplicate=True,
            character=metadata['character'],
            ascension=metadata['ascension']
        )

    # Extract metadata
    metadata = extract_run_metadata(run_data)

    # Compress run data for storage
    compressed_data = compress_run_data(run_data)

    # Store run with Steam ID
    new_run = Run(
        user_id=None,  # Not using user accounts for simple upload
        steam_id=steam_id,  # Store Steam ID for user identification
        run_file_hash=run_hash,
        character=metadata['character'],
        ascension=metadata['ascension'],
        num_players=metadata['num_players'],
        game_version=metadata['game_version'],
        victory=metadata['victory'],
        raw_data=compressed_data  # Store compressed
    )

    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    # Invalidate affected cache entries (no user_id for simple upload)
    invalidate_affected_cache(
        db,
        character=metadata['character'],
        ascension=metadata['ascension'],
        num_players=metadata['num_players'],
        user_id=None
    )

    return RunUploadResponse(
        id=new_run.id,
        status="accepted",
        duplicate=False,
        character=new_run.character,
        ascension=new_run.ascension
    )


class DeleteMyDataRequest(BaseModel):
    """Request to delete all data for a Steam ID."""
    steam_id: str


class DeleteMyDataResponse(BaseModel):
    """Response after deleting user data."""
    success: bool
    steam_id: str
    runs_deleted: int
    message: str


@router.post("/delete-my-data", response_model=DeleteMyDataResponse)
def delete_my_data(
    request: DeleteMyDataRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all runs associated with a Steam ID.

    IMPORTANT: This is a destructive operation that cannot be undone.
    Requires admin authentication via JWT token.

    Security:
    - Requires admin JWT token (not just access code)
    - Only admins can delete user data
    - Only deletes runs matching the exact Steam ID provided
    - Returns count of deleted runs for transparency

    Future enhancement: Use Steam OAuth to allow users to delete their own data.
    """
    # Verify admin privileges
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete user data"
        )
    steam_id = request.steam_id.strip()

    if not steam_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Steam ID cannot be empty"
        )

    # Count runs before deletion
    runs_to_delete = db.query(Run).filter(Run.steam_id == steam_id).all()
    num_runs = len(runs_to_delete)

    if num_runs == 0:
        return DeleteMyDataResponse(
            success=True,
            steam_id=steam_id,
            runs_deleted=0,
            message=f"No runs found for Steam ID {steam_id}"
        )

    # Delete all runs for this Steam ID
    db.query(Run).filter(Run.steam_id == steam_id).delete()
    db.commit()

    return DeleteMyDataResponse(
        success=True,
        steam_id=steam_id,
        runs_deleted=num_runs,
        message=f"Successfully deleted {num_runs} run(s) for Steam ID {steam_id}"
    )
