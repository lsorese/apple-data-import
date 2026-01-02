#!/usr/bin/env python3
"""
Strava API Integration for Apple Music Album Data

Fetches running data from Strava API and matches it with album listening timestamps.
Merges pace, distance, and other running metrics into the existing data.json file.
"""

import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional
import time
import sys

# Strava API Configuration
CLIENT_ID = "193286"
CLIENT_SECRET = "7c0564b4ea0552314ed091a0f1c0d2da8d50730c"
ACCESS_TOKEN = "c8fa2c2ca163cd637f20782beac8e13d9fab0c2c"
REFRESH_TOKEN = "066e50c6bbc850d2551cd9d852050ee058c99342"

STRAVA_API_BASE = "https://www.strava.com/api/v3"

# Rate limits: 100 requests per 15 minutes, 1000 per day
RATE_LIMIT_15MIN = 100
RATE_LIMIT_DAILY = 1000

class StravaClient:
    def __init__(self, client_id: str, client_secret: str, access_token: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.request_count = 0
        self.rate_limit_remaining = None
        self.rate_limit_usage = None

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

            print(f"  ✓ Access token refreshed successfully")
            print(f"  New access token: {self.access_token}")
            print(f"  New refresh token: {self.refresh_token}")

            return True

        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error refreshing token: {e}")
            return False

    def check_rate_limit(self, response: requests.Response):
        """Check and display rate limit info from response headers"""
        if 'X-RateLimit-Limit' in response.headers:
            limit_15min = response.headers.get('X-RateLimit-Limit', '').split(',')[0]
            usage_15min = response.headers.get('X-RateLimit-Usage', '').split(',')[0]
            self.rate_limit_remaining = int(limit_15min) - int(usage_15min) if limit_15min and usage_15min else None

            if self.rate_limit_remaining is not None and self.rate_limit_remaining < 20:
                print(f"  ⚠ Warning: Only {self.rate_limit_remaining} requests remaining in 15-minute window")

    def get_activities(self, after: Optional[int] = None, before: Optional[int] = None,
                      per_page: int = 200, max_requests: Optional[int] = None) -> List[Dict]:
        """Fetch activities from Strava API

        Args:
            after: Unix timestamp - only return activities after this time
            before: Unix timestamp - only return activities before this time
            per_page: Number of activities per page (max 200)
            max_requests: Maximum number of API requests to make (for testing)
        """
        activities = []
        page = 1

        while True:
            # Check if we've hit the request limit
            if max_requests and self.request_count >= max_requests:
                print(f"  Reached max request limit ({max_requests})")
                break

            print(f"  Fetching page {page}... (Request {self.request_count + 1})")

            url = f"{STRAVA_API_BASE}/athlete/activities"
            params = {
                "per_page": per_page,
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
                self.request_count += 1
                self.check_rate_limit(response)

                # If unauthorized, try refreshing token
                if response.status_code == 401:
                    print("  Access token expired, refreshing...")
                    if self.refresh_access_token():
                        headers["Authorization"] = f"Bearer {self.access_token}"
                        response = requests.get(url, headers=headers, params=params)
                        self.request_count += 1
                        self.check_rate_limit(response)
                    else:
                        print("  Failed to refresh token")
                        return activities

                response.raise_for_status()
                page_activities = response.json()

                if not page_activities:
                    break

                activities.extend(page_activities)
                print(f"    Got {len(page_activities)} activities")

                # Respect rate limits - wait between requests
                time.sleep(1)
                page += 1

            except requests.exceptions.RequestException as e:
                print(f"  Error fetching activities: {e}")
                break

        print(f"\nTotal API requests made: {self.request_count}")
        return activities

    def get_activity_details(self, activity_id: int) -> Optional[Dict]:
        """Fetch detailed information for a specific activity"""
        url = f"{STRAVA_API_BASE}/activities/{activity_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 401:
                if self.refresh_access_token():
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    response = requests.get(url, headers=headers)
                else:
                    return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"  Error fetching activity {activity_id}: {e}")
            return None


def parse_iso_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO timestamp from Apple Music data"""
    if not timestamp_str:
        return None
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def find_matching_strava_activity(album_timestamp: str, strava_activities: List[Dict],
                                  tolerance_minutes: int = 30) -> Optional[Dict]:
    """
    Find a Strava activity that matches the album listening timestamp.

    Args:
        album_timestamp: ISO timestamp of when the album was played
        strava_activities: List of Strava activities
        tolerance_minutes: How many minutes before/after to consider a match

    Returns:
        Matching Strava activity dict or None
    """
    album_time = parse_iso_timestamp(album_timestamp)
    if not album_time:
        return None

    tolerance_seconds = tolerance_minutes * 60
    best_match = None
    best_diff = float('inf')

    for activity in strava_activities:
        # Parse activity start time
        activity_start = parse_iso_timestamp(activity.get('start_date'))
        if not activity_start:
            continue

        # Calculate time difference in seconds
        time_diff = abs((album_time - activity_start).total_seconds())

        # Check if within tolerance and better than current best
        if time_diff <= tolerance_seconds and time_diff < best_diff:
            best_match = activity
            best_diff = time_diff

    return best_match


def meters_to_miles(meters: float) -> float:
    """Convert meters to miles"""
    return meters * 0.000621371


def seconds_to_pace(seconds: float, distance_miles: float) -> str:
    """
    Convert seconds and distance to pace (min/mile format)

    Args:
        seconds: Total time in seconds
        distance_miles: Distance in miles

    Returns:
        Pace string in format "MM:SS"
    """
    if distance_miles == 0:
        return "0:00"

    pace_seconds = seconds / distance_miles
    minutes = int(pace_seconds // 60)
    secs = int(pace_seconds % 60)

    return f"{minutes}:{secs:02d}"


def extract_strava_metrics(activity: Dict) -> Dict:
    """Extract relevant metrics from a Strava activity"""
    distance_meters = activity.get('distance', 0)
    distance_miles = meters_to_miles(distance_meters)
    moving_time = activity.get('moving_time', 0)
    elapsed_time = activity.get('elapsed_time', 0)

    return {
        'strava_activity_id': activity.get('id'),
        'strava_activity_name': activity.get('name', ''),
        'strava_activity_type': activity.get('type', ''),
        'strava_start_date': activity.get('start_date', ''),
        'strava_distance_miles': round(distance_miles, 2),
        'strava_distance_meters': distance_meters,
        'strava_moving_time_seconds': moving_time,
        'strava_elapsed_time_seconds': elapsed_time,
        'strava_pace_per_mile': seconds_to_pace(moving_time, distance_miles),
        'strava_elevation_gain_meters': activity.get('total_elevation_gain', 0),
        'strava_average_speed_mps': activity.get('average_speed', 0),
        'strava_max_speed_mps': activity.get('max_speed', 0),
        'strava_average_heartrate': activity.get('average_heartrate'),
        'strava_max_heartrate': activity.get('max_heartrate'),
        'strava_average_cadence': activity.get('average_cadence'),
        'strava_suffer_score': activity.get('suffer_score'),
        'strava_has_heartrate': activity.get('has_heartrate', False),
    }


def merge_strava_data(data_json_path: str, client_id: str, test_mode: bool = False, test_limit: int = 10):
    """Main function to merge Strava data into data.json

    Args:
        data_json_path: Path to the data.json file
        client_id: Strava API client ID
        test_mode: If True, only process a small subset of albums
        test_limit: Number of albums to process in test mode
    """

    # Load existing data
    print(f"Loading data from {data_json_path}...")
    try:
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {data_json_path} not found")
        sys.exit(1)

    all_albums = data.get('watch_albums', [])
    print(f"  Loaded {len(all_albums)} albums")

    # Test mode - limit the number of albums
    if test_mode:
        print(f"\n⚠ TEST MODE: Processing only first {test_limit} albums")
        albums_to_process = all_albums[:test_limit]
    else:
        albums_to_process = all_albums

    # Initialize Strava client
    print("\nInitializing Strava client...")
    client = StravaClient(client_id, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN)

    # Get date range from albums
    all_dates = []
    for album in albums_to_process:
        first_listen = parse_iso_timestamp(album.get('first_listen', ''))
        last_listen = parse_iso_timestamp(album.get('last_listen', ''))
        if first_listen:
            all_dates.append(first_listen)
        if last_listen:
            all_dates.append(last_listen)

    if not all_dates:
        print("No valid timestamps found in albums")
        sys.exit(1)

    earliest_date = min(all_dates)
    latest_date = max(all_dates)

    print(f"\nFetching Strava activities between:")
    print(f"  {earliest_date.isoformat()} and {latest_date.isoformat()}")

    # Convert to Unix timestamps
    after_timestamp = int(earliest_date.timestamp()) - (7 * 24 * 60 * 60)  # 7 days buffer
    before_timestamp = int(latest_date.timestamp()) + (7 * 24 * 60 * 60)   # 7 days buffer

    # Fetch all activities (with request limit in test mode)
    print("\nFetching Strava activities...")
    max_requests = 5 if test_mode else None
    activities = client.get_activities(after=after_timestamp, before=before_timestamp, max_requests=max_requests)
    print(f"  Fetched {len(activities)} total activities")

    # Filter for runs only
    runs = [a for a in activities if a.get('type') in ['Run', 'VirtualRun']]
    print(f"  Found {len(runs)} running activities")

    # Match albums with Strava activities
    print("\nMatching albums with Strava activities...")
    matched_count = 0

    for album in all_albums:
        # Try to match with first_listen timestamp
        first_listen = album.get('first_listen', '')

        if first_listen:
            match = find_matching_strava_activity(first_listen, runs, tolerance_minutes=60)

            if match:
                matched_count += 1
                strava_metrics = extract_strava_metrics(match)

                # Add all Strava metrics to album
                album.update(strava_metrics)

                print(f"  ✓ Matched '{album['album_name']}' with Strava run:")
                print(f"    {strava_metrics['strava_activity_name']} - {strava_metrics['strava_distance_miles']} mi @ {strava_metrics['strava_pace_per_mile']}/mi")

    print(f"\nMatched {matched_count} out of {len(all_albums)} albums with Strava activities")

    # Update statistics
    data['statistics']['albums_with_strava_data'] = matched_count
    data['statistics']['albums_without_strava_data'] = len(all_albums) - matched_count
    data['generated_at'] = datetime.now().isoformat()

    # Also update completed_watch_albums
    if 'completed_watch_albums' in data and data['completed_watch_albums']:
        completed = data['completed_watch_albums']
        for album in completed:
            # Find matching album in watch_albums that has strava data
            for watch_album in all_albums:
                if watch_album['album_name'] == album['album_name'] and 'strava_activity_id' in watch_album:
                    # Copy strava data to completed album
                    for key, value in watch_album.items():
                        if key.startswith('strava_'):
                            album[key] = value
                    break

    # Save updated data (skip in test mode to avoid overwriting)
    if test_mode:
        print(f"\n⚠ TEST MODE: Not saving data (would save to {data_json_path})")
        print("Run without --test flag to save changes")
    else:
        print(f"\nSaving updated data to {data_json_path}...")
        with open(data_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✓ Strava data merged successfully!")

    print(f"\nNew tokens (save these for future use):")
    print(f"  Access Token: {client.access_token}")
    print(f"  Refresh Token: {client.refresh_token}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Fetch Strava running data and merge with Apple Music album data'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: process only a small subset without saving'
    )
    parser.add_argument(
        '--test-limit',
        type=int,
        default=10,
        help='Number of albums to process in test mode (default: 10)'
    )
    parser.add_argument(
        '--client-id',
        type=str,
        help='Strava Client ID (get from https://www.strava.com/settings/api)'
    )

    args = parser.parse_args()

    data_json_path = "apple-music-watch-viewer/public/data.json"

    # Get client ID from args or prompt
    client_id = args.client_id
    if not client_id:
        client_id = input("Enter your Strava Client ID: ").strip()

    if not client_id:
        print("Error: Client ID is required")
        print("Get it from: https://www.strava.com/settings/api")
        sys.exit(1)

    try:
        merge_strava_data(data_json_path, client_id, test_mode=args.test, test_limit=args.test_limit)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
