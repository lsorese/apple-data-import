# Star/Favorite Albums Feature

## Overview

You can now star/favorite albums in your listening history. Starred albums are displayed with a green star (★) in the viewer, while unstarred albums show a grey star.

## How to Star Albums

Stars are managed via the `toggle_star.py` command-line tool:

### Interactive Search
```bash
./toggle_star.py search
```
This will prompt you to search for an album, then toggle its star status.

### List Starred Albums
```bash
./toggle_star.py list
```
Shows all currently starred albums.

### Toggle Specific Album
```bash
./toggle_star.py toggle "Album Name"
```
Toggles the star for a specific album by name.

## How It Works

1. **Data Storage**: Star status is stored in the `starred` field in `apple-music-watch-viewer/public/data.json`
2. **Preservation**: When you regenerate data with `analyze_music_watch.py`, existing starred states are preserved
3. **Viewer Display**:
   - Green star (★) = starred album
   - Grey star (★) = unstarred album
   - Star column is sortable (click header)

## Examples

```bash
# Find and star an album
./toggle_star.py search
# > Search for album or artist: cloud cult
# > Found: The Meaning Of 8 - Cloud Cult
# > Current state: unstarred
# > Toggle star? (y/n): y
# > ✓ The Meaning Of 8 is now starred

# List all starred albums
./toggle_star.py list
# > Starred albums (2):
# >   ★ Former Teenage Big Deal - Logan from the Internet
# >   ★ The Meaning Of 8 - Cloud Cult

# Unstar an album
./toggle_star.py toggle "Former Teenage Big Deal"
# > ✓ Former Teenage Big Deal is now unstarred
```

## Technical Details

- Stars are **not clickable** in the web viewer
- All star management is done via the command-line script
- Star states persist across data regeneration
- Mobile-responsive design included
- Star column can be sorted alongside other columns

## Data Format

Each album in `data.json` has a `starred` field:

```json
{
  "album_name": "Former Teenage Big Deal",
  "artist_name": "Logan from the Internet",
  "starred": true,
  ...
}
```

Default value is `false` for new albums.
