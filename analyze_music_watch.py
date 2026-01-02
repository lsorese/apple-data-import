#!/usr/bin/env python3
"""
Apple Music Apple Watch Album Analyzer

Analyzes Apple Music play history to find albums played on Apple Watch,
with artist information extracted from Container Details.
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

class WatchAlbumAnalyzer:
    def __init__(self, play_activity_path: str, container_details_path: str, artist_mapping_path: str = None):
        self.play_activity_path = play_activity_path
        self.container_details_path = container_details_path
        self.artist_mapping_path = artist_mapping_path

        # Album to artist mapping
        self.album_to_artist: Dict[str, str] = {}

        # Data structures
        self.album_tracks: Dict[str, Set[str]] = defaultdict(set)
        self.listened_tracks: Dict[str, Set[str]] = defaultdict(set)
        self.album_play_counts: Dict[str, int] = defaultdict(int)
        self.watch_albums: Set[str] = set()
        self.album_first_listen: Dict[str, str] = {}
        self.album_last_listen: Dict[str, str] = {}

        # Debug info
        self.device_types_found: Set[str] = set()
        self.device_os_names_found: Set[str] = set()

    def load_artist_mapping(self):
        """Load album-to-artist mapping from Container Details CSV"""
        print(f"Loading artist information from {self.container_details_path}...")

        try:
            with open(self.container_details_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    if row.get('Container Type') == 'ALBUM':
                        desc = row.get('Container Description', '')
                        artists_field = row.get('Artists', '')

                        # Parse 'Artist - Album' format
                        if ' - ' in desc:
                            parts = desc.split(' - ', 1)
                            artist = parts[0].strip()
                            album = parts[1].strip()

                            # Normalize album name (remove " - Single")
                            if album.endswith(' - Single'):
                                album = album[:-9]

                            # Keep first occurrence (usually the most accurate)
                            if album not in self.album_to_artist:
                                self.album_to_artist[album] = artist

                        # Also try the Artists field if available and desc parsing failed
                        elif artists_field and desc:
                            # Use desc as album name and Artists field as artist
                            album = desc.strip()
                            if album.endswith(' - Single'):
                                album = album[:-9]

                            if album not in self.album_to_artist:
                                self.album_to_artist[album] = artists_field.strip()

            print(f"  Loaded {len(self.album_to_artist)} albums with artist information")

        except FileNotFoundError:
            print(f"  Warning: Could not find '{self.container_details_path}'")
            print("  Artist information will not be available")

        # Load additional artist mapping from API lookups if available
        if self.artist_mapping_path:
            try:
                print(f"\nLoading additional artist mappings from {self.artist_mapping_path}...")
                with open(self.artist_mapping_path, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                    api_mappings = mapping_data.get('artist_mapping', {})

                    # Add to existing mapping (don't overwrite Container Details data)
                    added = 0
                    for album, artist in api_mappings.items():
                        if album not in self.album_to_artist:
                            self.album_to_artist[album] = artist
                            added += 1

                    print(f"  Added {added} artists from API lookups")
                    print(f"  Total albums with artist info: {len(self.album_to_artist)}")

            except FileNotFoundError:
                print(f"  Note: Artist mapping file not found (run fetch_artists.py to create it)")
            except Exception as e:
                print(f"  Warning: Could not load artist mapping: {e}")

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

    def process_play_activity(self):
        """Process the Play Activity CSV file"""
        print(f"\nProcessing {self.play_activity_path}...")

        row_count = 0
        skipped_rows = 0
        watch_plays = 0

        with open(self.play_activity_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                row_count += 1
                if row_count % 10000 == 0:
                    print(f"  Processed {row_count:,} rows...")

                # Only process Apple Watch plays
                if not self.is_watch_device(row):
                    continue

                watch_plays += 1

                # Get album and song info
                album_name = (row.get('Album Name') or
                            row.get('Container Album Name') or
                            row.get('Container Name', '')).strip()

                # Remove " - Single" suffix if present
                if album_name.endswith(' - Single'):
                    album_name = album_name[:-9]

                song_name = row.get('Song Name', '').strip()

                # Skip if no album or song name
                if not album_name or not song_name:
                    skipped_rows += 1
                    continue

                # Track all unique songs in this album
                self.album_tracks[album_name].add(song_name)

                # Check if this track was listened to
                if self.is_track_listened(row):
                    self.listened_tracks[album_name].add(song_name)

                # Increment play count for album
                self.album_play_counts[album_name] += 1

                # Mark as Watch album
                self.watch_albums.add(album_name)

                # Track listen dates
                event_timestamp = row.get('Event End Timestamp', '') or row.get('Event Start Timestamp', '')
                if event_timestamp:
                    # Update first listen (earliest date)
                    if album_name not in self.album_first_listen:
                        self.album_first_listen[album_name] = event_timestamp
                    elif event_timestamp < self.album_first_listen[album_name]:
                        self.album_first_listen[album_name] = event_timestamp

                    # Update last listen (latest date)
                    if album_name not in self.album_last_listen:
                        self.album_last_listen[album_name] = event_timestamp
                    elif event_timestamp > self.album_last_listen[album_name]:
                        self.album_last_listen[album_name] = event_timestamp

        print(f"\nCompleted processing {row_count:,} rows")
        print(f"  Apple Watch plays: {watch_plays:,}")
        print(f"  Skipped {skipped_rows:,} Watch plays (missing album/song info)")
        print(f"  Found {len(self.watch_albums)} unique albums on Apple Watch")
        print(f"\nDevice types found: {sorted(self.device_types_found)}")
        print(f"Device OS names found: {sorted(self.device_os_names_found)}")

    def get_watch_albums(self) -> List[Dict]:
        """Get list of albums played on Apple Watch with completion data"""
        watch_list = []

        for album_name in self.watch_albums:
            all_tracks = self.album_tracks.get(album_name, set())
            listened = self.listened_tracks.get(album_name, set())
            total_tracks = len(all_tracks)
            listened_tracks = len(listened)

            completion_percentage = (listened_tracks / total_tracks * 100) if total_tracks > 0 else 0

            # Skip albums with less than 50% completion
            if completion_percentage < 50:
                continue

            # Get artist from mapping
            artist_name = self.album_to_artist.get(album_name, '')

            watch_list.append({
                'album_name': album_name,
                'artist_name': artist_name,
                'total_tracks': total_tracks,
                'listened_tracks': listened_tracks,
                'completion_percentage': round(completion_percentage, 1),
                'play_count': self.album_play_counts[album_name],
                'first_listen': self.album_first_listen.get(album_name, ''),
                'last_listen': self.album_last_listen.get(album_name, ''),
                'starred': False
            })

        # Sort by play count (desc)
        watch_list.sort(key=lambda x: -x['play_count'])

        return watch_list

    def generate_report(self, output_path: str):
        """Generate JSON report with Apple Watch album analysis"""
        print("\nGenerating report...")

        watch_albums = self.get_watch_albums()

        # Load existing starred states if data.json exists
        existing_starred = {}
        try:
            import os
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    for album in existing_data.get('watch_albums', []):
                        if album.get('starred'):
                            existing_starred[album['album_name']] = True
                print(f"  Preserving {len(existing_starred)} starred albums from existing data")
        except Exception as e:
            print(f"  Note: Could not load existing starred states: {e}")

        # Apply existing starred states to new albums
        for album in watch_albums:
            if album['album_name'] in existing_starred:
                album['starred'] = True

        # Count how many have artist info
        with_artist = sum(1 for album in watch_albums if album['artist_name'])

        # Filter completed albums from watch list
        completed_watch_albums = [a for a in watch_albums if a['completion_percentage'] >= COMPLETION_THRESHOLD * 100]

        report = {
            'generated_at': datetime.now().isoformat(),
            'config': {
                'completion_threshold': COMPLETION_THRESHOLD,
                'listen_threshold': LISTEN_THRESHOLD
            },
            'statistics': {
                'watch_albums': len(watch_albums),
                'completed_watch_albums': len(completed_watch_albums),
                'albums_with_artist_info': with_artist,
                'albums_without_artist_info': len(watch_albums) - with_artist,
                'device_types_found': sorted(list(self.device_types_found)),
                'device_os_names_found': sorted(list(self.device_os_names_found))
            },
            'watch_albums': watch_albums,
            'completed_watch_albums': completed_watch_albums
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved to {output_path}")
        print(f"\nSummary:")
        print(f"  Apple Watch albums: {len(watch_albums)}")
        print(f"  Completed Watch albums (≥{COMPLETION_THRESHOLD*100}%): {len(completed_watch_albums)}")
        print(f"  Albums with artist info: {with_artist} ({with_artist/len(watch_albums)*100:.1f}%)")

def main():
    play_activity_path = "Apple Music Play Activity.csv"
    container_details_path = "Apple Music - Container Details.csv"
    artist_mapping_path = "artist_mapping.json"
    output_path = "apple-music-watch-viewer/public/data.json"

    try:
        analyzer = WatchAlbumAnalyzer(play_activity_path, container_details_path, artist_mapping_path)
        analyzer.load_artist_mapping()
        analyzer.process_play_activity()
        analyzer.generate_report(output_path)

        print("\n✓ Analysis complete!")
        print(f"✓ Data saved to {output_path}")

    except FileNotFoundError as e:
        print(f"Error: Could not find required file")
        print(f"  {e}")
        print("\nPlease ensure these files exist in the current directory:")
        print(f"  - {play_activity_path}")
        print(f"  - {container_details_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
