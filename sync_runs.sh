#!/bin/bash
# Sync run history files from the game's save directory to the working directory

GAME_SAVE_DIR="$HOME/Library/Application Support/SlayTheSpire2/steam/76561198032986989"
WORKING_DIR="$(cd "$(dirname "$0")" && pwd)/run_history_data"

echo "Syncing run history files..."
echo "From: $GAME_SAVE_DIR"
echo "To:   $WORKING_DIR"
echo ""

# Sync profile1
if [ -d "$GAME_SAVE_DIR/profile1/saves/history" ]; then
    echo "Syncing profile1..."
    rsync -av "$GAME_SAVE_DIR/profile1/saves/history/" "$WORKING_DIR/profile1/"
else
    echo "Warning: profile1 not found"
fi

# Sync profile2
if [ -d "$GAME_SAVE_DIR/profile2/saves/history" ]; then
    echo "Syncing profile2..."
    rsync -av "$GAME_SAVE_DIR/profile2/saves/history/" "$WORKING_DIR/profile2/"
else
    echo "Warning: profile2 not found"
fi

# Sync profile3
if [ -d "$GAME_SAVE_DIR/profile3/saves/history" ]; then
    echo "Syncing profile3..."
    rsync -av "$GAME_SAVE_DIR/profile3/saves/history/" "$WORKING_DIR/profile3/"
else
    echo "Note: profile3 not found (this is normal if you don't use it)"
fi

echo ""
echo "Sync complete!"
echo ""
echo "Total runs:"
find "$WORKING_DIR" -name "*.run" | wc -l
