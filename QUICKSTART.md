# Quick Start - Updating Apple Music Data

## Simple 3-Step Process

### 1. Download your latest Apple Music data from Apple

Get your data export from Apple Privacy portal

### 2. Copy the required CSV files

Copy these 2 files to the `apple-data-import/` folder:
- `Apple Music Play Activity.csv`
- `Apple Music - Container Details.csv`

### 3. Run the import script

```bash
./import_apple_data.sh
```

Done! Your viewer is now updated with the latest data.

---

## What This Does

The script will:
1. ✓ Verify the required files are present
2. ✓ Copy them to the working directory
3. ✓ Analyze your Apple Watch listening history
4. ✓ Generate `apple-music-watch-viewer/public/data.json`

## View Your Data

Open the viewer:
```bash
open apple-music-watch-viewer/public/index.html
```

Or run it locally:
```bash
cd apple-music-watch-viewer
npm run dev
```

## Optional: Fetch Missing Artists

If some albums are missing artist information, you can fetch them from Apple's API:

```bash
python3 fetch_artists.py
./import_apple_data.sh  # Re-run to include the new data
```

Note: This may be slow due to API rate limits.

---

## Files You Need to Keep

**Source Data (in apple-data-import/):**
- `Apple Music Play Activity.csv` - Your complete listening history
- `Apple Music - Container Details.csv` - Album and artist metadata

**Scripts:**
- `import_apple_data.sh` - Main import script
- `analyze_music_watch.py` - Analysis engine
- `fetch_artists.py` - Optional artist fetcher

**Viewer:**
- `apple-music-watch-viewer/` - The web viewer app

Everything else is generated and can be recreated.
