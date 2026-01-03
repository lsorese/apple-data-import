#!/usr/bin/env python3
"""
Merge data_maybe.json into data.json

Takes the potential album matches from data_maybe.json and adds them to the main data.json file.
Updates statistics and preserves existing data.
"""

import json
from datetime import datetime

DATA_JSON_PATH = "apple-music-watch-viewer/src/data.json"
MAYBE_JSON_PATH = "apple-music-watch-viewer/src/data_maybe.json"
BACKUP_PATH = "apple-music-watch-viewer/src/data_backup.json"

def main():
    print("=" * 70)
    print("Merging data_maybe.json into data.json")
    print("=" * 70)

    # Load existing data
    print(f"\nLoading existing data from {DATA_JSON_PATH}...")
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_albums = data.get('watch_albums', [])
    existing_completed = data.get('completed_watch_albums', [])
    print(f"  Current albums: {len(existing_albums)}")
    print(f"  Current completed albums: {len(existing_completed)}")

    # Create backup
    print(f"\nCreating backup at {BACKUP_PATH}...")
    with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("  ✓ Backup created")

    # Load maybe data
    print(f"\nLoading potential albums from {MAYBE_JSON_PATH}...")
    with open(MAYBE_JSON_PATH, 'r', encoding='utf-8') as f:
        maybe_data = json.load(f)

    maybe_albums = maybe_data.get('maybe_albums', [])
    print(f"  Found {len(maybe_albums)} potential albums to add")

    # Track what we're adding
    added_count = 0
    skipped_count = 0

    # Build a set of existing album names for quick lookup
    existing_album_names = {album['album_name'] for album in existing_albums}

    print("\nProcessing potential albums...")
    for maybe_album in maybe_albums:
        album_name = maybe_album['album_name']

        # Check if album already exists
        if album_name in existing_album_names:
            print(f"  ⊘ Skipping '{album_name}' (already exists)")
            skipped_count += 1

            # Update existing album with strava data if it doesn't have it
            for existing_album in existing_albums:
                if existing_album['album_name'] == album_name:
                    # If existing album doesn't have strava data, add it
                    if 'strava_activity_id' not in existing_album:
                        # Copy strava fields
                        for key in ['strava_activity_id', 'strava_activity_name', 'strava_start_date',
                                  'strava_distance_miles', 'strava_moving_time_seconds']:
                            if key in maybe_album:
                                existing_album[key] = maybe_album[key]
                        print(f"    → Added Strava data to existing album")
                    break
            continue

        # Prepare album for adding
        # Remove 'confidence' field and calculate completion_percentage if needed
        album_to_add = maybe_album.copy()
        album_to_add.pop('confidence', None)

        # Calculate completion percentage (unique_tracks / play_count ratio isn't perfect,
        # but we'll use unique_tracks as listened_tracks and estimate total_tracks)
        # For simplicity, we'll set completion based on play patterns
        unique_tracks = album_to_add.pop('unique_tracks', 1)

        # Set total_tracks = listened_tracks for these albums
        # (we don't have perfect data from the CSV search)
        album_to_add['total_tracks'] = unique_tracks
        album_to_add['listened_tracks'] = unique_tracks
        album_to_add['completion_percentage'] = 100.0  # Assume complete since we found significant plays

        # Add starred field
        album_to_add['starred'] = False

        print(f"  ✓ Adding '{album_name}' by {album_to_add.get('artist_name', 'Unknown')}")
        print(f"    {album_to_add['play_count']} plays, {unique_tracks} tracks")
        print(f"    Run: {album_to_add.get('strava_activity_name', '')} on {album_to_add.get('strava_start_date', '')}")

        existing_albums.append(album_to_add)
        added_count += 1

    # Sort albums by play_count descending
    existing_albums.sort(key=lambda x: -x.get('play_count', 0))

    # Update statistics
    albums_with_strava = sum(1 for a in existing_albums if 'strava_activity_id' in a)
    albums_with_artist = sum(1 for a in existing_albums if a.get('artist_name'))
    albums_with_genre = sum(1 for a in existing_albums if a.get('genre'))

    data['watch_albums'] = existing_albums
    data['generated_at'] = datetime.now().isoformat()
    data['statistics']['watch_albums'] = len(existing_albums)
    data['statistics']['albums_with_strava_data'] = albums_with_strava
    data['statistics']['albums_without_strava_data'] = len(existing_albums) - albums_with_strava
    data['statistics']['albums_with_artist_info'] = albums_with_artist
    data['statistics']['albums_without_artist_info'] = len(existing_albums) - albums_with_artist
    data['statistics']['albums_with_genre_data'] = albums_with_genre
    data['statistics']['albums_without_genre_data'] = len(existing_albums) - albums_with_genre

    # Save updated data
    print(f"\nSaving updated data to {DATA_JSON_PATH}...")
    with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("✓ MERGE COMPLETE!")
    print("=" * 70)
    print(f"  Albums added: {added_count}")
    print(f"  Albums skipped (duplicates): {skipped_count}")
    print(f"  Total albums: {len(existing_albums)}")
    print(f"  Total completed albums: {len(completed_albums)}")
    print(f"  Albums with Strava data: {albums_with_strava}")
    print(f"\n  Backup saved to: {BACKUP_PATH}")
    print(f"  Updated data saved to: {DATA_JSON_PATH}")


if __name__ == '__main__':
    main()
