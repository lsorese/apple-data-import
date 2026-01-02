#!/bin/bash
# Import new Apple Music data and regenerate the viewer
#
# Usage: ./import_apple_data.sh
#   This will look for CSV files in the apple-data-import/ folder

set -e

echo "🎵 Apple Music Data Importer"
echo "============================="
echo ""

IMPORT_DIR="apple-data-import"
REQUIRED_FILES=(
    "Apple Music Play Activity.csv"
    "Apple Music - Container Details.csv"
)

# Check if import directory exists
if [ ! -d "$IMPORT_DIR" ]; then
    echo "❌ Error: $IMPORT_DIR directory not found"
    echo ""
    echo "Please create the directory and add your Apple Music CSV files:"
    echo "  mkdir -p $IMPORT_DIR"
    exit 1
fi

# Check for required files in import directory
echo "📋 Checking for required files in $IMPORT_DIR/..."
missing_files=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$IMPORT_DIR/$file" ]; then
        echo "  ✓ Found: $file"
    else
        echo "  ✗ Missing: $file"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo ""
    echo "❌ Missing required files. Please add these to $IMPORT_DIR/:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "💡 Tip: Download your Apple data and copy the CSV files to $IMPORT_DIR/"
    exit 1
fi

echo ""
echo "📥 Copying data files to working directory..."

# Copy files from import directory
for file in "${REQUIRED_FILES[@]}"; do
    cp "$IMPORT_DIR/$file" "./$file"
    echo "  ✓ Copied: $file"
done

echo ""
echo "📊 Analyzing Apple Watch play activity..."
python3 analyze_music_watch.py

if [ $? -ne 0 ]; then
    echo "❌ Analysis failed"
    exit 1
fi

echo ""
echo "✅ Data import complete!"
echo ""
echo "📁 Updated file: apple-music-watch-viewer/public/data.json"
echo ""
echo "🌐 Next steps:"
echo "  • Test locally:"
echo "    cd apple-music-watch-viewer && npm run dev"
echo ""
echo "  • Or view directly:"
echo "    open apple-music-watch-viewer/public/index.html"
echo ""
echo "💡 Optional: Run fetch_artists.py to get missing artist info from Apple API"
echo ""
