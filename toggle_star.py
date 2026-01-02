#!/usr/bin/env python3
"""
Toggle star status for albums in data.json
"""

import json
import sys
from pathlib import Path

DATA_FILE = Path("apple-music-watch-viewer/public/data.json")

def load_data():
    """Load the data.json file"""
    if not DATA_FILE.exists():
        print(f"Error: {DATA_FILE} not found")
        sys.exit(1)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """Save the data.json file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_album(data, search_term):
    """Find albums matching the search term"""
    search_lower = search_term.lower()
    matches = []

    for album in data['watch_albums']:
        if (search_lower in album['album_name'].lower() or
            (album.get('artist_name') and search_lower in album['artist_name'].lower())):
            matches.append(album)

    return matches

def toggle_star(album_name):
    """Toggle the star status for an album"""
    data = load_data()

    found = False
    for album in data['watch_albums']:
        if album['album_name'] == album_name:
            album['starred'] = not album.get('starred', False)
            found = True
            new_state = "starred" if album['starred'] else "unstarred"
            print(f"✓ {album['album_name']} is now {new_state}")
            break

    if not found:
        print(f"Error: Album '{album_name}' not found")
        sys.exit(1)

    save_data(data)

def list_starred():
    """List all starred albums"""
    data = load_data()

    starred = [a for a in data['watch_albums'] if a.get('starred')]

    if not starred:
        print("No starred albums")
        return

    print(f"\nStarred albums ({len(starred)}):\n")
    for album in starred:
        artist = album.get('artist_name', 'Unknown')
        print(f"  ★ {album['album_name']} - {artist}")

def interactive_search():
    """Interactive search and toggle"""
    data = load_data()

    search = input("Search for album or artist: ").strip()
    if not search:
        print("No search term provided")
        return

    matches = find_album(data, search)

    if not matches:
        print(f"No albums found matching '{search}'")
        return

    if len(matches) == 1:
        album = matches[0]
        current_state = "starred" if album.get('starred') else "unstarred"
        artist = album.get('artist_name', 'Unknown')

        print(f"\nFound: {album['album_name']} - {artist}")
        print(f"Current state: {current_state}")

        confirm = input("Toggle star? (y/n): ").strip().lower()
        if confirm == 'y':
            toggle_star(album['album_name'])
    else:
        print(f"\nFound {len(matches)} matches:\n")
        for i, album in enumerate(matches, 1):
            artist = album.get('artist_name', 'Unknown')
            star = "★" if album.get('starred') else "☆"
            print(f"  {i}. {star} {album['album_name']} - {artist}")

        print()
        choice = input(f"Select album (1-{len(matches)}) or 'q' to quit: ").strip()

        if choice.lower() == 'q':
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                toggle_star(matches[idx]['album_name'])
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./toggle_star.py search           - Interactive search and toggle")
        print("  ./toggle_star.py list             - List all starred albums")
        print("  ./toggle_star.py toggle \"Album\"   - Toggle specific album")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'search':
        interactive_search()
    elif command == 'list':
        list_starred()
    elif command == 'toggle' and len(sys.argv) >= 3:
        album_name = sys.argv[2]
        toggle_star(album_name)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
