"""
Analytics computation engine.

Refactored from card_pickrate_analysis.py to work with database data instead of files.
"""
from collections import defaultdict
from typing import List, Dict, Any, Optional
from compression import decompress_run_data
from card_metadata import get_card_metadata


class CardPickRateAnalyzer:
    """
    Analyze card pick rates from a list of run data.
    """

    def __init__(self, runs: List[Dict[str, Any]], kernel_bandwidth: int = 2, character_filter: Optional[str] = None):
        """
        Initialize the analyzer.

        Args:
            runs: List of run data dictionaries (from database)
            kernel_bandwidth: Bandwidth for kernel smoothing (default: 2)
            character_filter: Optional character filter (e.g., "CHARACTER.REGENT") to exclude cross-class cards
        """
        self.runs = runs
        self.kernel_bandwidth = kernel_bandwidth
        self.character_filter = character_filter

        # Extract character color for filtering (CHARACTER.REGENT -> regent)
        self.character_color = None
        if character_filter:
            # Extract character name from CHARACTER.X format
            if character_filter.startswith("CHARACTER."):
                self.character_color = character_filter.replace("CHARACTER.", "").lower()

        # Data structures to store pick rates
        # Format: card_id -> floor -> {"offered": count, "picked": count}
        self.raw_data = defaultdict(lambda: defaultdict(lambda: {"offered": 0, "picked": 0}))

        # Data structures for skip rates (excludes shops)
        # Format: card_id -> floor -> {"offered": count, "skipped": count}
        self.skip_data = defaultdict(lambda: defaultdict(lambda: {"offered": 0, "skipped": 0}))

        # Baseline skip rate (overall skip rate per floor, regardless of which cards offered)
        # Format: floor -> {"total_offers": count, "total_skips": count}
        self.baseline_skip_data = defaultdict(lambda: {"total_offers": 0, "total_skips": 0})

        # Win rate data by act
        # Format: card_id -> act -> {"picked": count, "won": count}
        self.winrate_data = defaultdict(lambda: defaultdict(lambda: {"picked": 0, "won": 0}))

        # Processed pick rates
        # Format: card_id -> floor -> pick_rate (0.0 to 1.0)
        self.raw_pickrates = defaultdict(dict)
        self.smoothed_pickrates = defaultdict(dict)

        # Processed skip rates
        # Format: card_id -> floor -> skip_rate (0.0 to 1.0)
        self.raw_skiprates = defaultdict(dict)
        self.smoothed_skiprates = defaultdict(dict)

        # Baseline skip rates (smoothed)
        # Format: floor -> skip_rate (0.0 to 1.0)
        self.baseline_skiprates = {}
        self.smoothed_baseline_skiprates = {}

        # Processed win rates
        # Format: card_id -> act -> win_rate (0.0 to 1.0)
        self.winrates_by_act = defaultdict(dict)

        self.runs_processed = 0

    def extract_card_choices(self, run_data: Dict[str, Any]):
        """
        Extract all card choices from a run's map_point_history.

        Also tracks skip rates (excluding shops) and win rates by act.
        """
        map_history = run_data.get('map_point_history', [])
        victory = run_data.get('win', False)

        # Track which cards were picked in each act of this run (to avoid double-counting wins)
        # Format: {card_id: set of acts where it was picked}
        cards_picked_per_act_this_run = defaultdict(set)

        for act_idx, act_points in enumerate(map_history):
            act_number = act_idx + 1  # Acts are 1-indexed

            for point_idx, point in enumerate(act_points):
                # Check if this is a shop (exclude from pick/skip rate analysis)
                room_type = point.get('room_type', '')
                is_shop = room_type == 'shop'

                player_stats = point.get('player_stats', [])
                if not player_stats:
                    continue

                # Get player 1 stats
                stats = player_stats[0]
                card_choices = stats.get('card_choices', [])

                if not card_choices:
                    continue

                # Calculate floor number
                floor = sum(len(act) for act in map_history[:act_idx]) + point_idx + 1

                # Check if all cards in this offer were skipped
                all_skipped = all(not choice.get('was_picked', False) for choice in card_choices)

                # Track baseline skip data (exclude shops)
                if not is_shop:
                    self.baseline_skip_data[floor]["total_offers"] += 1
                    if all_skipped:
                        self.baseline_skip_data[floor]["total_skips"] += 1

                # Process each card in the offer
                for choice in card_choices:
                    card_info = choice.get('card', {})
                    card_id = card_info.get('id', '')
                    was_picked = choice.get('was_picked', False)

                    if not card_id:
                        continue

                    # Filter out cross-class cards if character filter is enabled
                    if self.character_color:
                        metadata = get_card_metadata(card_id)
                        if metadata and metadata.get('color') != self.character_color:
                            continue

                    # Track pick rate data (exclude shops)
                    if not is_shop:
                        self.raw_data[card_id][floor]["offered"] += 1
                        if was_picked:
                            self.raw_data[card_id][floor]["picked"] += 1

                        # Track skip rate data
                        self.skip_data[card_id][floor]["offered"] += 1
                        if all_skipped:
                            self.skip_data[card_id][floor]["skipped"] += 1

                    # Track when cards are picked (for win rate calculation later)
                    if was_picked:
                        cards_picked_per_act_this_run[card_id].add(act_number)

        # After processing all acts in this run, update win rate data
        # Only count each (card, act) combination once per run
        for card_id, acts in cards_picked_per_act_this_run.items():
            for act_number in acts:
                self.winrate_data[card_id][act_number]["picked"] += 1
                if victory:
                    self.winrate_data[card_id][act_number]["won"] += 1

    def process_runs(self):
        """Process all runs to extract card choices."""
        for run_data in self.runs:
            self.extract_card_choices(run_data)
            self.runs_processed += 1

    def calculate_raw_pickrates(self):
        """Calculate raw pick rates from the collected data."""
        for card_id, floor_data in self.raw_data.items():
            for floor, counts in floor_data.items():
                offered = counts["offered"]
                picked = counts["picked"]

                if offered > 0:
                    self.raw_pickrates[card_id][floor] = picked / offered
                else:
                    self.raw_pickrates[card_id][floor] = 0.0

    def calculate_raw_skiprates(self):
        """Calculate raw skip rates from the collected data."""
        for card_id, floor_data in self.skip_data.items():
            for floor, counts in floor_data.items():
                offered = counts["offered"]
                skipped = counts["skipped"]

                if offered > 0:
                    self.raw_skiprates[card_id][floor] = skipped / offered
                else:
                    self.raw_skiprates[card_id][floor] = 0.0

        # Calculate baseline skip rates
        for floor, counts in self.baseline_skip_data.items():
            total_offers = counts["total_offers"]
            total_skips = counts["total_skips"]

            if total_offers > 0:
                self.baseline_skiprates[floor] = total_skips / total_offers
            else:
                self.baseline_skiprates[floor] = 0.0

    def calculate_winrates(self):
        """Calculate win rates by act."""
        for card_id, act_data in self.winrate_data.items():
            for act, counts in act_data.items():
                picked = counts["picked"]
                won = counts["won"]

                if picked > 0:
                    self.winrates_by_act[card_id][act] = won / picked
                else:
                    self.winrates_by_act[card_id][act] = 0.0

    def apply_kernel_smoothing(self):
        """Apply kernel smoothing to pick rates and skip rates."""
        b = self.kernel_bandwidth

        # Smooth pick rates
        for card_id, floor_rates in self.raw_pickrates.items():
            if not floor_rates:
                continue

            floors = sorted(floor_rates.keys())
            min_floor = min(floors)
            max_floor = max(floors)

            # Apply smoothing for each floor
            for floor in floors:
                # Determine the window for smoothing
                lower_bound = max(min_floor, floor - b)
                upper_bound = min(max_floor, floor + b)

                # Adjust if we're at boundaries to maintain 2*b + 1 total bandwidth
                total_bandwidth = 2 * b + 1
                current_range = upper_bound - lower_bound + 1

                if current_range < total_bandwidth:
                    if floor - b < min_floor:
                        # At lower boundary, extend upper
                        upper_bound = min(max_floor, lower_bound + total_bandwidth - 1)
                    elif floor + b > max_floor:
                        # At upper boundary, extend lower
                        lower_bound = max(min_floor, upper_bound - total_bandwidth + 1)

                # Collect pick rates in the window
                window_rates = []
                window_weights = []  # Weight by number of offers

                for f in range(lower_bound, upper_bound + 1):
                    if f in floor_rates:
                        window_rates.append(floor_rates[f])
                        # Weight by number of times offered
                        weight = self.raw_data[card_id][f]["offered"]
                        window_weights.append(weight)

                # Calculate weighted average
                if window_rates and sum(window_weights) > 0:
                    weighted_sum = sum(r * w for r, w in zip(window_rates, window_weights))
                    total_weight = sum(window_weights)
                    self.smoothed_pickrates[card_id][floor] = weighted_sum / total_weight
                else:
                    self.smoothed_pickrates[card_id][floor] = 0.0

        # Smooth skip rates
        for card_id, floor_rates in self.raw_skiprates.items():
            if not floor_rates:
                continue

            floors = sorted(floor_rates.keys())
            min_floor = min(floors)
            max_floor = max(floors)

            for floor in floors:
                lower_bound = max(min_floor, floor - b)
                upper_bound = min(max_floor, floor + b)

                total_bandwidth = 2 * b + 1
                current_range = upper_bound - lower_bound + 1

                if current_range < total_bandwidth:
                    if floor - b < min_floor:
                        upper_bound = min(max_floor, lower_bound + total_bandwidth - 1)
                    elif floor + b > max_floor:
                        lower_bound = max(min_floor, upper_bound - total_bandwidth + 1)

                window_rates = []
                window_weights = []

                for f in range(lower_bound, upper_bound + 1):
                    if f in floor_rates:
                        window_rates.append(floor_rates[f])
                        weight = self.skip_data[card_id][f]["offered"]
                        window_weights.append(weight)

                if window_rates and sum(window_weights) > 0:
                    weighted_sum = sum(r * w for r, w in zip(window_rates, window_weights))
                    total_weight = sum(window_weights)
                    self.smoothed_skiprates[card_id][floor] = weighted_sum / total_weight
                else:
                    self.smoothed_skiprates[card_id][floor] = 0.0

        # Smooth baseline skip rates
        if self.baseline_skiprates:
            floors = sorted(self.baseline_skiprates.keys())
            min_floor = min(floors)
            max_floor = max(floors)

            for floor in floors:
                lower_bound = max(min_floor, floor - b)
                upper_bound = min(max_floor, floor + b)

                total_bandwidth = 2 * b + 1
                current_range = upper_bound - lower_bound + 1

                if current_range < total_bandwidth:
                    if floor - b < min_floor:
                        upper_bound = min(max_floor, lower_bound + total_bandwidth - 1)
                    elif floor + b > max_floor:
                        lower_bound = max(min_floor, upper_bound - total_bandwidth + 1)

                window_rates = []
                window_weights = []

                for f in range(lower_bound, upper_bound + 1):
                    if f in self.baseline_skiprates:
                        window_rates.append(self.baseline_skiprates[f])
                        weight = self.baseline_skip_data[f]["total_offers"]
                        window_weights.append(weight)

                if window_rates and sum(window_weights) > 0:
                    weighted_sum = sum(r * w for r, w in zip(window_rates, window_weights))
                    total_weight = sum(window_weights)
                    self.smoothed_baseline_skiprates[floor] = weighted_sum / total_weight
                else:
                    self.smoothed_baseline_skiprates[floor] = 0.0

    def get_summary_stats(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get summary statistics for a specific card."""
        if card_id not in self.raw_data:
            return None

        total_offered = sum(counts["offered"] for counts in self.raw_data[card_id].values())
        total_picked = sum(counts["picked"] for counts in self.raw_data[card_id].values())
        overall_pickrate = total_picked / total_offered if total_offered > 0 else 0.0

        floors = sorted(self.raw_pickrates.get(card_id, {}).keys())

        return {
            "card_id": card_id,
            "total_offered": total_offered,
            "total_picked": total_picked,
            "overall_pickrate": overall_pickrate,
            "floors_seen": len(floors),
            "floor_range": (min(floors), max(floors)) if floors else (0, 0)
        }

    def export_to_dict(self) -> Dict[str, Any]:
        """Export results to dictionary format (compatible with JSON output)."""
        output = {
            "cards": {},
            "baseline_skip_data": {
                "raw": dict(self.baseline_skiprates),
                "smoothed": dict(self.smoothed_baseline_skiprates)
            }
        }

        for card_id in self.raw_data.keys():
            stats = self.get_summary_stats(card_id)
            if stats:
                output["cards"][card_id] = {
                    "summary": stats,
                    "raw_pickrates": dict(self.raw_pickrates.get(card_id, {})),
                    "smoothed_pickrates": dict(self.smoothed_pickrates.get(card_id, {})),
                    "raw_skiprates": dict(self.raw_skiprates.get(card_id, {})),
                    "smoothed_skiprates": dict(self.smoothed_skiprates.get(card_id, {})),
                    "winrates_by_act": dict(self.winrates_by_act.get(card_id, {})),
                    "raw_data": {
                        str(floor): counts
                        for floor, counts in self.raw_data[card_id].items()
                    },
                    "skip_data": {
                        str(floor): counts
                        for floor, counts in self.skip_data.get(card_id, {}).items()
                    },
                    "winrate_data": {
                        str(act): counts
                        for act, counts in self.winrate_data.get(card_id, {}).items()
                    }
                }

        return output

    def run_analysis(self) -> Dict[str, Any]:
        """Run the complete analysis pipeline and return results."""
        self.process_runs()
        self.calculate_raw_pickrates()
        self.calculate_raw_skiprates()
        self.calculate_winrates()
        self.apply_kernel_smoothing()
        return self.export_to_dict()


def compute_pickrates(runs: List[Dict[str, Any]], bandwidth: int = 2, character: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to compute pick rates from a list of runs.

    Args:
        runs: List of run data dictionaries
        bandwidth: Kernel smoothing bandwidth
        character: Optional character filter (e.g., "CHARACTER.REGENT") to exclude cross-class cards

    Returns:
        Dictionary with card pick rate data
    """
    analyzer = CardPickRateAnalyzer(runs, kernel_bandwidth=bandwidth, character_filter=character)
    return analyzer.run_analysis()
