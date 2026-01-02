#!/bin/bash

# Apple Music Play Activity Analyzer
# Run this script to regenerate the analysis

echo "🎵 Apple Music Play Activity Analyzer"
echo "======================================"
echo ""

# Check if CSV file exists
if [ ! -f "Apple Music Play Activity.csv" ]; then
    echo "❌ Error: 'Apple Music Play Activity.csv' not found"
    echo "   Please ensure the file is in the current directory"
    exit 1
fi

# Run the analyzer
echo "Running analysis..."
echo ""
python3 analyze_music.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Analysis complete!"
    echo ""
    echo "📊 View results:"
    echo "   Open outputs/index.html in your browser"
    echo ""
    echo "💾 Raw data:"
    echo "   outputs/data.json"
else
    echo ""
    echo "❌ Analysis failed"
    exit 1
fi
