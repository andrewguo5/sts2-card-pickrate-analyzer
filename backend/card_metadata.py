"""
Card metadata loader and cache.

Fetches card data from Spire Codex API on startup and caches in memory.
This avoids rate limiting concerns by only fetching once per backend restart.
"""
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# In-memory cache: card_id -> card metadata
CARD_METADATA_CACHE: Dict[str, dict] = {}

# Spire Codex API base URL
SPIRE_CODEX_API = "https://spire-codex.com/api"


def load_card_metadata():
    """
    Fetch all card metadata from Spire Codex API on startup.

    This function fetches cards for all characters and caches them.
    It's called once when the backend starts, so it doesn't create
    ongoing load on the Spire Codex API.
    """
    global CARD_METADATA_CACHE

    # Fetch cards for each character color + colorless cards
    colors = ['ironclad', 'silent', 'regent', 'necrobinder', 'defect', 'colorless']
    total_cards = 0

    logger.info("Loading card metadata from Spire Codex API...")

    for color in colors:
        try:
            url = f"{SPIRE_CODEX_API}/cards?color={color}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            cards = response.json()

            for card in cards:
                # Store with CARD. prefix to match run history format
                card_id = f"CARD.{card['id']}"
                CARD_METADATA_CACHE[card_id] = {
                    'name': card['name'],
                    'type': card['type'],
                    'rarity': card['rarity'],
                    'cost': card['cost'],
                    'star_cost': card.get('star_cost'),
                    'color': card['color'],
                    'description': card['description'],
                    'image_url': card.get('image_url'),
                    'damage': card.get('damage'),
                    'block': card.get('block'),
                }
                total_cards += 1

            logger.info(f"  ✓ Loaded {len(cards)} cards for {color}")

        except requests.exceptions.RequestException as e:
            logger.error(f"  ✗ Failed to load cards for {color}: {e}")
        except Exception as e:
            logger.error(f"  ✗ Error processing cards for {color}: {e}")

    logger.info(f"Card metadata cache loaded: {total_cards} cards total")


def get_card_metadata(card_id: str) -> Optional[dict]:
    """
    Get metadata for a specific card.

    Args:
        card_id: Card ID (with or without CARD. prefix)

    Returns:
        Card metadata dict, or None if not found
    """
    # Ensure CARD. prefix
    if not card_id.startswith("CARD."):
        card_id = f"CARD.{card_id}"

    return CARD_METADATA_CACHE.get(card_id)


def get_all_card_metadata() -> Dict[str, dict]:
    """
    Get all cached card metadata.

    Returns:
        Dictionary of card_id -> metadata
    """
    return CARD_METADATA_CACHE.copy()
