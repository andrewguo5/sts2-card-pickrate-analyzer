#!/usr/bin/env python3
"""
Generate card pick rate analyses for all characters and buckets.

Creates 30 analysis files (5 characters × 6 buckets):
- Singleplayer A10
- Singleplayer A0-9
- Multiplayer A10
- Multiplayer A0-9
- Singleplayer All Ascensions
- Multiplayer All Ascensions
"""

import subprocess
import os
from pathlib import Path

# Characters to analyze
CHARACTERS = [
    "CHARACTER.IRONCLAD",
    "CHARACTER.SILENT",
    "CHARACTER.REGENT",
    "CHARACTER.NECROBINDER",
    "CHARACTER.DEFECT"
]

# Buckets to generate
BUCKETS = [
    {"name": "singleplayer_a10", "ascension": "A10", "multiplayer": "singleplayer"},
    {"name": "singleplayer_a0-9", "ascension": "A0-9", "multiplayer": "singleplayer"},
    {"name": "multiplayer_a10", "ascension": "A10", "multiplayer": "multiplayer"},
    {"name": "multiplayer_a0-9", "ascension": "A0-9", "multiplayer": "multiplayer"},
    {"name": "singleplayer_all", "ascension": "ALL", "multiplayer": "singleplayer"},
    {"name": "multiplayer_all", "ascension": "ALL", "multiplayer": "multiplayer"},
    {"name": "all", "ascension": "ALL", "multiplayer": "all"},
]

def get_char_shortname(character):
    """Get short name for character."""
    return character.replace("CHARACTER.", "").lower()

def generate_analysis(character, bucket, output_dir="pickrate-viz/data"):
    """Generate a single analysis file."""
    char_short = get_char_shortname(character)
    output_file = f"{output_dir}/{char_short}_{bucket['name']}.json"

    print(f"Generating: {char_short}_{bucket['name']}...")

    cmd = [
        "python3", "card_pickrate_analysis.py",
        "--character", character,
        "--ascension", bucket['ascension'],
        "--multiplayer", bucket['multiplayer'],
        "--bandwidth", "2",
        "--output", output_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✓ Success: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e.stderr}")
        return False

def main():
    print("="*80)
    print("GENERATING ALL CARD PICK RATE ANALYSES")
    print("="*80)
    print(f"Characters: {len(CHARACTERS)}")
    print(f"Buckets: {len(BUCKETS)}")
    print(f"Total analyses: {len(CHARACTERS) * len(BUCKETS)}")
    print("="*80)

    # Create output directory
    output_dir = "pickrate-viz/data"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate all analyses
    total = len(CHARACTERS) * len(BUCKETS)
    success_count = 0
    failed = []

    for i, character in enumerate(CHARACTERS, 1):
        char_short = get_char_shortname(character)
        print(f"\n[{i}/{len(CHARACTERS)}] Processing {char_short.upper()}...")
        print("-"*80)

        for bucket in BUCKETS:
            if generate_analysis(character, bucket, output_dir):
                success_count += 1
            else:
                failed.append(f"{char_short}_{bucket['name']}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total analyses: {total}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed analyses:")
        for f in failed:
            print(f"  - {f}")

    print("\n" + "="*80)
    print("All analyses complete!")
    print(f"Output directory: {output_dir}/")
    print("="*80)

if __name__ == "__main__":
    main()
