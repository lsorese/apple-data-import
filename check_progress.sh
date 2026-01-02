#!/bin/bash
# Check fetch_artists.py progress

PID=$(ps aux | grep "fetch_artists.py" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$PID" ]; then
    echo "❌ fetch_artists.py is not running"
    exit 1
fi

# Get process start time
START_TIME=$(ps -p $PID -o lstart= 2>/dev/null)
if [ -z "$START_TIME" ]; then
    echo "❌ Could not get process info"
    exit 1
fi

# Calculate elapsed seconds
NOW=$(date +%s)
START=$(date -j -f "%a %b %d %H:%M:%S %Y" "$START_TIME" +%s 2>/dev/null)
ELAPSED_SECONDS=$((NOW - START))

# Format elapsed time
HOURS=$((ELAPSED_SECONDS / 3600))
MINS=$(( (ELAPSED_SECONDS % 3600) / 60 ))
SECS=$((ELAPSED_SECONDS % 60))

echo "⏱  Running for: ${HOURS}h ${MINS}m ${SECS}s"

# Estimate progress (5 seconds per request)
REQUESTS=$((ELAPSED_SECONDS / 5))
echo "📊 Estimated requests attempted: ~$REQUESTS / 230"

# Check artist mapping file
ARTIST_COUNT=$(python3 -c "import json; data = json.load(open('artist_mapping.json')); print(len(data['artist_mapping']))" 2>/dev/null)
echo "💾 Artists in cache: $ARTIST_COUNT"
echo ""
echo "ℹ️  Script saves results at the END, so count won't increase until it finishes"
echo "   Expected total time: ~20 minutes (230 albums at 5s each)"
