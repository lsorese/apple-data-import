#!/usr/bin/env python3
"""
Add genre data to existing data.json from Container Details CSV
"""

import csv
import json
import sys

def clean_genres(genres_string):
    """Remove useless genres like 'Music' and clean up the genre list"""
    if not genres_string:
        return ''

    # Split by comma, strip whitespace
    genres = [g.strip() for g in genres_string.split(',')]

    # Filter out useless/generic genres
    filtered_genres = [g for g in genres if g.lower() not in ['music']]

    # Return cleaned genre string
    return ', '.join(filtered_genres) if filtered_genres else ''

def load_genres_from_csv(csv_path):
    """Load album to genre mapping from Container Details CSV"""
    album_to_genre = {}

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row.get('Container Type') == 'ALBUM':
                    desc = row.get('Container Description', '')
                    genres_field = row.get('Genres', '')

                    # Parse 'Artist - Album' format
                    if ' - ' in desc and genres_field:
                        parts = desc.split(' - ', 1)
                        album = parts[1].strip()

                        # Normalize album name (remove " - Single")
                        if album.endswith(' - Single'):
                            album = album[:-9]

                        # Keep first occurrence, clean up genres
                        if album not in album_to_genre:
                            cleaned_genres = clean_genres(genres_field.strip())
                            if cleaned_genres:
                                album_to_genre[album] = cleaned_genres

                    # Also try using desc directly as album name
                    elif desc and genres_field:
                        album = desc.strip()
                        if album.endswith(' - Single'):
                            album = album[:-9]

                        if album not in album_to_genre:
                            cleaned_genres = clean_genres(genres_field.strip())
                            if cleaned_genres:
                                album_to_genre[album] = cleaned_genres

        print(f"Loaded {len(album_to_genre)} albums with genre data from {csv_path}")
        return album_to_genre

    except FileNotFoundError:
        print(f"Warning: Could not find {csv_path}")
        return {}

def add_genres_to_data(data_json_path, container_csv_paths):
    """Add genre data to existing data.json"""

    # Load existing data
    print(f"\nLoading data from {data_json_path}...")
    try:
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {data_json_path} not found")
        sys.exit(1)

    albums = data.get('watch_albums', [])
    print(f"  Found {len(albums)} albums")

    # Load genre data from all CSV files
    all_genres = {}
    for csv_path in container_csv_paths:
        genres = load_genres_from_csv(csv_path)
        all_genres.update(genres)

    print(f"\nTotal unique albums with genre data: {len(all_genres)}")

    # Add genre data to albums
    matched_count = 0
    for album in albums:
        album_name = album['album_name']
        if album_name in all_genres:
            album['genre'] = all_genres[album_name]
            matched_count += 1

    print(f"\nMatched {matched_count} out of {len(albums)} albums with genre data")

    # Update statistics
    data['statistics']['albums_with_genre_data'] = matched_count
    data['statistics']['albums_without_genre_data'] = len(albums) - matched_count

    # Save updated data
    print(f"\nSaving updated data to {data_json_path}...")
    with open(data_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✓ Genre data added successfully!")

    # Show some examples
    print("\nSample albums with genres:")
    count = 0
    for album in albums:
        if album.get('genre') and count < 5:
            print(f"  {album['album_name'][:40]:40} - {album['genre']}")
            count += 1

def main():
    data_json_path = "apple-music-watch-viewer/public/data.json"

    # Multiple possible Container Details CSV locations
    container_csv_paths = [
        "Apple Music - Container Details.csv",
        "../Apple_Media_Services 2/Apple Music Activity/Apple Music - Container Details.csv"
    ]

    try:
        add_genres_to_data(data_json_path, container_csv_paths)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
