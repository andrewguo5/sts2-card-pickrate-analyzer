"""
Analytics computation engine.

Refactored from card_pickrate_analysis.py to work with database data instead of files.
"""
from collections import defaultdict
from typing import List, Dict, Any, Optional
from compression import decompress_run_data


class CardPickRateAnalyzer:
    """
    Analyze card pick rates from a list of run data.
    """

    def __init__(self, runs: List[Dict[str, Any]], kernel_bandwidth: int = 2):
        """
        Initialize the analyzer.

        Args:
            runs: List of run data dictionaries (from database)
            kernel_bandwidth: Bandwidth for kernel smoothing (default: 2)
        """
        self.runs = runs
        self.kernel_bandwidth = kernel_bandwidth

        # Data structures to store pick rates
        # Format: card_id -> floor -> {"offered": count, "picked": count}
        self.raw_data = defaultdict(lambda: defaultdict(lambda: {"offered": 0, "picked": 0}))

        # Processed pick rates
        # Format: card_id -> floor -> pick_rate (0.0 to 1.0)
        self.raw_pickrates = defaultdict(dict)
        self.smoothed_pickrates = defaultdict(dict)

        self.runs_processed = 0

    def extract_card_choices(self, run_data: Dict[str, Any]):
        """Extract all card choices from a run's map_point_history."""
        map_history = run_data.get('map_point_history', [])

        for act_idx, act_points in enumerate(map_history):
            for point_idx, point in enumerate(act_points):
                player_stats = point.get('player_stats', [])

                if not player_stats:
                    continue

                # Get player 1 stats
                stats = player_stats[0]
                card_choices = stats.get('card_choices', [])

                for choice in card_choices:
                    card_info = choice.get('card', {})
                    card_id = card_info.get('id', '')
                    was_picked = choice.get('was_picked', False)

                    # Get floor number
                    floor = card_info.get('floor_added_to_deck')

                    # If not available, estimate from position
                    if floor is None:
                        floor = sum(len(act) for act in map_history[:act_idx]) + point_idx + 1

                    if card_id:
                        self.raw_data[card_id][floor]["offered"] += 1
                        if was_picked:
                            self.raw_data[card_id][floor]["picked"] += 1

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

    def apply_kernel_smoothing(self):
        """Apply kernel smoothing to pick rates."""
        b = self.kernel_bandwidth

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
            "cards": {}
        }

        for card_id in self.raw_data.keys():
            stats = self.get_summary_stats(card_id)
            if stats:
                output["cards"][card_id] = {
                    "summary": stats,
                    "raw_pickrates": dict(self.raw_pickrates.get(card_id, {})),
                    "smoothed_pickrates": dict(self.smoothed_pickrates.get(card_id, {})),
                    "raw_data": {
                        str(floor): counts
                        for floor, counts in self.raw_data[card_id].items()
                    }
                }

        return output

    def run_analysis(self) -> Dict[str, Any]:
        """Run the complete analysis pipeline and return results."""
        self.process_runs()
        self.calculate_raw_pickrates()
        self.apply_kernel_smoothing()
        return self.export_to_dict()


def compute_pickrates(runs: List[Dict[str, Any]], bandwidth: int = 2) -> Dict[str, Any]:
    """
    Convenience function to compute pick rates from a list of runs.

    Args:
        runs: List of run data dictionaries
        bandwidth: Kernel smoothing bandwidth

    Returns:
        Dictionary with card pick rate data
    """
    analyzer = CardPickRateAnalyzer(runs, kernel_bandwidth=bandwidth)
    return analyzer.run_analysis()
