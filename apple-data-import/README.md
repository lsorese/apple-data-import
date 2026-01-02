# Apple Music Data Import

Place your new Apple Music CSV files here when you want to update the data.

## Required Files

Only these 2 files are needed:

1. **Apple Music Play Activity.csv** - Main play history data
2. **Apple Music - Container Details.csv** - Album and artist information

## How to Update

1. Download your latest Apple Music data from Apple
2. Copy the 2 required CSV files to this folder
3. Run the import script:
   ```bash
   ./import_apple_data.sh
   ```

That's it! The script will automatically process the data and update the viewer.

## What Gets Updated

- `apple-music-watch-viewer/public/data.json` - The data file used by the viewer

## Optional Enhancement

After running the import, you can optionally fetch missing artist information:
```bash
python3 fetch_artists.py
./import_apple_data.sh  # Re-run to include the new artist data
```
