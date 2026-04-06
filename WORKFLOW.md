# Complete Workflow Guide

This guide walks you through the complete process from game data to interactive visualization.

## Quick Start

```bash
# 1. Sync run data from the game
./sync_runs.sh

# 2. Generate pick rate analysis
python3 card_pickrate_analysis.py --character CHARACTER.REGENT --ascension A10

# 3. Start the web visualization
./start_viz.sh

# 4. Open your browser to: http://localhost:8000
```

That's it! You now have an interactive card pick rate analyzer.

---

## Detailed Workflow

### Step 1: Sync Run History Data

After playing games, copy the latest run files from the game's save directory:

```bash
./sync_runs.sh
```

This script copies `.run` files from:
- `~/Library/Application Support/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/`

To:
- `run_history_data/profile*/`

### Step 2: Generate Pick Rate Analysis

Run the analysis script with your desired parameters:

```bash
python3 card_pickrate_analysis.py \
    --character CHARACTER.REGENT \
    --ascension A10 \
    --bandwidth 2 \
    --output card_pickrates.json
```

**Parameters:**
- `--character`: Which character to analyze
  - `CHARACTER.REGENT`
  - `CHARACTER.IRONCLAD`
  - `CHARACTER.SILENT`
  - `CHARACTER.NECROBINDER`
  - `CHARACTER.DEFECT`

- `--ascension`: Which ascension levels to include
  - `A10` - Only Ascension 10
  - `A0-9` - Ascensions 0 through 9
  - `0`, `1`, `2`, ... - Specific ascension level

- `--bandwidth`: Kernel smoothing parameter (default: 2)
  - Lower = less smoothing (more noisy)
  - Higher = more smoothing (less noisy)
  - Recommended: 2

- `--version`: Optional game version filter
  - `v0.99.1`
  - `v0.102.0`
  - etc.

- `--output`: Output JSON file (default: card_pickrates.json)

The script will:
1. Filter runs matching your criteria
2. Extract all card choices from map_point_history
3. Calculate raw pick rates per floor
4. Apply kernel smoothing
5. Export results to JSON

### Step 3: Launch Web Visualization

```bash
./start_viz.sh
```

Or manually:
```bash
cd pickrate-viz
python3 -m http.server 8000
```

Then open: **http://localhost:8000**

### Step 4: Interact with the Visualization

**Features:**
- **Search**: Type in the search box to filter cards
- **Select Card**: Click any card in the left sidebar
- **View Chart**: See smoothed (blue area) and raw (purple dashed) pick rates
- **Hover**: Mouse over chart for exact values
- **Data Table**: Scroll down for floor-by-floor breakdown

---

## Common Use Cases

### Analyze Different Characters

```bash
# Ironclad A10
python3 card_pickrate_analysis.py --character CHARACTER.IRONCLAD --ascension A10

# Necrobinder A0-9
python3 card_pickrate_analysis.py --character CHARACTER.NECROBINDER --ascension A0-9
```

### Compare Different Smoothing

```bash
# Less smoothing (more detail, more noise)
python3 card_pickrate_analysis.py --character CHARACTER.REGENT --ascension A10 --bandwidth 1

# More smoothing (less detail, less noise)
python3 card_pickrate_analysis.py --character CHARACTER.REGENT --ascension A10 --bandwidth 4
```

### Filter by Game Version

```bash
# Only latest version
python3 card_pickrate_analysis.py \
    --character CHARACTER.REGENT \
    --ascension A10 \
    --version v0.102.0
```

---

## Other Useful Scripts

### Basic Statistics

```bash
# Get overview of all runs
python3 analyze_runs.py
```

Shows:
- Character distribution
- Ascension levels
- Game versions
- Win/loss rates
- Character+Ascension win rates

### Examine Run Structure

```bash
# Look at detailed structure of run files
python3 examine_run_structure.py
```

Shows:
- Top-level fields
- Key bucketing fields
- Player info
- Map point history

### Text-Based Visualization

```bash
# View pick rates in terminal
python3 visualize_pickrates.py

# View specific card
python3 visualize_pickrates.py --card GLOW

# Show top N cards
python3 visualize_pickrates.py --top 20
```

### Optimize Bandwidth

```bash
# Evaluate different bandwidth values
python3 optimize_bandwidth.py --min-b 0 --max-b 8

# Compare bandwidth for specific card
python3 optimize_bandwidth.py --card BEGONE
```

---

## File Organization

```
Spire.mbgg/
├── run_history_data/           # Run files from game
│   ├── profile1/
│   └── profile2/
│
├── pickrate-viz/               # Web visualization
│   ├── index.html              # React app
│   ├── card_pickrates.json     # Generated data
│   └── README.md
│
├── card_pickrate_analysis.py   # Main analysis script
├── visualize_pickrates.py      # Terminal visualization
├── analyze_runs.py             # Basic statistics
├── examine_run_structure.py    # Data structure explorer
├── optimize_bandwidth.py       # Bandwidth optimization
│
├── sync_runs.sh                # Sync from game
├── start_viz.sh                # Launch web server
│
├── README.md                   # Project overview
├── WORKFLOW.md                 # This file
└── bandwidth_recommendations.md # Bandwidth selection guide
```

---

## Tips & Tricks

### Refreshing Data

After playing new games:
1. Run `./sync_runs.sh` to get new run files
2. Re-run `card_pickrate_analysis.py` to regenerate JSON
3. Refresh your browser (Cmd+R or Ctrl+R)

### Multiple Analyses

You can create multiple JSON files for different analyses:

```bash
# Regent A10
python3 card_pickrate_analysis.py \
    --character CHARACTER.REGENT \
    --ascension A10 \
    --output regent_a10.json

# Ironclad A0-9
python3 card_pickrate_analysis.py \
    --character CHARACTER.IRONCLAD \
    --ascension A0-9 \
    --output ironclad_a09.json
```

Then swap the JSON file in `pickrate-viz/` directory.

### Low Sample Size

If you see warnings about low sample size:
- Play more games!
- Use broader filters (e.g., A0-9 instead of A10)
- Increase bandwidth for more smoothing
- Focus on commonly offered cards

### Performance

The web app loads the entire JSON in memory. If you have thousands of runs:
- Consider filtering to recent game versions only
- Split analysis by character
- The app should still be fast with 100+ runs per character

---

## Next Steps

Ideas for future enhancements:
- Win rate correlation (cards that lead to wins)
- Deck archetypes (cluster common card combinations)
- Relic analysis (pick rates for relics)
- Floor-by-floor deck evolution
- Comparison between ascension levels
- Multi-character comparison view
