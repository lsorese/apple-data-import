#!/usr/bin/env python3
"""
Remove heart rate data from data.json
"""

import json
from datetime import datetime

DATA_JSON_PATH = "apple-music-watch-viewer/src/data.json"

def main():
    print("Removing heart rate data from data.json...")

    # Load existing data
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Remove heart rate fields from all albums
    removed_count = 0
    for album in data.get('watch_albums', []):
        if 'strava_average_heartrate' in album:
            del album['strava_average_heartrate']
            removed_count += 1
        if 'strava_max_heartrate' in album:
            del album['strava_max_heartrate']
        if 'strava_has_heartrate' in album:
            del album['strava_has_heartrate']

    # Also remove from completed albums
    for album in data.get('completed_watch_albums', []):
        if 'strava_average_heartrate' in album:
            del album['strava_average_heartrate']
        if 'strava_max_heartrate' in album:
            del album['strava_max_heartrate']
        if 'strava_has_heartrate' in album:
            del album['strava_has_heartrate']

    # Update generated_at timestamp
    data['generated_at'] = datetime.now().isoformat()

    # Save updated data
    with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Removed heart rate data from {removed_count} albums")
    print(f"✓ Updated data saved to {DATA_JSON_PATH}")


if __name__ == '__main__':
    main()
