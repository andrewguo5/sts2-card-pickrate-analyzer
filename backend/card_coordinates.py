"""
Card coordinate computation for 2D visualizations.

Computes two axes for each card:
- X-axis (Pickability): How pickable/playable a card is based on pick rate and skip rate
- Y-axis (Conditional Power): How well the card performs given that it was picked (win rate)
"""
from typing import Dict, Any, Optional


def compute_pickability(pick_rate: float, skip_rate: float) -> float:
    """
    Compute the pickability metric for a card.

    Pickability measures how pickable and playable a card is based on:
    - High pick rate (card is frequently picked when offered)
    - Low skip rate (card rarely causes the entire offer to be skipped)

    Args:
        pick_rate: Estimated pick rate (0.0 to 1.0)
        skip_rate: Estimated skip rate (0.0 to 1.0)

    Returns:
        Pickability score normalized to [0, 1] where:
        - 1.0 = always picked, never skipped (highly pickable)
        - 0.0 = never picked, always skipped (not pickable)
    """
    # Pickability = pick_rate - skip_rate
    # This ranges from -1 (never picked, always skipped) to +1 (always picked, never skipped)
    raw_pickability = pick_rate - skip_rate

    # Normalize to [0, 1] by adding 1 and dividing by 2
    normalized = (raw_pickability + 1.0) / 2.0

    return normalized


def compute_conditional_power(win_rate: float) -> float:
    """
    Compute the conditional power metric for a card.

    Conditional power measures how well a card performs given that it was picked.
    This is simply the estimated win rate of runs that picked this card.

    Args:
        win_rate: Estimated win rate (0.0 to 1.0)

    Returns:
        Conditional power score [0, 1] where:
        - 1.0 = always wins when picked
        - 0.0 = never wins when picked
    """
    return win_rate


def estimate_rate_with_succession(successes: int, trials: int) -> float:
    """
    Estimate a rate using the rule of succession (Laplace smoothing).

    This adds 1 to the numerator and 2 to the denominator to provide
    a better estimate when sample sizes are small.

    Args:
        successes: Number of successes
        trials: Number of trials

    Returns:
        Estimated rate using rule of succession
    """
    if trials == 0:
        return 0.5  # No data, return neutral estimate

    return (successes + 1) / (trials + 2)


def compute_card_coordinates(card_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Compute 2D coordinates for a card based on its analytics data.

    Args:
        card_data: Card analytics data containing:
            - raw_data: Pick/offer counts by floor
            - skip_data: Skip/offer counts by floor
            - winrate_data: Pick/win counts (overall and by act)

    Returns:
        Dictionary with:
            - x: Pickability score [0, 1]
            - y: Conditional power score [0, 1]
            - pick_rate_estimate: Estimated pick rate
            - skip_rate_estimate: Estimated skip rate
            - win_rate_estimate: Estimated win rate
            - total_offered: Total times card was offered
            - total_picked: Total times card was picked
    """
    # Aggregate pick rate data across all floors
    total_offered = 0
    total_picked = 0

    for floor_data in card_data.get('raw_data', {}).values():
        total_offered += floor_data.get('offered', 0)
        total_picked += floor_data.get('picked', 0)

    # Aggregate skip rate data across all floors
    total_skip_offered = 0
    total_skipped = 0

    for floor_data in card_data.get('skip_data', {}).values():
        total_skip_offered += floor_data.get('offered', 0)
        total_skipped += floor_data.get('skipped', 0)

    # Get overall win rate data
    overall_winrate_data = card_data.get('winrate_data', {}).get('overall', {})
    total_picked_for_winrate = overall_winrate_data.get('picked', 0)
    total_won = overall_winrate_data.get('won', 0)

    # Estimate rates using rule of succession
    pick_rate_estimate = estimate_rate_with_succession(total_picked, total_offered)
    skip_rate_estimate = estimate_rate_with_succession(total_skipped, total_skip_offered)
    win_rate_estimate = estimate_rate_with_succession(total_won, total_picked_for_winrate)

    # Compute coordinates
    x = compute_pickability(pick_rate_estimate, skip_rate_estimate)
    y = compute_conditional_power(win_rate_estimate)

    return {
        'x': x,
        'y': y,
        'pick_rate_estimate': pick_rate_estimate,
        'skip_rate_estimate': skip_rate_estimate,
        'win_rate_estimate': win_rate_estimate,
        'total_offered': total_offered,
        'total_picked': total_picked,
        'total_picked_for_winrate': total_picked_for_winrate,
        'total_won': total_won
    }


def compute_all_card_coordinates(analytics_data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Compute coordinates for all cards in an analytics dataset.

    Args:
        analytics_data: Full analytics data with 'cards' dictionary

    Returns:
        Dictionary mapping card_id -> coordinate data
    """
    result = {}

    for card_id, card_data in analytics_data.get('cards', {}).items():
        try:
            coords = compute_card_coordinates(card_data)
            result[card_id] = coords
        except Exception as e:
            # Skip cards with invalid data
            print(f"Warning: Could not compute coordinates for {card_id}: {e}")
            continue

    return result
