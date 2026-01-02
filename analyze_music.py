#!/usr/bin/env python3
"""
Apple Music Play Activity Analyzer

Analyzes Apple Music play history to find:
1. Albums that are 70% completed (configurable threshold)
2. Albums played on Apple Watch
"""

import csv
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, Set, List, Tuple
import sys

# Configuration
COMPLETION_THRESHOLD = 0.70  # 70% of tracks must be listened to
LISTEN_THRESHOLD = 0.50      # Track must be played for 50% of duration

class MusicAnalyzer:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.album_tracks: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        self.listened_tracks: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        self.album_play_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        self.watch_albums: Set[Tuple[str, str]] = set()
        self.device_types_found: Set[str] = set()
        self.device_os_names_found: Set[str] = set()
        # Track first and last listen dates
        self.album_first_listen: Dict[Tuple[str, str], str] = {}
        self.album_last_listen: Dict[Tuple[str, str], str] = {}

    def is_watch_device(self, row: Dict[str, str]) -> bool:
        """Detect if a play was on Apple Watch"""
        device_type = row.get('Device Type', '').upper()
        device_os = row.get('Device OS Name', '').upper()
        device_name = row.get('Client Device Name', '').upper()

        # Track what we're seeing for debugging
        if device_type:
            self.device_types_found.add(device_type)
        if device_os:
            self.device_os_names_found.add(device_os)

        # Check for Apple Watch indicators
        watch_indicators = ['WATCH', 'WATCHOS']

        return any(indicator in device_type or indicator in device_os or indicator in device_name
                  for indicator in watch_indicators)

    def is_track_listened(self, row: Dict[str, str]) -> bool:
        """Check if a track was listened to (>50% of duration)"""
        try:
            play_duration = float(row.get('Play Duration Milliseconds', 0) or 0)
            media_duration = float(row.get('Media Duration In Milliseconds', 0) or 0)

            if media_duration == 0:
                return False

            listen_percentage = play_duration / media_duration
            return listen_percentage >= LISTEN_THRESHOLD
        except (ValueError, TypeError):
            return False

    def get_album_key(self, row: Dict[str, str]) -> Tuple[str, str]:
        """Create a unique key for an album (album name only - artist not available in export)"""
        # Try different fields for album info
        album_name = (row.get('Album Name') or
                     row.get('Container Album Name') or
                     row.get('Container Name', ''))

        # Note: Apple Music Play Activity export does not include artist names
        # Using empty string so albums are keyed by name only
        artist_name = ''

        return (album_name.strip(), artist_name.strip())

    def process_csv(self):
        """Process the CSV file and collect data"""
        print(f"Processing {self.csv_path}...")

        row_count = 0
        skipped_rows = 0

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                row_count += 1
                if row_count % 10000 == 0:
                    print(f"  Processed {row_count:,} rows...")

                # Get album and song info
                album_key = self.get_album_key(row)
                song_name = row.get('Song Name', '').strip()

                # Skip if no album or song name
                if not album_key[0] or not song_name:
                    skipped_rows += 1
                    continue

                # Track all unique songs in this album
                self.album_tracks[album_key].add(song_name)

                # Check if this track was listened to
                if self.is_track_listened(row):
                    self.listened_tracks[album_key].add(song_name)

                # Increment play count for album
                self.album_play_counts[album_key] += 1

                # Track listen dates
                event_timestamp = row.get('Event End Timestamp', '') or row.get('Event Start Timestamp', '')
                if event_timestamp:
                    # Update first listen (earliest date)
                    if album_key not in self.album_first_listen:
                        self.album_first_listen[album_key] = event_timestamp
                    elif event_timestamp < self.album_first_listen[album_key]:
                        self.album_first_listen[album_key] = event_timestamp

                    # Update last listen (latest date)
                    if album_key not in self.album_last_listen:
                        self.album_last_listen[album_key] = event_timestamp
                    elif event_timestamp > self.album_last_listen[album_key]:
                        self.album_last_listen[album_key] = event_timestamp

                # Check if played on Apple Watch
                if self.is_watch_device(row):
                    self.watch_albums.add(album_key)

        print(f"\nCompleted processing {row_count:,} rows")
        print(f"Skipped {skipped_rows:,} rows (missing album/song info)")
        print(f"Found {len(self.album_tracks)} unique albums")
        print(f"Found {len(self.watch_albums)} albums played on Apple Watch")
        print(f"\nDevice types found: {sorted(self.device_types_found)}")
        print(f"Device OS names found: {sorted(self.device_os_names_found)}")

    def calculate_completed_albums(self) -> List[Dict]:
        """Find albums that meet the completion threshold"""
        completed = []

        for album_key, all_tracks in self.album_tracks.items():
            listened = self.listened_tracks.get(album_key, set())
            total_tracks = len(all_tracks)
            listened_tracks = len(listened)

            if total_tracks == 0:
                continue

            completion_percentage = listened_tracks / total_tracks

            if completion_percentage >= COMPLETION_THRESHOLD:
                completed.append({
                    'album_name': album_key[0],
                    'total_tracks': total_tracks,
                    'listened_tracks': listened_tracks,
                    'completion_percentage': round(completion_percentage * 100, 1),
                    'play_count': self.album_play_counts[album_key],
                    'first_listen': self.album_first_listen.get(album_key, ''),
                    'last_listen': self.album_last_listen.get(album_key, '')
                })

        # Sort by completion percentage (desc), then by play count (desc)
        completed.sort(key=lambda x: (-x['completion_percentage'], -x['play_count']))

        return completed

    def get_watch_albums(self) -> List[Dict]:
        """Get list of albums played on Apple Watch"""
        watch_list = []

        for album_key in self.watch_albums:
            all_tracks = self.album_tracks.get(album_key, set())
            listened = self.listened_tracks.get(album_key, set())
            total_tracks = len(all_tracks)
            listened_tracks = len(listened)

            completion_percentage = (listened_tracks / total_tracks * 100) if total_tracks > 0 else 0

            watch_list.append({
                'album_name': album_key[0],
                'total_tracks': total_tracks,
                'listened_tracks': listened_tracks,
                'completion_percentage': round(completion_percentage, 1),
                'play_count': self.album_play_counts[album_key],
                'first_listen': self.album_first_listen.get(album_key, ''),
                'last_listen': self.album_last_listen.get(album_key, '')
            })

        # Sort by play count (desc)
        watch_list.sort(key=lambda x: -x['play_count'])

        return watch_list

    def generate_report(self, output_path: str):
        """Generate JSON report with all analysis results"""
        print("\nGenerating report...")

        completed_albums = self.calculate_completed_albums()
        watch_albums = self.get_watch_albums()

        report = {
            'generated_at': datetime.now().isoformat(),
            'config': {
                'completion_threshold': COMPLETION_THRESHOLD,
                'listen_threshold': LISTEN_THRESHOLD
            },
            'statistics': {
                'total_albums': len(self.album_tracks),
                'completed_albums': len(completed_albums),
                'watch_albums': len(watch_albums),
                'device_types_found': sorted(list(self.device_types_found)),
                'device_os_names_found': sorted(list(self.device_os_names_found))
            },
            'completed_albums': completed_albums,
            'watch_albums': watch_albums
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved to {output_path}")
        print(f"\nSummary:")
        print(f"  Total albums: {report['statistics']['total_albums']}")
        print(f"  Completed albums (≥{COMPLETION_THRESHOLD*100}%): {len(completed_albums)}")
        print(f"  Apple Watch albums: {len(watch_albums)}")

def main():
    csv_path = "Apple Music Play Activity.csv"
    output_path = "outputs/data.json"

    try:
        analyzer = MusicAnalyzer(csv_path)
        analyzer.process_csv()
        analyzer.generate_report(output_path)

        print("\n✓ Analysis complete!")

    except FileNotFoundError:
        print(f"Error: Could not find '{csv_path}'")
        print("Please ensure the file exists in the current directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
