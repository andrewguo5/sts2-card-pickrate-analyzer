#!/usr/bin/env python3
"""
Optimize kernel bandwidth for card pick rate smoothing.

Provides several methods to evaluate and select optimal bandwidth:
1. Cross-validation: Leave-one-out prediction error
2. Visual comparison: Plot different bandwidths side-by-side
3. Bias-variance tradeoff: Analyze smoothness vs. fidelity to data
4. AIC/BIC: Information criteria for model selection
"""

import json
import glob
import argparse
from collections import defaultdict
import math


def load_raw_data(character, ascension_level, game_version=None):
    """
    Load raw pick rate data (not smoothed).
    Returns: card_id -> floor -> {"offered": count, "picked": count}
    """
    from card_pickrate_analysis import CardPickRateAnalyzer

    analyzer = CardPickRateAnalyzer(
        character=character,
        ascension_level=ascension_level,
        game_version=game_version,
        kernel_bandwidth=0  # Not used for raw data
    )
    analyzer.process_runs()

    return analyzer.raw_data, analyzer.runs_processed


def apply_smoothing_with_bandwidth(raw_data, bandwidth):
    """
    Apply kernel smoothing with a specific bandwidth.
    Returns: card_id -> floor -> smoothed_rate
    """
    smoothed = defaultdict(dict)

    for card_id, floor_data in raw_data.items():
        # Calculate raw rates first
        raw_rates = {}
        for floor, counts in floor_data.items():
            if counts["offered"] > 0:
                raw_rates[floor] = counts["picked"] / counts["offered"]

        if not raw_rates:
            continue

        floors = sorted(raw_rates.keys())
        min_floor = min(floors)
        max_floor = max(floors)

        # Apply smoothing for each floor
        for floor in floors:
            # Determine window
            lower_bound = max(min_floor, floor - bandwidth)
            upper_bound = min(max_floor, floor + bandwidth)

            # Adjust to maintain bandwidth at boundaries
            total_bandwidth = 2 * bandwidth + 1
            current_range = upper_bound - lower_bound + 1

            if current_range < total_bandwidth:
                if floor - bandwidth < min_floor:
                    upper_bound = min(max_floor, lower_bound + total_bandwidth - 1)
                elif floor + bandwidth > max_floor:
                    lower_bound = max(min_floor, upper_bound - total_bandwidth + 1)

            # Collect weighted rates
            window_rates = []
            window_weights = []

            for f in range(lower_bound, upper_bound + 1):
                if f in raw_rates:
                    window_rates.append(raw_rates[f])
                    weight = raw_data[card_id][f]["offered"]
                    window_weights.append(weight)

            # Calculate weighted average
            if window_rates and sum(window_weights) > 0:
                weighted_sum = sum(r * w for r, w in zip(window_rates, window_weights))
                total_weight = sum(window_weights)
                smoothed[card_id][floor] = weighted_sum / total_weight
            else:
                smoothed[card_id][floor] = 0.0

    return smoothed


def cross_validation_score(raw_data, bandwidth):
    """
    Leave-one-out cross-validation.
    For each observation, predict it using smoothing of all other observations.
    Returns mean squared prediction error.
    """
    total_error = 0.0
    total_observations = 0

    for card_id, floor_data in raw_data.items():
        floors = sorted(floor_data.keys())

        if len(floors) < 3:  # Need minimum data
            continue

        for test_floor in floors:
            # Leave out this floor
            train_data = {card_id: {f: counts for f, counts in floor_data.items() if f != test_floor}}

            # Apply smoothing on training data
            smoothed = apply_smoothing_with_bandwidth(train_data, bandwidth)

            # Get prediction
            if card_id in smoothed and test_floor in smoothed[card_id]:
                predicted = smoothed[card_id][test_floor]
            else:
                # If we can't predict, use global mean
                all_offered = sum(c["offered"] for c in floor_data.values())
                all_picked = sum(c["picked"] for c in floor_data.values())
                predicted = all_picked / all_offered if all_offered > 0 else 0.5

            # Get actual
            actual = (floor_data[test_floor]["picked"] / floor_data[test_floor]["offered"]
                     if floor_data[test_floor]["offered"] > 0 else 0.0)

            # Squared error weighted by number of offers
            weight = floor_data[test_floor]["offered"]
            error = (predicted - actual) ** 2
            total_error += error * weight
            total_observations += weight

    return total_error / total_observations if total_observations > 0 else float('inf')


def calculate_roughness(smoothed_rates):
    """
    Calculate roughness penalty: sum of squared second derivatives.
    Measures how "wiggly" the smoothed curve is.
    """
    total_roughness = 0.0

    for card_id, floor_rates in smoothed_rates.items():
        floors = sorted(floor_rates.keys())

        if len(floors) < 3:
            continue

        # Calculate second derivatives
        for i in range(1, len(floors) - 1):
            f_prev = floors[i-1]
            f_curr = floors[i]
            f_next = floors[i+1]

            # Second derivative approximation
            second_deriv = (floor_rates[f_next] - 2*floor_rates[f_curr] + floor_rates[f_prev])
            total_roughness += second_deriv ** 2

    return total_roughness


def calculate_bias_variance(raw_data, bandwidth):
    """
    Estimate bias and variance components.

    Bias: How far smoothed values are from raw values (underfitting)
    Variance: How much smoothed values vary (overfitting)
    """
    smoothed = apply_smoothing_with_bandwidth(raw_data, bandwidth)

    total_bias_sq = 0.0
    total_variance = 0.0
    n_points = 0

    for card_id, floor_data in raw_data.items():
        floors = sorted(floor_data.keys())

        if len(floors) < 3:
            continue

        raw_rates = []
        smoothed_vals = []
        weights = []

        for floor in floors:
            if floor_data[floor]["offered"] > 0:
                raw_rate = floor_data[floor]["picked"] / floor_data[floor]["offered"]
                smooth_rate = smoothed[card_id].get(floor, raw_rate)

                raw_rates.append(raw_rate)
                smoothed_vals.append(smooth_rate)
                weights.append(floor_data[floor]["offered"])

        if not raw_rates:
            continue

        # Bias: difference between smoothed and raw (weighted)
        for raw, smooth, weight in zip(raw_rates, smoothed_vals, weights):
            bias = smooth - raw
            total_bias_sq += (bias ** 2) * weight

        # Variance: how much smoothed values vary
        if len(smoothed_vals) > 1:
            mean_smooth = sum(s * w for s, w in zip(smoothed_vals, weights)) / sum(weights)
            for smooth, weight in zip(smoothed_vals, weights):
                variance = (smooth - mean_smooth) ** 2
                total_variance += variance * weight

        n_points += sum(weights)

    avg_bias_sq = total_bias_sq / n_points if n_points > 0 else 0.0
    avg_variance = total_variance / n_points if n_points > 0 else 0.0

    return avg_bias_sq, avg_variance


def evaluate_bandwidth_range(raw_data, min_b=0, max_b=10):
    """
    Evaluate multiple bandwidth values and return metrics.
    """
    results = []

    print("\nEvaluating bandwidth values from {} to {}...".format(min_b, max_b))
    print("-" * 80)
    print(f"{'b':>3} {'CV Error':>12} {'Roughness':>12} {'Bias²':>12} {'Variance':>12} {'Total':>12}")
    print("-" * 80)

    for b in range(min_b, max_b + 1):
        # Cross-validation error
        cv_error = cross_validation_score(raw_data, b)

        # Smoothed results
        smoothed = apply_smoothing_with_bandwidth(raw_data, b)

        # Roughness
        roughness = calculate_roughness(smoothed)

        # Bias-variance
        bias_sq, variance = calculate_bias_variance(raw_data, b)

        # Total error (CV error is already MSE, so it combines bias and variance)
        total = cv_error

        results.append({
            'bandwidth': b,
            'cv_error': cv_error,
            'roughness': roughness,
            'bias_squared': bias_sq,
            'variance': variance,
            'total_error': total
        })

        print(f"{b:>3} {cv_error:>12.6f} {roughness:>12.6f} {bias_sq:>12.6f} "
              f"{variance:>12.6f} {total:>12.6f}")

    print("-" * 80)

    # Find optimal bandwidth
    best_by_cv = min(results, key=lambda x: x['cv_error'])

    print(f"\nOptimal bandwidth by cross-validation: b = {best_by_cv['bandwidth']}")
    print(f"  CV Error: {best_by_cv['cv_error']:.6f}")

    return results


def visual_comparison(raw_data, card_id, bandwidths=[0, 1, 2, 3, 5]):
    """
    Show visual comparison of different bandwidths for a specific card.
    """
    if card_id not in raw_data:
        print(f"Card {card_id} not found in data")
        return

    card_name = card_id.replace("CARD.", "")
    floor_data = raw_data[card_id]
    floors = sorted(floor_data.keys())

    print("\n" + "=" * 80)
    print(f"BANDWIDTH COMPARISON: {card_name}")
    print("=" * 80)

    # Calculate raw rates
    raw_rates = {}
    for floor in floors:
        if floor_data[floor]["offered"] > 0:
            raw_rates[floor] = floor_data[floor]["picked"] / floor_data[floor]["offered"]

    # Header
    print(f"\n{'Floor':>6} {'Offered':>8} {'Raw':>8}", end="")
    for b in bandwidths:
        print(f" b={b:>2}", end="")
    print()
    print("-" * (30 + 8 * len(bandwidths)))

    # Apply smoothing for each bandwidth
    smoothed_by_b = {}
    for b in bandwidths:
        smoothed_by_b[b] = apply_smoothing_with_bandwidth(raw_data, b)

    # Print table
    for floor in floors:
        offered = floor_data[floor]["offered"]
        raw = raw_rates.get(floor, 0.0)

        print(f"{floor:>6} {offered:>8} {raw:>7.1%}", end="")

        for b in bandwidths:
            smoothed_val = smoothed_by_b[b].get(card_id, {}).get(floor, 0.0)
            print(f" {smoothed_val:>6.1%}", end="")

        print()

    print("-" * (30 + 8 * len(bandwidths)))


def main():
    parser = argparse.ArgumentParser(description='Optimize kernel bandwidth')
    parser.add_argument('--character', default='CHARACTER.REGENT',
                       help='Character to analyze')
    parser.add_argument('--ascension', default='A10',
                       help='Ascension level')
    parser.add_argument('--version', default=None,
                       help='Game version filter')
    parser.add_argument('--min-b', type=int, default=0,
                       help='Minimum bandwidth to test (default: 0)')
    parser.add_argument('--max-b', type=int, default=10,
                       help='Maximum bandwidth to test (default: 10)')
    parser.add_argument('--card', default=None,
                       help='Show visual comparison for specific card')

    args = parser.parse_args()

    print("=" * 80)
    print("KERNEL BANDWIDTH OPTIMIZATION")
    print("=" * 80)
    print(f"Character:       {args.character}")
    print(f"Ascension:       {args.ascension}")
    print(f"Game Version:    {args.version or 'All'}")
    print("=" * 80)

    # Load raw data
    print("\nLoading run data...")
    raw_data, runs_processed = load_raw_data(args.character, args.ascension, args.version)
    print(f"Processed {runs_processed} runs")
    print(f"Found {len(raw_data)} unique cards")

    # Evaluate bandwidth range
    results = evaluate_bandwidth_range(raw_data, args.min_b, args.max_b)

    # Visual comparison if requested
    if args.card:
        card_id = args.card if args.card.startswith("CARD.") else f"CARD.{args.card}"
        visual_comparison(raw_data, card_id, bandwidths=[0, 1, 2, 3, 5, 7])
    else:
        # Show comparison for highest-sample card
        max_offers = 0
        max_card = None
        for card_id, floor_data in raw_data.items():
            total_offers = sum(counts["offered"] for counts in floor_data.values())
            if total_offers > max_offers:
                max_offers = total_offers
                max_card = card_id

        if max_card:
            visual_comparison(raw_data, max_card, bandwidths=[0, 1, 2, 3, 5, 7])


if __name__ == "__main__":
    main()
