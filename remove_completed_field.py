#!/usr/bin/env python3
"""
Remove completed_watch_albums field from data.json
"""

import json
from datetime import datetime

DATA_JSON_PATH = "apple-music-watch-viewer/src/data.json"

def main():
    print("Removing completed_watch_albums field from data.json...")

    # Load existing data
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Remove completed_watch_albums field
    if 'completed_watch_albums' in data:
        del data['completed_watch_albums']
        print("  ✓ Removed completed_watch_albums field")

    # Also remove from statistics if present
    if 'statistics' in data:
        stats = data['statistics']
        if 'completed_watch_albums' in stats:
            del stats['completed_watch_albums']
            print("  ✓ Removed completed_watch_albums from statistics")

    # Update generated_at timestamp
    data['generated_at'] = datetime.now().isoformat()

    # Save updated data
    with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Updated data saved to {DATA_JSON_PATH}")


if __name__ == '__main__':
    main()
