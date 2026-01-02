#!/bin/bash

# Quick start script for Apple Music Play Activity Analyzer

echo "🎵 Apple Music Play Activity Analyzer"
echo "======================================"
echo ""

# Check if CSV file exists
if [ ! -f "Apple Music Play Activity.csv" ]; then
    echo "❌ Error: 'Apple Music Play Activity.csv' not found"
    echo "   Please ensure the file is in the current directory"
    exit 1
fi

# Check if data needs to be generated
if [ ! -f "outputs/data.json" ]; then
    echo "📊 Running analysis for the first time..."
    echo ""
    python3 analyze_music.py

    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Analysis failed"
        exit 1
    fi
    echo ""
fi

# Start the web server
echo "🚀 Starting web server..."
echo ""
python3 serve.py
