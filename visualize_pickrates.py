#!/usr/bin/env python3
"""
Visualize card pick rates by floor.

Creates text-based and optional matplotlib charts showing how pick rates
vary across floors for specific cards.
"""

import json
import argparse
from pathlib import Path


def load_pickrate_data(json_file):
    """Load pick rate analysis results from JSON."""
    with open(json_file, 'r') as f:
        return json.load(f)


def print_card_pickrate_chart(card_id, card_data, width=60):
    """
    Print a text-based chart of pick rates by floor.

    Shows both raw and smoothed pick rates.
    """
    card_name = card_id.replace("CARD.", "")
    summary = card_data["summary"]
    raw_rates = card_data["raw_pickrates"]
    smoothed_rates = card_data["smoothed_pickrates"]
    raw_data = card_data["raw_data"]

    print("\n" + "=" * 80)
    print(f"CARD: {card_name}")
    print("=" * 80)
    print(f"Total Offered:    {summary['total_offered']}")
    print(f"Total Picked:     {summary['total_picked']}")
    print(f"Overall Pick Rate: {summary['overall_pickrate']:.1%}")
    print(f"Floors Seen:      {summary['floors_seen']}")
    print(f"Floor Range:      {summary['floor_range'][0]} - {summary['floor_range'][1]}")
    print("=" * 80)

    # Get floor data
    floors = sorted([int(f) for f in raw_rates.keys()])

    if not floors:
        print("No data available")
        return

    # Print detailed table
    print(f"\n{'Floor':>6} {'Offered':>8} {'Picked':>7} {'Raw Rate':>10} {'Smoothed':>10} {'Chart':>20}")
    print("-" * 80)

    for floor in floors:
        floor_str = str(floor)
        offered = raw_data[floor_str]["offered"]
        picked = raw_data[floor_str]["picked"]
        raw_rate = raw_rates[floor_str]
        smoothed_rate = smoothed_rates[floor_str]

        # Create mini bar chart
        bar_length = int(smoothed_rate * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)

        print(f"{floor:>6} {offered:>8} {picked:>7} {raw_rate:>9.1%} {smoothed_rate:>9.1%} {bar}")

    # Create ASCII chart for smoothed rates
    print("\nSmoothed Pick Rate by Floor:")
    print("-" * 80)

    max_rate = max(smoothed_rates.values()) if smoothed_rates else 1.0
    chart_height = 15

    # Create chart grid
    for row in range(chart_height, -1, -1):
        threshold = (row / chart_height) * max_rate

        # Y-axis label
        if row == chart_height:
            print(f"{max_rate:>5.1%} |", end="")
        elif row == 0:
            print(f"{'0%':>5} |", end="")
        elif row == chart_height // 2:
            print(f"{max_rate/2:>5.1%} |", end="")
        else:
            print("      |", end="")

        # Plot points
        for floor in floors:
            floor_str = str(floor)
            rate = smoothed_rates[floor_str]

            if rate >= threshold and rate < threshold + (max_rate / chart_height):
                print("█", end="")
            elif rate >= threshold:
                print("█", end="")
            else:
                print(" ", end="")

        print()

    # X-axis
    print("      +" + "-" * len(floors))
    print("       ", end="")
    for i, floor in enumerate(floors):
        if i % 5 == 0:
            print(str(floor % 10), end="")
        else:
            print(" ", end="")
    print()
    print(f"       Floor")


def print_top_cards_comparison(data, top_n=10, min_offers=5):
    """
    Print a comparison of top cards with their overall pick rates
    and pick rate trends.
    """
    print("\n" + "=" * 80)
    print(f"TOP {top_n} CARDS COMPARISON")
    print("=" * 80)

    # Get cards sorted by overall pick rate
    cards_with_stats = []
    for card_id, card_data in data["cards"].items():
        summary = card_data["summary"]
        if summary["total_offered"] >= min_offers:
            cards_with_stats.append((card_id, card_data))

    cards_with_stats.sort(key=lambda x: x[1]["summary"]["overall_pickrate"], reverse=True)

    print(f"\n{'Card':<30} {'Overall':>8} {'Early':>8} {'Mid':>8} {'Late':>8} {'Trend':>10}")
    print("-" * 80)

    for card_id, card_data in cards_with_stats[:top_n]:
        card_name = card_id.replace("CARD.", "")[:28]
        summary = card_data["summary"]
        smoothed = card_data["smoothed_pickrates"]

        overall_rate = summary["overall_pickrate"]

        # Calculate early/mid/late rates
        floors = sorted([int(f) for f in smoothed.keys()])
        if len(floors) >= 3:
            early_floors = floors[:len(floors)//3]
            mid_floors = floors[len(floors)//3:2*len(floors)//3]
            late_floors = floors[2*len(floors)//3:]

            early_rate = sum(smoothed[str(f)] for f in early_floors) / len(early_floors)
            mid_rate = sum(smoothed[str(f)] for f in mid_floors) / len(mid_floors)
            late_rate = sum(smoothed[str(f)] for f in late_floors) / len(late_floors)

            # Determine trend
            if late_rate > early_rate * 1.2:
                trend = "↗ Rising"
            elif late_rate < early_rate * 0.8:
                trend = "↘ Falling"
            else:
                trend = "→ Stable"
        else:
            early_rate = mid_rate = late_rate = overall_rate
            trend = "- N/A"

        print(f"{card_name:<30} {overall_rate:>7.1%} {early_rate:>7.1%} "
              f"{mid_rate:>7.1%} {late_rate:>7.1%} {trend:>10}")


def main():
    parser = argparse.ArgumentParser(description='Visualize card pick rates')
    parser.add_argument('--input', default='card_pickrates.json',
                       help='Input JSON file (default: card_pickrates.json)')
    parser.add_argument('--card', default=None,
                       help='Specific card to visualize (e.g., CARD.GLOW)')
    parser.add_argument('--top', type=int, default=10,
                       help='Number of top cards to compare (default: 10)')
    parser.add_argument('--min-offers', type=int, default=5,
                       help='Minimum offers to display (default: 5)')

    args = parser.parse_args()

    # Load data
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found")
        print("Run card_pickrate_analysis.py first to generate the data")
        return

    data = load_pickrate_data(args.input)

    # Print metadata
    print("=" * 80)
    print("CARD PICK RATE VISUALIZATION")
    print("=" * 80)
    print(f"Character:       {data['metadata']['character']}")
    print(f"Ascension:       {data['metadata']['ascension_level']}")
    print(f"Game Version:    {data['metadata']['game_version'] or 'All'}")
    print(f"Runs Processed:  {data['metadata']['runs_processed']}")
    print("=" * 80)

    # Show comparison
    print_top_cards_comparison(data, top_n=args.top, min_offers=args.min_offers)

    # Show specific card if requested
    if args.card:
        card_id = args.card if args.card.startswith("CARD.") else f"CARD.{args.card}"
        if card_id in data["cards"]:
            print_card_pickrate_chart(card_id, data["cards"][card_id])
        else:
            print(f"\nError: Card '{card_id}' not found in data")
            print("Available cards:", ", ".join([c.replace("CARD.", "")
                                                for c in list(data["cards"].keys())[:10]]))
    else:
        # Show top 3 cards by default
        cards_with_stats = []
        for card_id, card_data in data["cards"].items():
            if card_data["summary"]["total_offered"] >= args.min_offers:
                cards_with_stats.append((card_id, card_data))

        cards_with_stats.sort(key=lambda x: x[1]["summary"]["overall_pickrate"], reverse=True)

        for card_id, card_data in cards_with_stats[:3]:
            print_card_pickrate_chart(card_id, card_data)


if __name__ == "__main__":
    main()
