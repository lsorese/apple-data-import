#!/usr/bin/env python3
"""
Fetch missing artist information from Apple Music API

Uses the iTunes Search API to look up artist names for albums
that are missing artist information from Container Details.
"""

import json
import time
import urllib.parse
import urllib.request
from typing import Dict, Optional

# Rate limiting - Apple allows ~20 requests/minute
RATE_LIMIT_DELAY = 5.0  # seconds between requests (12 requests/minute, safely under limit)

def search_apple_music(album_name: str) -> Optional[str]:
    """
    Search Apple Music API for album and return artist name

    Returns artist name if found, None otherwise
    """
    try:
        # Clean up album name for search
        search_term = album_name.strip()

        # URL encode the search term
        encoded_term = urllib.parse.quote(search_term)

        # iTunes Search API endpoint
        url = f"https://itunes.apple.com/search?term={encoded_term}&entity=album&limit=5"

        # Make request
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

            # Check if we got results
            if data.get('resultCount', 0) > 0:
                results = data.get('results', [])

                # Try to find exact or close match
                for result in results:
                    result_album = result.get('collectionName', '')
                    result_artist = result.get('artistName', '')

                    # Check for exact match (case insensitive)
                    if result_album.lower() == album_name.lower():
                        return result_artist

                    # Check for close match (album name in result or vice versa)
                    if (album_name.lower() in result_album.lower() or
                        result_album.lower() in album_name.lower()):
                        return result_artist

                # If no exact match, return first result's artist
                if results:
                    return results[0].get('artistName', '')

        return None

    except Exception as e:
        print(f"  Error searching for '{album_name}': {e}")
        return None

def fetch_missing_artists(data_path: str, output_path: str):
    """
    Load data.json, fetch missing artists, and save updated mapping
    """
    print("Loading existing data...")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Load existing artist mapping if it exists
    existing_mapping = {}
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_mapping = existing_data.get('artist_mapping', {})
            print(f"Loaded {len(existing_mapping)} existing artist mappings")
    except FileNotFoundError:
        print("No existing artist mapping found, starting fresh")

    # Find albums without artist info, excluding ones we already have
    albums_without_artist = [
        album for album in data['watch_albums']
        if not album.get('artist_name') and album['album_name'] not in existing_mapping
    ]

    print(f"\nFound {len(albums_without_artist)} albums without artist information")
    print(f"This will make approximately {len(albums_without_artist)} API requests")
    print(f"Estimated time: ~{len(albums_without_artist) * RATE_LIMIT_DELAY / 60:.1f} minutes")
    print("\nStarting API lookups...\n")

    # Start with existing mapping
    artist_mapping = existing_mapping.copy()
    found_count = 0
    not_found_count = 0

    for i, album in enumerate(albums_without_artist, 1):
        album_name = album['album_name']

        print(f"[{i}/{len(albums_without_artist)}] Searching: {album_name[:50]}...")

        artist = search_apple_music(album_name)

        if artist:
            artist_mapping[album_name] = artist
            found_count += 1
            print(f"  ✓ Found: {artist}")
        else:
            not_found_count += 1
            print(f"  ✗ Not found")

        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)

        # Progress update every 10 items
        if i % 10 == 0:
            print(f"\nProgress: {i}/{len(albums_without_artist)} " +
                  f"(Found: {found_count}, Not found: {not_found_count})\n")

    # Save the mapping
    print(f"\n\nSaving artist mapping to {output_path}...")

    total_in_mapping = len(artist_mapping)
    output_data = {
        'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_searched': len(albums_without_artist),
        'found': found_count,
        'not_found': not_found_count,
        'artist_mapping': artist_mapping
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Complete!")
    print(f"\nResults from this run:")
    print(f"  New artists found: {found_count}/{len(albums_without_artist)} ({found_count/len(albums_without_artist)*100:.1f}% success rate)" if len(albums_without_artist) > 0 else "  No new albums to search")
    print(f"  Not found: {not_found_count}")
    print(f"\nTotal artists in mapping: {total_in_mapping}")
    print(f"\nArtist mapping saved to: {output_path}")
    print(f"\nNext steps:")
    print(f"  1. Review the mapping in {output_path}")
    print(f"  2. Re-run analyze_music_watch.py to incorporate the new artist data")

def main():
    data_path = "apple-music-watch-viewer/public/data.json"
    output_path = "artist_mapping.json"

    try:
        fetch_missing_artists(data_path, output_path)
    except FileNotFoundError:
        print(f"Error: Could not find '{data_path}'")
        print("Please run analyze_music_watch.py first to generate the data file")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Partial results may not be saved.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
