# Apple Music + Strava Integration Features

## Overview
This application displays your Apple Music listening history from your Apple Watch, enhanced with running data from Strava.

## Features Implemented

### 📊 Expandable Run Details
- Click the 📊 button in the "Run" column to expand detailed running metrics
- Shows: Distance, Pace, Moving Time, Elevation Gain, Heart Rate (avg/max)
- Expandable rows keep the table compact while providing detailed information

### 🏃 Multi-Album Run Detection
- Automatically detects when multiple albums were listened to on the same run
- Shows a badge: "🎵 X albums" when multiple albums are on one run
- Lists all albums from that run in the expanded details
- Current album is highlighted in green

### 📈 Running Metrics Displayed
- **Distance**: Total miles run
- **Pace**: Minutes per mile (e.g., "8:30/mi")
- **Moving Time**: Active running time (MM:SS format)
- **Elevation Gain**: Total meters climbed (if available)
- **Average Heart Rate**: Average BPM during the run (if available)
- **Max Heart Rate**: Peak BPM during the run (if available)

### 🎯 Sortable Columns
- **Album**: Alphabetical sort
- **Artist**: Alphabetical sort
- **Completion**: Sort by listening completion percentage
- **Date**: Sort by first listen date (default: newest first)
- **Run**: Sort to show albums with/without run data
- **★ (Starred)**: Sort favorites to the top

### 🔍 Filtering
- **Search**: Filter by album name or artist name
- **Year Filter**: View albums from specific years

### ⭐ Favorites
- Star your favorite albums for easy access
- Stars are preserved across data refreshes

## Data Integration

### Match Rate
- **347 out of 467 albums** (74.3%) matched with Strava runs
- Matches albums within ±30 minutes of run start time

### Data Sources
- **Apple Music**: Play activity, completion rates, timestamps
- **Strava**: Running metrics, heart rate, elevation
- **Manual**: Artist information from Container Details CSV

## Visual Design

### Color Scheme
- Background: Black (#000)
- Text: Light gray (#d0d0d0)
- Accent: Green (#00ff00)
- Borders: Dark gray (#333, #222)

### Run Details Styling
- Dark background (#0a0a0a)
- Green border top to indicate expandable section
- Grid layout for stats (responsive)
- Green accent for values
- Current album highlighted in green when showing multi-album runs

### Visual Grouping
- Albums from the same run show in the "Albums on this run" section
- Current album has green left border
- Other albums from same run have gray borders
- Shows artist name in lighter gray

## Mobile Responsive
- Table converts to card layout on mobile
- All data remains accessible
- Expandable rows work on touch devices

## Future Enhancement Ideas

### Additional Comparisons
1. **Album Duration vs Run Duration**
   - Show if you finished the album
   - Display remaining/extra time

2. **Songs Per Mile**
   - Calculate tracks/mile ratio
   - Show pacing through the album

3. **Weather Data**
   - Temperature, conditions during run
   - Requires additional API integration

4. **Run Location**
   - Show map or location name
   - Group runs by route

5. **Time of Day Analysis**
   - Morning vs evening listening patterns
   - Energy levels (heart rate) by time

6. **Album Intensity Score**
   - Correlate genre/mood with pace/HR
   - Discover which albums push you harder

7. **Streak Tracking**
   - Consecutive days listening
   - Most-played albums over time

8. **Playlist Generation**
   - Auto-generate playlists based on run distance
   - "5K albums" vs "10K albums"

## Technical Details

### File Structure
```
apple-music-watch-viewer/
  public/
    index.html          - Main HTML structure
    app.js              - JavaScript logic, rendering
    styles.css          - All styling
    data.json           - Combined music + run data
```

### Scripts
- `analyze_music_watch.py` - Processes Apple Music data
- `fetch_strava_data.py` - Fetches and merges Strava data
- `get_strava_token.py` - Helper for OAuth tokens

### Data Flow
1. Export Apple Music data
2. Run `analyze_music_watch.py` to process music data
3. Run `fetch_strava_data.py` to add Strava metrics
4. Frontend reads `data.json` and renders

## Usage Tips

1. **Finding Multi-Album Runs**
   - Sort by "Run" column
   - Look for 🎵 badges in expanded details

2. **Analyzing Performance**
   - Sort by pace to find your fastest albums
   - Check heart rate data to see effort levels

3. **Tracking Progress**
   - Use year filter to compare yearly stats
   - Star exceptional runs for easy reference

4. **Searching**
   - Search by artist to find all their albums
   - Search by album name for specific listens
