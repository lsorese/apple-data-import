#!/usr/bin/env python3
"""
Find Missing Albums for 2025 Runs

This script:
1. Checks for 2025 runs in Strava that are NOT in data.json
2. For those runs, finds albums listened to around that time (any device)
3. Generates data_maybe.json with potential matches
"""

import json
import csv
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import time

# Strava API Configuration
CLIENT_ID = "193286"
CLIENT_SECRET = "7c0564b4ea0552314ed091a0f1c0d2da8d50730c"
ACCESS_TOKEN = "c8fa2c2ca163cd637f20782beac8e13d9fab0c2c"
REFRESH_TOKEN = "066e50c6bbc850d2551cd9d852050ee058c99342"
STRAVA_API_BASE = "https://www.strava.com/api/v3"

# Paths
DATA_JSON_PATH = "apple-music-watch-viewer/src/data.json"
PLAY_ACTIVITY_PATH = "Apple Music Play Activity.csv"
CONTAINER_DETAILS_PATH = "Apple Music - Container Details.csv"
OUTPUT_PATH = "apple-music-watch-viewer/src/data_maybe.json"

# Matching tolerance: how close should album listening be to run time
TIME_TOLERANCE_MINUTES = 60  # 1 hour before/after run

class StravaClient:
    def __init__(self, client_id: str, client_secret: str, access_token: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token

    def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        print("Refreshing Strava access token...")

        url = "https://www.strava.com/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()

            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']

            print(f"  ✓ Access token refreshed")
            return True

        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error refreshing token: {e}")
            return False

    def get_activities(self, after: Optional[int] = None, before: Optional[int] = None) -> List[Dict]:
        """Fetch activities from Strava API"""
        activities = []
        page = 1

        while True:
            print(f"  Fetching Strava activities page {page}...")

            url = f"{STRAVA_API_BASE}/athlete/activities"
            params = {
                "per_page": 200,
                "page": page
            }

            if after:
                params["after"] = after
            if before:
                params["before"] = before

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            try:
                response = requests.get(url, headers=headers, params=params)

                # If unauthorized, try refreshing token
                if response.status_code == 401:
                    print("  Access token expired, refreshing...")
                    if self.refresh_access_token():
                        headers["Authorization"] = f"Bearer {self.access_token}"
                        response = requests.get(url, headers=headers, params=params)
                    else:
                        print("  Failed to refresh token")
                        return activities

                response.raise_for_status()
                page_activities = response.json()

                if not page_activities:
                    break

                activities.extend(page_activities)
                print(f"    Got {len(page_activities)} activities")

                time.sleep(1)  # Respect rate limits
                page += 1

            except requests.exceptions.RequestException as e:
                print(f"  Error fetching activities: {e}")
                break

        return activities


def parse_iso_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO timestamp"""
    if not timestamp_str:
        return None
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def load_existing_runs(data_json_path: str) -> Set[str]:
    """Load run dates that already have albums matched"""
    print(f"Loading existing data from {data_json_path}...")

    try:
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        albums = data.get('watch_albums', [])
        run_dates = set()

        # Collect all Strava activity start dates that are already matched
        for album in albums:
            if 'strava_start_date' in album:
                run_dates.add(album['strava_start_date'])

        print(f"  Found {len(run_dates)} runs already matched with albums")
        return run_dates

    except FileNotFoundError:
        print(f"  Error: {data_json_path} not found")
        return set()


def get_2025_runs(client: StravaClient, existing_run_dates: Set[str]) -> List[Dict]:
    """Get all 2025 runs that are NOT already in data.json"""
    print("\nFetching 2025 runs from Strava...")

    # Date range for 2025
    start_2025 = datetime(2025, 1, 1, tzinfo=None)
    end_2025 = datetime(2025, 12, 31, 23, 59, 59, tzinfo=None)

    after_timestamp = int(start_2025.timestamp())
    before_timestamp = int(end_2025.timestamp())

    # Fetch activities
    activities = client.get_activities(after=after_timestamp, before=before_timestamp)

    # Filter for runs only
    runs = [a for a in activities if a.get('type') in ['Run', 'VirtualRun']]
    print(f"  Found {len(runs)} total runs in 2025")

    # Filter out runs already in data.json
    new_runs = []
    for run in runs:
        start_date = run.get('start_date', '')
        if start_date not in existing_run_dates:
            new_runs.append(run)

    print(f"  Found {len(new_runs)} runs NOT in data.json")
    return new_runs


def load_artist_mapping(container_details_path: str) -> Dict[str, str]:
    """Load album-to-artist mapping"""
    print(f"\nLoading artist information from {container_details_path}...")

    album_to_artist = {}
    album_to_genre = {}

    try:
        with open(container_details_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row.get('Container Type') == 'ALBUM':
                    desc = row.get('Container Description', '')
                    genres_field = row.get('Genres', '')

                    # Parse 'Artist - Album' format
                    if ' - ' in desc:
                        parts = desc.split(' - ', 1)
                        artist = parts[0].strip()
                        album = parts[1].strip()

                        # Normalize album name
                        if album.endswith(' - Single'):
                            album = album[:-9]

                        if album not in album_to_artist:
                            album_to_artist[album] = artist

                        if album not in album_to_genre and genres_field:
                            album_to_genre[album] = genres_field.strip()

        print(f"  Loaded {len(album_to_artist)} albums with artist information")

    except FileNotFoundError:
        print(f"  Warning: Could not find '{container_details_path}'")

    return album_to_artist, album_to_genre


def find_albums_near_run(run: Dict, play_activity_path: str,
                         album_to_artist: Dict[str, str],
                         album_to_genre: Dict[str, str],
                         tolerance_minutes: int = TIME_TOLERANCE_MINUTES) -> List[Dict]:
    """Find albums listened to around the time of a run"""

    run_start = parse_iso_timestamp(run.get('start_date', ''))
    if not run_start:
        return []

    run_duration_seconds = run.get('moving_time', 0)
    run_end = run_start + timedelta(seconds=run_duration_seconds)

    # Search window: tolerance before run start to tolerance after run end
    search_start = run_start - timedelta(minutes=tolerance_minutes)
    search_end = run_end + timedelta(minutes=tolerance_minutes)

    # Track albums and their plays during this window
    album_plays = {}  # album_name -> {plays, tracks, first_play, last_play}

    print(f"  Searching for albums between {search_start.isoformat()} and {search_end.isoformat()}")

    with open(play_activity_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            event_timestamp = row.get('Event End Timestamp', '') or row.get('Event Start Timestamp', '')
            play_time = parse_iso_timestamp(event_timestamp)

            if not play_time:
                continue

            # Check if play is within search window
            if search_start <= play_time <= search_end:
                album_name = (row.get('Album Name') or
                            row.get('Container Album Name') or
                            row.get('Container Name', '')).strip()

                # Normalize album name
                if album_name.endswith(' - Single'):
                    album_name = album_name[:-9]

                song_name = row.get('Song Name', '').strip()

                if not album_name or not song_name:
                    continue

                # Initialize album tracking
                if album_name not in album_plays:
                    album_plays[album_name] = {
                        'plays': 0,
                        'tracks': set(),
                        'first_play': event_timestamp,
                        'last_play': event_timestamp
                    }

                # Update album info
                album_plays[album_name]['plays'] += 1
                album_plays[album_name]['tracks'].add(song_name)

                # Update first/last play times
                if event_timestamp < album_plays[album_name]['first_play']:
                    album_plays[album_name]['first_play'] = event_timestamp
                if event_timestamp > album_plays[album_name]['last_play']:
                    album_plays[album_name]['last_play'] = event_timestamp

    # Convert to list format
    albums = []
    for album_name, info in album_plays.items():
        artist_name = album_to_artist.get(album_name, '')
        genre_name = album_to_genre.get(album_name, '')

        albums.append({
            'album_name': album_name,
            'artist_name': artist_name,
            'genre': genre_name,
            'play_count': info['plays'],
            'unique_tracks': len(info['tracks']),
            'first_listen': info['first_play'],
            'last_listen': info['last_play'],
            'strava_activity_id': run.get('id'),
            'strava_activity_name': run.get('name', ''),
            'strava_start_date': run.get('start_date', ''),
            'strava_distance_miles': round(run.get('distance', 0) * 0.000621371, 2),
            'strava_moving_time_seconds': run.get('moving_time', 0),
            'confidence': 'maybe'  # Flag to indicate this is a potential match
        })

    return albums


def main():
    print("=" * 70)
    print("Finding Missing Albums for 2025 Runs")
    print("=" * 70)

    # Initialize Strava client
    client = StravaClient(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN)

    # Load existing matched runs
    existing_run_dates = load_existing_runs(DATA_JSON_PATH)

    # Get 2025 runs not in data.json
    new_runs = get_2025_runs(client, existing_run_dates)

    if not new_runs:
        print("\n✓ No missing runs found! All 2025 runs already have albums matched.")
        return

    # Load artist mapping
    album_to_artist, album_to_genre = load_artist_mapping(CONTAINER_DETAILS_PATH)

    # Find albums for each missing run
    print(f"\nSearching for albums near {len(new_runs)} unmatched runs...")

    all_maybe_albums = []

    for i, run in enumerate(new_runs, 1):
        run_name = run.get('name', 'Unknown')
        run_date = run.get('start_date', '')
        distance_miles = round(run.get('distance', 0) * 0.000621371, 2)

        print(f"\n[{i}/{len(new_runs)}] {run_name} ({run_date}) - {distance_miles} mi")

        albums = find_albums_near_run(run, PLAY_ACTIVITY_PATH, album_to_artist, album_to_genre)

        if albums:
            print(f"  ✓ Found {len(albums)} potential album(s):")
            for album in albums:
                print(f"    - {album['album_name']} by {album['artist_name']} ({album['play_count']} plays, {album['unique_tracks']} tracks)")
            all_maybe_albums.extend(albums)
        else:
            print(f"  ✗ No albums found near this run")

    # Generate output
    if all_maybe_albums:
        output = {
            'generated_at': datetime.now().isoformat(),
            'description': 'Potential album matches for 2025 runs not yet in data.json',
            'search_criteria': {
                'time_tolerance_minutes': TIME_TOLERANCE_MINUTES,
                'year': 2025
            },
            'statistics': {
                'missing_runs': len(new_runs),
                'potential_albums': len(all_maybe_albums)
            },
            'maybe_albums': all_maybe_albums
        }

        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 70)
        print("✓ COMPLETE!")
        print("=" * 70)
        print(f"  Missing 2025 runs: {len(new_runs)}")
        print(f"  Potential albums found: {len(all_maybe_albums)}")
        print(f"\n  Output saved to: {OUTPUT_PATH}")
    else:
        print("\n" + "=" * 70)
        print("No albums found for any of the missing runs")
        print("=" * 70)


if __name__ == '__main__':
    main()
