#!/usr/bin/env python3
"""
Examine the detailed structure of a Slay the Spire 2 run file.
This helps understand what data is available for analytics.
"""

import json
import glob
from pathlib import Path


def print_json_structure(obj, indent=0, max_depth=4, max_items=3):
    """
    Print the structure of a JSON object in a readable format.
    Shows types and a few sample values for lists.
    """
    prefix = "  " * indent

    if isinstance(obj, dict):
        print(f"{prefix}{{")
        for i, (key, value) in enumerate(obj.items()):
            if i >= max_items and len(obj) > max_items:
                print(f"{prefix}  ... ({len(obj) - max_items} more keys)")
                break
            print(f"{prefix}  {key}: ", end="")
            if indent < max_depth:
                print_json_structure(value, indent + 1, max_depth, max_items)
            else:
                print(f"{type(value).__name__}")
        print(f"{prefix}}}")

    elif isinstance(obj, list):
        if not obj:
            print(f"[] (empty)")
        else:
            print(f"[{len(obj)} items]")
            if indent < max_depth:
                for i, item in enumerate(obj[:max_items]):
                    print(f"{prefix}  [{i}]: ", end="")
                    print_json_structure(item, indent + 1, max_depth, max_items)
                if len(obj) > max_items:
                    print(f"{prefix}  ... ({len(obj) - max_items} more items)")
            else:
                print(f"{prefix}  (type: {type(obj[0]).__name__})")

    elif isinstance(obj, str):
        if len(obj) > 50:
            print(f'"{obj[:50]}..." (str, len={len(obj)})')
        else:
            print(f'"{obj}" (str)')

    elif isinstance(obj, (int, float, bool)) or obj is None:
        print(f"{obj} ({type(obj).__name__})")

    else:
        print(f"{type(obj).__name__}")


def examine_run_file(filename):
    """Load and display the structure of a run file."""

    with open(filename, 'r') as f:
        data = json.load(f)

    print("=" * 80)
    print(f"EXAMINING: {Path(filename).name}")
    print("=" * 80)

    # Print top-level keys
    print("\nTOP-LEVEL KEYS:")
    print("-" * 80)
    for key in sorted(data.keys()):
        value = data[key]
        value_type = type(value).__name__
        if isinstance(value, list):
            print(f"  {key:30} : list[{len(value)}]")
        elif isinstance(value, dict):
            print(f"  {key:30} : dict with {len(value)} keys")
        else:
            print(f"  {key:30} : {value_type} = {value}")

    # Print full structure (limited depth)
    print("\n\nFULL STRUCTURE:")
    print("-" * 80)
    print_json_structure(data, max_depth=3, max_items=2)

    # Print some specific useful info
    print("\n\n" + "=" * 80)
    print("KEY BUCKETING FIELDS:")
    print("=" * 80)
    print(f"Character:     {data.get('players', [{}])[0].get('character', 'N/A')}")
    print(f"Ascension:     {data.get('ascension', 'N/A')}")
    print(f"Game Version:  {data.get('build_id', 'N/A')}")
    print(f"Game Mode:     {data.get('game_mode', 'N/A')}")
    print(f"Win:           {data.get('win', 'N/A')}")
    print(f"Abandoned:     {data.get('was_abandoned', 'N/A')}")
    print(f"Platform:      {data.get('platform_type', 'N/A')}")
    print(f"Seed:          {data.get('seed', 'N/A')}")
    print(f"Run Time:      {data.get('run_time', 'N/A')} seconds")
    print(f"Acts:          {', '.join(data.get('acts', []))}")

    if data.get('killed_by_encounter', 'NONE.NONE') != 'NONE.NONE':
        print(f"Killed By:     {data.get('killed_by_encounter', 'N/A')}")
    if data.get('killed_by_event', 'NONE.NONE') != 'NONE.NONE':
        print(f"Killed By Event: {data.get('killed_by_event', 'N/A')}")

    # Player info
    print("\n" + "=" * 80)
    print("PLAYER INFO:")
    print("=" * 80)
    for i, player in enumerate(data.get('players', [])):
        print(f"\nPlayer {i + 1}:")
        print(f"  Character: {player.get('character', 'N/A')}")
        print(f"  Deck Size: {len(player.get('deck', []))}")
        print(f"  Relics:    {len(player.get('relics', []))}")
        print(f"  Potions:   {len(player.get('potions', []))}")

    # Map point history summary
    print("\n" + "=" * 80)
    print("MAP POINT HISTORY:")
    print("=" * 80)
    map_history = data.get('map_point_history', [])
    print(f"Total Acts: {len(map_history)}")
    for act_num, act_points in enumerate(map_history, 1):
        print(f"  Act {act_num}: {len(act_points)} map points")

        # Count room types
        room_types = {}
        for point in act_points:
            point_type = point.get('map_point_type', 'unknown')
            room_types[point_type] = room_types.get(point_type, 0) + 1

        print(f"    Room types: {dict(room_types)}")


if __name__ == "__main__":
    # Find a recent run file
    run_files = sorted(glob.glob("run_history_data/**/*.run", recursive=True))

    if not run_files:
        print("No run files found in run_history_data/")
    else:
        # Examine the most recent file
        print(f"Found {len(run_files)} run files total\n")
        examine_run_file(run_files[-1])
