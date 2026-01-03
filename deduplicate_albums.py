#!/usr/bin/env python3
"""
Remove duplicate albums from data.json

When duplicates are found, merge them by:
- Keeping the entry with more play data
- Preserving starred status if either is starred
- Taking the earliest first_listen and latest last_listen
"""

import json
from datetime import datetime

DATA_JSON_PATH = "apple-music-watch-viewer/src/data.json"

def merge_albums(albums_with_same_name):
    """Merge duplicate album entries intelligently"""
    if len(albums_with_same_name) == 1:
        return albums_with_same_name[0]

    # Sort by play_count descending to get the "main" entry first
    sorted_albums = sorted(albums_with_same_name, key=lambda x: x.get('play_count', 0), reverse=True)
    merged = sorted_albums[0].copy()

    # Merge data from other entries
    for album in sorted_albums[1:]:
        # Preserve starred if any are starred
        if album.get('starred', False):
            merged['starred'] = True

        # Take earliest first_listen
        if album.get('first_listen'):
            current_first = merged.get('first_listen', '')
            if not current_first or album['first_listen'] < current_first:
                merged['first_listen'] = album['first_listen']

        # Take latest last_listen
        if album.get('last_listen'):
            current_last = merged.get('last_listen', '')
            if not current_last or album['last_listen'] > current_last:
                merged['last_listen'] = album['last_listen']

        # Sum play counts (or keep the higher one - your choice)
        # For now, we keep the higher play count (already sorted)
        # But we could also add them:
        # merged['play_count'] = merged.get('play_count', 0) + album.get('play_count', 0)

        # If merged doesn't have strava data but this one does, take it
        if not merged.get('strava_activity_id') and album.get('strava_activity_id'):
            for key in album:
                if key.startswith('strava_'):
                    merged[key] = album[key]

    return merged

def main():
    print("=" * 70)
    print("Deduplicating albums in data.json")
    print("=" * 70)

    # Load data
    print(f"\nLoading {DATA_JSON_PATH}...")
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    albums = data.get('watch_albums', [])
    print(f"  Total albums: {len(albums)}")

    # Group by album name
    album_groups = {}
    for album in albums:
        name = album['album_name']
        if name not in album_groups:
            album_groups[name] = []
        album_groups[name].append(album)

    # Find duplicates
    duplicates = {name: albs for name, albs in album_groups.items() if len(albs) > 1}

    if not duplicates:
        print("\n✓ No duplicates found!")
        return

    print(f"\nFound {len(duplicates)} duplicate album(s):")
    for name, albs in duplicates.items():
        print(f"  - {name} ({len(albs)} entries)")

    # Merge duplicates
    deduplicated_albums = []
    for name, albs in album_groups.items():
        merged = merge_albums(albs)
        deduplicated_albums.append(merged)

    # Sort by play_count
    deduplicated_albums.sort(key=lambda x: -x.get('play_count', 0))

    # Update data
    data['watch_albums'] = deduplicated_albums

    # Update statistics
    albums_with_strava = sum(1 for a in deduplicated_albums if 'strava_activity_id' in a)
    albums_with_artist = sum(1 for a in deduplicated_albums if a.get('artist_name'))
    albums_with_genre = sum(1 for a in deduplicated_albums if a.get('genre'))

    data['generated_at'] = datetime.now().isoformat()
    data['statistics']['watch_albums'] = len(deduplicated_albums)
    data['statistics']['albums_with_strava_data'] = albums_with_strava
    data['statistics']['albums_without_strava_data'] = len(deduplicated_albums) - albums_with_strava
    data['statistics']['albums_with_artist_info'] = albums_with_artist
    data['statistics']['albums_without_artist_info'] = len(deduplicated_albums) - albums_with_artist
    data['statistics']['albums_with_genre_data'] = albums_with_genre
    data['statistics']['albums_without_genre_data'] = len(deduplicated_albums) - albums_with_genre

    # Save
    print(f"\nSaving deduplicated data...")
    with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("✓ DEDUPLICATION COMPLETE!")
    print("=" * 70)
    print(f"  Original albums: {len(albums)}")
    print(f"  Deduplicated albums: {len(deduplicated_albums)}")
    print(f"  Removed: {len(albums) - len(deduplicated_albums)} duplicate(s)")

if __name__ == '__main__':
    main()
