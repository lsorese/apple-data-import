#!/usr/bin/env python3
"""
Link Ashnikko Smoochies album to the December 25th Strava run
"""

import json
from datetime import datetime

DATA_JSON_PATH = "apple-music-watch-viewer/src/data.json"

def main():
    print("Linking Ashnikko album to Strava run...")

    # Load data
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    albums = data.get('watch_albums', [])

    # Find the Ashnikko Smoochies album
    for album in albums:
        if album.get('album_name') == 'Smoochies' and album.get('artist_name') == 'Ashnikko':
            print(f"\nFound album: {album['album_name']} by {album['artist_name']}")

            # Add the Strava activity info
            album['strava_activity_id'] = 16830927461
            album['strava_activity_name'] = 'First run with new exercise buddy.'
            album['strava_activity_type'] = 'Run'
            album['strava_start_date'] = '2025-12-24T15:30:18Z'

            # Keep the data you provided (which is slightly different from Strava's)
            # Your data: 3.35 mi, 38:22 (2302s), 11:27/mi, 100ft
            # Strava API: 3.34 mi, 38:15 (2295s)
            # We'll use your more accurate data
            album['strava_distance_miles'] = 3.35
            album['strava_distance_meters'] = 5391.8  # 3.35 mi in meters
            album['strava_moving_time_seconds'] = 2302
            album['strava_elapsed_time_seconds'] = 2683  # 44:43
            album['strava_pace_per_mile'] = '11:27'
            album['strava_elevation_gain_meters'] = 30.48

            print(f"\nLinked to Strava activity:")
            print(f"  Activity ID: {album['strava_activity_id']}")
            print(f"  Activity name: {album['strava_activity_name']}")
            print(f"  Distance: {album['strava_distance_miles']} mi")
            print(f"  Time: {album['strava_moving_time_seconds']}s (38:22)")
            print(f"  Pace: {album['strava_pace_per_mile']}/mi")

            break
    else:
        print("Could not find Smoochies by Ashnikko")
        return

    # Update statistics
    albums_with_strava = sum(1 for a in albums if 'strava_activity_id' in a)
    data['statistics']['albums_with_strava_data'] = albums_with_strava
    data['statistics']['albums_without_strava_data'] = len(albums) - albums_with_strava

    # Update timestamp
    data['generated_at'] = datetime.now().isoformat()

    # Save
    with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Updated and saved to {DATA_JSON_PATH}")


if __name__ == '__main__':
    main()
