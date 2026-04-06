#!/usr/bin/env python3
"""
Analyze Slay the Spire 2 run history data.
This script examines .run files and provides statistics on characters, ascension levels, and versions.
"""

import json
import glob
from collections import Counter, defaultdict
from pathlib import Path


def analyze_run_files(data_dir="run_history_data"):
    """Analyze all run files in the data directory."""

    # Find all run files
    run_files = glob.glob(f"{data_dir}/**/*.run", recursive=True)
    print(f"Total run files found: {len(run_files)}\n")

    if not run_files:
        print(f"No .run files found in {data_dir}")
        return

    # Statistics collectors
    characters = Counter()
    ascensions = Counter()
    versions = Counter()
    game_modes = Counter()
    win_loss = {"wins": 0, "losses": 0, "abandoned": 0}

    # More detailed bucketing
    char_asc_wins = defaultdict(lambda: {"wins": 0, "total": 0})
    char_version = defaultdict(Counter)

    # Process each run file
    for run_file in run_files:
        try:
            with open(run_file, 'r') as f:
                data = json.load(f)

            # Character info is in players list
            character = "UNKNOWN"
            if 'players' in data and len(data['players']) > 0:
                character = data['players'][0].get('character', 'UNKNOWN')
                characters[character] += 1

            # Ascension level
            ascension = data.get('ascension', 0)
            ascensions[ascension] += 1

            # Version (build_id)
            version = data.get('build_id', 'UNKNOWN')
            versions[version] += 1

            # Game mode
            game_mode = data.get('game_mode', 'UNKNOWN')
            game_modes[game_mode] += 1

            # Win/Loss/Abandoned
            if data.get('was_abandoned', False):
                win_loss['abandoned'] += 1
            elif data.get('win', False):
                win_loss['wins'] += 1
            else:
                win_loss['losses'] += 1

            # Character + Ascension bucketing
            key = f"{character}_A{ascension}"
            char_asc_wins[key]["total"] += 1
            if data.get('win', False):
                char_asc_wins[key]["wins"] += 1

            # Character + Version bucketing
            char_version[character][version] += 1

        except Exception as e:
            print(f"Error processing {run_file}: {e}")

    # Print results
    print("=" * 60)
    print("CHARACTER DISTRIBUTION")
    print("=" * 60)
    for char, count in characters.most_common():
        char_name = char.replace("CHARACTER.", "")
        win_rate = sum(1 for k, v in char_asc_wins.items()
                      if k.startswith(char) for _ in range(v["wins"])) / count * 100
        print(f"{char_name:20} {count:3} runs")

    print("\n" + "=" * 60)
    print("ASCENSION LEVELS")
    print("=" * 60)
    for asc in sorted(ascensions.keys()):
        count = ascensions[asc]
        print(f"Ascension {asc:2}: {count:3} runs")

    print("\n" + "=" * 60)
    print("GAME VERSIONS")
    print("=" * 60)
    for ver, count in versions.most_common():
        print(f"{ver:15} {count:3} runs")

    print("\n" + "=" * 60)
    print("GAME MODES")
    print("=" * 60)
    for mode, count in game_modes.most_common():
        print(f"{mode:15} {count:3} runs")

    print("\n" + "=" * 60)
    print("WIN/LOSS STATISTICS")
    print("=" * 60)
    total_completed = win_loss['wins'] + win_loss['losses']
    if total_completed > 0:
        win_rate = win_loss['wins'] / total_completed * 100
        print(f"Wins:      {win_loss['wins']:3} ({win_rate:.1f}%)")
        print(f"Losses:    {win_loss['losses']:3}")
    print(f"Abandoned: {win_loss['abandoned']:3}")
    print(f"Total:     {sum(win_loss.values()):3}")

    print("\n" + "=" * 60)
    print("CHARACTER + ASCENSION WIN RATES (min 2 runs)")
    print("=" * 60)
    for key in sorted(char_asc_wins.keys()):
        stats = char_asc_wins[key]
        if stats["total"] >= 2:  # Only show if at least 2 runs
            win_rate = stats["wins"] / stats["total"] * 100
            char = key.split("_")[0].replace("CHARACTER.", "")
            asc = key.split("_")[1]
            print(f"{char:20} {asc:3} : {stats['wins']:2}/{stats['total']:2} ({win_rate:5.1f}%)")

    return {
        "characters": characters,
        "ascensions": ascensions,
        "versions": versions,
        "game_modes": game_modes,
        "win_loss": win_loss,
        "char_asc_wins": char_asc_wins,
        "char_version": char_version
    }


if __name__ == "__main__":
    analyze_run_files()
