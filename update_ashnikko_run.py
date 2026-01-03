#!/usr/bin/env python3
"""
Update Ashnikko album with correct Strava data from December 25th run
"""

import json
from datetime import datetime

DATA_JSON_PATH = "apple-music-watch-viewer/src/data.json"

def main():
    print("Updating Ashnikko album with correct Strava data...")

    # Load data
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    albums = data.get('watch_albums', [])

    # Find the Ashnikko Smoochies album (the one around Dec 25-31)
    for album in albums:
        if album.get('album_name') == 'Smoochies' and album.get('artist_name') == 'Ashnikko':
            print(f"\nFound album: {album['album_name']} by {album['artist_name']}")
            print(f"Current first listen: {album.get('first_listen', 'N/A')}")

            # Update with the December 25th run data you provided
            # Converting the data you gave:
            # 3.35 mi, 38:22 (2302 seconds), pace 11:27/mi, elevation 100ft (30.48m)

            album['strava_distance_miles'] = 3.35
            album['strava_moving_time_seconds'] = 2302  # 38:22 = 38*60 + 22
            album['strava_pace_per_mile'] = '11:27'
            album['strava_elevation_gain_meters'] = 30.48  # 100 ft

            # You mentioned it's December 25th, not 31st
            # Update the first_listen to December 25th if needed
            # Keeping the time component from original
            if album.get('first_listen', '').startswith('2025-12-31'):
                album['first_listen'] = album['first_listen'].replace('2025-12-31', '2025-12-25')
                album['last_listen'] = album.get('last_listen', '').replace('2025-12-31', '2025-12-25') if album.get('last_listen') else album['first_listen']

            print(f"\nUpdated data:")
            print(f"  Distance: {album['strava_distance_miles']} mi")
            print(f"  Time: {album['strava_moving_time_seconds']} seconds (38:22)")
            print(f"  Pace: {album['strava_pace_per_mile']}/mi")
            print(f"  Elevation: {album['strava_elevation_gain_meters']}m (100ft)")
            print(f"  First listen: {album['first_listen']}")

            break
    else:
        print("Could not find Smoochies by Ashnikko")
        return

    # Update timestamp
    data['generated_at'] = datetime.now().isoformat()

    # Save
    with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Updated and saved to {DATA_JSON_PATH}")


if __name__ == '__main__':
    main()
