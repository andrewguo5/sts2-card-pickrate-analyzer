#!/bin/bash
# Start the Card Pick Rate Visualization web app

echo "Starting Card Pick Rate Visualization Server..."
echo "========================================"
echo ""
echo "Server will start at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "Make sure you have run card_pickrate_analysis.py first!"
echo ""

cd pickrate-viz
python3 -m http.server 8000
