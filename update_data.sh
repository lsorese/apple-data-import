#!/bin/bash
# Update Apple Music Watch data and deploy

set -e

echo "🎵 Apple Music Watch Data Updater"
echo "=================================="
echo ""

# Check for required CSV files
if [ ! -f "Apple Music Play Activity.csv" ]; then
    echo "❌ Error: Apple Music Play Activity.csv not found"
    exit 1
fi

if [ ! -f "Apple Music - Container Details.csv" ]; then
    echo "❌ Error: Apple Music - Container Details.csv not found"
    exit 1
fi

# Run analyzer
echo "📊 Step 1: Analyzing Apple Watch play activity..."
python3 analyze_music_watch.py

if [ $? -ne 0 ]; then
    echo "❌ Analysis failed"
    exit 1
fi

echo ""
echo "✅ Analysis complete!"
echo ""

# Ask if user wants to fetch artists
read -p "🔍 Fetch missing artists from Apple API? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "⏳ Fetching artists (this may take a while and might be rate-limited)..."
    python3 fetch_artists.py

    if [ $? -eq 0 ]; then
        echo ""
        echo "🔄 Re-running analysis with new artist data..."
        python3 analyze_music_watch.py
    fi
fi

echo ""
echo "✅ Data update complete!"
echo ""
echo "📁 Updated file: apple-music-watch-viewer/public/data.json"
echo ""
echo "Next steps:"
echo "  1. Test locally: cd apple-music-watch-viewer && python3 -m http.server 8000 --directory public"
echo "  2. Commit changes: cd apple-music-watch-viewer && git add . && git commit -m 'Update data'"
echo "  3. Deploy: git push (Vercel auto-deploys) or run 'vercel --prod'"
echo ""
