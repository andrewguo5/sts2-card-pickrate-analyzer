# Slay the Spire 2 Analytics Project

This project performs data analytics on Slay the Spire 2 run histories and displays them for users.

## Project Overview

The project has three main components:
1. **Run History Retrieval** - Retrieve run histories and store them in a run history database
2. **Data Analytics** - Perform analytics by reading from the run history database and store results in an analytics database
3. **Data Rendering** - Render analytics from the database on a simple webpage

## Future Architecture

Eventually this will scale to a server-based architecture:
- Users can upload their data to a central server
- UserIds will be used as primary keys in the run history DB
- Whitelisted users only (for manageable scale and security)
- Parts 1 and 2 will run on the server
- Part 3 will render analytics on a webpage

## Current Status: Local Development

### Completed
- ✅ Analyzed STS2 decompiled code to understand run history storage
- ✅ Located run history files on local machine
- ✅ Copied run history data to working subdirectory
- ✅ Analyzed run history data format and structure
- ✅ Identified key bucketing fields

### Run History Location

Run histories are stored at:
```
~/Library/Application Support/SlayTheSpire2/steam/{STEAM_ID}/profile{N}/saves/history/*.run
```

Each `.run` file is a JSON file with detailed information about a single run.

### Key Bucketing Fields

Based on the analysis, the primary fields for bucketing data are:

1. **Character** (`players[0].character`)
   - `CHARACTER.IRONCLAD`
   - `CHARACTER.SILENT`
   - `CHARACTER.REGENT`
   - `CHARACTER.NECROBINDER`
   - `CHARACTER.DEFECT`

2. **Ascension Level** (`ascension`)
   - Integer from 0 to 10

3. **Game Version** (`build_id`)
   - Examples: `v0.99.1`, `v0.98.3`, `v0.102.0`
   - Can differentiate between Public Release and Beta versions

Additional useful fields:
- `game_mode` - "standard", etc.
- `win` - boolean
- `was_abandoned` - boolean
- `platform_type` - "steam", etc.
- `run_time` - total seconds
- `seed` - run seed
- `start_time` - Unix timestamp
- `acts` - list of acts played
- `killed_by_encounter` - what killed the player
- `map_point_history` - detailed floor-by-floor progression

### Run Data Structure

Each run file contains:
- **Top-level metadata**: ascension, version, win/loss, seed, etc.
- **Player data**: character, final deck, relics, potions
- **Map point history**: Detailed progression through each floor
  - Room types (monster, elite, boss, shop, rest_site, treasure, etc.)
  - Player stats after each room (HP, gold, damage taken, etc.)
  - Card/relic/potion choices made
  - Event choices

### Current Data

In this working directory:
- `run_history_data/` - Copied run histories from local machine
  - `profile1/` - 33 runs
  - `profile2/` - 64 runs
  - **Total: 97 runs**

### Analysis Scripts

Two Python scripts are available for analyzing the data:

1. **`analyze_runs.py`** - Provides high-level statistics
   - Character distribution
   - Ascension level distribution
   - Game version distribution
   - Win/loss statistics
   - Character + Ascension win rates

2. **`examine_run_structure.py`** - Examines detailed structure of run files
   - Shows JSON structure
   - Displays key bucketing fields
   - Shows player info and map progression

Run with:
```bash
python3 analyze_runs.py
python3 examine_run_structure.py
```

## Next Steps

1. **Database Design**
   - Design schema for run history database
   - Design schema for analytics database
   - Consider SQLite for local development, PostgreSQL for production

2. **Run History Ingestion**
   - Create script to parse .run files and insert into database
   - Handle userId bucketing for future multi-user support
   - Create update mechanism to add new runs

3. **Analytics Engine**
   - Define analytics to compute (win rates, popular cards, etc.)
   - Create analytics computation scripts
   - Store results in analytics database

4. **Web Rendering**
   - Choose web framework (Flask/FastAPI for backend, React/Vue for frontend)
   - Design UI/UX for displaying analytics
   - Create visualizations (charts, tables, etc.)

## Data Privacy

All run data is from the local machine. When scaling to a server:
- Implement user authentication
- Use whitelisting for access control
- Ensure data is only accessible to authorized users
