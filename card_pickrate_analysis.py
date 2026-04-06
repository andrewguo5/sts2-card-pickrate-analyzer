#!/usr/bin/env python3
"""
Card Pick Rate Analysis for Slay the Spire 2

Analyzes card pick rates by floor for a specific character, ascension level,
and game version. Applies kernel smoothing to handle low sample sizes.

Methodology:
1. Filter runs by character, ascension, singleplayer, and version
2. Extract all card_choices from map_point_history
3. Calculate raw pick rates per floor (picked / offered)
4. Apply kernel smoothing with configurable bandwidth
5. Output raw and smoothed pick rates
"""

import json
import glob
from collections import defaultdict
from pathlib import Path
import argparse


class CardPickRateAnalyzer:
    def __init__(self, character, ascension_level, game_version=None, kernel_bandwidth=2):
        """
        Initialize the analyzer.

        Args:
            character: Character ID (e.g., "CHARACTER.REGENT")
            ascension_level: Either an int (0-10) or "A10" for just A10, "A0-9" for A0-A9
            game_version: Optional game version filter (e.g., "v0.99.1")
            kernel_bandwidth: Bandwidth for kernel smoothing (default: 2)
        """
        self.character = character
        self.ascension_level = ascension_level
        self.game_version = game_version
        self.kernel_bandwidth = kernel_bandwidth

        # Data structures to store pick rates
        # Format: card_id -> floor -> {"offered": count, "picked": count}
        self.raw_data = defaultdict(lambda: defaultdict(lambda: {"offered": 0, "picked": 0}))

        # Processed pick rates
        # Format: card_id -> floor -> pick_rate (0.0 to 1.0)
        self.raw_pickrates = defaultdict(dict)
        self.smoothed_pickrates = defaultdict(dict)

        self.runs_processed = 0

    def parse_ascension_filter(self):
        """Parse ascension level filter."""
        if isinstance(self.ascension_level, int):
            return [self.ascension_level]
        elif self.ascension_level == "A10":
            return [10]
        elif self.ascension_level == "A0-9":
            return list(range(0, 10))
        else:
            raise ValueError(f"Invalid ascension level: {self.ascension_level}")

    def filter_run(self, run_data):
        """Check if a run matches our filters."""
        # Check singleplayer
        if len(run_data.get('players', [])) != 1:
            return False

        # Check character
        player_char = run_data['players'][0].get('character', '')
        if player_char != self.character:
            return False

        # Check ascension
        run_ascension = run_data.get('ascension', 0)
        valid_ascensions = self.parse_ascension_filter()
        if run_ascension not in valid_ascensions:
            return False

        # Check version if specified
        if self.game_version:
            run_version = run_data.get('build_id', '')
            if run_version != self.game_version:
                return False

        return True

    def extract_card_choices(self, run_data):
        """Extract all card choices from a run's map_point_history."""
        map_history = run_data.get('map_point_history', [])

        for act_idx, act_points in enumerate(map_history):
            for point_idx, point in enumerate(act_points):
                player_stats = point.get('player_stats', [])

                if not player_stats:
                    continue

                # Get player 1 stats (singleplayer)
                stats = player_stats[0]
                card_choices = stats.get('card_choices', [])

                for choice in card_choices:
                    card_info = choice.get('card', {})
                    card_id = card_info.get('id', '')
                    was_picked = choice.get('was_picked', False)

                    # Get floor number - use floor_added_to_deck if available
                    floor = card_info.get('floor_added_to_deck')

                    # If not available, estimate from position in map history
                    if floor is None:
                        # Count up to current position to get floor estimate
                        floor = sum(len(act) for act in map_history[:act_idx]) + point_idx + 1

                    if card_id:
                        self.raw_data[card_id][floor]["offered"] += 1
                        if was_picked:
                            self.raw_data[card_id][floor]["picked"] += 1

    def process_runs(self, data_dir="run_history_data"):
        """Process all run files matching our filters."""
        run_files = glob.glob(f"{data_dir}/**/*.run", recursive=True)

        for run_file in run_files:
            try:
                with open(run_file, 'r') as f:
                    run_data = json.load(f)

                if self.filter_run(run_data):
                    self.extract_card_choices(run_data)
                    self.runs_processed += 1
            except Exception as e:
                print(f"Error processing {run_file}: {e}")

        print(f"Processed {self.runs_processed} runs matching filters")

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
                # Adjust window at boundaries to maintain bandwidth
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

    def get_summary_stats(self, card_id):
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

    def print_results(self, min_offers=5, top_n=20):
        """Print analysis results."""
        print("\n" + "=" * 80)
        print(f"CARD PICK RATE ANALYSIS")
        print("=" * 80)
        print(f"Character:       {self.character}")
        print(f"Ascension:       {self.ascension_level}")
        print(f"Game Version:    {self.game_version or 'All'}")
        print(f"Kernel Bandwidth: {self.kernel_bandwidth}")
        print(f"Runs Processed:  {self.runs_processed}")
        print("=" * 80)

        # Get cards sorted by total offers
        card_stats = []
        for card_id in self.raw_data.keys():
            stats = self.get_summary_stats(card_id)
            if stats and stats["total_offered"] >= min_offers:
                card_stats.append(stats)

        card_stats.sort(key=lambda x: x["overall_pickrate"], reverse=True)

        print(f"\nTop {top_n} Cards by Overall Pick Rate (min {min_offers} offers):")
        print("-" * 80)
        print(f"{'Card ID':<40} {'Offered':>8} {'Picked':>8} {'Pick Rate':>10}")
        print("-" * 80)

        for stats in card_stats[:top_n]:
            card_name = stats["card_id"].replace("CARD.", "")
            print(f"{card_name:<40} {stats['total_offered']:>8} {stats['total_picked']:>8} "
                  f"{stats['overall_pickrate']:>9.1%}")

    def export_to_json(self, output_file):
        """Export results to JSON for visualization."""
        output = {
            "metadata": {
                "character": self.character,
                "ascension_level": str(self.ascension_level),
                "game_version": self.game_version,
                "kernel_bandwidth": self.kernel_bandwidth,
                "runs_processed": self.runs_processed
            },
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

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\nResults exported to: {output_file}")

    def run_analysis(self, export_file=None):
        """Run the complete analysis pipeline."""
        print("Starting card pick rate analysis...")

        self.process_runs()
        self.calculate_raw_pickrates()
        self.apply_kernel_smoothing()
        self.print_results()

        if export_file:
            self.export_to_json(export_file)


def main():
    parser = argparse.ArgumentParser(description='Analyze card pick rates')
    parser.add_argument('--character', default='CHARACTER.REGENT',
                       help='Character to analyze (default: CHARACTER.REGENT)')
    parser.add_argument('--ascension', default='A10',
                       help='Ascension level: A10, A0-9, or specific number (default: A10)')
    parser.add_argument('--version', default=None,
                       help='Game version filter (e.g., v0.99.1)')
    parser.add_argument('--bandwidth', type=int, default=2,
                       help='Kernel smoothing bandwidth (default: 2)')
    parser.add_argument('--output', default='card_pickrates.json',
                       help='Output JSON file (default: card_pickrates.json)')
    parser.add_argument('--min-offers', type=int, default=5,
                       help='Minimum offers to display (default: 5)')

    args = parser.parse_args()

    analyzer = CardPickRateAnalyzer(
        character=args.character,
        ascension_level=args.ascension,
        game_version=args.version,
        kernel_bandwidth=args.bandwidth
    )

    analyzer.run_analysis(export_file=args.output)


if __name__ == "__main__":
    main()
